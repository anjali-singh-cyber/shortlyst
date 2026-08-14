from dotenv import load_dotenv
from core.read_resume import read_resume
from core.extract_resume import extract_resume

load_dotenv()

file_path = "uploads/resumes/Amsterdam-Modern-Resume-Template.pdf"  # change this to a real resume file on your machine

text = read_resume(file_path)
print(f"DEBUG: text is {'None' if text is None else f'{len(text)} chars'}")  # temp debug line

resume = extract_resume(text)
print(resume.model_dump_json(indent=2))