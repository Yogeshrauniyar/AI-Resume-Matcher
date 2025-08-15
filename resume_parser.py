import pdfplumber
from docx import Document
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Load model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def extract_text(uploaded_file):
    """
    Extract text based on uploaded file type (PDF, DOCX, or plain text).
    """
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(uploaded_file)
    else:
        # Assume plain text file
        return str(uploaded_file.read(), "utf-8")

def semantic_similarity(text1, text2):
    """
    Compute semantic similarity score between two texts (percentage).
    Returns 0 if either text is empty.
    """
    if not text1.strip() or not text2.strip():
        return 0.0
    embeddings = model.encode([text1, text2])
    sim_score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return round(sim_score * 100, 2)

def parse_resume_sections(text):
    """
    Parse resume text into logical sections by headers like Skills, Education, Projects, Experience.
    Returns dictionary of sections with text content.
    """
    section_headers = ['skills', 'education', 'projects', 'experience']
    sections = {header: "" for header in section_headers}
    text_lower = text.lower()

    indices = {}
    for header in section_headers:
        match = re.search(rf'\b{header}\b', text_lower)
        if match:
            indices[header] = match.start()

    sorted_headers = sorted(indices.items(), key=lambda x: x[1])

    for i, (header, start_idx) in enumerate(sorted_headers):
        end_idx = sorted_headers[i + 1][1] if i + 1 < len(sorted_headers) else len(text)
        content = text[start_idx:end_idx].strip()
        content = re.sub(rf'(?i){header}', '', content).strip()
        sections[header] = content

    return sections

def parse_job_description_sections(text):
    """
    Parse job description text into sections similar to resume sections.
    """
    section_headers = ['skills', 'education', 'projects', 'experience']
    sections = {header: "" for header in section_headers}
    text_lower = text.lower()

    indices = {}
    for header in section_headers:
        match = re.search(rf'\b{header}\b', text_lower)
        if match:
            indices[header] = match.start()

    sorted_headers = sorted(indices.items(), key=lambda x: x[1])

    for i, (header, start_idx) in enumerate(sorted_headers):
        end_idx = sorted_headers[i + 1][1] if i + 1 < len(sorted_headers) else len(text)
        content = text[start_idx:end_idx].strip()
        content = re.sub(rf'(?i){header}', '', content).strip()
        sections[header] = content

    return sections
