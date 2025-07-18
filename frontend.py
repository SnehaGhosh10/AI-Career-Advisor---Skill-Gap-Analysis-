import streamlit as st
import os
from backend import analyze_resume_vs_jd

# Load GROQ_API_KEY from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY is None:
    st.error("🚫 GROQ_API_KEY not found in environment variables. Please set it before running the app.")
    st.stop()

# Streamlit page config
st.set_page_config(page_title="AI Career Advisor", layout="centered")
st.title("🧑‍💼✨ AI Career Advisor")
st.markdown("Upload your **Resume (PDF)** and paste a **Job Description (JD)** to receive smart, actionable career insights powered by AI.")

# File uploader for resume
uploaded_resume = st.file_uploader("📂 **Upload Your Resume (PDF)**", type=["pdf"])

# JD input area
jd_text = st.text_area("📝 **Paste Job Description Here**", height=200)

# Analyze button
if st.button("🚀 Analyze My Resume"):
    if uploaded_resume and jd_text.strip():
        with st.spinner("🤖 Thinking... Analyzing your resume against the job description."):
            try:
                result = analyze_resume_vs_jd(uploaded_resume, jd_text)
            except Exception as e:
                st.error(f"❌ An error occurred during analysis: {e}")
                st.stop()
        
        st.success("✅ Analysis Complete!")

        # Check for parsing errors
        if "error" in result:
            st.error("⚠️ Could not parse the AI output properly.")
            st.text_area("🔍 Raw AI Output for Debugging", result.get("raw_output", "No output available."), height=300)

        else:
            # Match Score
            st.markdown("## 🎯 Match Score")
            st.markdown(f"<h2 style='color:#4CAF50'>{result['match_score']}%</h2>", unsafe_allow_html=True)

            # Missing Skills
            st.markdown("## 🧩 Missing Key Skills")
            if result.get('missing_skills'):
                st.markdown(
                    "".join([f"✅ {skill}<br>" for skill in result['missing_skills']]),
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("🎉 All required skills are present!")

            # Recommendations
            st.markdown("## 🛠️ Improvement Recommendations")
            if result.get("recommendations"):
                for rec in result["recommendations"]:
                    st.markdown(f"💡 {rec}")
            else:
                st.markdown("✅ No additional recommendations at this time.")

            # Career Advice
            st.markdown("## 🌱 Personalized Career Advice")
            if result.get("feedback"):
                st.info(f"💭 {result['feedback']}")
            else:
                st.info("No additional feedback provided at this time.")

    else:
        st.warning("⚠️ Please upload a resume and paste a job description to proceed with analysis.")

# Footer
st.markdown("---")
st.caption("🚀 Built with ❤️ using Streamlit + Groq LLM for fast, insightful resume analysis. Connect your potential with opportunities!")
