from sqlmodel import Session, select

from app.models import User
from app.repositories.base import CRUDRepository


class UserRepository(CRUDRepository[User]):
    def __init__(self, session: Session) -> None:
        super().__init__(User, session)

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        db_obj = self.session.exec(statement).first()
        return db_obj
