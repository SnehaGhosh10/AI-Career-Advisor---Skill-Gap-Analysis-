# ai_resume_advisor_backend.py

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.document_loaders import PyMuPDFLoader
from dotenv import load_dotenv
import os, json, logging, shutil, uuid

# ---------------- Logging ----------------
log_handler = logging.FileHandler("app.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# ---------------- Load env ----------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(temperature=0, model_name="llama3-70b-8192", groq_api_key=GROQ_API_KEY)

# ---------------- FastAPI app ----------------
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ---------------- Prompt Template ----------------
prompt_template = PromptTemplate(
    input_variables=["resume", "jd"],
    template=(
        "You are an AI Career Coach. Compare the provided RESUME and JOB DESCRIPTION (JD) carefully and generate a clear, human-readable analysis including:
\n"
        "1️⃣ A match percentage score between 0-100.
\n"
        "2️⃣ List of missing or recommended skills for the JD.
\n"
        "3️⃣ Personalized recommendations for improving resume alignment.
\n"
        "4️⃣ A concise 3-5 line friendly feedback summary for the candidate.
\n\n"
        "Please return the output in a clear markdown format for display without any JSON or additional explanations.
\n\n"
        "RESUME:\n{resume}\n\nJD:\n{jd}"
    )
)

# ---------------- Route ----------------
@app.post("/analyze/")
async def analyze_resume_jd(file: UploadFile = File(...), jd_text: str = Form(...)):
    # Save uploaded resume
    session_id = str(uuid.uuid4())
    temp_resume_path = f"temp_{session_id}.pdf"
    with open(temp_resume_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Extract text from PDF
    loader = PyMuPDFLoader(temp_resume_path)
    resume_docs = loader.load()
    resume_text = " ".join([doc.page_content for doc in resume_docs])

    # Prepare and invoke the chain
    chain = LLMChain(llm=llm, prompt=prompt_template)
    result = chain.invoke({"resume": resume_text[:12000], "jd": jd_text[:12000]})
    analysis_content = result["text"].strip()

    # Log and clean up
    logger.info(f"Analysis completed for session {session_id}")
    os.remove(temp_resume_path)

    return {"analysis": analysis_content}

# ---------------- Health Check ----------------
@app.get("/")
async def health():
    return {"message": "AI Resume Advisor Backend running 🚀"}

# ---------------- Run ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ai_resume_advisor_backend:app", host="0.0.0.0", port=8000, reload=True)