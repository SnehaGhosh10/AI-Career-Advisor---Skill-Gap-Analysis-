import streamlit as st
import requests
import uuid
import pyperclip
 
FASTAPI_URL = "https://mycareerapi.fly.dev/query/"


st.set_page_config(page_title="🧑‍💻 AI Career Advisor", page_icon="🧑‍💻")
st.title("🧑‍💻 AI Career Advisor: Resume & JD Skill Gap Analyzer")

if 'threads' not in st.session_state:
    st.session_state.threads = {}
if 'current_thread_id' not in st.session_state:
    st.session_state.current_thread_id = None

def start_new_analysis():
    new_thread_id = str(uuid.uuid4())
    st.session_state.threads[new_thread_id] = []
    st.session_state.current_thread_id = new_thread_id
    st.success(f"Started new analysis session: {new_thread_id}")

if st.button("Start New Analysis"):
    start_new_analysis()

with st.sidebar:
    st.header("Analysis History")
    if st.session_state.threads:
        ids = [f"Session {k[:8]}" for k in st.session_state.threads.keys()]
        sel = st.selectbox("Select Analysis", ["Select"] + ids)
        if sel != "Select":
            tid = list(st.session_state.threads.keys())[ids.index(sel)]
            st.session_state.current_thread_id = tid
    else:
        st.info("No analyses yet. Start a new analysis.")

resume_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
jd_text = st.text_area("Paste JD Text Here")

if st.button("Run Analysis"):
    if not st.session_state.current_thread_id:
        st.error("Start a new analysis session first.")
    elif resume_file and jd_text:
        files = {"resume": resume_file.getvalue()}
        payload = {"query": "analyze_resume_jd", "config": {"thread_id": st.session_state.current_thread_id, "jd_text": jd_text}}
        response = requests.post(FASTAPI_URL, json=payload)
        if response.status_code == 200:
            result = response.json()
            st.session_state.threads[st.session_state.current_thread_id].append(result["response"])
            st.success("Analysis complete.")
        else:
            st.error(f"Error: {response.text}")
    else:
        st.error("Upload resume and paste JD text.")

if st.session_state.current_thread_id:
    st.subheader("📊 Analysis Results")
    results = st.session_state.threads[st.session_state.current_thread_id]
    if results:
        for idx, result in enumerate(results):
            st.json(result)
            col1, col2 = st.columns(2)
            if col1.button(f"Copy {idx+1}"):
                pyperclip.copy(str(result))
                st.success("Copied.")
            if col2.button(f"Delete {idx+1}"):
                st.session_state.threads[st.session_state.current_thread_id].pop(idx)
                st.rerun()
    if st.button("Delete Session"):
        del st.session_state.threads[st.session_state.current_thread_id]
        st.session_state.current_thread_id = None
        st.rerun()