# ingest.py
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

# Configure the embedding model
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
persist_directory = 'db'

def ingest_data():
    # Load documents from the knowledge_base directory
    loader = DirectoryLoader('./knowledge_base/', glob="./*.md", show_progress=True)
    documents = loader.load()

    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    # Create the vector store and persist it
    vectordb = Chroma.from_documents(documents=texts,
                                     embedding=embeddings,
                                     persist_directory=persist_directory)
    vectordb.persist()
    print("Knowledge base ingested and persisted to ChromaDB.")

if __name__ == '__main__':
    ingest_data()