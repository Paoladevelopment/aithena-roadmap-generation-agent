from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from tutorgpt.core.llm_config import get_llm

tools_llm = get_llm(model="gpt-3.5-turbo")

@tool
def suggest_topics(description: str) -> list[str]:
    """Given a vague or general user input, return a list of suggested learning topics."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant that helps users discover specific learning topics from vague interests."),
        ("human", "The user said: {description}\nSuggest 3 to 5 possible learning topics.")
    ])

    messages = prompt.invoke({"description": description})
    response = tools_llm.invoke(messages)

    return [s.strip("-• ") for s in response.content.strip().split("\n") if s.strip()]


@tool
def map_interest_to_goals(interest: str) -> list[str]:
    """Given a user interest, return potential learning goals or roles the user could pursue."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant that maps user interests to practical learning goals or career paths."),
        ("human", "Given the interest: {interest}\nSuggest 3 to 5 potential learning goals or directions.")
    ])

    messages = prompt.invoke({"interest": interest})
    response = tools_llm.invoke(messages)

    return [s.strip("-• ") for s in response.content.strip().split("\n") if s.strip()]