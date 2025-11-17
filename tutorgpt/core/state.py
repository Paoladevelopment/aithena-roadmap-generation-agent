from typing import Annotated, Literal, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages

class UserInfo(TypedDict):
    name: str
    username: str
    email: str
    user_id: str

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

# Simple in-memory snapshot of the last graph state.
_last_state: Optional["State"] = None

def set_last_state(state: "State") -> None:
    """Store the latest graph state in memory."""
    global _last_state
    _last_state = state

def get_last_state() -> Optional["State"]:
    """Return the last stored graph state, if any."""
    return _last_state