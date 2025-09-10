import os
import json
from typing import List, Optional 
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from screening_tools import get_test
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
load_dotenv()
os.environ['GOOGLE_API_KEY'] = os.getenv("GOOGLE_API_KEY")


SESSION_DIR = "sessions"
CHAT_LOGS_DIR = "chat_logs"
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)
if not os.path.exists(CHAT_LOGS_DIR):
    os.makedirs(CHAT_LOGS_DIR)


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectordb = Chroma(persist_directory='db', embedding_function=embeddings)
retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={'k': 4, 'fetch_k': 20})


ANONYMOUS_PROMPT_TEMPLATE = """

You are 'PSYBOT', a warm and friendly wellness companion for college students.
CRITICAL INSTRUCTION: NEVER start your reply with "Hi," "Hello," or any greeting. Jump directly into your supportive response.
Use the provided CONTEXT from your knowledge base to answer the user's QUESTION. The QUESTION may include past conversation history for context.

CONTEXT:
{context}

QUESTION:
{question}

PSYBOT's Empathetic Reply:
"""
ANONYMOUS_PROMPT = PromptTemplate.from_template(ANONYMOUS_PROMPT_TEMPLATE)
anonymous_qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever, chain_type_kwargs={"prompt": ANONYMOUS_PROMPT})


def _sanitize_user_id(user_id: str) -> str:
    return user_id.replace('/', '_').replace('\\', '_')

def save_chat_history(user_id, history):
    sanitized_user_id = _sanitize_user_id(user_id)
    filepath = os.path.join(CHAT_LOGS_DIR, f"{sanitized_user_id}.json")
    with open(filepath, 'w') as f:
        json.dump(history, f, indent=2)

def load_chat_history(user_id):
    sanitized_user_id = _sanitize_user_id(user_id)
    filepath = os.path.join(CHAT_LOGS_DIR, f"{sanitized_user_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []

def save_session(session_id, data):
  
    sanitized_id = _sanitize_user_id(session_id)
    filepath = os.path.join(SESSION_DIR, f"{sanitized_id}.json")
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_session(session_id):
    
    sanitized_id = _sanitize_user_id(session_id)
    filepath = os.path.join(SESSION_DIR, f"{sanitized_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
   
    return {"history": [], "test_state": {"active": False, "test_name": None, "current_question": 0, "answers": []}}


def start_test(session_state, test_name: str) -> str:
    test = get_test(test_name)
    if not test:
        return "I'm sorry, I don't have that test available."
    state = session_state["test_state"]
    state["active"], state["test_name"], state["current_question"], state["answers"] = True, test_name, 0, []
    options_str = "\n".join([f"{idx}. {opt}" for idx, opt in enumerate(test["options"])])
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
        result = anonymous_qa_chain.invoke({"query": conversation_transcript})
        bot_reply = result['result']
    
    history.append(f"User: {user_message}")
    history.append(f"Bot: {bot_reply}")
    save_session(session_id, session)
    return bot_reply


CONSULTANCY_PROMPT_TEMPLATE = """
You are 'PSYBOT', an empathetic wellness companion continuing a conversation with a user.
CRITICAL INSTRUCTION: NEVER start your reply with a greeting. Jump directly into your supportive response.

Use the following context to inform your reply:

**1. Knowledge Base Context (for answering specific questions):**
{context}

**2. Ongoing Chat History (for conversational flow):**
{chat_history}

**3. User's Recent Journal Entries (for deeper emotional context; refer to these gently and indirectly):**
{journal_entries}

---
**User's Latest Message:**
{user_message}

**PSYBOT's Empathetic Reply:**
"""
CONSULTANCY_PROMPT = PromptTemplate.from_template(CONSULTANCY_PROMPT_TEMPLATE)
consultancy_qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=retriever,
    chain_type_kwargs={"prompt": CONSULTANCY_PROMPT}
)

"""
def handle_consultancy_chat(user_message: str, user_id: str, journal_entries: Optional[List[str]] = None) -> str:
    history = load_chat_history(user_id)
    
    # Build the full context string to pass to the chain
    full_context = ""

    # Add the chat history
    full_context += "--- Start of Conversation History ---\n"
    full_context += "\n".join([f"User: {turn['user']}\nBot: {turn['bot']}" for turn in history])
    full_context += "\n--- End of Conversation History ---\n\n"

    # Add the journal entries if they exist
    if journal_entries:
        full_context += "--- Start of Recent Journal Entries ---\n"
        full_context += "- " + "\n- ".join(journal_entries)
        full_context += "\n--- End of Recent Journal Entries ---\n\n"

    # Add the user's latest message
    full_context += f"--- User's Latest Message ---\n{user_message}"

    # Invoke the chain with the single, combined context
    result = consultancy_qa_chain.invoke({"query": full_context})
    bot_reply = result['result']
    
    # Save history as before
    history.append({"user": user_message, "bot": bot_reply})
    save_chat_history(user_id, history)
    
    return bot_reply

"""

consultancy_chain = (
    {
        # This is the key change:
        "context": RunnableLambda(lambda inputs: inputs['user_message']) | retriever,

        "user_message": lambda inputs: inputs['user_message'],
        "chat_history": lambda inputs: inputs['chat_history'],
        "journal_entries": lambda inputs: inputs['journal_entries'],
    }
    | CONSULTANCY_PROMPT
    | llm
    | StrOutputParser()
)

# --- 2. REVISED: Unified Handler for Consultancy Chat ---

def handle_consultancy_chat(
    user_message: str,
    user_id: str,
    journal_entries: Optional[List[dict]] = None,
    session_id: str = None, 
) -> str:
    """
    Handles chat for signed-in users, including test-taking logic.
    """
   
    if not session_id:
        session_id = user_id 

    session = load_session(session_id)
    test_state = session["test_state"]
    history = load_chat_history(user_id) 
    msg_lower = user_message.lower()

    if test_state["active"]:
        bot_reply = handle_test_response(session, user_message)
    elif "anxiety test" in msg_lower or "gad-7" in msg_lower:
        bot_reply = start_test(session, "gad7")
    elif "depression test" in msg_lower or "phq-9" in msg_lower:
        bot_reply = start_test(session, "phq9")
    else:
       
        chat_history_str = "\n".join(
            [f"User: {turn['user']}\nBot: {turn['bot']}" for turn in history]
        )
        
        journal_str = "No journal entries provided."
        if journal_entries:
            
            journal_str = "- " + "\n- ".join(journal_entries)

        
        bot_reply = consultancy_chain.invoke({
            "user_message": user_message,
            "chat_history": chat_history_str,
            "journal_entries": journal_str,
        })

    # Save the persistent chat history
    history.append({"user": user_message, "bot": bot_reply})
    save_chat_history(user_id, history)
    
    # Save the ephemeral session state (for tests)
    save_session(session_id, session)
    
    return bot_reply