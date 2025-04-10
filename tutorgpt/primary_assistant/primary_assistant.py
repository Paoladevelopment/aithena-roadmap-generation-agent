from tutorgpt.core.llm_config import get_llm

from tutorgpt.primary_assistant.prompts import primary_assistant_prompt
from tutorgpt.introduction_assistant.introduction_assistant import ToIntroductionAssistant
from tutorgpt.interest_discovery_assistant.interest_discovery_assistant import ToInterestDiscoveryAssistant
from tutorgpt.prior_knowledge_assistant.prior_knowledge_assistant import ToPriorKnowledgeAssistant
from tutorgpt.learning_preferences_assistant.learning_preferences_assistant import ToLearningPreferencesAssistant
from tutorgpt.time_availability_assistant.time_availability_assistant import ToTimeAvailabilityAssistant
from tutorgpt.resource_preferences_assistant.resource_preferences_assistant import ToResourcePreferencesAssistant
from tutorgpt.roadmap_generation_assistant.roadmap_generation_assistant import ToRoadmapGenerationAssistant

llm = get_llm()

assistant_runnable = primary_assistant_prompt | llm.bind_tools(
    [
        ToIntroductionAssistant,
        ToInterestDiscoveryAssistant,
        ToPriorKnowledgeAssistant,
        ToLearningPreferencesAssistant,
        ToTimeAvailabilityAssistant,
        ToResourcePreferencesAssistant,
        ToRoadmapGenerationAssistant
    ]
)