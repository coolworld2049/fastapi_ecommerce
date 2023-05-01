import asyncio
import logging

from auth_service.db.init_db import init_db
from auth_service.db.session import async_session


async def main() -> None:
    logging.info("Creating initial data")
    async with async_session() as db:
        await init_db(db)
    logging.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
