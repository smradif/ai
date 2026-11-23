# from dotenv import load_dotenv

from typing import Literal
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.types import Command
from agents.llm.llm import get_llm
from .constants import MINIMUM_TRANSFER_AMOUNT, SUPPORTED_CURRENCIES
from .models import MoneyState
from .utils import (
    get_transfer_url,
    is_valid_amount,
    is_valid_currency,
)
from agents.utils import get_last_user_message

llm, _, _ = get_llm()


class SupervisorDecision(BaseModel):
    next_node: Literal["amount_node", "currency_node", "done"]


class AmountExtraction(BaseModel):
    """Extract the amount from the user input"""

    amount: float | None = None


class CurrencyExtraction(BaseModel):
    f"""Extract the currency from the user input. The currency should be one of {SUPPORTED_CURRENCIES}"""
    currency: str | None = None


class ConfirmationState(BaseModel):
    f"""Ask the user to confirm their selection"""
    confirmation: bool | None = None


def get_money_transfer_graph(checkpointer):
    def main_node2(state: MoneyState):
        supervisor = llm.with_structured_output(SupervisorDecision)
        decision = supervisor.invoke(
            [
                SystemMessage(
                    content=(
                        "You are the supervisor for a money-transfer workflow. "
                        "Choose the next worker based on the conversation and the "
                        "current state. Route to amount_node when the amount has not "
                        "been captured in state (missing, null, or 0). Once the amount "
                        "is captured, route to currency_node when currency is missing "
                        "or null. Choose done only when both amount and currency are "
                        "present in state. Do not invent values."
                        f"\nCurrent amount: {state.get('amount')!r}"
                        f"\nCurrent currency: {state.get('currency')!r}"
                    )
                ),
                *state["messages"],
            ]
        )
        destination = END if decision.next_node == "done" else decision.next_node
        response = Command(
            goto=destination,
            update={
                "messages": [
                    # AIMessage(
                    #     content=(
                    #         "What amount would you like to transfer? "
                    #         "Please enter a number greater than 5."
                    #     )
                    # )
                ]
            },
        )
        return response

    def supervisor_node(state: MoneyState):
        if not state.get("amount"):
            return Command(goto="amount_node", update={"messages": []})
        if not state.get("currency"):
            return Command(goto="currency_node", update={"messages": []})
        if not state.get("confirmation") or state.get("confirmation") == False:
            return Command(goto="confirmation_node", update={"messages": []})
        return Command(
            goto=END,
            update={
                "messages": [
                    AIMessage(
                        content=f"All done. Please use the link to complete the process. {get_transfer_url(state)}"
                    )
                ]
            },
        )

    def amount_node(state: MoneyState):
        latest_user_message = get_last_user_message(state["messages"])
        prompt = SystemMessage(
            content=(
                "Extract the transfer amount explicitly provided by the user from their message."
                "Return null if the amount is not provided. Do not infer "
                "or convert an amount."
            )
        )
        response = llm.with_structured_output(AmountExtraction).invoke(
            [prompt, latest_user_message]
        )

        if response.amount is None:
            reply = f"""What amount would you like to transfer? 
                "Please enter a number greater than {MINIMUM_TRANSFER_AMOUNT}"""
            return {"messages": [AIMessage(content=reply)]}

        if not is_valid_amount(response.amount):
            reply = f"""The minimum transfer amount is {MINIMUM_TRANSFER_AMOUNT}. 
                Please enter an amount greater than {MINIMUM_TRANSFER_AMOUNT}."""
            return {"messages": [AIMessage(content=reply)]}
        response = Command(
            goto="supervisor_node",
            update={"amount": response.amount},
        )
        return response

    def currency_node(state: MoneyState):
        latest_user_message = get_last_user_message(state["messages"])
        prompt = SystemMessage(
            content=(
                f"""Extract the transfer currency explicitly provided by the user from 
                their message. The supported currencies are: { SUPPORTED_CURRENCIES} Return null if no currency is provided."""
            )
        )
        response = llm.with_structured_output(CurrencyExtraction).invoke(
            [prompt, latest_user_message]
        )

        if response.currency is None:
            reply = f"""What currency you want to transfer to?
                Please enter one of those: { SUPPORTED_CURRENCIES}"""
            return {"messages": [AIMessage(content=reply)]}
        if not is_valid_currency(response.currency):
            reply = f"""The currency you entered is not supported
                We support {SUPPORTED_CURRENCIES}"""
            return {"messages": [AIMessage(content=reply)]}
        response = Command(
            goto="supervisor_node",
            update={"currency": response.currency},
        )
        return response

    def confirmation_node(state: MoneyState):
        latest_user_message = get_last_user_message(state["messages"])
        prompt = SystemMessage(
            content=(
                f"""Extract a confirmation from the user they are happy to go ahead with the transfer. The user should replay should contain Yes or No"""
            )
        )
        response = llm.with_structured_output(ConfirmationState).invoke(
            [prompt, latest_user_message]
        )

        if response.confirmation is False:
            reply = f"""You have entered amount: {state.get('amount')} and currency: {state.get('currency')}. Please confirm you are happy to go ahead?"""
            return {"messages": [AIMessage(content=reply)]}
        response = Command(
            goto="supervisor_node",
            update={"confirmation": response.confirmation},
        )
        return response

    graph_builder = StateGraph(MoneyState)
    graph_builder.add_node("supervisor_node", supervisor_node)
    graph_builder.add_node("amount_node", amount_node)
    graph_builder.add_node("currency_node", currency_node)
    graph_builder.add_node("confirmation_node", confirmation_node)

    graph_builder.set_entry_point("supervisor_node")
    graph = graph_builder.compile(checkpointer=checkpointer)

    return graph
