# ai_resume_advisor_backend.py

import os
import json
import re
import ast
import tempfile

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyMuPDFLoader

# ✅ Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise EnvironmentError("🚫 GROQ_API_KEY not found in environment variables. Please check your .env.")

# ✅ Initialize Groq LLM
llm = ChatGroq(
    temperature=0,
    model_name="llama3-8b-8192",
    api_key=groq_api_key
)

# ✅ Prompt for structured JSON output
template = """
You are an expert AI Career Advisor evaluating how well a candidate's resume aligns with a specific job description (JD).

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Perform:
1. Extract candidate name, technical skills, experience, and education.
2. Extract relevant skills, qualifications, responsibilities from JD.
3. Do a skill gap analysis and list missing/weak skills.
4. Suggest 2-3 practical resume improvements.
5. Provide personalized career advice.

Return ONLY raw JSON:
- match_score (int from 0 to 100)
- missing_skills (list)
- recommendations (list)
- feedback (string)
"""

# ✅ Create LangChain prompt
prompt = PromptTemplate(
    input_variables=["resume_text", "jd_text"],
    template=template
)

# ✅ Create LLM chain
chain = LLMChain(llm=llm, prompt=prompt)

# ✅ Extract text from uploaded PDF resume
def extract_resume_text(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    loader = PyMuPDFLoader(tmp_path)
    pages = loader.load()
    resume_text = "\n".join(page.page_content for page in pages)
    return resume_text

# ✅ Main analysis function
def analyze_resume_vs_jd(uploaded_file, jd_text):
    resume_text = extract_resume_text(uploaded_file)

    response = chain.invoke({"resume_text": resume_text, "jd_text": jd_text})

    # Extract text depending on response structure
    response_text = response.get("text", str(response)) if isinstance(response, dict) else str(response)

    # Attempt JSON extraction
    try:
        json_match = re.search(r"\{[\s\S]*\}", response_text)
        if json_match:
            parsed_json = json.loads(json_match.group(0))
            if isinstance(parsed_json.get("match_score"), str):
                parsed_json["match_score"] = int(parsed_json["match_score"].replace("%", "").strip())
            return parsed_json
    except Exception as e:
        print(f"Regex JSON parse error: {e}")

    # Fallback using ast.literal_eval
    try:
        parsed = ast.literal_eval(response_text.strip())
        if isinstance(parsed, dict):
            if isinstance(parsed.get("match_score"), str):
                parsed["match_score"] = int(parsed["match_score"].replace("%", "").strip())
            return parsed
    except Exception as e:
        print(f"AST eval parse error: {e}")

    # Return raw output if parsing fails
    return {
        "error": "Could not parse response as valid JSON or Python dict.",
        "raw_output": response_text
    }
