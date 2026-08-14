import hashlib


def compute_text_hash(text: str) -> str:
    """
    Deterministic fingerprint of resume text content. Used to detect
    when the same resume is uploaded again (same candidate applying to
    a different role, or accidentally re-uploaded), so we can skip
    re-paying for LLM extraction on content we've already parsed.
    """
    normalized = text.strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()