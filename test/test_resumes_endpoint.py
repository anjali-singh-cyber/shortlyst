import requests

BASE_URL = "http://127.0.0.1:8000"

# Step 1: get a fresh job_id
jd_text = """
We are hiring a Backend Engineer to join our platform team.
Required skills: Python, FastAPI, PostgreSQL, Docker
Minimum experience: 2 years in a backend role
"""

jobs_response = requests.post(BASE_URL + "/jobs", data={"jd_text": jd_text})
job_id = jobs_response.json()["job_id"]
print(f"job_id: {job_id}\n")

# Step 2: upload resumes against that job_id
resume_files = [
    ("files", ("Amsterdam-Modern-Resume-Template.pdf",
               open("uploads/resumes/Amsterdam-Modern-Resume-Template.pdf", "rb"),
               "application/pdf")),
    ("files", ("New-York-Resume-Template-Creative.pdf",
               open("uploads/resumes/New-York-Resume-Template-Creative.pdf", "rb"),
               "application/pdf")),
]

resumes_response = requests.post(
    BASE_URL + "/resumes",
    data={"job_id": job_id},
    files=resume_files,
)

print(resumes_response.status_code)
print(resumes_response.json())