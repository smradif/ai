from logger.logger import LoggerInterface
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from agents.orchestrator.models import TicketState, CategoryState
from transformers import pipeline

id_to_label = {
    "LABEL_0": 'blling', 
    "LABEL_1": 'Feature Request', 
    "LABEL_2": 'general', 
    "LABEL_3": 'technical'
}

def get_classifier_node(llm, logger: LoggerInterface):
    async def node(state: TicketState):
        logger.info("Classifier node")
        classifier = pipeline("text-classification", model="Dragneel/ticket-classification-v1")
        raw_result = classifier(state["query"])
        result =  id_to_label.get(raw_result[0]["label"]) if len(raw_result) > 0 else "general"
        return {
            **state,
            "category": result,
            "messages": [AIMessage(content=result)],
        }

    return node
