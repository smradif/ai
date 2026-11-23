from logger.logger import LoggerInterface
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from agents.orchestrator.models import TicketState


def get_response_node(llm, logger: LoggerInterface):
    async def node(state: TicketState):
        logger.info("Response node")
        prompt = SystemMessage(content=("""
                Generate professional customer support response.
                Include:
                - Thank customer for reaching out
                - Acknowledge their issue
                - Provide solution/next steps
                - Offer further assistance
                Tone: Empathetic, professional, concise.
                    """))
        result = await llm.ainvoke(
            [
                prompt,
                HumanMessage(content=f"""
                    Customer Query: {state["query"]},
                    Resolution: {state["resolution"]},
                    Category: {state["category"]}
                    """),
            ]
        )

        return {
            **state,
            "final_response": result.content,
            "messages": [AIMessage(content=result.content)],
        }

    return node
