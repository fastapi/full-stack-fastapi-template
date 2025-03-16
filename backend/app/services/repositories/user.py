from typing import Optional

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.repository import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository for User model operations."""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_email(self, session: Session, *, email: str) -> Optional[User]:
        """Get a user by email."""
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()
    
    def create(self, session: Session, *, obj_in: UserCreate) -> User:
        """Create a new user with hashed password."""
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
            is_active=obj_in.is_active,
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def update(self, session: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        """Update a user, handling password hashing if needed."""
        update_data = obj_in.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(session, db_obj=db_obj, obj_in=UserUpdate(**update_data))
    
    def authenticate(self, session: Session, *, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = self.get_by_email(session=session, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user 