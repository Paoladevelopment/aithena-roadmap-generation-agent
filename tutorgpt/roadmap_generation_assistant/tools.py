from typing import Dict, Any, List
from langchain_core.tools import tool
from datetime import datetime
import uuid
from pymongo import MongoClient
import os
import json

from tutorgpt.core.llm_config import get_llm
from langchain_core.prompts import ChatPromptTemplate
from tutorgpt.tools.search_tools import resource_ranker, RankerInput
from tutorgpt.core.state import State

client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
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
    # Create a prompt for the LLM to extract and summarize the collected information
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
    
    # Extract messages from the state
    messages = state.get("messages", [])
    messages_text = "\n".join([f"{msg.type}: {msg.content}" for msg in messages])
    
    # Generate the summary using the LLM
    summary_response = llm.invoke(summary_prompt.format(messages=messages_text))

    summary = summary_response.content
    state["chat_summary"] = summary

    return summary

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

    roadmap_id = f"roadmap_{uuid.uuid4().hex[:8]}"
    user_email = state["user_info"]["email"]
    created_at = datetime.now()
    
    summary = state["chat_summary"]
    
    roadmap_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert curriculum designer. Your task is to generate a personalized learning roadmap for a user.
        
        Based on the user's subject of interest, prior knowledge, learning preferences, time availability, and resource preferences,
        create a structured learning roadmap with objectives and tasks.
        
        The roadmap should follow this exact JSON structure:
        {
          "roadmap_id": "roadmap_001",
          "title": "Subject Learning Path",
          "description": "A personalized learning path for the subject.",
          "objectives": [
            {
              "title": "Objective Title",
              "order_index": 1,
              "tasks": [
                {
                  "title": "Task Title",
                  "order_index": 1,
                  "resources": []
                }
              ]
            }
          ]
        }
        
        Guidelines:
        1. Include a set of clear, well-structured objectives that follow a logical learning progression.
        2. Each objective should contain a reasonable number of tasks that break down the learning into actionable steps.
        3. Ensure the order_index values are sequential (1, 2, 3, etc.)
        4. Leave the resources array empty (resources will be added later).
        5. Tailor the difficulty and pace based on the user's prior knowledge and time availability.
        6. Consider the user's learning style when structuring the objectives and tasks.
        
        Return ONLY the JSON structure without any additional text or explanation.
        """),
        ("user", f"""
        Subject: {subject}
        
        Summary of Collected Information:
        {summary}
        
        Generate a learning roadmap for this user.
        """)
    ])
    
    roadmap_response = llm.invoke(roadmap_prompt)
    roadmap_content = roadmap_response.content
    
    try:
        json_start = roadmap_content.find('{')
        json_end = roadmap_content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            roadmap_json = roadmap_content[json_start:json_end]
            roadmap = json.loads(roadmap_json)
        else:
            roadmap = {
                "roadmap_id": roadmap_id,
                "title": f"{subject} Learning Path",
                "description": f"A personalized learning path for {subject} based on your preferences and goals.",
                "objectives": []
            }
    except Exception as e:
        roadmap = {
            "roadmap_id": roadmap_id,
            "title": f"{subject} Learning Path",
            "description": f"A personalized learning path for {subject} based on your preferences and goals.",
            "objectives": []
        }
    
    if "roadmap_id" not in roadmap:
        roadmap["roadmap_id"] = roadmap_id
    if "title" not in roadmap:
        roadmap["title"] = f"{subject} Learning Path"
    if "description" not in roadmap:
        roadmap["description"] = f"A personalized learning path for {subject} based on your preferences and goals."
    if "objectives" not in roadmap:
        roadmap["objectives"] = []
    
    roadmap["user_id"] = user_email
    roadmap["created_at"] = created_at
    
    return roadmap

def parse_ranked_resources(resources: List[str]) -> List[Dict[str, str]]:
    parsed_resources = []

    for resource in resources:
        parts = resource.split(" - ", 1)
        if len(parts) == 2:
            title, url = parts
            resource_type = "article"

            if any(ext in url.lower() for ext in [".mp4", ".avi", ".mov", "youtube.com", "vimeo.com"]):
                resource_type = "video"
            elif any(ext in url.lower() for ext in [".pdf", ".epub", ".mobi"]):
                resource_type = "book"
            elif any(ext in url.lower() for ext in [".mp3", ".wav", ".ogg"]):
                resource_type = "audio"

            parsed_resources.append({
                "type": resource_type,
                "title": title,
                "url": url
            })

    return parsed_resources

@tool
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
    summary = state["chat_summary"]
    
    resource_preference = "resources"
    
    if "Resource Preferences" in summary:
        resource_section = summary.split("Resource Preferences")[1].split("\n\n")[0]
        if "videos" in resource_section.lower():
            resource_preference = "videos"
        elif "articles" in resource_section.lower():
            resource_preference = "articles"
        elif "books" in resource_section.lower():
            resource_preference = "books"
        elif "interactive" in resource_section.lower() or "tutorials" in resource_section.lower():
            resource_preference = "interactive"
    
    for objective in roadmap["objectives"]:
        for task in objective["tasks"]:
            task_title = task["title"]
            
            search_query = f"{subject} {task_title}"
            
            try:
                ranker_input = RankerInput(
                    learning_topic=search_query,
                    resource_preference=resource_preference
                )
                
                resources = resource_ranker(ranker_input)
                task["resources"] = parse_ranked_resources(resources)
            except Exception as e:
                task["resources"] = []
    
    return roadmap

@tool
def save_roadmap_to_database(roadmap: Dict[str, Any]) -> str:
    """
    Save the generated roadmap to the MongoDB database.
    
    Args:
        roadmap: The roadmap dictionary to save
        
    Returns:
        A confirmation message with the roadmap ID
    """

    result = roadmaps_collection.insert_one(roadmap)
    
    return f"Roadmap saved successfully with ID: {roadmap['roadmap_id']}" 