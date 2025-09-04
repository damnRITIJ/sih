import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from screening_tools import get_test

load_dotenv()
os.environ['GOOGLE_API_KEY'] = os.getenv("GOOGLE_API_KEY")

# --- Directories for session and persistent chat logs ---
SESSION_DIR = "sessions"
CHAT_LOGS_DIR = "chat_logs"
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)
if not os.path.exists(CHAT_LOGS_DIR):
    os.makedirs(CHAT_LOGS_DIR)

# 1. Initialize LLMs and other components...
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.5)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectordb = Chroma(persist_directory='db', embedding_function=embeddings)
retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={'k': 4, 'fetch_k': 20})

# --- RAG Chain Prompt ---
template = """
You are 'Dost', a warm, empathetic, and friendly wellness companion for college students. Your persona is like a supportive friend who is a good listener.
**CRITICAL INSTRUCTION: NEVER start your reply with "Hi," "Hello," "Hey," or any similar greeting. Jump directly into your supportive response.**
Use the provided "Knowledge Base Context" only if it is relevant to the user's latest message.

**Knowledge Base Context:**
{context}

**Ongoing Conversation:**
{question}

**Dost's Reply:**
"""
QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever, chain_type_kwargs={"prompt": QA_CHAIN_PROMPT})

# --- Session and History Helper Functions ---
def save_session(session_id, data):
    with open(os.path.join(SESSION_DIR, f"{session_id}.json"), 'w') as f:
        json.dump(data, f, indent=2)

def load_session(session_id):
    filepath = os.path.join(SESSION_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {"history": [], "test_state": {"active": False, "test_name": None, "current_question": 0, "answers": []}}

# --- MODIFIED: Helper functions for consultancy chat logs with filename sanitization ---
def save_chat_history(user_id, history):
    """Saves persistent chat history for a signed-in user."""
    # Sanitize the user_id to make it a valid filename by replacing slashes
    sanitized_user_id = user_id.replace("/", "_")
    filepath = os.path.join(CHAT_LOGS_DIR, f"{sanitized_user_id}.json")
    with open(filepath, 'w') as f:
        json.dump(history, f, indent=2)

def load_chat_history(user_id):
    """Loads persistent chat history for a signed-in user."""
    # Sanitize the user_id to find the correct file
    sanitized_user_id = user_id.replace("/", "_")
    filepath = os.path.join(CHAT_LOGS_DIR, f"{sanitized_user_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []

# --- Test Flow Functions (start_test, handle_test_response) ---
def start_test(session_state, test_name: str) -> str:
    test = get_test(test_name)
    if not test:
        return "I'm sorry, I don't have that test available."
    state = session_state["test_state"]
    state["active"], state["test_name"], state["current_question"], state["answers"] = True, test_name, 0, []
    options_str = "\n".join(test["options"])
    return f"{test['title']}\n\n{test['instructions']}\n{options_str}\n\nQuestion:\n{test['questions'][0]}"

def handle_test_response(session_state, user_answer: str) -> str:
    state = session_state["test_state"]
    test = get_test(state["test_name"])
    try:
        answer_value = int(user_answer.strip())
        if not (0 <= answer_value < len(test["options"])):
            raise ValueError
    except ValueError:
        return "Please provide a valid number from the options (e.g., 0, 1, 2, or 3)."
    
    state["answers"].append(answer_value)
    state["current_question"] += 1
    
    if state["current_question"] < len(test["questions"]):
        return f"Question:\n{test['questions'][state['current_question']]}"
    else:
        total_score = sum(state["answers"])
        result = "Score interpretation not found."
        for rule in test["scoring_rules"]:
            if rule["range"][0] <= total_score <= rule["range"][1]:
                result = rule["interpretation"]
                break
        state["active"] = False
        return f"Thank you for completing the assessment.\n\nYour total score is: {total_score}.\n\n**Interpretation:** {result}\n\nRemember, this is not a diagnosis. How can I help you further?"

# --- Main Handler for Anonymous Chat ---
def handle_anonymous_chat(user_message: str, session_id: str) -> str:
    session = load_session(session_id)
    test_state, history = session["test_state"], session["history"]
    bot_reply = ""
    msg_lower = user_message.lower()

    if test_state["active"]:
        bot_reply = handle_test_response(session, user_message)
    elif "anxiety test" in msg_lower or "gad-7" in msg_lower:
        bot_reply = start_test(session, "gad7")
    elif "depression test" in msg_lower or "phq-9" in msg_lower:
        bot_reply = start_test(session, "phq9")
    else:
        conversation_transcript = "\n".join(history) + f"\nUser: {user_message}"
        result = qa_chain.invoke({"query": conversation_transcript})
        bot_reply = result['result']
    
    history.append(f"User: {user_message}")
    history.append(f"Bot: {bot_reply}")
    save_session(session_id, session)
    return bot_reply

# --- Handler for Consultancy Chat ---
def handle_consultancy_chat(user_message: str, user_id: str) -> str:
    """Handles chats for signed-in users with persistent memory."""
    history = load_chat_history(user_id)
    
    # Format the history from a list of dicts into a string for the prompt
    conversation_transcript = "\n".join([f"User: {turn['user']}\nBot: {turn['bot']}" for turn in history])
    conversation_transcript += f"\nUser: {user_message}"

    # Use the same RAG chain for a consistent personality
    result = qa_chain.invoke({"query": conversation_transcript})
    bot_reply = result['result']
    
    # Save the new turn as a dictionary for structured logging
    history.append({"user": user_message, "bot": bot_reply})
    save_chat_history(user_id, history)
    
    return bot_reply