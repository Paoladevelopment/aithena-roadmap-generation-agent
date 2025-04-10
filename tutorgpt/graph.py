import json
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START

from tutorgpt.core.state import State
from tutorgpt.core.assistant import Assistant
from tutorgpt.core.dialog_flow import pop_dialog_state
from tutorgpt.core.utilities import _print_event, create_entry_node
from tutorgpt.tools.utilities import fetch_user_information
from tutorgpt.core.utilities import create_tool_node_with_fallback

from tutorgpt.introduction_assistant.introduction_assistant import introduction_runnable, introduction_tools
from tutorgpt.introduction_assistant.routes import route_introduction

from tutorgpt.interest_discovery_assistant.interest_discovery_assistant import interest_discovery_runnable, interest_discovery_tools
from tutorgpt.interest_discovery_assistant.routes import route_interest_discovery

from tutorgpt.prior_knowledge_assistant.prior_knowledge_assistant import prior_knowledge_runnable, prior_knowledge_tools
from tutorgpt.prior_knowledge_assistant.routes import route_prior_knowledge

from tutorgpt.learning_preferences_assistant.learning_preferences_assistant import learning_preferences_runnable, learning_preferences_tools
from tutorgpt.learning_preferences_assistant.routes import route_learning_preferences

from tutorgpt.time_availability_assistant.time_availability_assistant import time_availability_runnable, time_availability_tools
from tutorgpt.time_availability_assistant.routes import route_time_availability

from tutorgpt.resource_preferences_assistant.resource_preferences_assistant import resource_preferences_runnable, resource_preferences_tools
from tutorgpt.resource_preferences_assistant.routes import route_resource_preferences

from tutorgpt.roadmap_generation_assistant.roadmap_generation_assistant import roadmap_generation_runnable, roadmap_generation_tools
from tutorgpt.roadmap_generation_assistant.routes import route_roadmap_generation

from tutorgpt.primary_assistant.primary_assistant import assistant_runnable
from tutorgpt.primary_assistant.routes import route_primary_assistant
from tutorgpt.route_workflow import route_to_workflow

builder = StateGraph(State)

def user_info(state: State):
    if state.get("user_info"):
        return {}
    return {"user_info": fetch_user_information.invoke({})}

#Starting point
builder.add_node("fetch_user_info", user_info)
builder.add_edge(START, "fetch_user_info")


#Introduction assistant
builder.add_node(
    "enter_introduction",
    create_entry_node("Introduction assistant", "introduction")
)

builder.add_node("introduction", Assistant(introduction_runnable))
builder.add_edge("enter_introduction", "introduction")
builder.add_node(
    "introduction_tools",
    create_tool_node_with_fallback(introduction_tools)
)

builder.add_edge("introduction_tools", "introduction")
builder.add_conditional_edges(
    "introduction",
    route_introduction,
    ["introduction_tools", "leave_skill", END]
)

#Interest discovery assistant
builder.add_node(
    "enter_interest_discovery",
    create_entry_node("Interest discovery assistant", "interest_discovery")
)

builder.add_node("interest_discovery", Assistant(interest_discovery_runnable))
builder.add_edge("enter_interest_discovery", "interest_discovery")
builder.add_node(
    "interest_discovery_tools",
    create_tool_node_with_fallback(interest_discovery_tools)
)

builder.add_edge("interest_discovery_tools", "interest_discovery")
builder.add_conditional_edges(
    "interest_discovery",
    route_interest_discovery,
    ["interest_discovery_tools", "leave_skill", END]
)

#Prior knowledge assistant
builder.add_node(
    "enter_prior_knowledge",
    create_entry_node("Prior knowledge assistant", "prior_knowledge")
)

builder.add_node("prior_knowledge", Assistant(prior_knowledge_runnable))
builder.add_edge("enter_prior_knowledge", "prior_knowledge")
builder.add_node(
    "prior_knowledge_tools",
    create_tool_node_with_fallback(prior_knowledge_tools)
)

builder.add_edge("prior_knowledge_tools", "prior_knowledge")
builder.add_conditional_edges(
    "prior_knowledge",
    route_prior_knowledge,
    ["prior_knowledge_tools", "leave_skill", END]
)

#Learning preferences assistant
builder.add_node(
    "enter_learning_preferences",
    create_entry_node("Learning preferences assistant", "learning_preferences")
)

builder.add_node("learning_preferences", Assistant(learning_preferences_runnable))
builder.add_edge("enter_learning_preferences", "learning_preferences")
builder.add_node(
    "learning_preferences_tools",
    create_tool_node_with_fallback(learning_preferences_tools)
)

builder.add_edge("learning_preferences_tools", "learning_preferences")
builder.add_conditional_edges(
    "learning_preferences",
    route_learning_preferences,
    ["learning_preferences_tools", "leave_skill", END]
)

#Time availability assistant
builder.add_node(
    "enter_time_availability",
    create_entry_node("Time availability assistant", "time_availability")
)

builder.add_node("time_availability", Assistant(time_availability_runnable))
builder.add_edge("enter_time_availability", "time_availability")
builder.add_node(
    "time_availability_tools",
    create_tool_node_with_fallback(time_availability_tools)
)

builder.add_edge("time_availability_tools", "time_availability")
builder.add_conditional_edges(
    "time_availability",
    route_time_availability,
    ["time_availability_tools", "leave_skill", END]
)

#Resource preferences assistant
builder.add_node(
    "enter_resource_preferences",
    create_entry_node("Resource preferences assistant", "resource_preferences")
)

builder.add_node("resource_preferences", Assistant(resource_preferences_runnable))
builder.add_edge("enter_resource_preferences", "resource_preferences")
builder.add_node(
    "resource_preferences_tools",
    create_tool_node_with_fallback(resource_preferences_tools)
)

builder.add_edge("resource_preferences_tools", "resource_preferences")
builder.add_conditional_edges(
    "resource_preferences",
    route_resource_preferences,
    ["resource_preferences_tools", "leave_skill", END]
)

#Roadmap generation assistant
builder.add_node(
    "enter_roadmap_generation",
    create_entry_node("Roadmap generation assistant", "roadmap_generation")
)

builder.add_node("roadmap_generation", Assistant(roadmap_generation_runnable))
builder.add_edge("enter_roadmap_generation", "roadmap_generation")
builder.add_node(
    "roadmap_generation_tools",
    create_tool_node_with_fallback(roadmap_generation_tools)
)

builder.add_edge("roadmap_generation_tools", "roadmap_generation")
builder.add_conditional_edges(
    "roadmap_generation",
    route_roadmap_generation,
    ["roadmap_generation_tools", "leave_skill", END]
)

# Primay assistant
builder.add_node("leave_skill", pop_dialog_state)
builder.add_edge("leave_skill", "primary_assistant")

builder.add_node("primary_assistant", Assistant(assistant_runnable))

builder.add_conditional_edges(
    "primary_assistant",
    route_primary_assistant,
    [
        "enter_introduction",
        "enter_interest_discovery",
        "enter_prior_knowledge",
        "enter_learning_preferences",
        "enter_time_availability",
        "enter_resource_preferences",
        "enter_roadmap_generation",
        END,
    ],
)

builder.add_conditional_edges("fetch_user_info", route_to_workflow)
# The checkpointer lets the graph persist its state
# this is a complete memory for the entire graph.
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

def stream_graph_updates(user_input: str, thread_id: str, user_id: str):
    yield f"data: {{\"thread_id\": \"{thread_id}\"}}\n\n"

    config = {
        "configurable": 
            {
                "thread_id": thread_id,
                "user_id": user_id,
            }
        }

    _printed = set()
    for event in graph.stream(
        {
            "messages": 
                [
                    {
                        "role": "user", 
                        "content": user_input
                    }
                ]
            },
        config=config,
        stream_mode="values"
    ):
        _print_event(event, _printed)
        for value in event.values():
            if isinstance(value, list) and value:
                last_item = value[-1]

                if hasattr(last_item, "content"):
                    content = last_item.content
                    yield f"data: {json.dumps({'content': content})}\n\n"