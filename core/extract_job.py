from schemas.job import JobDescription
from prompts.job_extraction import JD_EXTRACTION_SYSTEM_PROMPT
from llm.client import extract_structured


def extract_job_description(raw_jd_text: str) -> JobDescription:
    """
    Takes raw job description text (however the HR pasted/uploaded it)
    and returns a validated JobDescription object.
    """
    result = extract_structured(
        system_prompt=JD_EXTRACTION_SYSTEM_PROMPT,
        user_content=raw_jd_text,
        schema=JobDescription,
    )
    return result  # type: ignore[return-value]