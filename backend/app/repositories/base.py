import uuid
from typing import Any, Generic, TypeVar

from sqlmodel import Session, func, select

from app.models import Entity

T = TypeVar("T", bound=Entity)


class CRUDRepository(Generic[T]):
    def __init__(self, table: type[T], session: Session) -> None:
        """
        CRUD repository for SQLModels.

        * `table`: A SQLModel table model class
        * `session`: A SQLModel session

        example usage:
        ```
        class UserRepository(CRUDRepository):
            def __init__(self, session: Session) -> None:
                super().__init__(User, session)
        ```
        """
        self.table = table
        self.session = session

    def get_by_id(self, id: uuid.UUID) -> T | None:
        statement = select(self.table).where(self.table.id == id)
        db_obj = self.session.exec(statement).first()
        return db_obj

    def count(self) -> int:
        statement = select(func.count()).select_from(self.table)
        count = self.session.exec(statement).one()
        return count

    def count_by_kwargs(self, **kwargs: Any) -> int:
        statement = select(func.count()).select_from(self.table).filter_by(**kwargs)
        count = self.session.exec(statement).one()
        return count

    def get_all(self, *, skip: int = 0, limit: int = 100) -> list[T]:
        statement = select(self.table).offset(skip).limit(limit)
        db_objs = self.session.exec(statement).all()
        return list(db_objs)

    def get_all_by_kwargs(
        self, *, skip: int = 0, limit: int = 100, **kwargs: Any
    ) -> list[T]:
        statement = select(self.table).filter_by(**kwargs).offset(skip).limit(limit)
        db_objs = self.session.exec(statement).all()
        return list(db_objs)

    def create(self, db_obj: T) -> T:
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def create_bulk(self, db_objs: list[T]) -> list[T]:
        self.session.bulk_save_objects(db_objs)
        self.session.commit()
        for db_obj in db_objs:
            self.session.refresh(db_obj)
        return db_objs

    def update(self, db_obj: T, *, update: dict[str, Any]) -> T:
        db_obj.sqlmodel_update(update)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, id: uuid.UUID) -> None:
        db_obj = self.get_by_id(id)
        if db_obj is not None:
            self.session.delete(db_obj)
            self.session.commit()
