# utils.py

from langchain.document_loaders import PyMuPDFLoader
import logging

def extract_pdf_text(file_path):
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    return " ".join([doc.page_content for doc in docs])

def configure_logger(log_file="app.log"):
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    return logger
