from pydantic import BaseModel, Field

from tutorgpt.core.llm_config import get_llm
from tutorgpt.core.assistant import CompleteOrEscalate
from tutorgpt.roadmap_generation_assistant.tools import (
    summarize_collected_information,
    create_complete_roadmap
)
from tutorgpt.roadmap_generation_assistant.prompts import roadmap_generation_prompt

llm = get_llm()

roadmap_generation_tools = [
    summarize_collected_information,
    create_complete_roadmap
]

roadmap_generation_runnable = roadmap_generation_prompt | llm.bind_tools(
    roadmap_generation_tools + [CompleteOrEscalate]
)

class ToRoadmapGenerationAssistant(BaseModel):
    """Transfers control to the roadmap generation assistant to create a personalized learning roadmap."""

    request: str = Field(
        description=(
            "Reason why the roadmap generation assistant is being invoked, typically when the user is ready to receive "
            "their personalized learning roadmap after all information gathering stages are complete."
        )
    ) 