from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from pydantic import BaseModel, HttpUrl
from typing import List
from tutorgpt.models.tavily import SearchInput, SearchOutput, Resource, RankerInput

def build_resources(raw_results: List[dict]) -> List[Resource]:
    resources = []
    for r in raw_results:
        if "title" in r and "url" in r:
            try:
                resource = Resource(title=r["title"], url=r["url"])
                resources.append(resource)
            except Exception:
                continue
    return resources

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

    resources = resources = build_resources(raw_results)

    return SearchOutput(summary_answer=summary_answer, resources=resources)

@tool
def resource_ranker(input_data: RankerInput) -> SearchOutput:
    """
    Returns top 5 learning resources based on the user's topic and resource preferences.
    """
    query = f"top {input_data.resource_preference} resources to learn about {input_data.learning_topic}"

    print(f"[resource_ranker] Tavily Search query: '{query}'")

    results = search_learning_resources(SearchInput(
        query=query,
        search_depth="basic"
    ))

    return SearchOutput(
        summary_answer=results.summary_answer,
        resources=results.resources[:3]
    )