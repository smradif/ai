from logger.logger import LoggerInterface
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from agents.orchestrator.models import TicketState


def get_billing_node(llm, logger: LoggerInterface):
    async def node(state: TicketState):
        logger.info("Billing node")
        prompt = SystemMessage(content=("""
                    You are a billing support specialist.
                    Analyze the billing issue and provide:
                    1. Explanation of the charge/issue
                    2. Resolution steps
                    3. Reference information
                    Keep response professional and clear.
                    """))
        result = await llm.ainvoke([prompt, HumanMessage(content=f"""
                Customer query: {state["query"]},
                FAQ Match: {state["faq_match"]},
                priority: {state["priority"]},
                """)])

        return {
            "resolution": result.content,
            "messages": [AIMessage(content=result.content)],
        }

    return node
