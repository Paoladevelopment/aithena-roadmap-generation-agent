import os
from typing import Optional
from uuid import uuid4

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from tutorgpt.graph import stream_graph_updates


# Load environment variables
load_dotenv()

# Access environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CORS_ORIGINS = ["http://localhost:3000"]
CORS_METHODS = ["GET", "POST"]

# Initialize FastAPI app
app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=CORS_METHODS,
    allow_headers=["*"],
)

class AuthenticatedResponse(BaseModel):
    message: str

def get_auth_key(authorization: str = Header(...)) -> None:
    auth_key = os.getenv("AUTH_KEY")
    if not auth_key:
        raise HTTPException(status_code=500, detail="AUTH_KEY not configured")
    expected_header = f"Bearer {auth_key}"
    if authorization != expected_header:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/")
async def say_hello():
    return {"message": "Hello World"}


class MessageList(BaseModel):
    human_say: str


sessions = {}


@app.get("/botname", response_model=None)
async def get_bot_name(authorization: Optional[str] = Header(None)):
    load_dotenv()
    return "bot_name"


@app.post("/chat", response_class=StreamingResponse)
async def chat_with_tutor_agent(
    req: MessageList, 
    thread_id: Optional[str] = Query(default=None), 
    authorization: Optional[str] = Header(None)
    ):

    thread_id = thread_id or str(uuid4())

    user_input = req.human_say
    return StreamingResponse(
        stream_graph_updates(user_input, thread_id),
        media_type="text/event-stream"
    )


# Main entry point
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)