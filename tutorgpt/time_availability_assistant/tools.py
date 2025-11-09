from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from tutorgpt.core.llm_config import get_llm, safe_llm_invoke

tools_llm = get_llm(model="gpt-3.5-turbo")

@tool
def assess_time_availability(user_description: str) -> dict:
    """
    Assess the user's available time for learning based on their description of their schedule.
    Returns a dictionary with available time slots and constraints.
    """
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert at analyzing time availability and scheduling constraints. "
            "Analyze the user's description of their schedule and provide a structured assessment."
        ),
        (
            "human",
            "User's description: {user_description}\n\n"
            "Provide a JSON response with:\n"
            "1. available_hours_per_week: estimated number of hours available for learning\n"
            "2. preferred_times: list of preferred times for learning (e.g., 'mornings', 'evenings', 'weekends')\n"
            "3. constraints: list of time constraints or commitments that may affect learning\n"
            "4. consistency_level: 'high', 'medium', or 'low' based on how consistent their schedule is"
        )
    ])

    messages = prompt.invoke({"user_description": user_description})
    response = safe_llm_invoke(tools_llm, messages)
    
    # Parse the response into a dictionary
    # Note: In a production environment, you'd want to add proper JSON parsing and error handling
    return eval(response.content)