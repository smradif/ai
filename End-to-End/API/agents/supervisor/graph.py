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
    get_last_user_message,
    get_transfer_url,
    is_valid_amount,
    is_valid_currency,
)

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
    action: Literal[
        "confirm",
        "change_amount",
        "change_currency",
        "not_confirmed",
    ]


def get_supervisor_graph(checkpointer):
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
        if state.get("awaiting_confirmation"):
            return Command(
                goto="confirmation_node",
                update={"amount": response.amount},
            )
        response = Command(goto="supervisor_node", update={"amount": response.amount})
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
        if state.get("awaiting_confirmation"):
            return Command(
                goto="confirmation_node",
                update={"currency": response.currency},
            )
        response = Command(
            goto="supervisor_node",
            update={"currency": response.currency},
        )
        return response

    def confirmation_node(state: MoneyState):
        if state.get("awaiting_confirmation"):
            reply = (
                f"Updated transfer: amount {state.get('amount')}, currency "
                f"{state.get('currency')}. Are you happy to proceed? Say yes to "
                "confirm, or request another change."
            )
            return {
                "awaiting_confirmation": False,
                "confirmation": False,
                "messages": [AIMessage(content=reply)],
            }

        latest_user_message = get_last_user_message(state["messages"])
        prompt = SystemMessage(
            content=(
                "Determine the user's intent about the proposed transfer. Return "
                "'confirm' only for an explicit yes/approval. Return 'change_amount' "
                "if they want to edit the amount, and 'change_currency' if they want "
                "to edit the currency, including when they provide a replacement "
                "value in the same message. Otherwise return 'not_confirmed'. "
                f"The current amount is {state.get('amount')}; the current currency "
                f"is {state.get('currency')}."
            )
        )
        response = llm.with_structured_output(ConfirmationState).invoke(
            [prompt, latest_user_message]
        )

        if response.action == "change_amount":
            return Command(
                goto="amount_node",
                update={
                    "amount": None,
                    "confirmation": False,
                    "awaiting_confirmation": True,
                },
            )
        if response.action == "change_currency":
            return Command(
                goto="currency_node",
                update={
                    "currency": None,
                    "confirmation": False,
                    "awaiting_confirmation": True,
                },
            )
        if response.action == "confirm":
            return Command(
                goto="supervisor_node",
                update={"confirmation": True},
            )

        reply = (
            f"You have entered amount: {state.get('amount')} and currency: "
            f"{state.get('currency')}. Please say yes to confirm, or tell me "
            "the new amount or currency you want to use."
        )
        return {
            "confirmation": False,
            "messages": [AIMessage(content=reply)],
        }

    graph_builder = StateGraph(MoneyState)
    graph_builder.add_node("supervisor_node", supervisor_node)
    graph_builder.add_node("amount_node", amount_node)
    graph_builder.add_node("currency_node", currency_node)
    graph_builder.add_node("confirmation_node", confirmation_node)

    graph_builder.set_entry_point("supervisor_node")
    graph = graph_builder.compile(checkpointer=checkpointer)

    return graph
