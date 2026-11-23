# from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition
from langchain_core.messages import HumanMessage, SystemMessage
from agents.llm.llm import get_llm
from agents.tools.tavily import tavily_search_tool
from agents.person.graph import person_graph
from .constants import MESSAGES
from .models import MoneyAmountState, MoneyState

# load_dotenv()

memory = MemorySaver()
tools = [tavily_search_tool]
llm, llm_with_tools, _ = get_llm(tools=tools)


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def get_money_transfer_graph(checkpointer):
    def main_node(state: MoneyState):
        print("******* main_node")
        response = llm_with_tools.invoke(state["messages"])
        state["messages"].append(response)
        return state

    def router_node(state: MoneyState):
        print("******* router_node")
        if "amount" not in state or state["amount"] is 0:
            return "amount_node"
        if "currency" not in state or state["currency"] is None:
            return "currency_node"
        return END

    def amount_node2(state: MoneyState):
        if "amount" not in state or state["amount"] is None:
            state["messages"].append(
                SystemMessage(
                    content="Please provide the amount for the money transfer."
                )
            )
        return state

    def amount_node(state: MoneyState):
        print("******* amount_node")
        if "amount" not in state or state["amount"] is 0:
            print("******* amount_node: asking for amount")
            response = llm.with_structured_output(state["messages"])
            print("******* amount_node: response", response)
            return {
                "messages": state["messages"],
                "amount": response.amount,
            }
            # state["messages"].append(
            #     AIMessage(
            #         content="Please provide the amount for the money transfer.2222222"
            #     )
            # )
        return state

    def currency_node(state: MoneyState):
        if "currency" not in state or state["currency"] is None:
            state["messages"].append(
                SystemMessage(
                    content="Please provide the currency for the money transfer."
                )
            )
        return state

    graph_builder = StateGraph(MoneyState)
    graph_builder.add_node("main_node", main_node)
    graph_builder.add_node("router_node", router_node)
    graph_builder.add_node("amount_node", amount_node)
    graph_builder.add_node("currency_node", currency_node)
    # graph_builder.add_edge("main_node", "router_node")
    graph_builder.add_edge("router_node", "amount_node")
    graph_builder.add_edge("router_node", "currency_node")
    graph_builder.add_conditional_edges(
        "main_node",
        router_node,
        # {
        #     "amount_node": lambda state: "amount" not in state or state["amount"] is None,
        #     "currency_node": lambda state: "currency" not in state or state["currency"] is None,
        #     END: lambda state: "amount" in state and state["amount"] is not None and "currency" in state and state["currency"] is not None,
        # },
    )
    graph_builder.set_entry_point("main_node")
    graph = graph_builder.compile(checkpointer=checkpointer)

    return graph


def get_money_transfer_graph2():

    def money_entry_node(state: MoneyState):
        print("******* money_entry_node")
        # if MESSAGES not in state or state[MESSAGES] is None:
        #   print("iiiiiiiiiiiiiiiiis null")
        #   state[MESSAGES] = []
        #   state["amount"] = 0
        #   state["country"] = ""
        #   state["currency"] = ""
        # if state['amount'] is None:
        #     return {"messages": [{"role": "assistant", "content": "**Error** Missing required field: amount"}]}

        # if state['country'] is None:
        #     return {"messages": [{"role": "assistant", "content": "**Error** Missing required field: country"}]}
        # if state['currency'] is None:
        #     return {"messages": [{"role": "assistant", "content": "**Error** Missing required field: currency"}]}
        # response2 = structured_llm.invoke(state["messages"])
        # print(response2)
        response = llm_with_tools.invoke(state["messages"])
        # print(response)
        # if "process_started" not in state or state["process_started"] is False:
        #     state["process_started"] = True
        state["messages"].append(response)
        return state

    def amount_validation_node(state: MoneyState):
        # Extract HumanMessage from state
        human_message = None
        for message in state["messages"]:
            if isinstance(message, HumanMessage):
                human_message = message
                break
        print("**** Human message", human_message)
        if human_message and is_float(human_message.content):
            state["amount"] = float(human_message.content)
            # if "process_started" in state and state["process_started"] is True and "amount" not in state:
            state["amount"] = human_message.content
            state["messages"].append(
                SystemMessage(
                    content=f"Ask the user for the country and city where the money should be sent to."
                )
            )
            state["messages"].append(
                HumanMessage(content=f"The user has provided amount: {state['amount']}")
            )
            # print("state after setting amount", state)
            # if "process_started" not in state or state["process_started"] is False:
            # state["process_started"] = True
            print("******* returning user_name_node")
            return "user_name_node"
        # if state is not None and state["amount"] is None:
        #     state["amount"] = human_message.content
        # print("****human_message", state)
        return "money_entry_node"

    def user_name_node(state: MoneyState):
        # Extract HumanMessage from state
        if "amount" in state:
            state["messages"].append(
                SystemMessage(content=f"Ask the user for his name")
            )
            state["messages"].append(
                HumanMessage(content=f"The user has provided amount: {state['amount']}")
            )
            response = llm_with_tools.invoke(state["messages"])
            state["messages"].append(response)
            print("******* state in name node", state)
        return state

    def name_validation_node(state: MoneyState):
        print("******* name_validation_node")
        # print("******* state", state["messages"])

        # Extract HumanMessage from state
        human_message = None
        for message in state["messages"]:
            if isinstance(message, HumanMessage):
                human_message = message
                break
        if human_message and is_float(human_message.content):
            state["amount"] = float(human_message.content)
            # if "process_started" in state and state["process_started"] is True and "amount" not in state:
            state["amount"] = human_message.content
            state["messages"].append(
                SystemMessage(
                    content=f"Ask the user for the country and city where the money should be sent to."
                )
            )
            state["messages"].append(
                HumanMessage(content=f"The user has provided amount: {state['amount']}")
            )
            # print("name_validation_node")
            # if "process_started" not in state or state["process_started"] is False:
            # state["process_started"] = True
            return END
        # if state is not None and state["amount"] is None:
        #     state["amount"] = human_message.content
        # print("****human_message", state)
        return END

    graph_builder = StateGraph(MoneyState)

    # graph_builder.add_node("validation_agent", validation_agent)
    # graph_builder.add_conditional_edges("validation_agent", {
    #     "money_entry_node": lambda output: output.get("status") == "valid",
    #     END: lambda output: isinstance(output, dict) and output.get("status") == "error"
    # })
    graph_builder.add_node("money_entry_node", money_entry_node)
    graph_builder.set_entry_point("money_entry_node")
    graph_builder.add_node("tools", ToolNode(tools=tools))
    graph_builder.add_conditional_edges("money_entry_node", amount_validation_node)
    graph_builder.add_edge("money_entry_node", "tools")
    graph_builder.add_edge("tools", "money_entry_node")
    graph_builder.add_node("user_name_node", person_graph)
    graph_builder.add_conditional_edges("user_name_node", name_validation_node)
    # graph_builder.add_edge("user_name_node", END)
    graph = graph_builder.compile(checkpointer=memory, interrupt_before=["tools"])

    return graph


def get_money_transfer_graph(checkpointer):
    def main_node(state: MoneyState):
        print("***** state", state)
        if state.get("amount") in (None, 0):
            return Command(goto="amount_node")
        if not state.get("currency"):
            return Command(goto="currency_node")
        return Command(goto=END)

    def amount_node2(state: MoneyState):
        if "amount" not in state or state["amount"] is None:
            state["messages"].append(
                SystemMessage(
                    content="Please provide the amount for the money transfer."
                )
            )
        return state

    def amount_node(state: MoneyState):
        print("11111")
        if state.get("amount") not in (None, 0):
            return {
                            "messages": [
                                AIMessage(
                                    content=(
                                        "What amount would you like to transfer? "
                                        "Please enter a number greater than 56666."
                                    )
                                )
                            ]
                        }
        print("22222")
        latest_user_message = next(
            (
                message
                for message in reversed(state["messages"])
                if isinstance(message, HumanMessage)
            ),
            None,
        )
        print("33333")
        if latest_user_message is None:
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "What amount would you like to transfer? "
                            "Please enter a number greater than 5."
                        )
                    )
                ]
            }

        extraction_prompt = SystemMessage(
            content=(
                "Extract the transfer amount explicitly provided by the user from "
                "their message. Return null if no amount is provided. Do not infer "
                "or convert an amount."
            )
        )
        response = llm.with_structured_output(AmountExtraction).invoke(
            [extraction_prompt, latest_user_message]
        )
       
        if response.amount is None:
            reply = (
                "What amount would you like to transfer? "
                "Please enter a number greater than 5."
            )
            # print("********* amount", response.amount, state["messages"])
            return {"messages": [AIMessage(content=reply)]}

        if not math.isfinite(response.amount) or response.amount <= 5:
            reply = (
                "The minimum transfer amount is 5. "
                "Please enter an amount greater than 5."
            )
            return {"messages": [AIMessage(content=reply)]}
        print("******* last")
        return {"amount": response.amount}

    def currency_node(state: MoneyState):
        return {
            "messages": [
                AIMessage(content="What currency would you like to use for the transfer?")
            ]
        }

    graph_builder = StateGraph(MoneyState)
    graph_builder.add_node("main_node", main_node)
    graph_builder.add_node("amount_node", amount_node)
    graph_builder.add_node("currency_node", currency_node)

    graph_builder.set_entry_point("main_node")
    graph = graph_builder.compile(checkpointer=checkpointer)

    return graph