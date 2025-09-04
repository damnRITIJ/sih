# chatbot.py
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import json

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

# 1. Initialize LLMs and Embeddings
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3, convert_system_message_to_human=True)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# 2. Load the persisted vector database
persist_directory = 'db'
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
retriever = vectordb.as_retriever(search_kwargs={"k": 3}) # Retrieve top 3 relevant chunks

# 3. Define the Triage/Severity Classification Function
def classify_severity(user_message: str) -> dict:
    prompt = f"""
    Analyze the following user message from a mental health chat.
    Classify its severity into ONE of three categories: 'low_risk', 'moderate_distress', or 'high_risk_crisis'.
    - 'high_risk_crisis' is for messages indicating immediate danger, self-harm, or suicidal thoughts.
    - 'moderate_distress' is for messages showing clear emotional pain, high stress, or helplessness.
    - 'low_risk' is for general questions, mild stress, or requests for information.

    Message: "{user_message}"

    Respond ONLY with a JSON object in the format: {{"severity": "..."}}
    """
    try:
        response = llm.invoke(prompt)
        # Ensure the response is a valid JSON
        result = json.loads(response.content)
        if 'severity' in result and result['severity'] in ['low_risk', 'moderate_distress', 'high_risk_crisis']:
            return result
        else:
            return {"severity": "low_risk"} # Default to safe option on malformed response
    except (json.JSONDecodeError, TypeError):
        return {"severity": "low_risk"} # Default to safe option on error

# 4. Define the RAG Chain for generating helpful responses
template = """
You are 'Dost', a compassionate AI assistant providing supportive first-aid for college students.
Use the following pieces of context to answer the user's question.
Your tone should be warm, reassuring, and non-judgmental.
Keep your answers concise and practical.
If you don't know the answer from the context, state that you can only provide information from your knowledge base, and suggest they rephrase.
Do not make up advice or information.

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

# 5. The Main Orchestrator Function
def handle_anonymous_chat(user_message: str) -> str:
    # Step 1: Classify severity
    severity_result = classify_severity(user_message)
    severity = severity_result['severity']

    # Step 2: Branch logic based on severity
    if severity == 'high_risk_crisis':
        return "It sounds like you are going through a very difficult time. Please know that immediate help is available. You can connect with professionals by calling the 24/7 university helpline at (1800-XXX-XXXX). Your safety is the most important thing."

    elif severity == 'moderate_distress':
        rag_response = qa_chain.invoke({"query": user_message})
        suggestion = "\n\nI hope this information is helpful. Please remember, talking to someone can make a big difference. If you'd like, I can guide you on how to book a confidential session with a university counselor."
        return rag_response['result'] + suggestion

    else: # low_risk
        rag_response = qa_chain.invoke({"query": user_message})
        return rag_response['result']