from logger.logger import LoggerInterface
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from ..models import TicketState


def get_faq_node(llm, retriever, logger: LoggerInterface):
    async def node(state: TicketState):
        logger.info("FAQ node")
        query = state["query"]
        prompt = SystemMessage(content=("""
                       You are a FAQ matching specialist.
                       If customer query matches any FAQ, return ONLY the answer.
                       If no match, respond 'NO_MATCH'.
                       Be strict - only match if directly relevant.
                       """))
        faq_list = await retriever.ainvoke(query)
        result = await llm.ainvoke(
            [prompt, HumanMessage(content=f"Customer query: {query} FAQs: {faq_list}")]
        )

        faq = result.content if "NO_MATCH" not in result.content else ""

        return {
            **state,
            "faq_match": faq,
            "messages": [AIMessage(content=result.content)],
        }

    return node
