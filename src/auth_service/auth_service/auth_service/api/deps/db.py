from loguru import logger
from sqlalchemy import text
from starlette.requests import Request

from auth_service.db.session import async_scoped_factory


async def get_db(request: Request):
    try:
        async with async_scoped_factory() as s:
            try:
                await s.execute(text("BEGIN"))
                yield s
                await s.execute(text("COMMIT"))
            except Exception as e:
                if request.app.debug:
                    logger.warning(f'{e.__class__} - ROLLBACK')
                await s.execute(text("ROLLBACK"))
            await s.close()
    finally:
        await async_scoped_factory.remove()
