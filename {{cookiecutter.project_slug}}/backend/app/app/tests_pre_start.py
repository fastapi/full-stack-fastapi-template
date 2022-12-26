import logging
import asyncio
from sqlalchemy import text
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

#from app.db.session import SessionLocal
from app.db.session import async_session, engine_async
from app.db import base  # noqa: F401
from app.db.init_db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init() -> None:
    try:
        # Try to create session to check if DB is awake
        # db = SessionLocal()
        async with engine_async.begin() as conn:
            logger.info("DROP DATABASE")
            await conn.run_sync(base.Base.metadata.drop_all)
            logger.info("CREATE DATABASE")
            await conn.run_sync(base.Base.metadata.create_all)
        db = async_session()
        await init_db(db=db)
        await db.execute("SELECT 1")
        logger.info("DATABASE DONE")
    except Exception as e:
        logger.error(e)
        raise e


async def main() -> None:
    logger.info("Initializing service")
    await init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    asyncio.run(main())
