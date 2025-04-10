from typing import Annotated, Literal, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages

class UserInfo(TypedDict):
    name: str
    username: str
    email: str

def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """Push or pop the state."""
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: UserInfo
    chat_summary: str
    dialog_state: Annotated[
        list[
            Literal[
                "assistant",
                "introduction",
                "interest_discovery",
                "prior_knowledge",
                "learning_preferences",
                "time_availability",
                "resource_preferences",
                "roadmap_generation",
            ]
        ],
        update_dialog_stack,
    ]