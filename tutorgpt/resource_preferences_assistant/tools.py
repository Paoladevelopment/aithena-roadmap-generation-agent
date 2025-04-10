from typing import Dict, Any
from langchain_core.tools import tool

@tool
def assess_resource_preferences(learning_style: str, prior_knowledge: str, time_availability: str) -> Dict[str, Any]:
    """
    Assess a user's resource preferences based on their learning style, prior knowledge, and time availability.
    
    Args:
        learning_style: The user's preferred learning style (e.g., visual, auditory, reading/writing, kinesthetic)
        prior_knowledge: The user's level of prior knowledge in the subject
        time_availability: The user's available time for learning
        
    Returns:
        A dictionary containing the user's resource preferences
    """
    preferences = {
        "preferred_formats": [],
        "preferred_platforms": [],
        "preferred_difficulty": "",
        "preferred_pace": "",
        "preferred_interactivity": ""
    }
    

    if "visual" in learning_style.lower():
        preferences["preferred_formats"].extend(["videos", "diagrams", "infographics"])
    if "auditory" in learning_style.lower():
        preferences["preferred_formats"].extend(["podcasts", "audio lectures", "discussions"])
    if "reading" in learning_style.lower():
        preferences["preferred_formats"].extend(["textbooks", "articles", "documentation"])
    if "kinesthetic" in learning_style.lower():
        preferences["preferred_formats"].extend(["hands-on exercises", "projects", "interactive tutorials"])
    

    if "limited" in time_availability.lower():
        preferences["preferred_platforms"].extend(["mobile apps", "microlearning platforms"])
    else:
        preferences["preferred_platforms"].extend(["online courses", "learning management systems"])
    

    if "beginner" in prior_knowledge.lower():
        preferences["preferred_difficulty"] = "beginner-friendly"
    elif "intermediate" in prior_knowledge.lower():
        preferences["preferred_difficulty"] = "intermediate"
    else:
        preferences["preferred_difficulty"] = "advanced"


    if "limited" in time_availability.lower():
        preferences["preferred_pace"] = "self-paced"
    else:
        preferences["preferred_pace"] = "structured"
    

    if "kinesthetic" in learning_style.lower() or "visual" in learning_style.lower():
        preferences["preferred_interactivity"] = "high"
    else:
        preferences["preferred_interactivity"] = "moderate"
    
    return preferences