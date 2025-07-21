import streamlit as st
import os
from backend import analyze_resume_vs_jd

# Load GROQ_API_KEY from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY is None:
    st.error("🚫 GROQ_API_KEY not found in environment variables. Please set it before running the app.")
    st.stop()

# Inject custom CSS for dual pink-blue gradient background and clean card-like container
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f9a8d4 0%, #a5f3fc 100%);
    }
    .main-container {
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 15px;
        padding: 30px;
        max-width: 700px;
        margin: auto;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Page configuration
st.set_page_config(page_title="AI Career Advisor", layout="centered")

# Centered container for a clean card appearance
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.title("🛠️ AI Career Advisor")
    st.markdown("Upload your **Resume (PDF)** and paste a **Job Description (JD)** to get AI-powered career insights.")

    # File uploader for resume
    uploaded_resume = st.file_uploader("📂 Upload Resume (PDF)", type=["pdf"])

    # JD input area
    jd_text = st.text_area("📝 Paste Job Description Here", height=200)

    # Analyze button
    if st.button("🚀 Analyze", use_container_width=True):
        if uploaded_resume and jd_text.strip():
            with st.spinner("🔄 Analyzing your resume against the JD..."):
                try:
                    result = analyze_resume_vs_jd(uploaded_resume, jd_text)
                except Exception as e:
                    st.error(f"❌ Error during analysis: {e}")
                    st.stop()

            st.success("✅ Analysis Complete")

            if "error" in result:
                st.error("⚠️ Could not parse the LLM output.")
                st.text_area("📝 Raw LLM Output", result.get("raw_output", "No output available."), height=300)
            else:
                st.markdown("### 📊 Match Score")
                st.markdown(f"<h2 style='color:#10b981'>{result['match_score']}%</h2>", unsafe_allow_html=True)

                st.markdown("### 🧩 Missing Skills")
                if result.get('missing_skills'):
                    st.markdown(
                        "".join([f"- {skill}<br>" for skill in result['missing_skills']]),
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown("*✅ None!*")

                st.markdown("### 🪄 Recommendations")
                if result.get("recommendations"):
                    for rec in result["recommendations"]:
                        st.markdown(f"🔹 {rec}")
                else:
                    st.markdown("*No specific recommendations.*")

                st.markdown("### 🎓 Career Advice")
                if result.get("feedback"):
                    st.info(result["feedback"])
                else:
                    st.info("No additional feedback provided.")
        else:
            st.warning("⚠️ Please upload a resume and paste a job description before analyzing.")

    st.markdown("---")
    st.caption("Built with ❤️ using Streamlit + Groq LLM for fast, accurate resume analysis.")

    st.markdown('</div>', unsafe_allow_html=True)