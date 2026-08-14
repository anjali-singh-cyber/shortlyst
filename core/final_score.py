from schemas.job import JobDescription
from schemas.resume import Resume
from schemas.match import MatchResult
from core.scoring import compute_skill_match
from prompts.verdict_prompt import VERDICT_SYSTEM_PROMPT
from llm.client import extract_structured
from pydantic import BaseModel, Field


class _VerdictOutput(BaseModel):
    """
    Internal schema — only what we ask the LLM to generate. The
    deterministic fields (skill_match_pct, missing_skills, candidate_name)
    are added afterward in final_score(), not requested from the LLM.
    """
    overall_fit_pct: float = Field(description="Holistic fit score, 0-100")
    verdict: str = Field(description="1-2 sentence final verdict")
    extraction_confidence: str = Field(description="'high', 'medium', or 'low'")


def final_score(job: JobDescription, resume: Resume) -> MatchResult:
    """
    Produces the final MatchResult for one candidate.

    Two-step process:
    1. Deterministic skill match (code, no LLM) — core/scoring.py
    2. LLM verdict call — sees ONLY the structured job/resume JSON,
       never raw resume text, minimizing hallucination surface.
    """
    skill_match_pct, missing_skills = compute_skill_match(job, resume)

    # Build a compact JSON view for the LLM — structured data only.
    grounding_input = (
        f"JOB DESCRIPTION:\n{job.model_dump_json(indent=2)}\n\n"
        f"CANDIDATE RESUME:\n{resume.model_dump_json(indent=2)}\n\n"
        f"COMPUTED SKILL MATCH: {skill_match_pct}% "
        f"(missing: {missing_skills if missing_skills else 'none'})"
    )

    verdict_output = extract_structured(
        system_prompt=VERDICT_SYSTEM_PROMPT,
        user_content=grounding_input,
        schema=_VerdictOutput,
    )

    return MatchResult(
        candidate_name=resume.name,
        skill_match_pct=skill_match_pct,
        missing_skills=missing_skills,
        overall_fit_pct=verdict_output.overall_fit_pct,  # type: ignore[attr-defined]
        verdict=verdict_output.verdict,  # type: ignore[attr-defined]
        extraction_confidence=verdict_output.extraction_confidence,  # type: ignore[attr-defined]
    )