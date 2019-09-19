from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.declarative import declarative_base, declared_attr


class CustomBase(object):
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def to_schema(self, schema_cls):
        return schema_cls(**self.__dict__)

    @classmethod
    def from_schema(cls, schema_obj):
        return cls(**jsonable_encoder(schema_obj))


Base = declarative_base(cls=CustomBase)
