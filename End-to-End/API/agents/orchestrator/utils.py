from langchain.messages import HumanMessage


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


def get_priority(query: str):
    if any(k in query for k in ["urgent", "critical", "asap", "emergency"]):
        return "high"
    if any(k in query for k in ["question", "wondering"]):
        return "low"
    return "medium"
