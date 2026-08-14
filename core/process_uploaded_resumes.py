import asyncio
from schemas.job import JobDescription
from schemas.match import MatchResult
from core.file_reader import extract_text_from_bytes
from core.file_validation import validate_resume_bytes, FileValidationError
from core.extract_resume import extract_resume_async
from core.hashing import compute_text_hash
from core.cache import get_cached_resume, save_resume_to_cache
from core.final_score import final_score

MAX_CONCURRENT_LLM_CALLS = 5


async def _process_one_upload(
    filename: str,
    file_bytes: bytes,
    job: JobDescription,
    semaphore: asyncio.Semaphore,
    results: list[MatchResult],
    skipped: list[dict],
) -> None:
    """
    Mirrors _process_one() from batch_process.py, but works on
    in-memory bytes (from an API upload) instead of a file on disk,
    and produces a scored MatchResult at the end instead of just a
    parsed Resume — this endpoint does read -> extract -> score in
    one pass, since that's the whole point of /resumes.
    """
    # Step 1: security validation
    try:
        validate_resume_bytes(file_bytes, filename)
    except FileValidationError as e:
        skipped.append({"filename": filename, "reason": str(e)})
        return

    # Step 2: extract text (resumes only accept pdf/docx, unlike JD's
    # more permissive txt support)
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix not in ("pdf", "docx"):
        skipped.append({"filename": filename, "reason": "Unsupported format"})
        return

    text = extract_text_from_bytes(file_bytes, filename)
    if text is None:
        skipped.append({"filename": filename, "reason": "Unreadable or empty content"})
        return

    # Step 3: cache check
    text_hash = compute_text_hash(text)
    cached_resume = get_cached_resume(text_hash)

    if cached_resume is not None:
        result = final_score(job, cached_resume)
        results.append(result)
        return

    # Step 4: the LLM call — gated by the semaphore
    async with semaphore:
        try:
            parsed_resume = await extract_resume_async(text)
            save_resume_to_cache(text_hash, parsed_resume)
            result = final_score(job, parsed_resume)
            results.append(result)
        except Exception as e:
            skipped.append({"filename": filename, "reason": f"Processing failed: {e}"})


async def process_uploaded_resumes(
    job: JobDescription,
    uploaded_files: list[tuple[str, bytes]],  # (filename, file_bytes) pairs
) -> tuple[list[MatchResult], list[dict]]:
    """
    Entry point for the /resumes endpoint. Returns (results, skipped)
    so the API can report both successes and — just as importantly —
    exactly which files were skipped and why.
    """
    results: list[MatchResult] = []
    skipped: list[dict] = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_LLM_CALLS)

    await asyncio.gather(*[
        _process_one_upload(filename, file_bytes, job, semaphore, results, skipped)
        for filename, file_bytes in uploaded_files
    ])

    return results, skipped
