import random
from typing import Any

from sqlalchemy import Update, Delete, Insert, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import declarative_base

from auth_service.core.config import get_app_settings
from auth_service.db.base import MasterSlaves, ReplicaType

Base: DeclarativeBase = declarative_base()

engines = MasterSlaves(
    master_url=get_app_settings().postgres_asyncpg_master,
    slaves_url=get_app_settings().postgres_asyncpg_slaves,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)


def ping_connection(engine):
    c = engine.connect()
    try:
        c.execute(text("select 1"))
        c.close()
    except DBAPIError as e:
        if e.connection_invalidated:
            pass


class RoutingSession(Session):
    def get_bind(
        self,
        mapper=None,
        *,
        clause=None,
        bind=None,
        _sa_skip_events=None,
        _sa_skip_for_implicit_returning=False,
        **kw: Any,
    ):
        if self._flushing or isinstance(clause, (Insert, Update, Delete)):
            return random.choice(
                engines.engine[ReplicaType.master]
            ).sync_engine
        else:
            try:
                slave: AsyncEngine = random.choice(
                    engines.engine[ReplicaType.slave]
                ).sync_engine
                with slave.sync_engine.engine.begin() as c:
                    c.execute(text("select 1"))
            except Exception:
                return random.choice(
                    engines.engine[ReplicaType.master]
                ).sync_engine


SessionLocal = async_sessionmaker(
    sync_session_class=RoutingSession, autoflush=False, expire_on_commit=False
)
