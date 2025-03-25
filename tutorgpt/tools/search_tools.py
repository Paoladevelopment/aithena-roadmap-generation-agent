from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from pydantic import BaseModel
from typing import List

class SearchInput(BaseModel):
    query: str
    search_depth: str

class SearchOutput(BaseModel):
    summary_answer: str
    resources: List[str]

class RankerInput(BaseModel):
    learning_topic: str
    resource_preference: str

def search_learning_resources(input_data: SearchInput) -> SearchOutput:
    """
    Search for learning resources related to the given topic using Tavily
    `search_depth` can be either "basic" or "advanced".
    """
    search_engine = TavilySearch(
        max_results=20,
        topic="general",
        include_answer= True,
        include_images= False,
    )

    result = search_engine.invoke({
        "query": input_data.query,
        "search_depth": input_data.search_depth
    })

    summary_answer = result.get("answer", "")
    raw_results = result.get("results", [])

    # Show title + direct URL
    resources = [f"{r['title']} - {r['url']}" for r in raw_results]

    return SearchOutput(summary_answer=summary_answer, resources=resources)

@tool
def resource_ranker(input_data: RankerInput) -> SearchOutput:
    """
    Returns top 5 learning resources based on the user's topic and resource preferences.
    """
    query = f"top {input_data.resource_preference} for learning {input_data.learning_topic}"

    results = search_learning_resources(SearchInput(
        query=query,
        search_depth="basic"
    ))

    return results.resources[:5]