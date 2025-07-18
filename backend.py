from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain.document_loaders import PyMuPDFLoader
from dotenv import load_dotenv
import os
import json
import re
import ast
import tempfile

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise EnvironmentError("🚫 GROQ_API_KEY not found in environment variables.")

# Initialize Groq LLM with llama3
llm = ChatGroq(
    temperature=0,
    model_name="llama3-8b-8192",
    api_key=groq_api_key
)

# Prompt for structured JSON analysis
template = """
You are an expert AI Career Advisor. Evaluate how well a candidate's resume aligns with a specific job description (JD).

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Tasks:
1. Extract: candidate's name, technical skills, experience (roles + duration), education.
2. Extract: relevant skills, qualifications, responsibilities from JD.
3. Perform skill gap analysis: list missing/weak relevant skills.
4. Suggest 2-3 concise resume improvements aligned with JD.
5. Provide short, actionable personalized career advice.

Return ONLY valid, minified JSON in EXACTLY this format:
{"match_score": int, "missing_skills": ["skill1","skill2"], "recommendations": ["tip1","tip2"], "feedback": "short personalized advice"}

Return ONLY the JSON, no markdown, commentary, or explanations.
"""

# Create prompt template
prompt = PromptTemplate(
    input_variables=["resume_text", "jd_text"],
    template=template
)

# Create LLM chain
chain = LLMChain(llm=llm, prompt=prompt)

# Extract text from uploaded PDF resume
def extract_resume_text(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    loader = PyMuPDFLoader(tmp_path)
    pages = loader.load()
    resume_text = "\n".join([page.page_content for page in pages])
    return resume_text

# Main analysis function
def analyze_resume_vs_jd(uploaded_file, jd_text):
    resume_text = extract_resume_text(uploaded_file)

    try:
        response = chain.invoke({"resume_text": resume_text, "jd_text": jd_text})
    except Exception as e:
        return {"error": f"LLM invocation error: {str(e)}"}

    # Extract response text safely
    response_text = ""
    if isinstance(response, dict) and "text" in response:
        response_text = response["text"]
    else:
        response_text = str(response).strip()

    # Try direct JSON loading first (if LLM outputs clean JSON)
    try:
        parsed_json = json.loads(response_text)
        if isinstance(parsed_json.get("match_score"), str):
            parsed_json["match_score"] = int(parsed_json["match_score"].replace("%", "").strip())
        return parsed_json
    except Exception:
        pass

    # Try regex extraction if extra text surrounds JSON
    try:
        json_match = re.search(r"\{[\s\S]*\}", response_text)
        if json_match:
            cleaned_json = json_match.group(0)
            parsed_json = json.loads(cleaned_json)
            if isinstance(parsed_json.get("match_score"), str):
                parsed_json["match_score"] = int(parsed_json["match_score"].replace("%", "").strip())
            return parsed_json
    except Exception:
        pass

    # Fallback using ast.literal_eval if returned Python dict as string
    try:
        parsed = ast.literal_eval(response_text)
        if isinstance(parsed, dict):
            if isinstance(parsed.get("match_score"), str):
                parsed["match_score"] = int(parsed["match_score"].replace("%", "").strip())
            return parsed
    except Exception:
        pass

    # Final fallback with raw output for debugging
    return {
        "error": "Could not parse response as valid JSON or Python dict.",
        "raw_output": response_text
    }
