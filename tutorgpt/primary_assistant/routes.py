from langgraph.graph import END
from langgraph.prebuilt import tools_condition

from tutorgpt.core.state import State
from tutorgpt.introduction_assistant.introduction_assistant import ToIntroductionAssistant
from tutorgpt.interest_discovery_assistant.interest_discovery_assistant import ToInterestDiscoveryAssistant
from tutorgpt.prior_knowledge_assistant.prior_knowledge_assistant import ToPriorKnowledgeAssistant
from tutorgpt.learning_preferences_assistant.learning_preferences_assistant import ToLearningPreferencesAssistant
from tutorgpt.time_availability_assistant.time_availability_assistant import ToTimeAvailabilityAssistant
from  tutorgpt.resource_preferences_assistant.resource_preferences_assistant import ToResourcePreferencesAssistant
from tutorgpt.roadmap_generation_assistant.roadmap_generation_assistant import ToRoadmapGenerationAssistant

def route_primary_assistant(
    state: State,
):
    route = tools_condition(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        name = tool_calls[0]["name"]
        if name == ToIntroductionAssistant.__name__:
            return "enter_introduction"
        elif name == ToInterestDiscoveryAssistant.__name__:
            return "enter_interest_discovery"
        elif name == ToPriorKnowledgeAssistant.__name__:
            return "enter_prior_knowledge"
        elif name == ToLearningPreferencesAssistant.__name__:
            return "enter_learning_preferences"
        elif name == ToTimeAvailabilityAssistant.__name__:
            return "enter_time_availability"
        elif name == ToResourcePreferencesAssistant.__name__:
            return "enter_resource_preferences"
        elif name == ToRoadmapGenerationAssistant.__name__:
            return "enter_roadmap_generation"
        return "primary_assistant_tools"
    raise ValueError("Invalid route")