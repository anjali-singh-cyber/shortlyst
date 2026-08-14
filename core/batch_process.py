import asyncio
from pathlib import Path
from dataclasses import dataclass, field
from schemas.resume import Resume
from core.read_resume import read_resume
from core.extract_resume import extract_resume_async
from core.hashing import compute_text_hash
from core.cache import get_cached_resume, save_resume_to_cache
from core.file_validation import validate_resume_file, FileValidationError

MAX_CONCURRENT_LLM_CALLS = 5


@dataclass
class BatchResult:
    parsed: list[tuple[str, Resume]] = field(default_factory=list)
    skipped_unsupported: list[str] = field(default_factory=list)
    skipped_unreadable: list[str] = field(default_factory=list)
    failed_extraction: list[tuple[str, str]] = field(default_factory=list)


async def _process_one(
    file_path: Path,
    semaphore: asyncio.Semaphore,
    result: BatchResult,
) -> None:
    filename = file_path.name

    # NEW: security validation happens before we even attempt to read
    # the file's content.
    try:
        validate_resume_file(str(file_path))
    except FileValidationError as e:
        if file_path.suffix.lower() not in (".pdf", ".docx"):
            result.skipped_unsupported.append(filename)
        else:
            result.skipped_unreadable.append(filename)
        return

    # Step 1: read the file — fast, local, no need to gate this
    text = read_resume(str(file_path))
    # ... rest unchanged

    if text is None:
        if file_path.suffix.lower() not in (".pdf", ".docx"):
            result.skipped_unsupported.append(filename)
        else:
            result.skipped_unreadable.append(filename)
        return

    # Step 2: cache check — also fast and local
    text_hash = compute_text_hash(text)
    cached = get_cached_resume(text_hash)

    if cached is not None:
        result.parsed.append((filename, cached))
        return

    # Step 3: the actual LLM call — THIS is what we gate with the semaphore.
    # Only MAX_CONCURRENT_LLM_CALLS of these can be "inside" this block
    # across all resumes at once; everyone else waits their turn here.
    async with semaphore:
        try:
            parsed_resume = await extract_resume_async(text)
            save_resume_to_cache(text_hash, parsed_resume)
            result.parsed.append((filename, parsed_resume))
        except Exception as e:
            result.failed_extraction.append((filename, str(e)))


async def process_resume_folder_async(folder_path: str) -> BatchResult:
    """
    Async version — processes resumes with bounded concurrency
    (MAX_CONCURRENT_LLM_CALLS at a time) instead of one at a time.
    """
    result = BatchResult()
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_LLM_CALLS)

    files = [f for f in sorted(folder.iterdir()) if f.is_file()]

    # asyncio.gather runs all these coroutines concurrently — the
    # semaphore inside _process_one is what actually caps how many
    # LLM calls happen at once, even though all tasks "start" together.
    await asyncio.gather(*[_process_one(f, semaphore, result) for f in files])

    return result