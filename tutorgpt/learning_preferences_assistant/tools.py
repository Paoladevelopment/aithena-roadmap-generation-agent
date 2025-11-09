from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from tutorgpt.core.llm_config import get_llm, safe_llm_invoke

tools_llm = get_llm(model="gpt-3.5-turbo")

@tool
def identify_learning_style(user_responses: str) -> dict:
    """
    Identify the user's learning style based on their responses to learning preference questions.
    Returns a dictionary with their primary learning style and characteristics.
    """
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert at identifying learning styles and preferences. "
            "Analyze the user's responses and determine their primary learning style and characteristics."
        ),
        (
            "human",
            "User's responses: {user_responses}\n\n"
            "Provide a JSON response with:\n"
            "1. primary_style: 'visual', 'auditory', 'reading/writing', or 'kinesthetic'\n"
            "2. secondary_style: another learning style that may be present\n"
            "3. characteristics: list of specific learning characteristics they exhibit\n"
            "4. study_environment: preferred study environment based on their responses"
        )
    ])

    messages = prompt.invoke({"user_responses": user_responses})
    response = safe_llm_invoke(tools_llm, messages)
    
    # Parse the response into a dictionary
    # Note: In a production environment, you'd want to add proper JSON parsing and error handling
    return eval(response.content)