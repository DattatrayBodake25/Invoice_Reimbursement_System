from fastapi import FastAPI
from app.api import analyze, chatbot

app = FastAPI(
    title="Invoice Reimbursement System",
    description="LLM-powered API for invoice analysis and chatbot RAG",
    version="1.0.0"
)

# Include API routers
app.include_router(analyze.router, prefix="/analyze",tags=["Invoice Analysis"])
app.include_router(chatbot.router, prefix="/chatbot",tags=["Chatbot"])