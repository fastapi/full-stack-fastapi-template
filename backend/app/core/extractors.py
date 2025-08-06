import os
import tempfile
from app.core.db import engine
from sqlmodel import Session, select
import textract
import requests
from app.models import Document
from app.s3 import extract_text_from_s3_file

def extract_text_and_save_to_db(s3_url: str, document_id: str) -> None:
    try:
        with Session(engine) as session:
            text = extract_text_from_s3_file(s3_url)

            document_query = select(Document).where(Document.id == document_id)
            document = session.exec(document_query).first()

            if not document:
                raise Exception(f"Document with ID {document_id} not found")

            document.extracted_text = text
            session.add(document)
            session.commit()

    except Exception as e:
        print(f"Failed to extract and chunk text for document {document_id}: {e}")
    