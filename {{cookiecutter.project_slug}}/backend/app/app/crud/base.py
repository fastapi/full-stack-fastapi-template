from typing import List, Optional, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.db.base_class import Base
from pydantic import BaseModel


class CrudBase:

    def __init__(self, db_model: Base):
        """
        CrudBase instances are used to provide the basic CRUD methods for a given object type (get, get_multi, update, create and delete).
        
        In order to use it, follow this steps when you define a new DB model:
        - create a class that inherites from CrudBase
        - override basic methods with proper types (to get better completion in your IDE)
        - create an instance of your newly created class, providing the DB model as an argument
        
        E.g.:

            # model definition in app/schemas/item.py
            class ItemCreate(...)
                ...

            class ItemUpdate(...)
                ...

            # model definition in app/models/item.py
            class Item(Base):
                id: int
                ...

            # crud definition in app/crud/item.py
            from app.models.item import Item
            from app.schemas.item import ItemUpdate, ItemCreate
            from app.crud.base import CrudBase


            class CrudItem(CrudBase):

                def get(self, db_session: Session, obj_id: int) -> Optional[Item]:
                    return super(CrudItem, self).get(db_session, obj_id=obj_id)

                def get_multi(self, db_session: Session, *, skip=0, limit=100) -> List[Optional[Item]]:
                    return super(CrudItem, self).get_multi(db_session, skip=skip, limit=limit)

                def create(self, db_session: Session, *, obj_in: ItemCreate) -> Item:
                    return super(CrudItem, self).create(db_session, obj_in=obj_in)

                def update(self, db_session: Session, *, obj: Base, obj_in: ItemUpdate) -> Item:
                    return super(CrudItem, self).update(db_session, obj=obj, obj_in=obj_in)


            crud_item = CrudItem(Item)

        Arguments:
            db_model {Base} -- Class of the DB model which CRUD methods will be provided for
        """  # noqa
        self.db_model = db_model

    def get(self, db_session: Session, obj_id: int) -> Optional[Base]:
        """
        get returns the object from the Database that matches the given obj_id
        
        Arguments:
            db_session {Session} -- Dependency injection of the Database session, which will be used to commit/rollback changes.
            obj_id {int} -- ID of the object in the Database. It must be defined by a PrimaryKey on the 'id' column.
        
        Returns:
            Optional[Base] -- Returns an instance of self.db_model class if an object is found in the Database for the given obj_id. Returns None if there is no match found.
        """  # noqa
        return db_session.query(self.db_model).get(obj_id)

    def get_first_by(self, db_session: Session, **kwargs: Any) -> Optional[Base]:
        """
        get_by provides extended filtering capabilities: it returns the first object that matches all given **kwargs
        
        Arguments:
            db_session {Session} -- Dependency injection of the Database session, which will be used to commit/rollback changes.
        
        Keyword Arguments:
            kwargs {dict} -- filters formated as {attribute_name: attribute_value}
        
        Returns:
            Optional[Base] -- Returns an instance of self.db_model class if an object is found in the Database. Returns None if there is no match found.
        """  # noqa
        return db_session.query(self.db_model).filter_by(**kwargs).first()

    def get_multi(self, db_session: Session, *, skip=0, limit=100) -> List[Optional[Base]]:
        """
        get_multi queries all Database rows, without any filters, but with offset and limit options (for pagination purpose)
        
        Arguments:
            db_session {Session} -- Dependency injection of the Database session, which will be used to commit/rollback changes.
        
        Keyword Arguments:
            skip {int} -- Number of rows to skip from the results (default: {0})
            limit {int} -- Maximum number of rows to return (default: {100})
        
        Returns:
            List[Optional[Base]] -- Array of DB instances according given parameters. Might be empty if no objets are found.
        """  # noqa
        return db_session.query(self.db_model).offset(skip).limit(limit).all()

    def get_multi_by(self, db_session: Session, *, skip=0, limit=100, **kwargs: Any) -> List[Optional[Base]]:
        """
        get_multi_by behaves like get_by but returns all filtered objects with the same pagination behavior as in get_multi
        
        Arguments:
            db_session {Session} -- Dependency injection of the Database session, which will be used to commit/rollback changes.
        
        Keyword Arguments:
            skip {int} -- Number of rows to skip from the results (default: {0})
            limit {int} -- Maximum number of rows to return (default: {100})
            kwargs {dict} -- filters formated as {attribute_name: attribute_value}
        
        Returns:
            List[Optional[Base]] -- Array of DB instances according given parameters. Might be empty if no objets are found.
        """  # noqa
        return db_session.query(self.db_model).filter_by(**kwargs).offset(skip).limit(limit).all()

    def create(self, db_session: Session, *, obj_in: BaseModel) -> Base:
        """
        create adds a new row in the Database in the table defined by self.db_model. The column values are populated from the 'obj_in' pydantic object
        
        Arguments:
            db_session {Session} -- Dependency injection of the Database session, which will be used to commit/rollback changes.
            obj_in {BaseModel} -- A pydantic object that contains all mandatory values needed to create the Database row.
        
        Returns:
            Base -- The object inserted in the Database
        """  # noqa
        obj_in_data = jsonable_encoder(obj_in)
        obj = self.db_model(**obj_in_data)
        db_session.add(obj)
        db_session.commit()
        db_session.refresh(obj)
        return obj

    def update(self, db_session: Session, *, obj: Base, obj_in: BaseModel) -> Base:
        """
        update modifies an existing row (fetched from given obj) in the Database with values from given obj_in
        
        Arguments:
            db_session {Session} -- Dependency injection of the Database session, which will be used to commit/rollback changes.
            obj {Base} -- A DB instance of the object to update
            obj_in {BaseModel} -- A pydantic object that contains all values to update.
        
        Returns:
            Base -- The updated DB object, with all its attributes
        """  # noqa
        obj_data = jsonable_encoder(obj)
        update_data = obj_in.dict(skip_defaults=True)
        for field in obj_data:
            if field in update_data:
                setattr(obj, field, update_data[field])
        db_session.add(obj)
        db_session.commit()
        db_session.refresh(obj)
        return obj

    def delete(self, db_session: Session, obj_id: int) -> int:
        """
        delete removes the row from the database with the obj_id ID
        
        Arguments:
            db_session {Session} -- Dependency injection of the Database session, which will be used to commit/rollback changes.
            obj_id {int} -- ID of the row to remove from the Database. It must be defined by a PrimaryKey on the 'id' column.
        
        Returns:
            int -- number of rows deleted, i.e. 1 if the object has been found and deleted, 0 otherwise
        """  # noqa
        queried = db_session.query(self.db_model).filter(self.db_model.id == obj_id)
        counted = queried.count()
        if counted > 0:
            queried.delete()
            db_session.commit()
        return counted

    def remove(self, db_session: Session, *, obj_id: int) -> Optional[Base]:
        """
        remove does the same job as delete, with a different return value
        
        Returns:
            deleted object, if the deletion was successfull
            None if the object was already deleted from the Database
        """  # noqa
        obj = db_session.query(self.db_model).get(obj_id)
        db_session.delete(obj)
        db_session.commit()
        return obj
