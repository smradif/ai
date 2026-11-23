from logger.logger import LoggerInterface
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from agents.orchestrator.models import TicketState


def get_general_node(llm, logger: LoggerInterface):
    async def node(state: TicketState):
        logger.info("General node")
        prompt = SystemMessage(content=("""
                    You are a general support specialist.
                    Analyze the inquiry and provide:
                    1. Relevant information
                    2. Clear guidance
                    3. Next steps if needed
                    Keep response helpful and concise.
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
