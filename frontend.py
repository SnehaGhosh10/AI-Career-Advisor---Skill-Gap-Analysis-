# frontend.py
import streamlit as st
import requests
import uuid
import os

st.set_page_config(page_title="AI Career Advisor - Resume vs JD Analysis", layout="centered")

st.title("📊 AI Career Advisor")
st.subheader("Analyze your Resume against a Job Description")

FASTAPI_URL = "https://mycareerapi.fly.dev/query/"

# Session state for session_id
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.success(f"Started new analysis session: {st.session_state.session_id}")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
jd_text = st.text_area("Paste JD Text Here", height=200, placeholder="Paste the Job Description you want to match against your resume...")

if st.button("Run Analysis"):
    if uploaded_file is None:
        st.warning("Please upload your resume in PDF format.")
    elif jd_text.strip() == "":
        st.warning("Please paste the job description text.")
    else:
        with st.spinner("Analyzing your resume against the job description..."):
            # Save uploaded PDF temporarily
            temp_filename = "resume_temp.pdf"
            with open(temp_filename, "wb") as f:
                f.write(uploaded_file.read())

            payload = {
                "query": "resume_vs_jd_analysis",
                "config": {
                    "jd_text": jd_text
                }
            }

            try:
                response = requests.post(FASTAPI_URL, json=payload)
                if response.status_code == 200:
                    result = response.json().get("response", {})

                    if "match_score" in result:
                        st.header("📈 Analysis Results")
                        st.write(f"✅ **Match Score:** {result['match_score']}%")
                        st.write(f"🛠️ **Missing Skills:** {', '.join(result['missing_skills']) if result['missing_skills'] else 'None'}")
                        st.write(f"💡 **Recommendations:**")
                        for rec in result["recommendations"]:
                            st.write(f"- {rec}")
                        st.write(f"📝 **Feedback:** {result['feedback']}")
                    elif "raw" in result:
                        st.write("⚠️ The model returned raw text as it could not parse structured JSON:")
                        st.code(result["raw"])
                    else:
                        st.error("Unexpected response format.")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

        # Clean up the temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

st.sidebar.header("Analysis History")
st.sidebar.info("Analysis results will appear here after running.")
