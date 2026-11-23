from logger.logger import LoggerInterface
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from agents.orchestrator.models import TicketState


def get_technical_node(llm, logger: LoggerInterface):
    async def node(state: TicketState):
        logger.info("Technical node")
        prompt = SystemMessage(content=("""
                    You are a technical support expert.
                    Analyze the issue and provide:
                    1. Problem diagnosis
                    2. Step-by-step solution
                    3. Prevention tips
                    Keep response concise and actionable.
                    """))
        result = await llm.ainvoke(
            [
                prompt,
                HumanMessage(content=f"""
                    Customer query: {state["query"]},
                    FAQ Match: {state["faq_match"]},
                    priority: {state["priority"]},
                    """),
            ]
        )

        return {
            "resolution": result.content,
            "messages": [AIMessage(content=result.content)],
        }

    return node
