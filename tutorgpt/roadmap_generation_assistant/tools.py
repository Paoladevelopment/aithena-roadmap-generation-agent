from typing import Dict, Any, List
from langchain_core.tools import tool
from datetime import datetime, timezone
import uuid
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from tutorgpt.core.llm_config import get_llm, safe_llm_invoke
from langchain_core.prompts import ChatPromptTemplate
from tutorgpt.tools.search_tools import resource_ranker
from tutorgpt.models.tavily import Resource, SearchOutput, RankerInput

from tutorgpt.core.state import State
from tutorgpt.utils.config import settings

MONGODB_URI = settings.MONGODB_URI

client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
db = client["learning_roadmap"]
roadmaps_collection = db["roadmaps"]

llm = get_llm()

@tool
def summarize_collected_information(state: State) -> str:
    """
    Summarize the information collected throughout the learning roadmap generation process.
    This function extracts information from the conversation history (messages) rather than
    relying on the user_info object.
    
    Args:
        state: The complete state object containing the conversation history
        
    Returns:
        A formatted string summarizing the collected information
    """

    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert at summarizing information from conversations.
        
        Your task is to extract and summarize the following information from the conversation history:
        1. Learning interests/topics the user wants to learn about
        2. Prior knowledge the user has on these topics
        3. Learning preferences and style (visual, auditory, reading/writing, kinesthetic)
        4. Time availability for learning
        5. Resource preferences (videos, articles, books, etc.)
        
        Format the summary in a clear, structured way with sections for each type of information.
        If any information is missing, simply omit that section.
        
        End with a question asking if the user wants to proceed with generating their personalized learning roadmap.
        """),
        ("user", "Please summarize the information collected from this conversation:\n\n{messages}")
    ])
    
    messages = state.get("messages", [])
    messages_text = "\n".join([f"{msg.type}: {msg.content}" for msg in messages])
    
    summary_response = safe_llm_invoke(llm, summary_prompt.format(messages=messages_text))

    summary = summary_response.content
    state["chat_summary"] = summary

    return summary

def extract_title_and_description(lines: List[str], roadmap: Dict[str, Any]) -> int:
    """
    Modifies the roadmap dict in-place to fill in title and description.
    Returns the line index where objectives start.
    """
    for i, line in enumerate(lines):
        line = line.strip()

        if line.startswith("Roadmap Title:"):
            roadmap["title"] = line.replace("Roadmap Title:", "").strip()
        elif line.startswith("Description:"):
            roadmap["description"] = line.replace("Description:", "").strip()
        elif line.startswith("Objective"):
            return i
    return len(lines)

def extract_objectives_and_tasks(lines: List[str]) -> List[Dict[str, Any]]:
    """
    Parses objectives and their tasks from the lines.
    """
    objectives = []
    current_objective = None
    objective_index = 1

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.startswith("Objective") and ":" in line:
            title = line.split(":", 1)[1].strip()

            current_objective = {
                "objective_id": str(uuid.uuid4()),
                "title": title,
                "order_index": objective_index,
                "tasks": []
            }

            objectives.append(current_objective)
            objective_index += 1

        elif line.startswith("-") and ":" in line and current_objective is not None:
            task_title = line.split(":", 1)[1].strip()

            task = {
                "task_id": str(uuid.uuid4()),
                "title": task_title,
                "order_index": len(current_objective["tasks"]) + 1,
                "resources": []
            }

            current_objective["tasks"].append(task)

    return objectives

@tool
def generate_roadmap(subject: str, state: State) -> Dict[str, Any]:
    """
    Generate a learning roadmap based on the user's information and preferences using an LLM.
    
    Args:
        subject: The main subject or learning goal
        state: The complete state object containing the conversation history
        
    Returns:
        A dictionary containing the generated roadmap
    """

    created_at = datetime.now(timezone.utc).isoformat()

    user_email = state.get("user_info", {}).get("user_id", "unknown_user")
    summary = state.get("chat_summary", "")
    
    default_roadmap = {
        "title": f"{subject} learning path",
        "description": f"A personalized learning path for {subject} based on your preferences and goals.",
        "objectives": []
    }
    
    roadmap_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert curriculum designer. Your task is to outline a personalized learning roadmap based on the user's learning goals, prior knowledge, learning style, time availability, and resource preferences.

        Use the structured format shown below. The roadmap must reflect the user's preferences in terms of pace, difficulty, and learning format.
         
        Respond using only the following structured format:

        Roadmap Title: <title>
        Description: <description>

        Objective 1: <Objective title>
        - Task 1.1: <Task title>
        - Task 1.2: <Task title>
        - Task 1.3: <Task title>
        - (Add more if needed)

        Objective 2: <Objective title>
        - Task 2.1: <Task title>
        - Task 2.2: <Task title>
        - Task 2.3: <Task title>
        - (Add more if needed)

        ...
        Instructions:
        - Create a roadmap that matches the user's prior knowledge level. If the user is a beginner, ensure content starts from foundational topics.
        - Use structured progression: start with core concepts and move towards more complex ideas.
        - Align the roadmap with the user's preferred formats (e.g., books, articles, documentation, online courses).
        - Consider the user’s availability when designing the scope. If the user has high availability, include more objectives and tasks to leverage their time.
        - Tailor the learning to the user’s style and interactivity preference (e.g., reading, structured learning, moderate interactivity).
        - Do not include explanations, introductions, markdown, or formatting beyond the structure.

        Return only the roadmap as plain text.
        """),
        ("user", f"""Subject: {subject}

        Summary of collected Information:
        {summary}

        Please outline a roadmap following the format above.""")
    ])
    
    try:
        formatted_prompt = roadmap_prompt.format()
        roadmap_response = safe_llm_invoke(llm, formatted_prompt)
        roadmap_content = roadmap_response.content
        
        print(f"LLM Response: {roadmap_content}")
        
        roadmap = parse_structured_text_to_json(roadmap_content, default_roadmap)
        
    except Exception as e:
        print(f"Error in generate_roadmap: {e}")
        roadmap = default_roadmap
    
    roadmap["user_id"] = user_email
    roadmap["created_at"] = created_at
    
    return roadmap

def parse_structured_text_to_json(text: str, default_roadmap: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the structured text format into a JSON format.
    
    Args:
        text: The structured text from the LLM
        default_roadmap: The default roadmap to use if parsing fails
        
    Returns:
        A dictionary containing the parsed roadmap
    """
    try:
        roadmap = {
            "title": default_roadmap["title"],
            "description": default_roadmap["description"],
            "objectives": []
        }

        lines = text.strip().split('\n')

        start_index = extract_title_and_description(lines, roadmap)

        roadmap["objectives"] = extract_objectives_and_tasks(lines[start_index:])

        return roadmap
        
    except Exception as e:
        print(f"Error parsing structured text: {e}")
        return default_roadmap


@tool
def add_resources_and_save_roadmap(roadmap: dict, subject: str, state: State) -> str:
    """
    Add resources to the roadmap and then save it to the database.
    
    Args:
        roadmap: The roadmap dictionary
        subject: The main subject or learning goal
        state: The complete state object containing the conversation history
        
    Returns:
        A confirmation message with the roadmap ID
    """
    try:
        if not isinstance(roadmap, dict) or not roadmap:
            return "Error: Invalid or empty roadmap. Cannot add resources or save to database."
        
        updated_roadmap = add_resources_to_roadmap(roadmap, subject, state)
        
        return save_roadmap_to_database(updated_roadmap)
    except Exception as e:
        print(f"Error in add_resources_and_save_roadmap: {e}")
        return f"Error processing roadmap: {str(e)}"


def parse_ranked_resources(resources: List[Resource]) -> List[Dict[str, str]]:
    parsed_resources = []

    for resource in resources:
        parsed_resources.append({
            "type": "web",
            "title": resource.title,
            "url": str(resource.url)
        })

    return parsed_resources


def add_resources_to_roadmap(roadmap: Dict[str, Any], subject: str, state: State) -> Dict[str, Any]:
    """
    Add relevant resources to the roadmap based on the user's preferences using the resource_ranker tool.
    
    Args:
        roadmap: The roadmap dictionary
        subject: The main subject or learning goal
        state: The complete state object containing the conversation history
        
    Returns:
        The updated roadmap with resources added
    """
    if "objectives" not in roadmap:
        print("Error: roadmap does not have objectives")
        roadmap["objectives"] = []
    
    summary = state.get("chat_summary", "")
    print(f"[add_resources_to_roadmap] Summary extracted from state:\n{summary}\n")
    
    resource_preference = "web"
    
    if "Resource Preferences" in summary:
        try:
            resource_section = summary.split("Resource Preferences")[1].split("\n\n")[0]
            if "videos" in resource_section.lower():
                resource_preference = "videos"
            elif "articles" in resource_section.lower():
                resource_preference = "articles"
            elif "books" in resource_section.lower():
                resource_preference = "books"
            elif "interactive" in resource_section.lower() or "tutorials" in resource_section.lower():
                resource_preference = "interactive"
        except Exception as e:
            print(f"Error parsing resource preferences: {e}")
    
    for objective in roadmap["objectives"]:
        if not isinstance(objective, dict):
            continue
            
        if "tasks" not in objective:
            objective["tasks"] = []
            
        for task in objective["tasks"]:
            if not isinstance(task, dict) or "title" not in task:
                continue
                
            task_title = task["title"]
            
            search_query = f"{subject}, with focus on: {task_title}"
            
            try:
                ranker_input = RankerInput(
                    learning_topic=search_query,
                    resource_preference=resource_preference
                )
                
                search_output: SearchOutput = resource_ranker.invoke({"input_data": ranker_input.model_dump()})
                
                task["resources"] = parse_ranked_resources(search_output.resources)
            except Exception as e:
                print(f"Error adding resources to task: {e}")
                task["resources"] = []
    
    return roadmap

def save_roadmap_to_database(roadmap: Dict[str, Any]) -> str:
    """
    Save the generated roadmap to the MongoDB database.
    
    Args:
        roadmap: The roadmap dictionary to save
        
    Returns:
        A confirmation message with the roadmap ID
    """

    result = roadmaps_collection.insert_one(roadmap)
    
    return f"Roadmap saved successfully with ID: {str(result.inserted_id)}" 