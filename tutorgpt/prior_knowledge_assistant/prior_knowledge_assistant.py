from pydantic import BaseModel, Field

from tutorgpt.core.llm_config import get_llm
from tutorgpt.core.assistant import CompleteOrEscalate
from tutorgpt.prior_knowledge_assistant.tools import assess_prior_knowledge
from tutorgpt.prior_knowledge_assistant.prompts import prior_knowledge_prompt

llm = get_llm()

prior_knowledge_tools = [assess_prior_knowledge]

prior_knowledge_runnable = prior_knowledge_prompt | llm.bind_tools(
    prior_knowledge_tools + [CompleteOrEscalate]
)

class ToPriorKnowledgeAssistant(BaseModel):
    """Transfers control to the prior knowledge assistant to help assess the user's existing knowledge and suggest prerequisites."""

    request: str = Field(
        description=(
            "Reason why the prior knowledge assistant is being invoked, typically when the user is ready to assess their existing knowledge "
            "or when prerequisites need to be determined for their learning journey. This stage helps ensure the learning roadmap "
            "is appropriately tailored to the user's current skill level."
        )
    ) 