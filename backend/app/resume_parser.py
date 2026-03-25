"""Service for extracting and parsing resume/CV data from PDF and DOCX files."""

import io
import re

import docx
from PyPDF2 import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text content from a PDF file."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text content from a DOCX file."""
    doc = docx.Document(io.BytesIO(file_bytes))
    text_parts: list[str] = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text_parts.append(paragraph.text.strip())
    return "\n".join(text_parts)


def _extract_email(text: str) -> str:
    """Extract the first email address found in the text."""
    match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else ""


def _extract_phone(text: str) -> str:
    """Extract the first phone number found in the text (Brazilian format)."""
    patterns = [
        r"\+55\s*\(?\d{2}\)?\s*\d{4,5}[\-\s]?\d{4}",
        r"\(?\d{2}\)?\s*\d{4,5}[\-\s]?\d{4}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return ""


def _extract_linkedin(text: str) -> str:
    """Extract LinkedIn profile URL from the text."""
    match = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-_%]+/?", text
    )
    return match.group(0) if match else ""


def _extract_name(text: str) -> str:
    """Extract the candidate's name (typically the first non-empty line)."""
    lines = text.strip().split("\n")
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        if "@" in cleaned or "http" in cleaned.lower():
            continue
        if re.match(r"^[\d\(\)+\-\s]+$", cleaned):
            continue
        if len(cleaned) < 3 or len(cleaned) > 80:
            continue
        if re.match(r"^[A-ZÀ-ÖØ-Ýa-zà-öø-ÿ\s\.]+$", cleaned):
            return cleaned
    return ""


def _extract_city_state(text: str) -> tuple[str, str]:
    """Extract city and state (UF) from the text."""
    uf_list = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
        "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
        "RS", "RO", "RR", "SC", "SP", "SE", "TO",
    ]
    uf_pattern = "|".join(uf_list)

    patterns = [
        rf"([A-ZÀ-Öa-zà-ö\s]+)\s*[/\-,]\s*({uf_pattern})\b",
        rf"\b({uf_pattern})\s*[/\-,]\s*([A-ZÀ-Öa-zà-ö\s]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if groups[0] in uf_list:
                return groups[1].strip(), groups[0]
            return groups[0].strip(), groups[1].strip()

    return "", ""


def _extract_skills(text: str) -> list[str]:
    """Extract skills from common resume sections."""
    skills: list[str] = []

    section_patterns = [
        r"(?:habilidades|competências|skills|tecnologias|conhecimentos)\s*:?\s*\n?(.*?)(?:\n\n|\Z)",
        r"(?:HABILIDADES|COMPETÊNCIAS|SKILLS|TECNOLOGIAS|CONHECIMENTOS)\s*:?\s*\n?(.*?)(?:\n\n|\Z)",
    ]

    for pattern in section_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            section_text = match.group(1).strip()
            items = re.split(r"[,;•\-\n|]+", section_text)
            for item in items:
                cleaned = item.strip()
                if cleaned and len(cleaned) > 1 and len(cleaned) < 60:
                    skills.append(cleaned)
            break

    return skills


def _extract_education(text: str) -> list[str]:
    """Extract education entries from common resume sections."""
    education: list[str] = []

    section_patterns = [
        r"(?:formação|educação|education|formação acadêmica|escolaridade)\s*:?\s*\n?(.*?)(?:\n\n|\Z)",
        r"(?:FORMAÇÃO|EDUCAÇÃO|EDUCATION|FORMAÇÃO ACADÊMICA|ESCOLARIDADE)\s*:?\s*\n?(.*?)(?:\n\n|\Z)",
    ]

    for pattern in section_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            section_text = match.group(1).strip()
            lines = section_text.split("\n")
            for line in lines:
                cleaned = line.strip().lstrip("•-– ")
                if cleaned and len(cleaned) > 3:
                    education.append(cleaned)
            break

    return education


def _extract_experience(text: str) -> list[str]:
    """Extract work experience entries from common resume sections."""
    experience: list[str] = []

    section_patterns = [
        r"(?:experiência|experience|experiência profissional|histórico profissional)\s*:?\s*\n?(.*?)(?:\n\n|\Z)",
        r"(?:EXPERIÊNCIA|EXPERIENCE|EXPERIÊNCIA PROFISSIONAL|HISTÓRICO PROFISSIONAL)\s*:?\s*\n?(.*?)(?:\n\n|\Z)",
    ]

    for pattern in section_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            section_text = match.group(1).strip()
            lines = section_text.split("\n")
            for line in lines:
                cleaned = line.strip().lstrip("•-– ")
                if cleaned and len(cleaned) > 3:
                    experience.append(cleaned)
            break

    return experience


def parse_resume_text(text: str) -> dict[str, str | list[str]]:
    """Parse resume text and extract structured data.

    Returns a dictionary with the following keys:
        name, email, phone, city, state, linkedin, skills, education, experience
    """
    city, state = _extract_city_state(text)

    return {
        "name": _extract_name(text),
        "email": _extract_email(text),
        "phone": _extract_phone(text),
        "city": city,
        "state": state,
        "linkedin": _extract_linkedin(text),
        "skills": _extract_skills(text),
        "education": _extract_education(text),
        "experience": _extract_experience(text),
    }
