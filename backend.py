from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain.document_loaders import PyMuPDFLoader
from dotenv import load_dotenv
import os
import json
import tempfile
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise EnvironmentError("🚫 GROQ_API_KEY not found in environment variables.")

llm = ChatGroq(
    temperature=0,
    model_name="llama3-8b-8192",
    api_key=groq_api_key
)

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

Return STRICTLY only this JSON and no additional commentary.
"""

prompt = PromptTemplate(input_variables=["resume_text", "jd_text"], template=template)
chain = LLMChain(llm=llm, prompt=prompt)

def extract_resume_text(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    loader = PyMuPDFLoader(tmp_path)
    pages = loader.load()
    resume_text = "\n".join([page.page_content for page in pages])

    os.unlink(tmp_path)

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

    # Attempt direct JSON parsing first
    try:
        parsed_json = json.loads(response_text.strip())
        return {
            "success": True,
            "error": "",
            "data": parsed_json
        }
    except Exception as e:
        logging.warning(f"Direct JSON parse failed: {e}")

    # Fallback: extract JSON portion manually
    try:
        first_brace = response_text.find('{')
        last_brace = response_text.rfind('}')
        if first_brace != -1 and last_brace != -1:
            possible_json = response_text[first_brace:last_brace+1]
            parsed_json = json.loads(possible_json)
            return {
                "success": True,
                "error": "",
                "data": parsed_json
            }
        else:
            raise ValueError("No JSON object found in the response.")
    except Exception as e:
        logging.error(f"JSON parsing failed: {e}")
        return {
            "success": False,
            "error": f"JSON parsing failed: {e}",
            "data": None,
            "raw_output": response_text
        }