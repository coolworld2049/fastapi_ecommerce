from enum import Enum
from typing import Any

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine


class ReplType(str, Enum):
    master = "master"
    slave = "slave"


class MasterReplicas:
    __slots__ = ("engines",)

    def __init__(
        self, master_url: str, slaves_url: list[str], *args, **kwargs
    ):
        self.engines: dict[ReplType, AsyncEngine | tuple[AsyncEngine]] = {}
        self.engines.update(
            {ReplType.master: (create_async_engine(master_url, **kwargs),)}
        )
        self.engines.update(
            {
                ReplType.slave: tuple(
                    create_async_engine(url, **kwargs) for url in slaves_url
                )
                if slaves_url
                else []
            }
        )

    @property
    def get_all(self) -> tuple[Any, Any]:
        return (
            *self.engines[ReplType.master],
            *self.engines[ReplType.slave],
        )

    def get_master(self):
        eng = self.engines.get(ReplType.master)[0]
        return eng if eng else None

    def get_slaves(self):
        eng = self.engines.get(ReplType.slave)
        return eng if eng else None

    async def check_engines(self):
        for _type, _eng in self.engines.items():
            for i, eng in enumerate(_eng):
                try:
                    async with eng.begin() as conn:
                        await conn.execute(text("select 1"))
                    logger.info(f"repl_type: {_type.name}, url: {eng.url}")
                except ConnectionRefusedError as ex:
                    logger.error(
                        f"repl_type: {_type.name}, url: {eng.url}, {ex.__class__.__name__} {ex}"
                    )
