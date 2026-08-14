from dotenv import load_dotenv
from core.extract_job import extract_job_description
from core.extract_resume import extract_resume
from core.final_score import final_score

load_dotenv()

sample_jd = """
We are hiring a Backend Engineer to join our platform team.
Required skills: Python, FastAPI, PostgreSQL, Docker
Minimum experience: 2 years in a backend role
"""

partial_match_resume = """
Rahul Verma
rahul.verma@email.com

SKILLS
Python, Django, MySQL, Git, AWS

EXPERIENCE
Backend Developer — CloudNine Systems
March 2022 - Present
Built and maintained REST APIs using Django. Worked with MySQL databases
and deployed services on AWS EC2.

Junior Developer — StartupXYZ
June 2020 - Feb 2022
Wrote Python scripts for internal data processing.

PROJECTS
Inventory Management System - Django + MySQL based internal tool.
"""

job = extract_job_description(sample_jd)
resume = extract_resume(partial_match_resume)
result = final_score(job, resume)
print(result.model_dump_json(indent=2))