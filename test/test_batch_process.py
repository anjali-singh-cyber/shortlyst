from dotenv import load_dotenv
from core.batch_process import process_resume_folder

load_dotenv()

result = process_resume_folder("uploads/resumes")

print(f"✅ Parsed: {len(result.parsed)}")
for filename, resume in result.parsed:
    print(f"  - {filename}: {resume.name}")

print(f"\n⏭️  Skipped (unsupported format): {result.skipped_unsupported}")
print(f"⏭️  Skipped (unreadable/empty): {result.skipped_unreadable}")
print(f"❌ Failed extraction: {result.failed_extraction}")

