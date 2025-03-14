from typing import Any, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlmodel import Session, SQLModel, select

# Define a type variable for the SQLModel
ModelType = TypeVar("ModelType", bound=SQLModel)
# Define a type variable for the Create schema
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
# Define a type variable for the Update schema
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository class that provides standard CRUD operations.
    
    This class implements the repository pattern for database operations,
    providing a clean separation between the database and business logic.
    """
    
    def __init__(self, model: Type[ModelType]):
        """Initialize with the model class."""
        self.model = model
    
    def get(self, session: Session, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        return session.get(self.model, id)
    
    def get_multi(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        statement = select(self.model).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    def create(self, session: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)  # type: ignore
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def update(
        self, session: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update an existing record."""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(db_obj, key, value)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def remove(self, session: Session, *, id: Any) -> Optional[ModelType]:
        """Remove a record by ID."""
        obj = session.get(self.model, id)
        if obj:
            session.delete(obj)
            session.commit()
        return obj 