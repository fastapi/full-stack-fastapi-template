import uuid

from sqlmodel import Session, col, func, select

from app.models import Generation


def get_generation_by_id(*, session: Session, generation_id: uuid.UUID) -> Generation | None:
    return session.get(Generation, generation_id)


def list_generations(
    *,
    session: Session,
    user_id: uuid.UUID,
    is_superuser: bool,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Generation], int]:
    statement = select(Generation)
    count_statement = select(func.count()).select_from(Generation)

    if not is_superuser:
        statement = statement.where(Generation.user_id == user_id)
        count_statement = count_statement.where(Generation.user_id == user_id)

    statement = statement.order_by(col(Generation.created_at).desc()).offset(skip).limit(limit)

    count = session.exec(count_statement).one()
    generations = list(session.exec(statement).all())
    return generations, count


def create_generation(*, session: Session, generation: Generation) -> Generation:
    session.add(generation)
    session.commit()
    session.refresh(generation)
    return generation


def save_generation(*, session: Session, generation: Generation) -> Generation:
    session.add(generation)
    session.commit()
    session.refresh(generation)
    return generation
