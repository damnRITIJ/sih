# chatbot.py
# ... (add these imports at the top)
import json
import os
from typing import List, Dict

# ... (your existing code)

# --- NEW: Helper functions for persistent storage ---
CHAT_LOGS_DIR = "chat_logs"
if not os.path.exists(CHAT_LOGS_DIR):
    os.makedirs(CHAT_LOGS_DIR)

def load_chat_history(user_id: str) -> List[Dict[str, str]]:
    """Loads chat history for a given user from a JSON file."""
    filepath = os.path.join(CHAT_LOGS_DIR, f"{user_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return [] # Return an empty list if no history exists

def save_chat_history(user_id: str, history: List[Dict[str, str]]):
    """Saves chat history for a given user to a JSON file."""
    filepath = os.path.join(CHAT_LOGS_DIR, f"{user_id}.json")
    with open(filepath, 'w') as f:
        json.dump(history, f, indent=2)

# ---------------------------------------------------