import pathlib

from asyncpg import Connection, UndefinedFunctionError
from loguru import logger
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from auth_service import crud, schemas
from auth_service.core.config import get_app_settings
from auth_service.core.settings.base import AppEnvTypes
from auth_service.db.session import Base
from auth_service.db.session import SessionLocal
from auth_service.db.session import engine
from auth_service.db.session import pg_database
from auth_service.models.enums import UserRole


async def truncate_tables(conn: Connection):
    q = f"""select truncate_tables_where_owner('postgres')"""
    logger.info("truncate_tables_where_owner('postgres')")
    try:
        await conn.execute(q)
    except UndefinedFunctionError:
        pass


async def execute_sql_file(path: pathlib.Path, async_conn: Connection):
    try:
        with open(path, encoding="utf-8") as rf:
            res = await async_conn.execute(rf.read())
            logger.info(f"{path.name}: {res}")
    except Exception as e:
        logger.info(f"{path.name}: {e.args}")


async def create_all_models(_engine: AsyncEngine):
    async with _engine.begin() as conn:
        if get_app_settings().DEBUG:
            await conn.run_sync(Base.metadata.drop_all, checkfirst=True)
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
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
            role=UserRole.admin,
        )
        super_user = await crud.user.create(db, obj_in=user_in_admin)
        logger.info("created")
    else:
        logger.info("first superuser already exists")
    return super_user


async def execute_sql_files(
    conn: Connection,
    path_to_sql_dir: pathlib.Path = pathlib.Path(__file__).parent.__str__() + "/sql",
):
    for sql_f in pathlib.Path(path_to_sql_dir).iterdir():
        if not sql_f.is_dir() and not sql_f.name.startswith("_"):
            await execute_sql_file(sql_f, conn)


async def init_db():
    conn = await pg_database.get_connection()
    if get_app_settings().APP_ENV == AppEnvTypes.test:
        await truncate_tables(conn)
    await create_all_models(engine)
    await execute_sql_files(conn)
    async with SessionLocal() as db:
        await create_first_superuser(db)
    await conn.close()
