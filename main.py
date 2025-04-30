from typing import Optional
from uuid import uuid4

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from tutorgpt.graph import generate_chat_response
from auth import TokenData, decode_jwt_token


# Load environment variables
load_dotenv()

CORS_ORIGINS = ["*"]
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

# Main entry point
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)