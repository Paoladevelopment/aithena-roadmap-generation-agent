import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import tool

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(api_key=API_KEY)

project_root = Path(__file__).resolve().parents[2]
persist_directory = str(project_root / "chroma_db")

vector_db = Chroma(embedding_function=embeddings, collection_name="tutor_gpt", persist_directory=persist_directory)

retriever = vector_db.as_retriever(search_kwargs={"k": 2})

@tool
def retrieve_context(query: str) -> str:
    """Search the internal FAQ or knowledge base for information relevant to the user's question."""
    docs = retriever.invoke(query)
    print(docs)
    return "\n\n".join([doc.page_content for doc in docs])