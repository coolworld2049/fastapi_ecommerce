from collections.abc import AsyncGenerator

from asyncpg import Connection
from loguru import logger
from sqlalchemy import Result, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_app_settings
from app.db.session import SessionLocal
from app.models import User


async def get_db() -> AsyncGenerator:
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.close()


async def authorization_in_db(db: AsyncSession, current_user: User):
    await reset_session_user(db)
    if not await is_rolname_exist(db, current_user):
        await create_user_in_role(db, current_user)
    await reset_session_user(db)
    await set_session_user(db, current_user)


async def is_rolname_exist(db: AsyncSession, current_user: User):
    q = """select is_role_exists(:db_user)"""
    _result: Result = await db.execute(
        text(q),
        {"db_user": current_user.username},
    )

    result = _result.fetchone()._data[0] # noqa
    if get_app_settings().APP_ENV in ['dev', 'test']:
        logger.info(
            f"{f'{current_user.username} rolname exist' if result else f'{current_user.username} rolname not exist'}",
        )
    return result


async def create_user_in_role(db: AsyncSession, current_user: User):
    q = (
        """select create_user_in_role(:db_user, :hashed_password, :role, :db_name)"""
    )
    params = {
        "db_user": current_user.username,
        "hashed_password": current_user.hashed_password,
        "role": current_user.role,
        "db_name": db.bind.url.database
    }
    await db.execute(text(q), params=params)
    await db.commit()
    if get_app_settings().APP_ENV in ['dev', 'test']:
        logger.info("created")


async def drop_user_in_role(db: AsyncSession | Connection, current_user: User):
    q = """drop current_user """ + current_user.username
    if isinstance(db, Connection):
        await db.execute(q)
    elif isinstance(db, AsyncSession):
        await db.execute(text(q))
    if get_app_settings().APP_ENV in ['dev', 'test']:
        logger.info(current_user.username)


async def get_session_user(db: AsyncSession):
    q = """select session_user, current_user"""
    check_session_role_q_result: Result = await db.execute(text(q))
    if get_app_settings().APP_ENV in ['dev', 'test']:
        logger.info(check_session_role_q_result.scalar())


async def set_session_user(db: AsyncSession, current_user: User):
    q = """set session authorization """ + current_user.username
    if get_app_settings().APP_ENV in ['dev', 'test']:
        logger.info(current_user.username)
    await db.execute(text(q))


async def reset_session_user(db: AsyncSession):
    q = """reset session authorization"""
    if get_app_settings().APP_ENV in ['dev', 'test']:
        logger.info("reset")
    await db.execute(text(q))
