from core.read_resume import read_resume

# change this to a real resume file on your machine
file_path = "uploads/resumes/Amsterdam-Modern-Resume-Template.pdf"

text = read_resume(file_path)

if text is None:
    print("Could not read this file — unsupported format or empty/unreadable content.")
else:
    print("--- Extracted text ---")
    print(text)
    print(f"\n({len(text)} characters extracted)")