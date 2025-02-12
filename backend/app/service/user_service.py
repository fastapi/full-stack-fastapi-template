from typing import Any

from sqlmodel import Session

from app.core.security import verify_password
from app.model.user_model import UserModel
from app.models import User, UserCreate, UserUpdate, UserUpdateMe


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def create_user(cls, user_create: UserCreate) -> User:
        return UserModel(cls.session).create(user_create)

    def update_user(cls, db_user: User, user_in: UserUpdate) -> Any:
        return UserModel(cls.session).update(db_user, user_in)

    def get_user_by_email(cls, email: str) -> User | None:
        return UserModel(cls.session).get_by_email(email)

    def get_user_by_id(cls, user_id: str) -> User | None:
        return UserModel(cls.session).get_by_id(user_id)

    def get_users(cls, skip: int = 0, limit: int = 100) -> dict[str, Any]:
        return UserModel(cls.session).get_users(skip, limit)

    def update_user_me(cls, current_user: User, user_in: UserUpdateMe) -> User:
        if user_in.email:
            existing_user = cls.get_user_by_email(email=user_in.email)
            if existing_user and existing_user.id != current_user.id:
                raise ValueError("User with this email already exists")

        # Convert UserUpdateMe to UserUpdate since model expects UserUpdate
        update_data = UserUpdate(email=user_in.email, full_name=user_in.full_name)
        return UserModel(cls.session).update(current_user, update_data)

    def update_password(
        cls, current_user: User, current_password: str, new_password: str
    ) -> None:
        if not verify_password(current_password, current_user.hashed_password):
            raise ValueError("Incorrect password")
        if current_password == new_password:
            raise ValueError("New password cannot be the same as the current one")

        # Create UserUpdate with new password
        update_data = UserUpdate(password=new_password)
        UserModel(cls.session).update(current_user, update_data)

    def delete_user(
        cls, user_id: str, current_user_id: str, is_superuser: bool
    ) -> None:
        user = cls.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if user.id == current_user_id and is_superuser:
            raise ValueError("Super users are not allowed to delete themselves")

        UserModel(cls.session).delete_user(user_id)

    def authenticate(cls, email: str, password: str) -> User | None:
        db_user = cls.get_user_by_email(email)
        if not db_user:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        return db_user
