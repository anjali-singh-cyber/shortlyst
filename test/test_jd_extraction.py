from dotenv import load_dotenv
from core.extract_job import extract_job_description

load_dotenv()

sample_jd = """
We are hiring a Backend Engineer to join our platform team.

Required skills: Python, FastAPI, PostgreSQL, Docker
Minimum experience: 2 years in a backend role

Responsibilities:
- Design and build REST APIs
- Own database schema design and migrations
- Collaborate with the frontend team on API contracts

Nice to have: experience with Kubernetes, exposure to async Python.
"""

if __name__ == "__main__":
    job = extract_job_description(sample_jd)
    print(job.model_dump_json(indent=2))
    