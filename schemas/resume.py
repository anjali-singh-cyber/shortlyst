from pydantic import BaseModel, Field
from typing import Optional


class Experience(BaseModel):
    """
    One work experience entry. Every field is Optional — a resume might
    list a company and role but skip a description, or list a duration
    without explicit dates. We take whatever is actually there.
    """

    company: Optional[str] = Field(default=None, description="Company name")
    role: Optional[str] = Field(default=None, description="Job title held at this company")
    duration: Optional[str] = Field(
        default=None,
        description="Duration/dates as stated in the resume, e.g. 'Jan 2022 - Present'"
    )
    description: Optional[str] = Field(
        default=None,
        description="What the person did in this role, as described in the resume"
    )
    skills_used: Optional[list[str]] = Field(
        default=None,
        description="Skills/technologies explicitly mentioned in this experience entry"
    )


class Resume(BaseModel):
    """
    Structured representation of a resume.

    Resumes are wildly inconsistent in format — one might have a phone
    number and no projects section, another might have projects but no
    listed certifications. Every field is Optional by design. Nothing
    here is 'required' because no field is guaranteed to exist across
    real-world resumes.
    """

    name: Optional[str] = Field(default=None, description="Candidate's full name")
    email: Optional[str] = Field(default=None, description="Candidate's email address")
    phone: Optional[str] = Field(default=None, description="Candidate's phone number")
    total_experience: Optional[str] = Field(
        default=None,
        description="Total years of experience, only if explicitly stated in the resume"
    )
    skills: Optional[list[str]] = Field(
        default=None,
        description="Skills explicitly listed in a skills section"
    )
    experiences: Optional[list[Experience]] = Field(
        default=None,
        description="Work experience entries"
    )
    projects: Optional[list[str]] = Field(
        default=None,
        description="Project names/descriptions, if a projects section exists"
    )
    certifications: Optional[list[str]] = Field(
        default=None,
        description="Certifications listed, if any"
    )