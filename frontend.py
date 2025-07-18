import streamlit as st
import os
from backend import analyze_resume_vs_jd

st.set_page_config(page_title="AI Career Advisor", layout="centered")
st.title("🧑‍💼 AI Career Advisor")
st.markdown("Upload your **Resume (PDF)** and paste a **Job Description (JD)** below to receive personalized, actionable AI-powered career insights.")

uploaded_resume = st.file_uploader("📂 **Upload Your Resume (PDF)**", type=["pdf"])
jd_text = st.text_area("📝 **Paste Job Description Here**", height=200)

if st.button("🚀 Analyze My Resume"):
    if uploaded_resume and jd_text.strip():
        with st.spinner("🤖 Analyzing your resume against the job description..."):
            result = analyze_resume_vs_jd(uploaded_resume, jd_text)

        if result["success"]:
            st.success("✅ Analysis Complete!")
            data = result["data"]

            st.markdown("## 🎯 Match Score")
            st.markdown(f"<h2 style='color:#4CAF50'>{data.get('match_score', 0)}%</h2>", unsafe_allow_html=True)

            st.markdown("## 🧩 Missing Key Skills")
            if data.get("missing_skills"):
                st.markdown("<br>".join([f"✅ {skill}" for skill in data["missing_skills"]]), unsafe_allow_html=True)
            else:
                st.markdown("🎉 All key skills are present for this JD!")

            st.markdown("## 🛠️ Improvement Recommendations")
            if data.get("recommendations"):
                for rec in data["recommendations"]:
                    st.markdown(f"💡 {rec}")
            else:
                st.markdown("✅ No additional recommendations at this time.")

            st.markdown("## 🌱 Personalized Career Advice")
            if data.get("feedback"):
                st.info(f"💭 {data['feedback']}")
            else:
                st.info("No additional feedback provided.")

        else:
            st.error(f"⚠️ {result['error']}")
            st.text_area("🔍 Raw AI Output (for debugging)", result.get("raw_output", "No output captured."), height=300)

    else:
        st.warning("⚠️ Please upload a resume and paste a job description before analyzing.")

st.markdown("---")
st.caption("🚀 Built with ❤️ using Streamlit + Groq LLM for fast, insightful resume analysis. Empower your career journey with AI.")