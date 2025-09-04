# main.py
"""""
from fastapi import FastAPI
from pydantic import BaseModel
from anonymous import handle_anonymous_chat

app = FastAPI(
    title="Mental Wellness Chatbot API",
    description="API for the anonymous chat feature of the psychological intervention system."
)

# Pydantic models for request and response
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat/anonymous", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
This endpoint handles a user's message in an anonymous chat session.
    It classifies the severity and provides an appropriate response.

    response_text = handle_anonymous_chat(request.message)
    return ChatResponse(reply=response_text)

@app.get("/")
def read_root():
    return {"status": "API is running."}

"""


# main.py
# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from anonymous import handle_anonymous_chat

# --- Import CORSMiddleware ---
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mental Wellness Chatbot API",
    description="API for the anonymous chat feature of the psychological intervention system."
)

# --- Add the CORS middleware ---
# This is the essential part that fixes the error in your screenshot.
origins = ["*"] # Allows all origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Updated Pydantic models to include session_id ---
class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat/anonymous", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    This endpoint handles a user's message in an anonymous chat session.
    """
    response_text = handle_anonymous_chat(request.message, request.session_id)
    return ChatResponse(reply=response_text)

@app.get("/")
def read_root():
    return {"status": "API is running."}