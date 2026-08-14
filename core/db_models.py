from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
import uuid


class JobRecord(SQLModel, table=True):
    """
    One row per uploaded job description. We store the full extracted
    JobDescription as a JSON string (job_json) rather than splitting
    every field into its own column — simpler for an MVP, since we
    already trust Pydantic's validation on the way in/out. A 'more
    correct' relational design would split required_skills into its
    own table, but that's a v3-level optimization, not needed now.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    role: str
    job_json: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResultRecord(SQLModel, table=True):
    """One row per scored candidate, linked back to the job it was scored against."""
    id: int | None = Field(default=None, primary_key=True)
    job_id: str = Field(foreign_key="jobrecord.id")
    candidate_name: str | None = None
    overall_fit_pct: float
    result_json: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))