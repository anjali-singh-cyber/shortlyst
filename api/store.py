import json
from sqlmodel import Session, select
from schemas.job import JobDescription
from schemas.match import MatchResult
from core.db import engine
from core.db_models import JobRecord, ResultRecord


def create_job(job: JobDescription) -> str:
    with Session(engine) as session:
        record = JobRecord(
            role=job.role,
            job_json=job.model_dump_json(),
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record.id


def get_job(job_id: str) -> JobDescription | None:
    with Session(engine) as session:
        record = session.get(JobRecord, job_id)
        if record is None:
            return None
        return JobDescription.model_validate(json.loads(record.job_json))


def save_results(job_id: str, results: list[MatchResult]) -> None:
    with Session(engine) as session:
        for result in results:
            record = ResultRecord(
                job_id=job_id,
                candidate_name=result.candidate_name,
                overall_fit_pct=result.overall_fit_pct,
                result_json=result.model_dump_json(),
            )
            session.add(record)
        session.commit()


def get_results(job_id: str) -> list[MatchResult]:
    with Session(engine) as session:
        statement = select(ResultRecord).where(ResultRecord.job_id == job_id)
        records = session.exec(statement).all()
        return [MatchResult.model_validate(json.loads(r.result_json)) for r in records]