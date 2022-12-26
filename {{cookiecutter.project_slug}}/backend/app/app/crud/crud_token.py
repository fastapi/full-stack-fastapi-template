from __future__ import annotations
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models import User, Token
from app.schemas import RefreshTokenCreate, RefreshTokenUpdate


class CRUDToken(CRUDBase[Token, RefreshTokenCreate, RefreshTokenUpdate]):
    # Everything is user-dependent
    def create(self, db: Session, *, obj_in: str, user_obj: User) -> User:
        db_obj = db.query(self.model).filter(self.model.token == obj_in).first()
        if db_obj and db_obj.authenticates == user_obj:
            # In case the token was invalidated, then recreated with the same token key
            setattr(db_obj, "is_valid", True)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        if db_obj and db_obj.authenticates != user_obj:
            raise ValueError(f"Token mismatch between key and user.") 
        db_obj = Token(token=obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        user_obj.refresh_tokens.append(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def cancel_refresh_token(self, db: Session, *, db_obj: Token) -> Token:
        setattr(db_obj, "is_valid", False)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, *, user: User, token: str) -> Token:
        return user.refresh_tokens.filter(and_(self.model.token == token, self.model.is_valid == True)).first()

    def get_multi(self, *, user: User, skip: int = 0, limit: int = 100) -> List[Token]:
        return user.refresh_tokens.filter(self.model.is_valid == True).offset(skip).limit(limit).all()


token = CRUDToken(Token)
