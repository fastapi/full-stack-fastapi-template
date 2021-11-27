from sqlalchemy import create_engine
from sqlalchemy import event
import time
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

engine_async = create_async_engine(settings.SQLALCHEMY_DATABASE_URI_ASYNC, pool_pre_ping=True)
async_session = sessionmaker(
    bind=engine_async,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

if settings.PROFILE_QUERY_MODE:
    logging.basicConfig()
    logger = logging.getLogger("myapp.sqltime")
    logger.setLevel(logging.DEBUG)


    def before_cursor_execute(conn, cursor, statement,
                            parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
        logger.debug("Start Query: %s" % statement)

    def after_cursor_execute(conn, cursor, statement,
                            parameters, context, executemany):
        total = time.time() - conn.info['query_start_time'].pop(-1)
        logger.debug("Query Complete!")
        logger.debug("Total Time: %f" % total)

    event.listen(engine_async.sync_engine, "before_cursor_execute", before_cursor_execute)
    event.listen(engine_async.sync_engine, "after_cursor_execute", after_cursor_execute)