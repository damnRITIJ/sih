# main.py
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
    """
    This endpoint handles a user's message in an anonymous chat session.
    It classifies the severity and provides an appropriate response.
    """
    response_text = handle_anonymous_chat(request.message)
    return ChatResponse(reply=response_text)

@app.get("/")
def read_root():
    return {"status": "API is running."}