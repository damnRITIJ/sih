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



from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from anonymous import handle_anonymous_chat, handle_consultancy_chat 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mental Wellness Chatbot API",
    description="API for the psychological intervention system."
)

origins = ["*"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CORRECTED Pydantic models ---
class AnonymousChatRequest(BaseModel):
    user_message: str # <-- FIX: Changed from 'message' to 'user_message'
    session_id: str

class ConsultancyChatRequest(BaseModel):
    user_message: str # <-- FIX: Changed from 'message' to 'user_message'
    user_id: str
    session_id: str   # Added for consistency to handle test states
    journal_entries: Optional[List[dict]] = [] # Changed to dict for full entries

class ChatResponse(BaseModel):
    reply: str

# --- CORRECTED Endpoints ---
@app.post("/chat/anonymous", response_model=ChatResponse)
async def anonymous_chat_endpoint(request: AnonymousChatRequest):
    # Pass user_message instead of message
    response_text = handle_anonymous_chat(request.user_message, request.session_id)
    return ChatResponse(reply=response_text)

@app.post("/chat/consultancy", response_model=ChatResponse)
async def consultancy_chat_endpoint(request: ConsultancyChatRequest):
    response_text = handle_consultancy_chat(
        user_message=request.user_message, 
        user_id=request.user_id,
        journal_entries=request.journal_entries,
        session_id=request.session_id # Pass session_id to the handler
    )
    return ChatResponse(reply=response_text)

@app.get("/")
def read_root():
    return {"status": "API is running."}