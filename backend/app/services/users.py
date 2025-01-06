from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate
from app.repositories.users import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def create(self, *, user_create: UserCreate) -> User:
        db_obj = User.model_validate(
            user_create,
            update={"hashed_password": get_password_hash(user_create.password)},
        )
        return self.repository.create(db_obj)

    def update(self, *, db_user: User, user_update: UserUpdate) -> User:
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            password = update_data["password"]
            hashed_password = get_password_hash(password)
            update_data["hashed_password"] = hashed_password

        db_user = self.repository.update(db_user, update=update_data)
        return db_user

    def authenticate(self, *, email: str, password: str) -> User | None:
        db_user = self.repository.get_by_email(email=email)
        if not db_user:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        return db_user
