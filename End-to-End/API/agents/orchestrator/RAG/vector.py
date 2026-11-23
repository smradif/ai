from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os

readme_path = os.path.join(os.path.dirname(__file__), "faq.html")

if not os.path.exists(readme_path):
    raise FileNotFoundError(f"Could not find the file at {readme_path}")

with open(readme_path, "r", encoding="utf-8") as f:
    content = f.read()

# Split file into a few document chunks so the model can reason over it
chunks = [chunk.strip() for chunk in content.split("h3") if chunk.strip()]
# documents = [Document(page_content=chunk, id=str(i)) for i, chunk in enumerate(chunks)]

documents = []
for i, chunk in enumerate(chunks):
    document = Document(page_content=chunk, id=str(i))
    documents.append(document)

embeddings = OllamaEmbeddings(model="mxbai-embed-large")

db_location = os.path.join(os.path.dirname(__file__), "faq_db")

database_not_found = not os.path.exists(db_location)

if not os.path.exists(db_location):
    os.makedirs(db_location)

vector_store = Chroma(
    collection_name="money_collection",
    embedding_function=embeddings,
    persist_directory=db_location,
)

if database_not_found:
    vector_store.add_documents(documents)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})

