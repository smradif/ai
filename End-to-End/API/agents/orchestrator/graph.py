from langgraph.graph import StateGraph, END
from agents.llm.llm import get_llm
from .models import TicketState
from agents.orchestrator.RAG.vector import retriever
from logger.logger import get_logger
from agents.orchestrator.nodes import (
    billing_node,
    classifier_node,
    escalation_node,
    faq_node,
    general_node,
    orchestrator_node,
    response_node,
    technical_node,
)

llm, _, _ = get_llm()

logger = get_logger()


def get_orchestrator_graph(checkpointer=None):
    orchestrator = orchestrator_node.get_orchestrator_node(llm, logger=logger)
    faq = faq_node.get_faq_node(llm, retriever=retriever, logger=logger)
    classifier = classifier_node.get_classifier_node(llm, logger=logger)
    technical = technical_node.get_technical_node(llm, logger=logger)
    billing = billing_node.get_billing_node(llm, logger=logger)
    general = general_node.get_general_node(llm, logger=logger)
    escalation = escalation_node.get_escalation_node(llm, logger=logger)
    response = response_node.get_response_node(llm, logger=logger)

    def classifier_route(state: TicketState):
        category = state["category"]
        if category in "technical":
            return "technical_node"
        if category in "billing":
            return "billing_node"
        return "general_node"

    graph_builder = StateGraph(TicketState)
    graph_builder.add_node("orchestrator_node", orchestrator)
    graph_builder.add_node("faq_node", faq)
    graph_builder.add_node("classifier_node", classifier)
    graph_builder.add_node("technical_node", technical)
    graph_builder.add_node("billing_node", billing)
    graph_builder.add_node("general_node", general)
    graph_builder.add_node("escalation_node", escalation)
    graph_builder.add_node("response_node", response)

    graph_builder.set_entry_point("orchestrator_node")
    graph_builder.add_edge("orchestrator_node", "faq_node")
    graph_builder.add_edge("faq_node", "classifier_node")
    graph_builder.add_conditional_edges("classifier_node", classifier_route)
    graph_builder.add_edge("technical_node", "escalation_node")
    graph_builder.add_edge("billing_node", "escalation_node")
    graph_builder.add_edge("general_node", "escalation_node")
    graph_builder.add_edge("escalation_node", "response_node")
    graph_builder.add_edge("response_node", END)

    # graph = graph_builder.compile(checkpointer=checkpointer)
    graph = graph_builder.compile(checkpointer=checkpointer)

    return graph
