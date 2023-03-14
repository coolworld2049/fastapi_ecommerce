from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.db.session import SessionLocal


async def get_db():
    s: AsyncSession = SessionLocal()
    try:
        yield s
    except:
        await s.rollback()
    finally:
        await s.close()
