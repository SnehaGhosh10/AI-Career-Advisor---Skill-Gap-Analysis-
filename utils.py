def extract_pdf_text(file_path):
    from langchain.document_loaders import PyMuPDFLoader
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    return " ".join([doc.page_content for doc in docs])

def configure_logger():
    import logging
    handler = logging.FileHandler("app.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger