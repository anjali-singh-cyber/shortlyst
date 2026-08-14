from dotenv import load_dotenv
load_dotenv()


from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Optional
from pydantic import BaseModel
from core.extract_job import extract_job_description
from core.file_reader import extract_text_from_bytes
from api.store import create_job
from core.process_uploaded_resumes import process_uploaded_resumes
from api.store import get_job, save_results
from core.db import init_db

init_db()

app = FastAPI(title="FitCheck API")


class JDUploadResponse(BaseModel):
    job_id: str
    extracted_job: dict


@app.post("/jobs", response_model=JDUploadResponse)
async def upload_job_description(
    jd_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    """
    Accepts EITHER pasted text OR an uploaded file (PDF/DOCX/TXT) —
    not both. This mirrors how a person would actually give a JD to
    an assistant: sometimes typed, sometimes as a file, and the
    assistant shouldn't care which.
    """
    if not jd_text and not file:
        raise HTTPException(400, "Provide either jd_text or a file")
    if jd_text and file:
        raise HTTPException(400, "Provide only one of jd_text or file, not both")

    if file:
        file_bytes = await file.read()
        extracted_text = extract_text_from_bytes(file_bytes, file.filename)
        if extracted_text is None:
            raise HTTPException(
                400,
                "Could not read this file — unsupported format or no extractable text",
            )
    else:
        extracted_text = jd_text

    job = extract_job_description(extracted_text)
    job_id = create_job(job)
    return JDUploadResponse(job_id=job_id, extracted_job=job.model_dump())


@app.get("/health")
def health_check():
    return {"status": "ok"}

class ResumeUploadResponse(BaseModel):
    job_id: str
    results: list[dict]
    skipped: list[dict]


@app.post("/resumes", response_model=ResumeUploadResponse)
async def upload_resumes(
    job_id: str = Form(...),
    files: list[UploadFile] = File(...),
):
    """
    Step 2 of the HR flow: given a job_id from a previous /jobs call,
    upload a batch of resume files and get back scored results.
    """
    job = get_job(job_id)
    if job is None:
        raise HTTPException(404, f"job_id not found: {job_id}")

    uploaded_files = [(f.filename, await f.read()) for f in files]

    results, skipped = await process_uploaded_resumes(job, uploaded_files)
    save_results(job_id, results)

    return ResumeUploadResponse(
        job_id=job_id,
        results=[r.model_dump() for r in results],
        skipped=skipped,
    )