from typing import Any
from sqlmodel import Session

from app.model.users import User, UserCreate, UserUpdate
from app.core.security import verify_password


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user_create: UserCreate) -> User:
        return User.create(self.session, user_create)

    def update_user(self, db_user: User, user_in: UserUpdate) -> Any:
        return User.update(self.session, db_user, user_in)

    def get_user_by_email(self, email: str) -> User | None:
        return User.get_by_email(self.session, email)

    def authenticate(self, email: str, password: str) -> User | None:
        db_user = self.get_user_by_email(email)
        if not db_user:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        return db_user
