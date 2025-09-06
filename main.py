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
from typing import List, Optional # <-- Add List and Optional
# Make sure the filename and function names are correct
from anonymous import handle_anonymous_chat, handle_consultancy_chat 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mental Wellness Chatbot API",
    description="API for the psychological intervention system."
)

# --- Add the CORS middleware ---
origins = ["*"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic models for BOTH request types ---
class AnonymousChatRequest(BaseModel):
    message: str
    session_id: str

# --- MODIFIED: Pydantic model for the consultancy request now accepts journal entries ---
class ConsultancyChatRequest(BaseModel):
    message: str
    user_id: str
    journal_entries: Optional[List[str]] = None # This is the new field

class ChatResponse(BaseModel):
    reply: str

# --- Endpoint for Anonymous Chat (your existing code) ---
@app.post("/chat/anonymous", response_model=ChatResponse)
async def anonymous_chat_endpoint(request: AnonymousChatRequest):
    response_text = handle_anonymous_chat(request.message, request.session_id)
    return ChatResponse(reply=response_text)

# --- MODIFIED: The endpoint now passes journal entries to the handler ---
@app.post("/chat/consultancy", response_model=ChatResponse)
async def consultancy_chat_endpoint(request: ConsultancyChatRequest):
    """
    This endpoint handles conversations for signed-in users and can now receive journal entries.
    """
    response_text = handle_consultancy_chat(
        request.message, 
        request.user_id,
        request.journal_entries # Pass the new data to the logic function
    )
    return ChatResponse(reply=response_text)


@app.get("/")
def read_root():
    return {"status": "API is running."}
