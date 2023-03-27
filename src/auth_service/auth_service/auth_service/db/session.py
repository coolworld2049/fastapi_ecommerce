import random
from typing import Any

from sqlalchemy import Update, Delete, Insert, NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import declarative_base

from auth_service.core.config import get_app_settings
from auth_service.db.base import MasterSlaves, ReplicaType

Base: DeclarativeBase = declarative_base()

engines = MasterSlaves(
    master_url=get_app_settings().postgres_asyncpg_master,
    slaves_url=get_app_settings().postgres_asyncpg_slaves,
    poolclass=NullPool,
    isolation_level="AUTOCOMMIT",
)


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
                return random.choice(
                    engines.engine[ReplicaType.slave]
                ).sync_engine
            except IndexError:
                return random.choice(
                    engines.engine[ReplicaType.master]
                ).sync_engine


SessionLocal = async_sessionmaker(
    sync_session_class=RoutingSession, autoflush=False, expire_on_commit=False
)


async def get_db():
    s: AsyncSession = SessionLocal()
    try:
        yield s
    except Exception: # noqa
        await s.rollback()
    finally:
        await s.commit()
        await s.close()
