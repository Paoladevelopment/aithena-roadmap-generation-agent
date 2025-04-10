from typing import Literal

from tutorgpt.core.state import State

def route_to_workflow(
    state: State,
) -> Literal[
    "primary_assistant",
    "introduction",
    "interest_discovery",
    "prior_knowledge",
    "learning_preferences",
    "time_availability",
    "resource_preferences",
    "roadmap_generation"
]: 
    dialog_state = state.get("dialog_state")
    if not dialog_state:
        return "primary_assistant"
    return dialog_state[-1]