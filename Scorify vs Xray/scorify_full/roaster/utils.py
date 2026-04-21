import pdfplumber
from docx import Document
import os

def extract_text_from_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return _from_pdf(file_path)
    elif ext in ['.doc', '.docx']:
        return _from_docx(file_path)
    raise ValueError(f"Unsupported file type: {ext}")

def _from_pdf(path: str) -> str:
    text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text.append(t)
    result = '\n'.join(text).strip()
    if not result:
        raise ValueError("Could not extract text. Make sure it's not a scanned image.")
    return result

def _from_docx(path: str) -> str:
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    result = '\n'.join(paragraphs).strip()
    if not result:
        raise ValueError("Could not extract text from Word document.")
    return result

def is_valid_cv_file(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in ['.pdf', '.doc', '.docx']
