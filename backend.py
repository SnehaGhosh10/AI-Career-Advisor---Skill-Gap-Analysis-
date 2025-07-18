from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain.document_loaders import PyMuPDFLoader
from dotenv import load_dotenv
import os
import json
import re
import tempfile
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise EnvironmentError("🚫 GROQ_API_KEY not found in environment variables.")

# Initialize Groq LLM
llm = ChatGroq(
    temperature=0,
    model_name="llama3-8b-8192",
    api_key=groq_api_key
)

# Prompt Template
template = """
You are an expert AI Career Advisor evaluating how well a candidate's resume aligns with a specific job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Perform:
1. Extract candidate's name, technical skills, experience, education.
2. Extract relevant skills, qualifications, and responsibilities from JD.
3. Perform skill gap analysis listing missing/weak relevant skills.
4. Suggest 2-3 actionable resume improvements.
5. Provide 1-2 sentence personalized career advice.

Return ONLY valid minified JSON in EXACTLY this structure:
{"match_score": int, "missing_skills": ["skill1","skill2"], "recommendations": ["tip1","tip2"], "feedback": "short advice"}

Return STRICTLY only this JSON and no additional commentary. If you add any text outside the JSON, you will fail the task.
"""

prompt = PromptTemplate(
    input_variables=["resume_text", "jd_text"],
    template=template
)

# LLM Chain
chain = LLMChain(llm=llm, prompt=prompt)

def extract_resume_text(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    loader = PyMuPDFLoader(tmp_path)
    pages = loader.load()
    resume_text = "\n".join([page.page_content for page in pages])

    os.unlink(tmp_path)  # Clean up temp file

    return resume_text

def analyze_resume_vs_jd(uploaded_file, jd_text):
    resume_text = extract_resume_text(uploaded_file)

    try:
        response = chain.invoke({"resume_text": resume_text, "jd_text": jd_text})
    except Exception as e:
        logging.error(f"LLM invocation error: {e}")
        return {
            "success": False,
            "error": f"LLM invocation error: {str(e)}",
            "data": None,
            "raw_output": ""
        }

    response_text = response.get("text") if isinstance(response, dict) else str(response)
    logging.info(f"LLM raw response: {response_text}")

    json_match = re.search(r"\{(?:[^{}]|(?R))*\}", response_text, re.DOTALL)
    if json_match:
        try:
            cleaned_json = json_match.group(0)
            parsed_json = json.loads(cleaned_json)
            return {
                "success": True,
                "error": "",
                "data": parsed_json
            }
        except Exception as e:
            logging.error(f"JSON parsing failed: {e}")
            return {
                "success": False,
                "error": f"JSON parsing failed: {e}",
                "data": None,
                "raw_output": response_text
            }

    logging.error("Could not parse response as valid JSON.")
    return {
        "success": False,
        "error": "Could not parse response as valid JSON.",
        "data": None,
        "raw_output": response_text
    }