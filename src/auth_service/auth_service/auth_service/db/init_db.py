import pathlib

from asyncpg import Connection
from loguru import logger
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from auth_service import crud, schemas
from auth_service.core.config import get_app_settings
from auth_service.db.base import ReplType
from auth_service.db.session import Base
from auth_service.db.session import async_engines
from auth_service.models import UserRole
from auth_service.models.user_role import UserRoleEnum


async def execute_sql_file(
    path: pathlib.Path,
    conn: Connection,
):
    timeout = 5
    try:
        with open(path, encoding="utf-8") as rf:
            sql_file = rf.read()
            await conn.execute(sql_file, timeout=timeout)
            logger.info(f"path: {path.name}, result: executed")
    except TimeoutError:
        logger.error(f"path: {path.name}, result: TimeoutError")


async def base_metadata(
    eng: AsyncEngine, create: bool = False, drop: bool = False
):
    msg = f"repl_type: {ReplType.master.name}, url: {eng.url}"
    action = ""
    try:
        async with eng.begin() as conn:
            if drop:
                action = "dropped"
                await conn.run_sync(Base.metadata.drop_all)
            elif create:
                action = "created"
                await conn.run_sync(Base.metadata.create_all)
            else:
                raise ValueError(
                    "'drop' or 'create' must be True", drop, create
                )
            logger.info(action)
    except ConnectionRefusedError as ex:
        logger.error(f"{action}- {msg}, {ex.__class__.__name__} {ex}")


async def create_roles(db: AsyncSession):
    for r in UserRoleEnum:
        q = select(UserRole).where(UserRole.name == r.name)
        res = await db.execute(q)
        res = res.fetchone()
        if not res:
            db_obj = UserRole(name=r.name)  # noqa
            db.add(db_obj)
    await db.commit()


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
            is_verified=True,
            full_name="Super user",
            username="super_user_1000",
            role=UserRoleEnum.admin,
        )
        super_user = await crud.user.create(db, obj_in=user_in_admin)
        logger.info("created")
    else:
        logger.info("already exists")
    return super_user


async def init_db(db: AsyncSession):
    try:
        await async_engines.check_engines()
        await base_metadata(async_engines.get_master(), create=True)
        await create_roles(db)
        await create_first_superuser(db)
    except Exception as e:
        logger.exception(e)
