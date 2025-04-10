from pydantic import BaseModel, Field

from tutorgpt.core.llm_config import get_llm
from tutorgpt.core.assistant import CompleteOrEscalate
from tutorgpt.interest_discovery_assistant.tools import suggest_topics, map_interest_to_goals
from tutorgpt.interest_discovery_assistant.prompts import interest_discovery_prompt

llm = get_llm()

interest_discovery_tools = [suggest_topics, map_interest_to_goals]

interest_discovery_runnable = interest_discovery_prompt | llm.bind_tools(
    interest_discovery_tools + [CompleteOrEscalate]
)

class ToInterestDiscoveryAssistant(BaseModel):
    """Transfers control to the interest discovery assistant to help the user explore and define what topics or skills they want to learn."""

    request: str = Field(
        description=(
            "Reason why the interest discovery assistant is being invoked, typically when the user is ready to identify or clarify their learning interests. "
            "This stage helps surface potential topics or areas of curiosity that will guide the rest of the learning roadmap."
        )
    )