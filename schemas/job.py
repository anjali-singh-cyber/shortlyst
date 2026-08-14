from pydantic import BaseModel, Field
from typing import Optional


class JobDescription(BaseModel):
    """
    Structured representation of a job description.

    Only `role` is required. Real JDs are inconsistent — some don't
    state minimum experience, some skip education requirements entirely.
    Every other field is Optional so the LLM is never forced to invent
    a value just to satisfy the schema.
    """

    role: str = Field(description="The job title / role being hired for")

    required_skills: Optional[list[str]] = Field(
        default=None,
        description="Skills explicitly stated as required in the JD"
    )

    preferred_experience: Optional[str] = Field(
        default=None,
        description="Preferred (not mandatory) years/type of experience, if mentioned"
    )

    minimum_experience: Optional[str] = Field(
        default=None,
        description="Minimum years of experience required, if mentioned"
    )

    education_requirement: Optional[str] = Field(
        default=None,
        description="Education requirement, e.g. 'Bachelor's in CS or related field'"
    )

    responsibilities: Optional[list[str]] = Field(
        default=None,
        description="Key responsibilities listed in the JD"
    )