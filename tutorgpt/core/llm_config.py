import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

default_llm = ChatOpenAI(
    model="gpt-4o",
    api_key=API_KEY,
    temperature=0
)

def get_llm(model: str = "gpt-4o"):
    if model == "gpt-4o":
        return default_llm
    return ChatOpenAI(model=model, api_key=API_KEY)