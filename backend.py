from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.document_loaders import PyMuPDFLoader
from dotenv import load_dotenv
import os, json, logging

log_handler = logging.FileHandler("app.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(temperature=0, model="llama3-70b-8192", groq_api_key=GROQ_API_KEY)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class AnalysisRequest(BaseModel):
    query: str
    config: dict

@app.post("/query/")
async def analyze_resume_jd(req: AnalysisRequest):
    jd_text = req.config.get("jd_text", "")
    resume_path = "resume_temp.pdf"
    resume_text = ""
    if os.path.exists(resume_path):
        loader = PyMuPDFLoader(resume_path)
        resume_docs = loader.load()
        resume_text = " ".join([doc.page_content for doc in resume_docs])
    prompt_template = PromptTemplate(input_variables=["resume", "jd"], template="You are an AI Career Advisor. Compare RESUME and JD, return structured JSON with match_score, missing_skills, recommendations, feedback.\n\nRESUME:\n{resume}\n\nJD:\n{jd}\n\nJSON only.")
    chain = LLMChain(llm=llm, prompt=prompt_template)
    result = chain.invoke({"resume": resume_text[:12000], "jd": jd_text[:12000]})
    try:
        json_result = json.loads(result["text"].strip())
    except:
        json_result = {"raw": result["text"]}
    return {"response": json_result}

@app.get("/")
async def health():
    return {"message": "Backend running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn main:app --host 0.0.0.0 --port 8000