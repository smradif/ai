# from dotenv import load_dotenv
from typing import Literal
from pydantic import BaseModel
from langchain.agents import create_agent
from langgraph.graph import StateGraph, END
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import Command
from agents.llm.llm import get_llm
from langchain.tools import tool
from langchain.agents.middleware import HumanInTheLoopMiddleware
from datetime import date
from .tools import create_calendar_event, get_available_time_slots, send_email
from .constants import CREATE_CALENDAR_PROMPT, SEND_EMAIL_PROMPT, SUPERVISOR_PROMPT

llm, _, _ = get_llm()

calendar_agent = create_agent(
    model=llm,
    tools=[create_calendar_event, get_available_time_slots],
    system_prompt=CREATE_CALENDAR_PROMPT,
)

email_agent = create_agent(
    model=llm,
    tools=[send_email],
    system_prompt=SEND_EMAIL_PROMPT,
)


@tool
def schedule_events(request: str) -> str:
    """Schedule calendar events using natural language.

    Use this when the user wants to create, modify, or check calendar appointments.
    Handles date/time parsing, availability checking, and event creation.

    Input: Natural language scheduling request (e.g., 'meeting with design team
    next Tuesday at 2pm')
    """
    result = calendar_agent.invoke({"messages": [HumanMessage(content=request)]})

    return result["messages"][-1].content


@tool
def manage_emails(request: str) -> str:
    """Send emails using natural language.

    Use this when the user wants to send notifications, reminders, or any email
    communication. Handles recipient extraction, subject generation, and email
    composition.

    Input: Natural language email request (e.g., 'send them a reminder about
    the meeting')
    """
    result = email_agent.invoke({"messages": [HumanMessage(content=request)]})

    return result["messages"][-1].content


def get_calendar_graph():
    supervisor = create_agent(
        model=llm,
        tools=[schedule_events, manage_emails],
        system_prompt=SUPERVISOR_PROMPT,
        # checkpointer=checkpointer
    )
    return supervisor
