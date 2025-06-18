# 🧾 Invoice Reimbursement System

An intelligent, LLM-powered system for automatically analyzing and querying employee reimbursement invoices based on HR policy documents.

---

## 🚀 Overview

This project demonstrates a full-stack intelligent document processing system, built as part of an AI/ML internship assignment. It consists of:

- **Invoice Analysis** using Large Language Models (LLMs)
- **Vector Database** storage for semantic search
- **RAG-based Chatbot** for natural language querying
- Optional **Streamlit UI** for ease of use

---

## 📂 Project Structure

invoice_reimbursement_system/
│
├── app/ # All your core app code
│ ├── api/ # FastAPI routes
│ │ ├── analyze.py # Endpoint to analyze invoices
│ │ └── chatbot.py # Endpoint to query chatbot
│ ├── core/ # Business logic and processing
│ │ ├── analyzer.py # Invoice analysis using LLM
│ │ ├── rag_chatbot.py # RAG logic
│ │ └── vector_store.py # Chroma setup and functions
│ ├── utils/ # Utility functions
│ │ └── pdf_parser.py # PDF extraction logic
│ └── prompts/ # Prompt templates
│ ├── invoice_prompt.txt
│ └── chatbot_prompt.txt
│
├── streamlit_ui/ # Bonus: Streamlit UI
│ └── main.py
│
├── main.py # FastAPI app entry point
├── requirements.txt # All required libraries
├── .env # Store Gemini API Key
└── README.md # Documentation


---

## ⚙️ Technologies Used

- **Python 3.10+**
- **FastAPI** – API development
- **LangChain** – LLM Orchestration
- **ChromaDB** – Vector database
- **Google Gemini LLM + Embeddings**
- **PyMuPDF** – PDF extraction
- **Streamlit** – (Optional) Frontend for user interaction

---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/DattatrayBodake25/Invoice_Reimbursement_System.git
cd Invoice_Reimbursement_System
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a .env file at the root level and add your Gemini API key:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

## ▶️ Running the Application
Start the FastAPI Server
```bash
uvicorn main:app --reload
```
Visit the API docs at: http://localhost:8000/docs

## Run the Streamlit UI
```bash
cd streamlit_ui
streamlit run main.py
```

## 📌 How It Works
### ✅ Part 1: Invoice Reimbursement Analysis
Upload a ZIP of invoice PDFs and a policy PDF

The system parses and analyzes each invoice against policy using LLM

Results are embedded and stored in ChromaDB for later querying

### 💬 Part 2: RAG Chatbot
Ask natural questions like:
```
"Why was John's meal bill rejected?"

"Show me all declined travel invoices for May"
```

The system performs semantic + metadata search

LLM answers your question using retrieved data

## 💡 Prompt Engineering
Prompts are designed carefully for:

Invoice Analysis – Explains why an invoice was fully/partially/declined

Chatbot – Fetches context-aware results using RAG pipeline


## 🧠 Credits
Developed by Dattatray Bodake
AI/ML Internship Assignment | 2025

