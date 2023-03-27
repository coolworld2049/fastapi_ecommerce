import pathlib

from asyncpg import Connection
from loguru import logger
from pydantic import EmailStr
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service import crud, schemas
from auth_service.core.config import get_app_settings
from auth_service.db.session import Base, MasterSlaves, SessionLocal
from auth_service.db.session import engines
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
    ms: MasterSlaves, create: bool = False, drop: bool = False
):
    for _type, _eng in ms.engine.items():
        for eng in _eng:
            msg = f"engine_type: {_type.name}, url: {eng.url}"
            try:
                async with eng.begin() as conn:
                    if drop:
                        action = "metadata.drop_all"
                        await conn.run_sync(Base.metadata.drop_all)
                    elif create:
                        action = "metadata.create_all"
                        await conn.run_sync(Base.metadata.create_all)
                    else:
                        raise ValueError(
                            "'drop' or 'create' must be True", drop, create
                        )
                logger.opt(colors=True).info(
                    f"<fg 255,70,230>{action}</fg 255,70,230> - {msg}"
                )
            except ConnectionRefusedError as ex:
                logger.opt(colors=True).error(
                    f"<fg 255,70,230>{action}</fg 255,70,230> - {msg}, {ex.__class__.__name__} {ex}"
                )


async def create_roles(db: AsyncSession):
    for r in UserRoleEnum:
        if not await db.get(UserRole, r.name):
            await db.execute(insert(UserRole).values(name=r.name))
    await db.commit()


async def create_first_superuser(db: AsyncSession):
    await create_roles(db)
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
            full_name=get_app_settings().FIRST_SUPERUSER_FULLNAME,
            username=get_app_settings().FIRST_SUPERUSER_USERNAME,
            role=UserRoleEnum.admin,
        )
        super_user = await crud.user.create(db, obj_in=user_in_admin)
        logger.info("created")
    logger.info("already exists")
    return super_user


async def init_db():
    try:
        await engines.check_engines()
        await base_metadata(engines, create=True)
        async with SessionLocal() as db:
            await create_first_superuser(db)
    except Exception as e:
        logger.error(f"{e.__class__.__name__} {e}")
