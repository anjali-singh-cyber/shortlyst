from difflib import SequenceMatcher
from schemas.job import JobDescription
from schemas.resume import Resume


def _normalize(skill: str) -> str:
    """Lowercase and strip so 'React.js' and 'react js' compare fairly."""
    return skill.lower().strip().replace(".", "").replace("-", " ")


def _is_fuzzy_match(required_skill: str, candidate_skill: str, threshold: float = 0.8) -> bool:
    """
    Catches near-duplicates like 'React' vs 'React.js', 'Postgres' vs
    'PostgreSQL', without needing a hand-maintained synonym dictionary.
    SequenceMatcher gives a similarity ratio between 0 and 1; anything
    over the threshold counts as the same skill. Also treats exact
    substring matches (either direction) as a match, since fuzzy string
    similarity alone undervalues short skills like 'Git' vs 'Git/GitHub'.
    """
    a, b = _normalize(required_skill), _normalize(candidate_skill)
    if a in b or b in a:
        return True
    return SequenceMatcher(None, a, b).ratio() >= threshold


def compute_skill_match(job: JobDescription, resume: Resume) -> tuple[float, list[str]]:
    """
    Returns (skill_match_pct, missing_skills), computed entirely in code.

    This is deliberately NOT an LLM call. The same job + resume pair
    must always produce the same percentage — an HR comparing two
    candidates needs numbers she can trust are consistent, not numbers
    that might shift on a re-run.
    """
    required = job.required_skills or []
    candidate_skills = resume.skills or []

    if not required:
        # No required skills stated in the JD — nothing to score against.
        # Returning 100% here would be misleading (looks like a perfect
        # match), so we treat this as "unscoreable" and let the caller
        # / UI decide how to display it. 0.0 is a safer default than a
        # fabricated 100%.
        return 0.0, []

    missing = []
    matched_count = 0

    for req_skill in required:
        found = any(_is_fuzzy_match(req_skill, cand_skill) for cand_skill in candidate_skills)
        if found:
            matched_count += 1
        else:
            missing.append(req_skill)

    match_pct = round((matched_count / len(required)) * 100, 1)
    return match_pct, missing