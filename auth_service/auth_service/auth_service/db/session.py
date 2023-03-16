import random
import time

from asyncpg_utils.databases import Database
from loguru import logger
from sqlalchemy import event, Update, Delete
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base

from auth_service.core.config import get_app_settings

engines = {
    "master": create_async_engine(
        get_app_settings().postgres_asyncpg_master_dsn
    ),
    "slave_1": create_async_engine(
        get_app_settings().get_postgres_asyncpg_slave_dsn(1)
    ),
    "slave_2": create_async_engine(
        get_app_settings().get_postgres_asyncpg_slave_dsn(2)
    ),
}


class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None, bind=None, **kw):
        if self._flushing or isinstance(clause, (Update, Delete)):  # noqa
            return engines["master"].sync_engine
        else:
            return engines[random.choice(["slave_1", "slave_2"])].sync_engine


Base = declarative_base()

SessionLocal = async_sessionmaker(
    sync_session_class=RoutingSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

pg_database = Database(get_app_settings().postgres_master_dsn)

if get_app_settings().DEBUG:
    # noinspection PyUnusedLocal
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        conn.info.setdefault("query_start_time", []).append(time.time())
        logger.debug(
            f"Start Query: {statement}",
        )


if get_app_settings().DEBUG:
    # noinspection PyUnusedLocal
    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        total = time.time() - conn.info["query_start_time"].pop(-1)
        logger.debug("Query Complete!")
        logger.debug(f"Total Time: {total:0.4f}")
