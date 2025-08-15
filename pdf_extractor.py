# modules/pdf_extractor.py
import pdfplumber
from docx import Document
from typing import Union, IO

def extract_text_from_pdf_path(path: str) -> str:
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_pdf_filelike(f: IO) -> str:
    """Accepts a file-like object (e.g. Streamlit uploaded file / BytesIO)."""
    text = ""
    # pdfplumber can open file-like objects
    with pdfplumber.open(f) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    try:
        f.seek(0)
    except Exception:
        pass
    return text

def extract_text_from_docx_filelike(f: IO) -> str:
    # python-docx accepts a file-like object
    doc = Document(f)
    paragraphs = [p.text for p in doc.paragraphs if p.text]
    try:
        f.seek(0)
    except Exception:
        pass
    return "\n".join(paragraphs)

def extract_text(input: Union[str, IO]) -> str:
    """
    If input is a string -> treat as local file path.
    Otherwise treat as file-like (Streamlit uploaded file).
    """
    if isinstance(input, str):
        # path given: detect extension
        if input.lower().endswith(".pdf"):
            return extract_text_from_pdf_path(input)
        elif input.lower().endswith((".docx", ".doc")):
            return extract_text_from_docx_filelike(input)  # docx lib can open path
        else:
            with open(input, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    else:
        # assume file-like object from Streamlit
        mime = getattr(input, "type", "") or ""
        name = getattr(input, "name", "") or ""
        if "pdf" in mime or name.lower().endswith(".pdf"):
            return extract_text_from_pdf_filelike(input)
        elif "word" in mime or name.lower().endswith((".docx", ".doc")):
            return extract_text_from_docx_filelike(input)
        else:
            # plain text: uploaded_file.read() returns bytes
            data = input.read()
            try:
                text = data.decode("utf-8", errors="ignore")
            except Exception:
                text = str(data)
            try:
                input.seek(0)
            except Exception:
                pass
            return text
