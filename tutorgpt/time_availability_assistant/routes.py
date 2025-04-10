from langgraph.graph import END
from tutorgpt.core.state import State
from tutorgpt.core.assistant import CompleteOrEscalate
from langgraph.prebuilt import tools_condition

def route_time_availability(
    state: State
):
    route = tools_condition(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"
    return "time_availability_tools" 