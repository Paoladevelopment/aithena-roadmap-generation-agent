from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from typing import Callable


from langgraph.prebuilt import ToolNode
from langchain_core.messages import ToolMessage

from tutorgpt.core.state import State

def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


def create_entry_node(assistant_name: str, new_dialog_state: str) -> Callable:
    def entry_node(state: State) -> dict:
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]
        return {
            "messages": [
                ToolMessage(
                    content=(
                        f"You are now acting as the {assistant_name} within the personalized learning roadmap assistant flow. "
                        f"Focus on guiding the user through the '{new_dialog_state}' stage of the learning journey. "
                        "Use the context of the previous conversation to respond naturally and helpfully. "
                        "You may use tools to support the user's learning needs during this stage if needed. "
                        "If the user asks something unrelated or outside your scope, use the `CompleteOrEscalate` tool to hand control back to the main assistant. "
                        "Do not mention that you are a sub-assistant or that a handoff occurred — respond as if you've been assisting the whole time."
                    ),
                    tool_call_id=tool_call_id,
                )
            ],
            "dialog_state": new_dialog_state,
        }

    return entry_node


def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)
