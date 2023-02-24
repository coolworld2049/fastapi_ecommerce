from sqlalchemy.ext.declarative import declarative_base

from app.core.config import get_app_settings
from asyncpg_utils.databases import Database
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

engine: AsyncEngine = create_async_engine(
    get_app_settings().postgres_asyncpg_dsn,
    future=True,
    echo=False,
    json_serializer=jsonable_encoder,
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
