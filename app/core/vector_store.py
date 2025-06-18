import os
from typing import Dict
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

# Ensure Google API Key is set
if not os.environ.get("GOOGLE_API_KEY"):
    # Replace this with secure key loading in production (e.g., dotenv or secret manager)
    os.environ["GOOGLE_API_KEY"] = "your-google-api-key-here"

# Initialize Embeddings and Chroma Vector Store
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

vector_store = Chroma(
    collection_name="invoice_analysis",              # Logical name for grouping
    embedding_function=embeddings,                   # Embedding model
    persist_directory="./chroma_langchain_db"        # Persistent storage location
)

# Store invoice analysis text and metadata
def store_invoice_embedding(text: str, metadata: Dict):
    """
    Embeds the provided text and stores it in the Chroma vector store with metadata.

    Args:
        text (str): The full invoice content + LLM reasoning.
        metadata (dict): Information about employee, status, date, etc.
    """
    try:
        # Add to vector store
        vector_store.add_texts([text], metadatas=[metadata])

    except Exception as e:
        # Handle unexpected errors
        raise RuntimeError(f"Failed to store embedding: {str(e)}")