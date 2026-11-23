from logger.logger import LoggerInterface
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from agents.orchestrator.models import TicketState


def get_escalation_node(llm, logger: LoggerInterface):
    async def node(state: TicketState):
        logger.info("Escalation node")
        prompt = SystemMessage(content=("""
                Evaluate if ticket needs escalation to human.
                Escalate if:
                - Complex problem requiring domain expertise
                - Customer very frustrated
                - Unusual/rare case
                - Multiple failed attempts
                Respond: 'YES' or 'NO'
                    """))
        result = await llm.ainvoke([prompt, HumanMessage(content=f"""
                Customer query: {state["query"]},
                Category: {state["category"]},
                priority: {state["priority"]},
                """)])

        return {
            "needs_escalation": result.content,
            "messages": [AIMessage(content=result.content)],
        }

    return node
