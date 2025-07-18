# frontend.py
import streamlit as st
import os
from main_mod import analyze_resume_vs_jd

# Load GROQ_API_KEY from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY is None:
    st.error("🚫 GROQ_API_KEY not found in environment variables. Please set it before running the app.")
    st.stop()

# Streamlit page config
st.set_page_config(page_title="AI Career Advisor", layout="centered")
st.title("🤖 AI Career Advisor")
st.markdown("Upload your **Resume (PDF)** and paste a **Job Description (JD)** to get AI-powered career insights.")

# File uploader for resume
uploaded_resume = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])

# JD input area
jd_text = st.text_area("🧾 Paste Job Description Here", height=200)

# Analyze button
if st.button("🔍 Analyze"):
    if uploaded_resume and jd_text.strip():
        with st.spinner("🔄 Analyzing your resume against the JD..."):
            try:
                result = analyze_resume_vs_jd(uploaded_resume, jd_text)
            except Exception as e:
                st.error(f"❌ Error during analysis: {e}")
                st.stop()
        
        st.success("✅ Analysis Complete")

        # Check for parsing errors
        if "error" in result:
            st.error("⚠️ Could not parse the LLM output.")
            st.text_area("📝 Raw LLM Output", result.get("raw_output", "No output available."), height=300)

        else:
            # Match Score
            st.markdown("### 📈 <span style='font-size:22px;'>Match Score</span>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color:#4CAF50'>{result['match_score']}%</h2>", unsafe_allow_html=True)

            # Missing Skills
            st.markdown("### 🧠 <span style='font-size:22px;'>Missing Skills</span>", unsafe_allow_html=True)
            if result.get('missing_skills'):
                st.markdown(
                    "".join([f"- {skill}<br>" for skill in result['missing_skills']]),
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("*✅ None!*")

            # Recommendations
            st.markdown("### 🛠️ <span style='font-size:22px;'>Recommendations</span>", unsafe_allow_html=True)
            if result.get("recommendations"):
                for rec in result["recommendations"]:
                    st.markdown(f"🔹 {rec}")
            else:
                st.markdown("*No specific recommendations.*")

            # Career Advice
            st.markdown("### 🎯 <span style='font-size:22px;'>Career Advice</span>", unsafe_allow_html=True)
            if result.get("feedback"):
                st.info(result["feedback"])
            else:
                st.info("No additional feedback provided.")

    else:
        st.warning("⚠️ Please upload a resume and paste a job description before analyzing.")

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit + Groq LLM for fast, accurate resume analysis.")

