from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.config import get_app_settings
from auth_service.db.session import SessionLocal


async def get_pg_stat_activity(db: AsyncSession):
    if get_app_settings().APP_ENV in ["dev", "test"]:
        result = await db.execute(text("""select count(*) from pg_stat_activity;"""))
        logger.info(f"db_connection_count={result.fetchone()}")


async def get_db():
    s: AsyncSession = SessionLocal()
    try:
        yield s
    except:
        await s.rollback()
    finally:
        # await get_pg_stat_activity(s)
        await s.close()
