import fitz  # PyMuPDF - used for working with PDF files
import zipfile
import os
import re
from typing import List, Optional
from datetime import datetime


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text content from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: The extracted text from all pages of the PDF.
    """
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        # Catching unexpected issues during PDF reading
        print(f"Error reading PDF file '{pdf_path}': {e}")
    return text


def extract_pdfs_from_zip(zip_path: str, extract_dir: str) -> List[str]:
    """
    Extracts all PDF files from a ZIP archive to a specified directory.

    Args:
        zip_path (str): Path to the ZIP file.
        extract_dir (str): Directory where files should be extracted.

    Returns:
        List[str]: List of paths to the extracted PDF files.
    """
    pdf_files = []

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    except zipfile.BadZipFile:
        print(f"The file '{zip_path}' is not a valid ZIP archive.")
        return pdf_files
    except Exception as e:
        print(f"Unexpected error while extracting ZIP: {e}")
        return pdf_files

    try:
        # Collect all .pdf file paths from the extraction folder
        pdf_files = [
            os.path.join(extract_dir, f)
            for f in os.listdir(extract_dir)
            if f.lower().endswith('.pdf')
        ]
    except FileNotFoundError:
        print(f"The directory '{extract_dir}' was not found.")
    except Exception as e:
        print(f"Error listing PDF files: {e}")

    return pdf_files


def extract_invoice_date(text: str) -> Optional[str]:
    """
    Attempts to extract a valid date from invoice text using common formats.
    
    Supported formats:
    - DD/MM/YYYY
    - DD-MM-YYYY
    - YYYY-MM-DD
    - YYYY/MM/DD

    Args:
        text (str): Full text content of an invoice.

    Returns:
        Optional[str]: The invoice date in ISO format (YYYY-MM-DD) if found, else None.
    """
    # List of regex patterns to match common date formats
    date_patterns = [
        r"(\d{2}/\d{2}/\d{4})",       # e.g., 12/05/2024
        r"(\d{2}-\d{2}-\d{4})",       # e.g., 12-05-2024
        r"(\d{4}-\d{2}-\d{2})",       # e.g., 2024-05-12
        r"(\d{4}/\d{2}/\d{2})"        # e.g., 2024/05/12
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            raw_date = match.group(1)
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"):
                try:
                    parsed_date = datetime.strptime(raw_date, fmt)
                    return parsed_date.date().isoformat()  # Convert to YYYY-MM-DD format
                except ValueError:
                    # If format doesn't match, try the next one
                    continue
    return None  # No valid date found