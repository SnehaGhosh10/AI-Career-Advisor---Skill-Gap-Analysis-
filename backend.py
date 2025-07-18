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
import logging

# ------------------ Logging ------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ------------------ Load Environment Variables ------------------
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise EnvironmentError("🚫 GROQ_API_KEY not found in environment variables.")

# ------------------ Initialize Groq LLM ------------------
llm = ChatGroq(
    temperature=0,
    model_name="llama3-8b-8192",
    api_key=groq_api_key
)

# ------------------ Prompt Template ------------------
template = """
You are an expert AI Career Advisor. Evaluate how well a candidate's resume aligns with a specific job description (JD).

Read carefully:

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Your task:
1. Extract:
   - Candidate's name
   - Technical skills
   - Experience (roles and durations)
   - Education

2. Extract from JD:
   - Relevant skills
   - Required qualifications
   - Main responsibilities

3. Perform a skill gap analysis:
   - List only missing or weak skills relevant to the JD.

4. Suggest 2-3 actionable resume improvements to align with the JD.

5. Provide short, personalized career advice for the candidate.

Instructions:
- Consider only skills relevant to the JD.
- Be concise, avoid irrelevant details.
- Return ONLY valid, minified JSON using EXACTLY this structure:

{"match_score": int, "missing_skills": ["skill1","skill2"], "recommendations": ["tip1","tip2"], "feedback": "short personalized advice"}

Return only this JSON, without any markdown, commentary, or explanation.
"""

prompt = PromptTemplate(
    input_variables=["resume_text", "jd_text"],
    template=template
)

# ------------------ LLM Chain ------------------
chain = LLMChain(llm=llm, prompt=prompt)

# ------------------ Extract Text from Uploaded Resume ------------------
def extract_resume_text(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    loader = PyMuPDFLoader(tmp_path)
    pages = loader.load()
    resume_text = "\n".join([page.page_content for page in pages])
    return resume_text

# ------------------ Main Analysis Function ------------------
def analyze_resume_vs_jd(uploaded_file, jd_text):
    resume_text = extract_resume_text(uploaded_file)
    logging.info("Resume text extracted. Invoking Groq LLM...")

    # Using .invoke is correct here:
    response = chain.invoke({"resume_text": resume_text, "jd_text": jd_text})

    if isinstance(response, dict) and "text" in response:
        response_text = response["text"]
    else:
        response_text = str(response)

    # Clean Groq output
    response_text = response_text.strip().replace("```json", "").replace("```", "").strip()

    # Attempt JSON parsing using regex
    try:
        json_match = re.search(r"\{[\s\S]*\}", response_text)
        if json_match:
            cleaned_json = json_match.group(0)
            parsed_json = json.loads(cleaned_json)

            # Ensure match_score is an integer if returned as a string
            if isinstance(parsed_json.get("match_score"), str):
                parsed_json["match_score"] = int(parsed_json["match_score"].replace("%", "").strip())

            logging.info(f"Parsed JSON successfully: {parsed_json}")
            return parsed_json
    except Exception as e:
        logging.error(f"JSON parsing via regex failed: {e}")

    # Fallback using ast.literal_eval
    try:
        parsed = ast.literal_eval(response_text)
        if isinstance(parsed, dict):
            if isinstance(parsed.get("match_score"), str):
                parsed["match_score"] = int(parsed["match_score"].replace("%", "").strip())

            logging.info(f"Parsed JSON using ast.literal_eval: {parsed}")
            return parsed
    except Exception as e:
        logging.error(f"ast.literal_eval parsing failed: {e}")

    # Return raw output on failure
    logging.warning("Returning raw output due to parsing failure.")
    return {
        "error": "Could not parse response as valid JSON or Python dict.",
        "raw_output": response_text
    }
