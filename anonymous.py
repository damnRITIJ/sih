# anonymous.py

import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# --- NEW: Import the screening tools ---
# Make sure you have the screening_tools.py file in the same directory
from screening_tools import get_test

load_dotenv()
os.environ['GOOGLE_API_KEY'] = os.getenv("GOOGLE_API_KEY")

# --- NEW: Setup for reliable file-based session storage ---
SESSION_DIR = "sessions"
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

# 1. Initialize LLMs and Embeddings
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, convert_system_message_to_human=True)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# 2. Load the persisted vector database
persist_directory = 'db'
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
retriever = vectordb.as_retriever(search_kwargs={"k": 3})

# 3. Define the RAG Chain Prompt (Your current working version)
template = """
You are 'Dost', a compassionate AI assistant providing supportive first-aid for college students.
Use the following pieces of context to answer the user's question. The user's question may include past conversation history for context.
Your tone should be warm, reassuring, and non-judgmental. Keep your answers concise and practical.
If you don't know the answer from the context, state that you can only provide information from your knowledge base.

Context: {context}
Question: {question}

Helpful Answer:
"""
QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=retriever,
    return_source_documents=False,
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
)

# --- NEW: Helper functions to load and save session data from files ---
def save_session(session_id: str, data: dict):
    """Saves session data to a JSON file."""
    filepath = os.path.join(SESSION_DIR, f"{session_id}.json")
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_session(session_id: str) -> dict:
    """Loads session data from a JSON file or creates a new session."""
    filepath = os.path.join(SESSION_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    
    return {
        "history": [],
        "test_state": {
            "active": False,
            "test_name": None,
            "current_question": 0,
            "answers": []
        }
    }

# --- NEW: Functions to manage the test flow ---
def start_test(session_state, test_name: str) -> str:
    test = get_test(test_name)
    if not test:
        return "I'm sorry, I don't have that test available."

    state = session_state["test_state"]
    state["active"] = True
    state["test_name"] = test_name
    state["current_question"] = 0
    state["answers"] = []

    options_str = "\n".join(test["options"])
    first_question = test["questions"][0]
    return f"{test['title']}\n\n{test['instructions']}\n{options_str}\n\nQuestion:\n{first_question}"

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
        next_question = test["questions"][state["current_question"]]
        return f"Question:\n{next_question}"
    else:
        total_score = sum(state["answers"])
        result = "Score interpretation not found."
        for rule in test["scoring_rules"]:
            if rule["range"][0] <= total_score <= rule["range"][1]:
                result = rule["interpretation"]
                break
        
        state["active"] = False
        state["test_name"] = None
        
        return f"Thank you for completing the assessment.\n\nYour total score is: {total_score}.\n\n**Interpretation:** {result}\n\nRemember, this is not a diagnosis. It's a tool to help you understand your feelings. How can I help you further?"

# --- MODIFIED: The main handler function now routes logic and uses file storage ---
def handle_anonymous_chat(user_message: str, session_id: str) -> str:
    # Step 1: Load the entire session from a file
    session = load_session(session_id)
    test_state = session["test_state"]
    history = session["history"]
    
    bot_reply = ""

    # Step 2: Route the request to the correct handler
    if test_state["active"]:
        # If a test is in progress, handle the test answer
        bot_reply = handle_test_response(session, user_message)
    elif "anxiety test" in user_message.lower() or "gad-7" in user_message.lower():
        # If the user asks to start a test
        bot_reply = start_test(session, "gad7")
    else:
        # Otherwise, proceed with the normal RAG chat logic
        formatted_history = "\n".join(history)
        combined_input = f"This is our conversation so far:\n{formatted_history}\n\nMy new message is: {user_message}"
        result = qa_chain.invoke({"query": combined_input})
        bot_reply = result['result']

    # Step 3: Update history and save the entire session back to the file
    history.append(f"User: {user_message}")
    history.append(f"Bot: {bot_reply}")
    
    save_session(session_id, session)
    
    return bot_reply