import random
from asyncio import current_task
from contextlib import asynccontextmanager
from typing import Any

from loguru import logger
from sqlalchemy import Update, Delete, Insert, text, Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    async_scoped_session,
    AsyncSession, )
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import declarative_base

from auth_service.core.config import get_app_settings
from auth_service.core.settings.base import StageType
from auth_service.db.base import MasterReplica, ReplType

Base: DeclarativeBase = declarative_base()

async_engines = MasterReplica(
    master_url=get_app_settings().postgres_asyncpg_master,
    slaves_url=get_app_settings().postgres_asyncpg_replicas,
    pool_size=56,
    max_overflow=0,
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
            return async_engines.engine[ReplType.master][0].sync_engine
        else:
            try:
                slave: Engine = random.choice(async_engines.engine[ReplType.slave]).sync_engine
                with slave.engine.begin() as c:
                    c.execute(text("select 1"))
                return slave
            except (ConnectionError, SQLAlchemyError):
                return async_engines.engine[ReplType.master][0].sync_engine


async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    sync_session_class=RoutingSession,
)

async_scoped_factory = async_scoped_session(
    session_factory=async_session,
    scopefunc=current_task,
)


@asynccontextmanager
async def scoped_session():
    try:
        async with async_scoped_factory() as s:
            try:
                yield s
                await s.commit()
            except Exception as e:
                if get_app_settings().STAGE != StageType.prod:
                    logger.exception(e)
                await s.close()
    finally:
        await async_scoped_factory.remove()
