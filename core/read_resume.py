from pathlib import Path
from typing import Optional
import pdfplumber
from docx import Document


def _read_pdf(file_path: Path) -> str:
    """Extracts all text from a PDF, page by page."""
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _read_docx(file_path: Path) -> str:
    """Extracts all paragraph text from a Word document."""
    doc = Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())


def read_resume(file_path: str) -> Optional[str]:
    """
    Reads a resume file and returns its raw text, or None if the file
    isn't a supported format (per the original plan: if it's not PDF/DOCX,
    skip it, don't error the whole batch out).
    """
    path = Path(file_path)

    if not path.exists():
        return None

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        text = _read_pdf(path)
    elif suffix == ".docx":
        text = _read_docx(path)
    else:
        return None  # unsupported format — caller should skip and log this

    # A file that "reads" but yields no usable text (e.g. a scanned
    # image PDF with no OCR layer) is functionally the same as unreadable.
    if not text.strip():
        return None

    return text