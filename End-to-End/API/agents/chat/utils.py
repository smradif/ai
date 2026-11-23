import json
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from typing_extensions import List, TypedDict


class Conversation(TypedDict):
    content: str
    type: str


def convert_to_conversation(messages: List[BaseMessage]):
    conversations: List[Conversation] = []
    title = ""
    for message in messages:
        if isinstance(message, AIMessage) and len(message.content) > 0:
            conversations.append({"content": message.content, "type": "AIMessage"})
        elif isinstance(message, HumanMessage) and len(message.content) > 0:
            if len(title) == 0:
                title = message.content[:100]
            conversations.append({"content": message.content, "type": "HumanMessage"})

    return {"title": title, "conversation": json.dumps(conversations)}


def convert_to_messages(conversationRaw: str) -> List[BaseMessage]:
    messages: List[Conversation] = []
    conversations = [
        Conversation(**conversation) for conversation in json.loads(conversationRaw)
    ]
    for conversation in conversations:
        if conversation["type"] == "AIMessage":
            messages.append(AIMessage(content=conversation["content"]))
        elif conversation["type"] == "HumanMessage":
            messages.append(HumanMessage(content=conversation["content"]))
    return messages
