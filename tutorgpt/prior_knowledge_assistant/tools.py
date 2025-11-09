from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from tutorgpt.core.llm_config import get_llm, safe_llm_invoke

tools_llm = get_llm(model="gpt-3.5-turbo")

@tool
def assess_prior_knowledge(topic: str, user_description: str) -> dict:
    """
    Assess the user's prior knowledge of a topic based on their description.
    Returns a dictionary with knowledge level and key concepts they understand.
    """
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert at assessing prior knowledge in various domains. "
            "Analyze the user's description of their knowledge and provide a structured assessment."
        ),
        (
            "human",
            "Topic: {topic}\nUser's description: {user_description}\n\n"
            "Provide a JSON response with:\n"
            "1. knowledge_level: 'beginner', 'intermediate', or 'advanced'\n"
            "2. understood_concepts: list of key concepts they demonstrate understanding of\n"
            "3. knowledge_gaps: list of important concepts they might need to learn"
        )
    ])

    messages = prompt.invoke({"topic": topic, "user_description": user_description})
    response = safe_llm_invoke(tools_llm, messages)
    
    # Parse the response into a dictionary
    return eval(response.content)