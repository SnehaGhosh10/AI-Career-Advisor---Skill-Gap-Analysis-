# frontend.py

import streamlit as st
import os
from backend import analyze_resume_vs_jd

# Streamlit page config
st.set_page_config(page_title="AI Career Advisor", layout="centered")
st.title("🧑‍💼✨ AI Career Advisor")
st.markdown(
    "Upload your **Resume (PDF)** and paste a **Job Description (JD)** below to receive personalized, actionable AI-powered career insights."
)

# Upload and JD Input
uploaded_resume = st.file_uploader("📂 **Upload Your Resume (PDF)**", type=["pdf"])
jd_text = st.text_area("📝 **Paste Job Description Here**", height=200)

# Analyze button
if st.button("🚀 Analyze My Resume"):
    if uploaded_resume and jd_text.strip():
        with st.spinner("🤖 Analyzing your resume against the job description..."):
            result = analyze_resume_vs_jd(uploaded_resume, jd_text)

        st.success("✅ Analysis Complete!")

        if "error" in result:
            st.error("⚠️ Could not parse the AI output properly.")
            st.text_area("🔍 Raw AI Output (for debugging)", result.get("raw_output", "No output captured."), height=300)
        else:
            # Display Match Score
            st.markdown("## 🎯 Match Score")
            st.markdown(
                f"<h2 style='color:#4CAF50'>{result.get('match_score', 0)}%</h2>",
                unsafe_allow_html=True,
            )

            # Display Missing Skills
            st.markdown("## 🧩 Missing Key Skills")
            if result.get("missing_skills"):
                st.markdown(
                    "".join([f"✅ {skill}<br>" for skill in result["missing_skills"]]),
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("🎉 All key skills are present for this JD!")

            # Display Recommendations
            st.markdown("## 🛠️ Improvement Recommendations")
            if result.get("recommendations"):
                for rec in result["recommendations"]:
                    st.markdown(f"💡 {rec}")
            else:
                st.markdown("✅ No additional recommendations at this time.")

            # Display Career Advice
            st.markdown("## 🌱 Personalized Career Advice")
            if result.get("feedback"):
                st.info(f"💭 {result['feedback']}")
            else:
                st.info("No additional feedback provided.")
    else:
        st.warning("⚠️ Please upload a resume and paste a job description before analyzing.")

# Footer
st.markdown("---")
st.caption("🚀 Built with ❤️ using Streamlit + Groq LLM for fast, insightful resume analysis. Empower your career journey with AI.")
