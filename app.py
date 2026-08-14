import streamlit as st
import requests
import pandas as pd
from PIL import Image
import os

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")


logo = Image.open("assets/logo.png")

st.set_page_config(page_title="Shortlyst", page_icon=logo)

with st.sidebar:
    st.image(logo, width=200)
    st.markdown("---")

    if st.session_state.get("job_id"):
        st.markdown("**Currently screening for:**")
        st.info(st.session_state.get("current_role", "a role"))
    else:
        st.markdown("**How it works:**")
        st.markdown("1. Paste or upload a JD\n2. Upload resumes\n3. Get scored, ranked candidates")

    st.markdown("---")
    if st.button("🔄 Start Over", use_container_width=True):
        st.session_state.stage = "awaiting_jd"
        st.session_state.job_id = None
        if "display_results" in st.session_state:
            del st.session_state.display_results
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! Paste a job description below, or upload a JD file, and I'll get started."}
        ]
        st.rerun()

st.image(logo, width=280)
st.caption("Paste a job description to get started, then upload resumes to screen.")

# session_state persists across Streamlit's reruns — without this,
# the chat history would reset every time the HR does anything.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! Paste a job description below, or upload a JD file, and I'll get started."}
    ]

if "stage" not in st.session_state:
    st.session_state.stage = "awaiting_jd"   # awaiting_jd -> awaiting_resumes -> done

if "job_id" not in st.session_state:
    st.session_state.job_id = None


def call_jobs_api(jd_text: str = None, jd_file=None) -> dict:
    """Calls POST /jobs — same endpoint we tested via Swagger/requests earlier."""
    if jd_file is not None:
        files = {"file": (jd_file.name, jd_file.getvalue())}
        response = requests.post(f"{API_URL}/jobs", files=files)
    else:
        response = requests.post(f"{API_URL}/jobs", data={"jd_text": jd_text})

    response.raise_for_status()
    return response.json()


def call_resumes_api(job_id: str, resume_files: list) -> dict:
    """Calls POST /resumes with a batch of uploaded resume files."""
    files = [
        ("files", (f.name, f.getvalue(), f.type))
        for f in resume_files
    ]
    response = requests.post(
        f"{API_URL}/resumes",
        data={"job_id": job_id},
        files=files,
    )
    response.raise_for_status()
    return response.json()


# ---- Part C: render chat history ----
for msg in st.session_state.messages:
    avatar = logo if msg["role"] == "assistant" else "🧑‍💼"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])


# ---- Part D: JD input (stage 1) ----
if st.session_state.stage == "awaiting_jd":
    jd_file = st.file_uploader(
        "Or upload a JD file instead (PDF/DOCX/TXT)",
        type=["pdf", "docx", "txt"],
        key="jd_file_uploader",
    )

    if jd_file is not None:
        st.session_state.messages.append({"role": "user", "content": f"📎 Uploaded: {jd_file.name}"})
        with st.spinner("Reading job description..."):
            try:
                result = call_jobs_api(jd_file=jd_file)
                st.session_state.job_id = result["job_id"]
                role = result["extracted_job"].get("role", "this role")
                st.session_state.current_role = role  # NEW — used by the sidebar
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Got it — I've read the JD for **{role}**. Now upload the resumes you want screened."
                })
                st.session_state.stage = "awaiting_resumes"
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Sorry, I couldn't read that file: {e}"
                })
        st.rerun()

prompt = st.chat_input("Or paste the job description as text...")
if prompt and st.session_state.stage == "awaiting_jd":
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Reading job description..."):
        try:
            result = call_jobs_api(jd_text=prompt)
            st.session_state.job_id = result["job_id"]
            role = result["extracted_job"].get("role", "this role")
            st.session_state.current_role = role  # NEW — used by the sidebar
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Got it — I've read the JD for **{role}**. Now upload the resumes you want screened."
            })
            st.session_state.stage = "awaiting_resumes"
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Sorry, something went wrong reading that: {e}"
            })
    st.rerun()


# ---- Part E: resume upload (stage 2) ----
if st.session_state.stage == "awaiting_resumes":
    resume_files = st.file_uploader(
        "Upload resumes (PDF/DOCX) — you can select multiple",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key="resume_uploader",
    )

    if resume_files:
        if st.button(f"Score {len(resume_files)} resume(s)"):
            st.session_state.messages.append({
                "role": "user",
                "content": f"📎 Uploaded {len(resume_files)} resume(s) for screening."
            })
            with st.spinner("Screening resumes — this may take a moment..."):
                try:
                    result = call_resumes_api(st.session_state.job_id, resume_files)
                    st.session_state.last_results = result
                    st.session_state.stage = "done"
                except Exception as e:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Something went wrong while scoring: {e}"
                    })
            st.rerun()


# ---- Part F: process results ONCE, save to display_results ----
if st.session_state.stage == "done" and "last_results" in st.session_state:
    result = st.session_state.last_results
    results = result["results"]
    skipped = result["skipped"]

    summary_lines = [f"Done! Screened {len(results)} candidate(s).\n"]
    if skipped:
        summary_lines.append(f"\n⚠️ Skipped {len(skipped)} file(s):")
        for s in skipped:
            summary_lines.append(f"- {s['filename']}: {s['reason']}")

    st.session_state.messages.append({"role": "assistant", "content": "\n".join(summary_lines)})

    # sort best-fit first, so the HR sees the strongest candidates up top
    results_sorted = sorted(results, key=lambda r: r["overall_fit_pct"], reverse=True)

    # NEW: save to a SEPARATE, persistent key. last_results is deleted below
    # (so we don't reprocess/re-append the summary message on every rerun),
    # but display_results stays, so the cards below can keep rendering on
    # every future rerun while we're in the "done" stage.
    st.session_state.display_results = results_sorted

    del st.session_state.last_results
    st.rerun()


# ---- Render result cards — runs on EVERY rerun while stage == "done",
# so cards persist instead of flashing once and disappearing. ----
if st.session_state.stage == "done" and "display_results" in st.session_state:
    for r in st.session_state.display_results:
        fit = r["overall_fit_pct"]
        color = "🟢" if fit >= 60 else "🟡" if fit >= 30 else "🔴"

        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {color} {r['candidate_name'] or 'Unknown candidate'}")
            with col2:
                st.metric("Overall Fit", f"{fit}%")

            st.progress(fit / 100)

            c1, c2 = st.columns(2)
            c1.metric("Skill Match", f"{r['skill_match_pct']}%")
            c2.caption(f"Extraction confidence: **{r['extraction_confidence']}**")

            if r["missing_skills"]:
                st.markdown(f"**Missing:** {', '.join(r['missing_skills'])}")

            st.markdown(f"_{r['verdict']}_")

    df = pd.DataFrame(st.session_state.display_results)
    csv = df.to_csv(index=False)
    st.download_button(
        "📥 Download results as CSV",
        data=csv,
        file_name="shortlyst_results.csv",
        mime="text/csv",
    )


# ---- "Screen for a new role" reset button ----
if st.session_state.stage == "done":
    if st.button("🔄 Screen for a new role"):
        st.session_state.stage = "awaiting_jd"
        st.session_state.job_id = None
        if "display_results" in st.session_state:
            del st.session_state.display_results
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Sure — paste or upload a new job description whenever you're ready."
        })
        st.rerun()