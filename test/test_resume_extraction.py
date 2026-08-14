from dotenv import load_dotenv
from core.extract_resume import extract_resume

load_dotenv()

sample_resume = """
Anjali Singh
anjali.singh@email.com

SKILLS
Python, C++, Data Structures & Algorithms, Git

EXPERIENCE
Software Development Intern — TechCorp
June 2025 - August 2025
Worked on building internal automation tools using Python. Wrote scripts
to automate resume submission tracking.

PROJECTS
ConquerDSA - A personal DSA intelligence system unifying LeetCode and
GitHub activity.

NextStep - A Slack app that surfaces job listings via slash commands.
"""

if __name__ == "__main__":
    resume = extract_resume(sample_resume)
    print(resume.model_dump_json(indent=2))