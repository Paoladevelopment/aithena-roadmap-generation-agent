from pydantic import BaseModel, HttpUrl
from typing import List

class SearchInput(BaseModel):
    query: str
    search_depth: str

class Resource(BaseModel):
    title: str
    url: HttpUrl

class SearchOutput(BaseModel):
    summary_answer: str
    resources: List[Resource]

class RankerInput(BaseModel):
    learning_topic: str
    resource_preference: str