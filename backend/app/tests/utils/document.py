from sqlmodel import Session

from app import crud
from app.models import Document, DocumentCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_document(db: Session) -> Document:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    document_in = DocumentCreate(title=title, description=description)
    return crud.create_document(session=db, document_in=document_in, owner_id=owner_id)
