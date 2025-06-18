from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
import os
from uuid import uuid4
from datetime import datetime
from app.utils.pdf_parser import extract_text_from_pdf, extract_pdfs_from_zip, extract_invoice_date
from app.core.analyzer import analyze_invoice
from app.core.vector_store import store_invoice_embedding

router = APIRouter()

# Directory to temporarily store uploaded files
UPLOAD_DIR = "tmp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_policy_and_invoices(
    employee_name: str = Form(...),
    policy_pdf: UploadFile = File(...),
    invoices_zip: UploadFile = File(...)
):
    """
    Endpoint to upload an HR policy PDF and a ZIP of invoice PDFs.
    Analyzes each invoice against the policy using LLM and stores embeddings.

    Args:
        employee_name (str): Name of the employee uploading the files.
        policy_pdf (UploadFile): Uploaded HR policy PDF.
        invoices_zip (UploadFile): ZIP file containing invoice PDFs.

    Returns:
        dict: Summary of analysis for each invoice.
    """
    try:
        # Create a unique folder for this upload session
        session_id = str(uuid4())
        session_dir = os.path.join(UPLOAD_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)

        # === Save the uploaded policy PDF ===
        try:
            policy_path = os.path.join(session_dir, policy_pdf.filename)
            with open(policy_path, "wb") as f:
                f.write(await policy_pdf.read())
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"error": f"Failed to save policy PDF: {str(e)}"}
            )

        # === Save the uploaded invoices ZIP ===
        try:
            zip_path = os.path.join(session_dir, invoices_zip.filename)
            with open(zip_path, "wb") as f:
                f.write(await invoices_zip.read())
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"error": f"Failed to save invoice ZIP file: {str(e)}"}
            )

        # === Extract text from the policy PDF ===
        policy_text = extract_text_from_pdf(policy_path)
        if not policy_text.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "The policy PDF appears to be empty or unreadable."}
            )

        # === Extract PDFs from the ZIP and parse them ===
        invoice_paths = extract_pdfs_from_zip(zip_path, session_dir)
        if not invoice_paths:
            return JSONResponse(
                status_code=400,
                content={"error": "No valid PDF invoices found in the ZIP file."}
            )

        # Read and process each invoice
        invoice_texts = {}
        for path in invoice_paths:
            try:
                text = extract_text_from_pdf(path)
                if text.strip():  # Avoid storing empty content
                    invoice_texts[os.path.basename(path)] = text
            except Exception as e:
                print(f"Warning: Could not extract text from {path}: {e}")

        analysis_results = {}

        for filename, invoice_text in invoice_texts.items():
            try:
                # Analyze invoice content against the policy using LLM
                analysis = analyze_invoice(policy_text, invoice_text)

                # Combine invoice and LLM decision for embedding
                combined_text = f"{invoice_text}\n\nLLM Decision: {analysis['reason']}"

                # Prepare metadata for vector storage
                metadata = {
                    "employee_name": employee_name,
                    "invoice_file": filename,
                    "status": analysis["status"],
                    "reason": analysis["reason"],
                    "date": extract_invoice_date(invoice_text) or datetime.now().isoformat()
                }

                # Store in vector DB
                store_invoice_embedding(combined_text, metadata)
                analysis_results[filename] = analysis

            except Exception as e:
                analysis_results[filename] = {
                    "status": "Error",
                    "reason": f"Failed to analyze invoice: {str(e)}"
                }

        return {
            "employee_name": employee_name,
            "policy_summary": policy_text[:300],  # Optional: preview of the policy text
            "num_invoices": len(invoice_texts),
            "analysis_results": analysis_results
        }

    except Exception as e:
        # Catch-all error in case something unexpected goes wrong
        return JSONResponse(status_code=500, content={"error": f"Internal server error: {str(e)}"})