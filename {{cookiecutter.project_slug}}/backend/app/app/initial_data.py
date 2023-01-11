import logging
from pathlib import Path
import json
from passlib.totp import generate_secret

from app.gdb.init_gdb import init_gdb
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.gdb import NeomodelConfig
from app.core.config import settings

from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

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
def initNeo4j() -> None:
    try:
        NeomodelConfig().ready()
        init_gdb()
    except Exception as e:
        logger.error(e)
        raise e


def init() -> None:
    db = SessionLocal()
    init_db(db)


def main() -> None:
    logger.info("Creating initial data")
    initNeo4j()
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
