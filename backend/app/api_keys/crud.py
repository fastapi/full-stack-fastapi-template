from __future__ import annotations
from app.backend_pre_start import logger

import uuid
from typing import List

from sqlmodel import Session, select

from app.api_keys.models import ApiKey
from app.api_keys.schemas import ApiKeyCreate


def create_api_key(session: Session, user_id: uuid.UUID, api_key_in: ApiKeyCreate) -> ApiKey:
    api_key = ApiKey(user_id=user_id, name=api_key_in.name, key=api_key_in.key)
    session.add(api_key)
    session.commit()
    session.refresh(api_key)
    return api_key


def get_api_keys_for_user(session: Session, user_id: uuid.UUID) -> List[ApiKey]:
    statement = select(ApiKey).where(ApiKey.user_id == user_id)
    return list(session.exec(statement).all())


def get_api_key(session: Session, api_key_id: uuid.UUID) -> ApiKey | None:
    return session.get(ApiKey, api_key_id)


def delete_api_key(session: Session, api_key_id: uuid.UUID) -> None:
    api_key = session.get(ApiKey, api_key_id)
    if api_key:
        session.delete(api_key)
        session.commit()

def get_api_key_by_user(session: Session, user_id: uuid.UUID) -> ApiKey:
    statement = select(ApiKey).where(ApiKey.user_id == user_id)
    api_key = ApiKey(
        key='AIzaSyBzqezPY0EVJZfMGPfkG5TpHRtUZeeu_rE'
    )

    if not api_key:
        logger.error(f"No API key found for user_id: {user_id}")
        raise ValueError("No API key found! You need to create one Google Gemini API key to use this function.")

    return api_key