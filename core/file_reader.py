from io import BytesIO
from typing import Optional
import pdfplumber
from docx import Document


def extract_text_from_bytes(file_bytes: bytes, filename: str) -> Optional[str]:
    """
    Generic text extractor for uploaded file content — works on raw
    bytes directly (no need to save to disk first), unlike
    core/read_resume.py which reads from a file path. Used for both
    JD uploads and (soon) resume uploads coming through the API.

    Supports PDF, DOCX, and plain .txt — .txt wasn't handled before
    since resumes are rarely plain text, but JDs often get pasted
    from an email or Notion doc as a .txt export.
    """
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if suffix == "pdf":
        text_parts = []
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        text = "\n".join(text_parts)

    elif suffix == "docx":
        doc = Document(BytesIO(file_bytes))
        text = "\n".join(para.text for para in doc.paragraphs if para.text.strip())

    elif suffix == "txt":
        text = file_bytes.decode("utf-8", errors="ignore")

    else:
        return None  # unsupported format

    if not text.strip():
        return None  # empty/unreadable content, same principle as Part 3

    return text