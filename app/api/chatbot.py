from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from app.core.rag_chatbot import get_rag_response

router = APIRouter()

class ChatQuery(BaseModel):
    """
    Defines the expected input for the RAG chatbot endpoint.
    """
    query: str
    employee_name: Optional[str] = None
    date: Optional[str] = None  # Expected in ISO format: "YYYY-MM-DD"
    status: Optional[str] = None  # E.g., "Fully Reimbursed", "Partially Reimbursed", "Declined"

@router.post("/query")
async def chatbot_query(query_data: ChatQuery):
    """
    Handles POST requests to query the RAG chatbot.

    Uses optional filters like employee name, date, and reimbursement status.

    Args:
        query_data (ChatQuery): User's natural language query with optional filters.

    Returns:
        dict: Markdown-formatted response from the chatbot.
    """
    try:
        # Prepare filter dictionary, removing None values
        filters = {k: v for k, v in query_data.dict().items() if k != "query" and v is not None}

        # Call the core RAG logic
        response = get_rag_response(
            query=query_data.query,
            filters=filters
        )

        return {"response_markdown": response}

    except ValueError as ve:
        # Handle specific known input issues
        return JSONResponse(status_code=400, content={"error": str(ve)})

    except Exception as e:
        # Generic fallback for unexpected failures
        return JSONResponse(
            status_code=500,
            content={"error": f"An error occurred while processing your query: {str(e)}"}
        )