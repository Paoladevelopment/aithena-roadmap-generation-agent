import os
import time
import random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

default_llm = ChatOpenAI(
    model="gpt-4o",
    api_key=API_KEY,
    temperature=0,
    max_retries=3,
    request_timeout=60
)

def get_llm(model: str = "gpt-4o"):
    if model == "gpt-4o":
        return default_llm
    return ChatOpenAI(
        model=model, 
        api_key=API_KEY,
        max_retries=3,
        request_timeout=60
    )

def safe_llm_invoke(llm, prompt, max_retries=3):
    """Invoke LLM with rate limit handling"""
    for attempt in range(max_retries):
        try:
            return llm.invoke(prompt)
        except Exception as e:
            error_str = str(e).lower()
            print(f"LLM Error (attempt {attempt + 1}): {e}")
            
            if ("rate_limit" in error_str or "429" in error_str) and attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limit detected, waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                continue
            else:
                raise e
    return None