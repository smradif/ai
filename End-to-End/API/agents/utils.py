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
