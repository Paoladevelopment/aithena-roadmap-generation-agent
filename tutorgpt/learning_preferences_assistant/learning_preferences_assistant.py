from pydantic import BaseModel, Field

from tutorgpt.core.llm_config import get_llm
from tutorgpt.core.assistant import CompleteOrEscalate
from tutorgpt.learning_preferences_assistant.tools import identify_learning_style
from tutorgpt.learning_preferences_assistant.prompts import learning_preferences_prompt

llm = get_llm()

learning_preferences_tools = [identify_learning_style]

learning_preferences_runnable = learning_preferences_prompt | llm.bind_tools(
    learning_preferences_tools + [CompleteOrEscalate]
)

class ToLearningPreferencesAssistant(BaseModel):
    """Transfers control to the learning preferences assistant to help identify the user's learning style and preferences."""

    request: str = Field(
        description=(
            "Reason why the learning preferences assistant is being invoked, typically when the user is ready to identify "
            "their learning style and preferences. This stage helps ensure the learning roadmap is tailored to how the user "
            "learns best, including preferred learning methods, resources, and study environments."
        )
    ) 