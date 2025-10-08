from sqlmodel import Session

from app import crud
from app.models import DocumentCreate, DocumentPublic, User
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_document(db: Session, user: User | None = None) -> DocumentPublic:
    user = user or create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    extracted_text = f"Extracted text for {title} by {owner_id}"
    document_in = DocumentCreate(
        filename=f"{title}.pdf",
        content_type="application/pdf",
        size=1024,
        s3_url=f"https://example-bucket.s3.amazonaws.com/{title}.pdf",
        s3_key=f"{owner_id}/{title}.pdf",
        title=title,
    )
    return crud.create_document(
        session=db,
        document_in=document_in,
        owner_id=owner_id,
        extracted_text=extracted_text,
    )


def create_random_documents(db: Session) -> list[DocumentPublic]:
    user = create_random_user(db)
    return [create_random_document(db, user) for _ in range(3)]
