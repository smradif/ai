import os
import math
from urllib.parse import urlencode
from langchain.messages import HumanMessage
from .models import MoneyState
from .constants import MINIMUM_TRANSFER_AMOUNT, SUPPORTED_CURRENCIES


def get_transfer_url(state: MoneyState) -> str:
    url = os.getenv("MONEY_TRANSFER_URL")
    code = os.getenv("MONEY_TRANSFER_CODE")
    query_params = urlencode(
        {
            "code": code,
            "amount": state.get("amount"),
            "currency": state.get("currency"),
        }
    )
    full_url = f"{url}?{query_params}"
    return full_url


def get_last_user_message(messages: list):
    latest_user_message = next(
        (
            message
            for message in reversed(messages)
            if isinstance(message, HumanMessage)
        ),
        None,
    )
    return latest_user_message

def is_valid_amount(amount: float):
    return math.isfinite(amount) and amount >= MINIMUM_TRANSFER_AMOUNT


def is_valid_currency(currency: str):
    return currency in SUPPORTED_CURRENCIES