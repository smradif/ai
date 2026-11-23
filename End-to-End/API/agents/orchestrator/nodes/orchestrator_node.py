from datetime import datetime
from logger.logger import LoggerInterface
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from agents.orchestrator.models import TicketState
from agents.orchestrator.utils import get_priority


def get_orchestrator_node(llm, logger: LoggerInterface):
    async def node(state: TicketState):
        logger.info(source="Orchestrator node")
        prompt = SystemMessage(content=("""
                       You are a customer support specialist.
                       Extract from customer query:
                        1. Main issue
                        2. Product/service mentioned
                        3. Urgency (low/medium/high)
                        4. Sentiment (positive/neutral/negative)
                        Provide concise summary.
                        """))
        result = await llm.ainvoke([prompt, HumanMessage(content=state["query"])])

        priority = get_priority(state["query"].lower())

        return {
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "messages": [AIMessage(content=result.content)],
        }

    return node
