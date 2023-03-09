import asyncio
import logging

from tenacity import after_log
from tenacity import before_log
from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_fixed
from loguru import logger

max_tries = 60 * 2
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARNING),
)
async def init() -> None:
    from store_service.db.base import dbapp

    try:
        status = await dbapp.command("serverStatus")
        assert status["ok"] == 1.0
    except Exception as e:
        logger.info(e.args)
        raise e


def main() -> None:
    logger.warning("Initializing service")
    asyncio.run(init())
    logger.warning("Service finished initializing")


if __name__ == "__main__":
    main()
