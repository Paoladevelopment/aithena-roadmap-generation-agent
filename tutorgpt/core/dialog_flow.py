from langchain_core.messages import ToolMessage
from tutorgpt.core.state import State  


def pop_dialog_state(state: State) -> dict:
    """Pop the dialog stack and return to the main assistant."""
    messages = []

    if state["messages"][-1].tool_calls:
        messages.append(
            ToolMessage(
                content="Resuming dialog with the host assistant. Please reflect on the past conversation and assist the user as needed.",
                tool_call_id=state["messages"][-1].tool_calls[0]["id"],
            )
        )

    return {
        "dialog_state": "pop",
        "messages": messages,
    }