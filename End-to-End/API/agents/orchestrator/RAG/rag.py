from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from agents.money.RAG.vector import retriever


def get_open_chat_results(question):
    model = OllamaLLM(model="gpt-oss:20b")

    template = """
    You are a helpful money transfer assistant who helps gather information about money transfers.
    Your task is to provide the user with information about 101 money transfer.
    Use ONLY the following pieces of retrieved context to answer the question.
    If you do not know the answer or if it's not mentioned in the context, say
    'I am sorry, but that information is not available in our current service documentation.'
    Be concise and present fees clearly.

    question: {question}
    context: {context}
    """

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    context = retriever.invoke(question)
    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )
    return response.content if hasattr(response, "content") else str(response)
