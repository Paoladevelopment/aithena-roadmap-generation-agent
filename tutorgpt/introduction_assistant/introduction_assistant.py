from pydantic import BaseModel, Field

from tutorgpt.core.llm_config import get_llm
from tutorgpt.core.assistant import CompleteOrEscalate
from tutorgpt.introduction_assistant.tools import retrieve_context
from tutorgpt.introduction_assistant.prompts import introduction_prompt

llm = get_llm()

introduction_tools = [retrieve_context]

introduction_runnable = introduction_prompt | llm.bind_tools(
    introduction_tools + [CompleteOrEscalate]
)

class ToIntroductionAssistant(BaseModel):
    """Transfers control to the introduction assistant to greet the user and explain the purpose of the learning tutor."""

    request: str = Field(
        description="Reason why the introduction assistant is being invoked, typically to welcome the user or answer questions about the tutor's role."
    )