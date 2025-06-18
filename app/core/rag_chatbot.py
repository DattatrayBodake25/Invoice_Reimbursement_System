import os
from typing import Optional, Dict, List
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Load Google API key
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = "your-google-api-key-here"  # Replace with secure method in production

# Initialize LLM and Embeddings
llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
embedding_fn = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


# Initialize Vector Store
vector_store = Chroma(
    collection_name="invoice_analysis",
    embedding_function=embedding_fn,
    persist_directory="./chroma_langchain_db"
)

# Build filter for metadata search
def build_metadata_filter(filters: Dict[str, Optional[str]]) -> Dict:
    """
    Constructs a MongoDB-style filter dictionary for Chroma search based on provided metadata.
    """
    conditions = []
    for key, value in filters.items():
        if value:
            conditions.append({key: {"$eq": value}})
    
    if not conditions:
        return {}
    
    return {"$and": conditions}

# Generate RAG response based on vector search
def get_rag_response(query: str, filters: Dict[str, Optional[str]]) -> str:
    """
    Performs a similarity search on vector DB and queries LLM for a final answer.

    Args:
        query (str): User's question
        filters (dict): Optional metadata filters like employee_name, status, etc.

    Returns:
        str: LLM-generated response
    """
    try:
        metadata_filter = build_metadata_filter(filters)

        # Search documents with or without filters
        if metadata_filter:
            docs: List[Document] = vector_store.similarity_search(
                query=query,
                k=5,
                filter=metadata_filter
            )
        else:
            docs: List[Document] = vector_store.similarity_search(
                query=query,
                k=5
            )

        # If no documents found, return informative message
        if not docs:
            return "No relevant documents found for your query. Please refine your search."

        # Prepare combined context from top documents
        context = "\n\n---\n\n".join([doc.page_content for doc in docs])

        # Prepare system prompt using invoice data and user query
        prompt_template = ChatPromptTemplate.from_template("""
You are a helpful assistant specialized in employee reimbursement queries.
Use the following invoice analysis data to answer the user's question.

## Context:
{context}

## User Query:
{query}

Respond in clear and concise markdown format.
""")

        messages = prompt_template.format_messages(context=context, query=query)
        response = llm.invoke(messages)

        return response.content.strip()

    except Exception as e:
        # Handle unexpected failures gracefully
        return f"An error occurred while generating a response: {str(e)}"