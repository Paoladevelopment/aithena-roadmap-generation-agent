from typing import Optional
from uuid import uuid4
import asyncio
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from tutorgpt.graph import generate_chat_response
from auth import TokenData, decode_jwt_token
from tutorgpt.notifications import notifier


# Load environment variables
load_dotenv()

CORS_ORIGINS = ["*"]
CORS_METHODS = ["GET", "POST"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_running_loop()
    notifier.set_loop(loop)
    yield


# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=CORS_METHODS,
    allow_headers=["*"],
)

@app.get("/")
async def say_hello():
    return {"message": "Hello World"}


class MessageList(BaseModel):
    human_say: str


sessions = {}


@app.post("/chat", response_class=JSONResponse)
async def chat_with_tutor_agent(
    req: MessageList, 
    thread_id: Optional[str] = Query(default=None), 
    token_data: TokenData = Depends(decode_jwt_token)
):

    thread_id = thread_id or str(uuid4())
    user_id = str(token_data.user_id)

    user_input = req.human_say
    response_data = generate_chat_response(user_input, thread_id, user_id)
    return JSONResponse(content=response_data)


@app.get("/events")
async def sse_events(
    request: Request,
    token_data: TokenData = Depends(decode_jwt_token),
):
    """
    Server-Sent Events endpoint to notify when roadmaps are ready.
    The client should keep this connection open and listen for 'message' events.
    """
    user_id = str(token_data.user_id)

    async def event_generator():
        async for event in notifier.stream(user_id):
            if await request.is_disconnected():
                break
            yield event

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Main entry point
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)