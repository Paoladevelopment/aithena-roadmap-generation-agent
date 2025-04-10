from pydantic import BaseModel, Field

from tutorgpt.core.llm_config import get_llm
from tutorgpt.core.assistant import CompleteOrEscalate
from tutorgpt.time_availability_assistant.tools import assess_time_availability
from tutorgpt.time_availability_assistant.prompts import time_availability_prompt

llm = get_llm()

time_availability_tools = [assess_time_availability]

time_availability_runnable = time_availability_prompt | llm.bind_tools(
    time_availability_tools + [CompleteOrEscalate]
)

class ToTimeAvailabilityAssistant(BaseModel):
    """Transfers control to the time availability assistant to help assess the user's available time for learning."""

    request: str = Field(
        description=(
            "Reason why the time availability assistant is being invoked, typically when the user is ready to assess "
            "their available time for learning. This stage helps ensure the learning roadmap is tailored to the user's "
            "schedule and time constraints."
        )
    ) 