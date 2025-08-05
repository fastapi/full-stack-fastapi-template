import os
import tempfile
from app.core.db import engine
from sqlmodel import Session, select
import textract
import requests
from app.models import Document


def extract_text_from_file(s3_url: str) -> str:
    try:
        response = requests.get(s3_url)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name

        text = textract.process(tmp_path).decode("utf-8") or ""

        os.remove(tmp_path)

        return text

    except Exception as e:
        raise Exception(f"Failed to extract text: {e}")
    
def extract_text_and_save_to_db(s3_url: str, document_id: str) -> None:
    try:
        with Session(engine) as session:
            text = extract_text_from_file(s3_url)

            document_query = select(Document).where(Document.id == document_id)
            document = session.exec(document_query).first()

            if not document:
                raise Exception(f"Document with ID {document_id} not found")

            document.extracted_text = text
            session.add(document)
            session.commit()

    except Exception as e:
        print(f"Failed to extract and chunk text for document {document_id}: {e}")
    