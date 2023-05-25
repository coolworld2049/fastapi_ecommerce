import random
import time
from typing import Any

from loguru import logger
from sqlalchemy import Update, Delete, Insert, event
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import declarative_base

from auth_service.core.config import get_app_settings
from auth_service.db.base import MasterReplicas, ReplType

Base: DeclarativeBase = declarative_base()

async_engines = MasterReplicas(
    master_url=get_app_settings().postgres_asyncpg_master,
    slaves_url=get_app_settings().postgres_asyncpg_replicas,
    pool_size=get_app_settings().SQLALCHEMY_POOL_SIZE,
    isolation_level="READ COMMITTED",
)

class RoutingSession(Session):
    def get_bind(
        self,
        mapper=None,
        clause=None,
        **kwargs: Any,
    ):
        if self._flushing or isinstance(clause, (Insert, Update, Delete)):
            return async_engines.engines[ReplType.master][0].sync_engine
        else:
            return random.choice(async_engines.get_replicas()).sync_engine


async_session = async_sessionmaker(
    sync_session_class=RoutingSession
)

if get_app_settings().SQLALCHEMY_PROFILE_QUERY_MODE:
    def before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        conn.info.setdefault("query_start_time", []).append(time.time())
        logger.debug(f"Start Query: {statement}")


    def after_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        total = time.time() - conn.info["query_start_time"].pop(-1)
        logger.debug("Query Complete!")
        logger.debug("Total Time: %f" % total)


    event.listen(
        async_engines.get_master().sync_engine,
        "before_cursor_execute",
        before_cursor_execute,
    )
    event.listen(
        async_engines.get_master().sync_engine,
        "after_cursor_execute",
        after_cursor_execute,
    )


async def get_session():
    s = async_session()
    try:
        await s.begin()
        yield s
        await s.commit()
    except Exception as e:  # noqa
        await s.rollback()
        logger.warning(f"{e.__class__} {e} - ROLLBACK")
    finally:
        await s.close()
