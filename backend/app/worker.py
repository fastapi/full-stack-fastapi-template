"""ARQ worker: background job definitions and settings."""

from __future__ import annotations

import logging
import uuid

from arq.connections import RedisSettings

from app.core.config import settings

logger = logging.getLogger(__name__)


async def generate_race_embedding(ctx: dict, race_id_str: str) -> None:
    """ARQ job: compute and persist the embedding for a single race."""
    from sqlmodel import Session
    from app.core.db import engine
    from app import crud
    from app.services.ai import embed_race

    race_id = uuid.UUID(race_id_str)
    try:
        with Session(engine) as session:
            race = crud.get_race(session=session, race_id=race_id)
            if race is None:
                logger.warning("generate_race_embedding: race %s not found", race_id)
                return
            vector = await embed_race(race)
            crud.update_race_embedding(session=session, race_id=race_id, embedding=vector)
            logger.info("Embedded race %s (%d dims)", race_id, len(vector))
    except Exception:
        logger.exception("generate_race_embedding failed for race %s", race_id)
        raise


async def reindex_all_races(ctx: dict, batch_size: int = 50) -> None:
    """ARQ job: queue embedding generation for all un-embedded races."""
    from sqlmodel import Session
    from app.core.db import engine
    from app import crud

    with Session(engine) as session:
        races = crud.get_races_without_embedding(session=session, limit=batch_size)

    for race in races:
        await ctx["redis"].enqueue_job("generate_race_embedding", str(race.id))

    logger.info("Queued %d races for embedding", len(races))


class WorkerSettings:
    """ARQ worker configuration."""

    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    functions = [generate_race_embedding, reindex_all_races]
    max_jobs = 10
    job_timeout = 300  # 5 minutes per embedding job
