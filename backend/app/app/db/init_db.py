import pathlib

from asyncpg import Connection
from loguru import logger
from pydantic import EmailStr
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from app import crud
from app import schemas
from app.core.config import get_app_settings
from app.db.session import Base
from app.db.session import SessionLocal
from app.db.session import engine
from app.db.session import pg_database
from app.models.user_role import UserRole


async def _execute_sql_files(path: pathlib.Path, async_conn: Connection):
    try:
        with open(path, encoding="utf-8") as rf:
            res = await async_conn.execute(rf.read())
            logger.info(f"{path.name}: {res}")
    except Exception as e:
        logger.info(f"{path.name}: {e.args}")


async def create_all_models(_engine: AsyncEngine, metadata: MetaData):
    async with _engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
        logger.info(f"metadata.create_all")


async def create_first_superuser(db: AsyncSession):
    super_user = await crud.user.get_by_email(
        db,
        email=get_app_settings().FIRST_SUPERUSER_EMAIL,
    )
    if not super_user:
        user_in_admin = schemas.UserCreate(
            email=EmailStr(get_app_settings().FIRST_SUPERUSER_EMAIL),
            password=get_app_settings().FIRST_SUPERUSER_PASSWORD,
            password_confirm=get_app_settings().FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            full_name="No Name",
            username=get_app_settings().FIRST_SUPERUSER_USERNAME,
            role=UserRole.admin.name,
        )
        super_user = await crud.user.create(db, obj_in=user_in_admin)
        logger.info("created")
    else:
        logger.info("first superuser already exists")
    return super_user


async def execute_sql_files(conn: Connection, path_to_sql_dir: pathlib.Path = pathlib.Path(__file__).parent.__str__() + "/sql"):
    for sql_f in pathlib.Path(path_to_sql_dir).iterdir():
        if not sql_f.is_dir():
            await _execute_sql_files(sql_f, conn)


async def init_db():
    conn = await pg_database.get_connection()
    await create_all_models(engine, Base.metadata)
    await execute_sql_files(conn)
    async with SessionLocal() as db:
        await create_first_superuser(db)
    await conn.close()
