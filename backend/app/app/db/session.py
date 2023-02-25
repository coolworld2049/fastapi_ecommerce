from asyncpg_utils.databases import Database
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import get_app_settings

engine: AsyncEngine = create_async_engine(
    get_app_settings().postgres_asyncpg_dsn,
    poolclass=NullPool
)


Base = declarative_base()
Base.metadata.bind = engine

SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

pg_database = Database(get_app_settings().raw_postgres_dsn)
