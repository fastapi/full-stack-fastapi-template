from typing import Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from neomodel import db, Q, One, CardinalityViolation
from uuid import UUID
import inspect
from neomodel.relationship_manager import RelationshipDefinition, ZeroOrMore

from app.gdb import NeomodelConfig, NodeBase

ModelType = TypeVar("ModelType", bound=NodeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

NeomodelConfig().ready()


class NeoCRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        Neomodel CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A Neo4j Neomodel model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def _hexify(self, id: Union[UUID, str]) -> str:
        if isinstance(id, str):
            id = UUID(id)
        return id.hex

    def get_relationships(self, db_objs: Union[ModelType, List[ModelType]]) -> Union[ModelType, List[ModelType]]:
        if not db_objs:
            return db_objs
        is_list = isinstance(db_objs, list)
        if not is_list:
            db_objs = [db_objs]
        for db_obj in db_objs:
            # Get members of the object by getting its class type
            for key, relation in inspect.getmembers(db_obj.__class__):
                # an object can be accessed as a dict to subscript its attributes
                relation = db_obj.__dict__.get(key)
                if isinstance(relation, ZeroOrMore):
                    if db_obj.__dict__[key].all():
                        db_obj.__dict__[key] = db_obj.__dict__[key].all()
                    else:
                        db_obj.__dict__[key] = []
                elif isinstance(relation, One):
                    try:
                        db_obj.__dict__[key] = UUID(db_obj.__dict__[key].single().identifier)
                    except CardinalityViolation:
                        db_obj.__dict__[key] = None
            if not is_list:
                return db_obj
        return db_objs

    def _response(
        self, *, db_objs: Union[ModelType, List[ModelType]], get_raw: bool = False, get_first: bool = True
    ) -> Union[ModelType, List[ModelType]]:
        # create_or_update is used to create multiples, so returns a list (of 1)
        if get_first and isinstance(db_objs, list):
            db_objs = db_objs[0]
        if get_raw:
            return db_objs
        return self.get_relationships(db_objs)

    @db.read_transaction
    def get(self, *, id: UUID, get_raw: bool = False) -> Optional[ModelType]:
        id = self._hexify(id)
        db_obj = self.model.nodes.get_or_none(identifier=id)
        return self._response(db_objs=db_obj, get_raw=get_raw)

    @db.read_transaction
    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        db_objs = self.model.nodes.all()[skip : limit + skip]
        return self.get_relationships(db_objs)

    @db.read_transaction
    def get_multi_by_identifiers(self, *, skip: int = 0, limit: int = 100, ids_in=List[UUID]) -> List[ModelType]:
        ids_in = [self._hexify(id) for id in ids_in]
        db_objs = self.model.nodes.filter(Q(identifier__in=ids_in))[skip : limit + skip]
        return self.get_relationships(db_objs)

    @db.write_transaction
    def create(self, *, obj_in: CreateSchemaType, get_raw: bool = False, get_first: bool = True) -> ModelType:
        obj_in_data = obj_in.as_neo_dict
        db_obj = self.model.create_or_update(obj_in_data)  # type: ignore
        return self._response(db_objs=db_obj, get_raw=get_raw, get_first=get_first)

    @db.write_transaction
    def update(self, *, obj_in: UpdateSchemaType, get_raw: bool = False, get_first: bool = True) -> ModelType:
        obj_in_data = obj_in.as_neo_dict
        db_obj = self.model.create_or_update(obj_in_data)  # type: ignore
        return self._response(db_objs=db_obj, get_raw=get_raw, get_first=get_first)

    @db.write_transaction
    def remove(self, *, id: UUID) -> bool:
        id = self._hexify(id)
        obj = self.model.nodes.get(identifier=id)
        obj = obj.delete()
        return obj
