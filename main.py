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
from fastapi import FastAPI
from pydantic import BaseModel
# --- MODIFIED: Import both handler functions ---
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

# --- NEW: Pydantic model for the consultancy request ---
class ConsultancyChatRequest(BaseModel):
    message: str
    user_id: str

class ChatResponse(BaseModel):
    reply: str

# --- Endpoint for Anonymous Chat (your existing code) ---
@app.post("/chat/anonymous", response_model=ChatResponse)
async def anonymous_chat_endpoint(request: AnonymousChatRequest):
    response_text = handle_anonymous_chat(request.message, request.session_id)
    return ChatResponse(reply=response_text)

# --- NEW: The missing endpoint for Consultancy Chat ---
@app.post("/chat/consultancy", response_model=ChatResponse)
async def consultancy_chat_endpoint(request: ConsultancyChatRequest):
    """
    This endpoint handles conversations for signed-in users with persistent memory.
    """
    response_text = handle_consultancy_chat(request.message, request.user_id)
    return ChatResponse(reply=response_text)


@app.get("/")
def read_root():
    return {"status": "API is running."}