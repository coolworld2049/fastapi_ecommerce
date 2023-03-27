import asyncio

from loguru import logger

from auth_service.db.init_db import init_db


def main() -> None:
    logger.info("Creating initial data")
    asyncio.run(init_db())
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
