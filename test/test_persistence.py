# test_persistence.py
from core.db import engine
from sqlmodel import Session, select
from core.db_models import JobRecord, ResultRecord

with Session(engine) as session:
    jobs = session.exec(select(JobRecord)).all()
    results = session.exec(select(ResultRecord)).all()

print(f"Jobs found in DB: {len(jobs)}")
for j in jobs:
    print(f"  - {j.id}: {j.role}")

print(f"\nResults found in DB: {len(results)}")
for r in results:
    print(f"  - {r.candidate_name}: {r.overall_fit_pct}%")