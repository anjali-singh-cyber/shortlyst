from pathlib import Path

# Every real file format starts with a fixed byte signature.
# PDF files always start with these exact 5 bytes: %PDF-
PDF_MAGIC_BYTES = b"%PDF-"

# DOCX files are actually ZIP archives under the hood, so they start
# with the ZIP format's signature.
DOCX_MAGIC_BYTES = b"PK\x03\x04"

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB — generous for a resume, blocks abuse


class FileValidationError(Exception):
    """Raised when an uploaded file fails security validation."""
    pass


def validate_resume_file(file_path: str) -> None:
    """
    Validates a file BEFORE we attempt to read/parse it:
    1. Size check — rejects absurdly large files early (cheap check,
       prevents someone uploading a 2GB file to exhaust disk/memory).
    2. Magic-byte check — verifies the file's actual binary content
       matches what its extension claims, not just trusting the name.

    Raises FileValidationError if anything fails. Caller decides how
    to handle that (skip + log, in our batch pipeline's case).
    """
    path = Path(file_path)

    if not path.exists():
        raise FileValidationError(f"File does not exist: {file_path}")

    size = path.stat().st_size
    if size > MAX_FILE_SIZE_BYTES:
        raise FileValidationError(
            f"File exceeds {MAX_FILE_SIZE_BYTES // (1024*1024)}MB limit: {size} bytes"
        )

    if size == 0:
        raise FileValidationError("File is empty")

    suffix = path.suffix.lower()

    with open(path, "rb") as f:
        header = f.read(8)  # only need the first few bytes to check signature

    if suffix == ".pdf":
        if not header.startswith(PDF_MAGIC_BYTES):
            raise FileValidationError(
                f"File has .pdf extension but content doesn't match PDF format "
                f"(possible spoofed/corrupted file): {path.name}"
            )
    elif suffix == ".docx":
        if not header.startswith(DOCX_MAGIC_BYTES):
            raise FileValidationError(
                f"File has .docx extension but content doesn't match DOCX format "
                f"(possible spoofed/corrupted file): {path.name}"
            )
    else:
        raise FileValidationError(f"Unsupported file type: {suffix}")

def validate_resume_bytes(file_bytes: bytes, filename: str) -> None:
    """
    Same validation logic as validate_resume_file(), but for in-memory
    bytes from an API upload — there's no file on disk to check.
    """
    size = len(file_bytes)
    if size > MAX_FILE_SIZE_BYTES:
        raise FileValidationError(
            f"File exceeds {MAX_FILE_SIZE_BYTES // (1024*1024)}MB limit: {filename}"
        )
    if size == 0:
        raise FileValidationError(f"File is empty: {filename}")

    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    header = file_bytes[:8]

    if suffix == "pdf":
        if not header.startswith(PDF_MAGIC_BYTES):
            raise FileValidationError(
                f"File has .pdf extension but content doesn't match PDF format: {filename}"
            )
    elif suffix == "docx":
        if not header.startswith(DOCX_MAGIC_BYTES):
            raise FileValidationError(
                f"File has .docx extension but content doesn't match DOCX format: {filename}"
            )
    else:
        raise FileValidationError(f"Unsupported file type: {filename}")