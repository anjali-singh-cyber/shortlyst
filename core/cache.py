import json
from pathlib import Path
from schemas.resume import Resume

CACHE_FILE = Path("uploads/.resume_cache.json")


def _load_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_cache(cache: dict) -> None:
    # Ensure the parent folder exists before writing — on a fresh clone
    # (like Render's), an empty "uploads/" directory may not exist at all,
    # since Git never tracks empty folders. Creating it here means the
    # cache works regardless of what folders happened to get committed.
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def get_cached_resume(text_hash: str) -> Resume | None:
    """Returns a previously-parsed Resume if this exact content was seen before, else None."""
    cache = _load_cache()
    entry = cache.get(text_hash)
    if entry is None:
        return None
    return Resume.model_validate(entry)


def save_resume_to_cache(text_hash: str, resume: Resume) -> None:
    """Stores a parsed Resume keyed by its content hash for future reuse."""
    cache = _load_cache()
    cache[text_hash] = resume.model_dump()
    _save_cache(cache)