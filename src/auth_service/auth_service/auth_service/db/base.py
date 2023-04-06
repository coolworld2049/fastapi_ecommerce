from enum import Enum
from typing import Any

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine


class ReplType(str, Enum):
    master = "master"
    slave = "slave"


class MasterReplica:
    __slots__ = ("engine",)

    def __init__(self, master_url: str, slaves_url: str, *args, **kwargs):
        self.engine: dict[ReplType, AsyncEngine | tuple[AsyncEngine]] = {}
        self.engine.update(
            {ReplType.master: (create_async_engine(master_url, **kwargs),)}
        )
        self.engine.update(
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
            *self.engine[ReplType.master],
            *self.engine[ReplType.slave],
        )

    def get_master(self):
        eng = self.engine.get(ReplType.master)[0]
        return eng if eng else None

    def get_slaves(self):
        eng = self.engine.get(ReplType.slave)
        return eng if eng else None

    async def check_engines(self):
        for _type, _eng in self.engine.items():
            for i, eng in enumerate(_eng):
                try:
                    async with eng.begin() as conn:
                        await conn.execute(text("select 1"))
                    logger.info(f"repl_type: {_type.name}, url: {eng.url}")
                except ConnectionRefusedError as ex:
                    logger.error(
                        f"repl_type: {_type.name}, url: {eng.url}, {ex.__class__.__name__} {ex}"
                    )
