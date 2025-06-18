import os
import json
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Ensure API Key is set
if not os.environ.get("GOOGLE_API_KEY"):
    # You can load it securely via dotenv or env config in production
    os.environ["GOOGLE_API_KEY"] = "your-google-api-key-here"

#Initialize Gemini LLM
llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

# 📌 Set up embeddings (used for vector DB)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Chroma vector store (optional usage)
vector_store = Chroma(
    collection_name="policy_embeddings",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db"
)

#Analyze Invoice using LLM
def analyze_invoice(policy_text: str, invoice_text: str) -> dict:
    """
    Uses a Gemini LLM to analyze an invoice against a reimbursement policy.

    Args:
        policy_text (str): The reimbursement policy text.
        invoice_text (str): The content of the invoice.

    Returns:
        dict: A dictionary with status and reason from LLM response.
    """
    try:
        # Format the system prompt for the LLM using a template
        prompt_template = ChatPromptTemplate.from_template("""
You are a financial reimbursement assistant. Given a company's reimbursement policy and an invoice, classify the invoice into:
- Fully Reimbursed
- Partially Reimbursed
- Declined

Provide:
1. Reimbursement Status
2. Reason for your decision

## Reimbursement Policy:
{policy}

## Invoice:
{invoice}

Respond in JSON format like this:
{{
  "status": "Fully Reimbursed",
  "reason": "All items are food-related and within reimbursement policy"
}}
""")
        # Prepare the message for LLM
        messages = prompt_template.format_messages(
            policy=policy_text,
            invoice=invoice_text
        )

        # Invoke the LLM
        response = llm.invoke(messages)
        content = response.content.strip()

        # Clean markdown-style formatting if present (e.g., ```json blocks)
        if content.startswith("```json"):
            content = content.removeprefix("```json").strip()
        elif content.startswith("```"):
            content = content.removeprefix("```").strip()
        if content.endswith("```"):
            content = content.removesuffix("```").strip()

        # Try parsing the JSON string
        parsed = json.loads(content)

        # Validate keys in parsed response
        if not isinstance(parsed, dict) or "status" not in parsed or "reason" not in parsed:
            raise ValueError("LLM response is missing required fields.")

        return parsed

    except json.JSONDecodeError:
        # JSON decoding failed
        return {
            "status": "Error",
            "reason": f"Invalid JSON format in LLM response: {response.content}"
        }

    except Exception as e:
        # Catch-all for any other issues
        return {
            "status": "Error",
            "reason": f"Exception during analysis: {str(e)}"
        }