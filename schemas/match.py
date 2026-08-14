from pydantic import BaseModel, Field
from typing import Optional


class MatchResult(BaseModel):
    """
    Final output shown to the HR for one candidate.

    skill_match_pct and missing_skills are computed in plain Python
    (see core/scoring.py) — deterministic, reproducible, and explainable.
    overall_fit_pct and verdict come from the LLM, but only ever see
    already-extracted structured data, never raw resume text again.
    """

    candidate_name: Optional[str] = None
    skill_match_pct: float = Field(description="% of required skills matched, computed deterministically")
    missing_skills: list[str] = Field(description="Required skills not found in the resume")
    overall_fit_pct: float = Field(description="LLM's holistic fit assessment, 0-100")
    verdict: str = Field(description="Short 1-2 sentence summary of fit")
    extraction_confidence: str = Field(
        description="'high', 'medium', or 'low' — flags resumes that were sparse or poorly extracted"
    )