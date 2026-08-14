import asyncio
import time
from dotenv import load_dotenv
from core.batch_process import process_resume_folder_async

load_dotenv()

async def main():
    start = time.time()
    result = await process_resume_folder_async("uploads/resumes")
    elapsed = time.time() - start

    print(f"✅ Parsed: {len(result.parsed)}")
    for filename, resume in result.parsed:
        print(f"  - {filename}: {resume.name}")

    print(f"\n⏭️  Skipped (unsupported): {result.skipped_unsupported}")
    print(f"⏭️  Skipped (unreadable): {result.skipped_unreadable}")
    print(f"❌ Failed: {result.failed_extraction}")
    print(f"\n⏱️  Took {elapsed:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())