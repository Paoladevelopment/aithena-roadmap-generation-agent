from pydantic import BaseModel, Field

from tutorgpt.core.llm_config import get_llm
from tutorgpt.core.assistant import CompleteOrEscalate
from tutorgpt.resource_preferences_assistant.tools import assess_resource_preferences
from tutorgpt.resource_preferences_assistant.prompts import resource_preferences_prompt

llm = get_llm()

resource_preferences_tools = [assess_resource_preferences]

resource_preferences_runnable = resource_preferences_prompt | llm.bind_tools(
    resource_preferences_tools + [CompleteOrEscalate]
)

class ToResourcePreferencesAssistant(BaseModel):
    """Transfers control to the resource preferences assistant to help identify the user's preferred learning resources."""

    request: str = Field(
        description=(
            "Reason why the resource preferences assistant is being invoked, typically when the user is ready to identify "
            "their preferred learning resources. This stage helps ensure the learning roadmap includes resources that match "
            "the user's preferences and learning style."
        )
    ) 