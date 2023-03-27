import asyncio
import logging

from loguru import logger
from tenacity import after_log
from tenacity import before_log
from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_fixed

from db.session import engines

max_tries = 60 * 2  # 2 minute
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.ERROR),
    after=after_log(logger, logging.WARNING),
)
async def init() -> None:
    await engines.check_engines()


def main() -> None:
    logger.info("Initializing service")
    asyncio.run(init())
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
