from schemas.resume import Resume
from prompts.resume_extraction import RESUME_EXTRACTION_SYSTEM_PROMPT
from llm.client import extract_structured
from llm.client import extract_structured_async

def extract_resume(raw_resume_text: str) -> Resume:
    """
    Takes raw resume text (extracted from a PDF/DOCX) and returns a
    validated Resume object.
    """
    if not raw_resume_text or not raw_resume_text.strip():
        raise ValueError(
            "extract_resume() received empty text. This usually means "
            "read_resume() returned None upstream — check the file path "
            "and that the file was actually read successfully."
        )

    result = extract_structured(
        system_prompt=RESUME_EXTRACTION_SYSTEM_PROMPT,
        user_content=raw_resume_text,
        schema=Resume,
    )
    return result  # type: ignore[return-value]


async def extract_resume_async(raw_resume_text: str) -> Resume:
    if not raw_resume_text or not raw_resume_text.strip():
        raise ValueError(
            "extract_resume_async() received empty text. This usually means "
            "read_resume() returned None upstream."
        )

    result = await extract_structured_async(
        system_prompt=RESUME_EXTRACTION_SYSTEM_PROMPT,
        user_content=raw_resume_text,
        schema=Resume,
    )
    return result  # type: ignore[return-value]