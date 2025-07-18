from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain.document_loaders import PyMuPDFLoader
import os
from dotenv import load_dotenv
import json, re, ast
import tempfile

# Load environment variables
from dotenv import load_dotenv
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

# Prompt template for structured JSON output
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



# Create a prompt template
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

    response = chain.invoke({"resume_text": resume_text, "jd_text": jd_text})

    if isinstance(response, dict) and "text" in response:
        response_text = response["text"]
    else:
        response_text = str(response)

    # Try extracting JSON using regex
    try:
        json_match = re.search(r"\{[\s\S]*\}", response_text)
        if json_match:
            cleaned_json = json_match.group(0)
            parsed_json = json.loads(cleaned_json)
            # Ensure match_score is int
            if isinstance(parsed_json.get("match_score"), str):
                parsed_json["match_score"] = int(parsed_json["match_score"].replace("%", "").strip())
            return parsed_json
    except Exception:
        pass

    # Fallback using ast.literal_eval
    try:
        parsed = ast.literal_eval(response_text.strip())
        if isinstance(parsed, dict):
            if isinstance(parsed.get("match_score"), str):
                parsed["match_score"] = int(parsed["match_score"].replace("%", "").strip())
            return parsed
    except Exception:
        pass

    # If all parsing fails
    return {
        "error": "Could not parse response as valid JSON or Python dict.",
        "raw_output": response_text
    }
