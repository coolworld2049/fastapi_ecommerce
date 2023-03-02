from typing import Any
from typing import Dict
from typing import Generic
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from beanie import Document, PydanticObjectId, exceptions as beanie_exceptions
from beanie.odm.operators.update.general import Set
from pydantic import BaseModel
from uvicorn.main import logger

from product_service.models.request_params import RequestParams

DocumentType = TypeVar("DocumentType", bound=Document)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


def catch_exception(f) -> DocumentType | Any:
    async def wrapper(*arg, **kwargs):
        try:
            await f(*arg, **kwargs)
        except Exception as e:
            logger.error(e.args)
        except beanie_exceptions as e:
            logger.error(e.args)

    return wrapper


class CRUDBase(Generic[DocumentType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[DocumentType]):
        self.model = model

    async def get(self, id: PydanticObjectId) -> Optional[DocumentType]:
        return await self.model.find_one(self.model.id == PydanticObjectId(id))

    async def get_by_col(
        self, col: Any, val: Any
    ) -> Optional[DocumentType]:
        return await self.model.find_one({col: val})

    async def get_multi(
        self,
        request_params: RequestParams = None
    ) -> tuple[list[DocumentType], int]:
        if request_params.filter_by:
            res = self.model.find_many(request_params.filter_by,
                                       **request_params.dict(exclude={'filter_by'}))
            total = await res.count()
        else:
            res = self.model.find_many(**request_params.dict(exclude_none=True))
            total = await self.model.count()
        return await res.to_list(), total

    async def create(
        self, *, obj_in: CreateSchemaType
    ) -> DocumentType:
        return await self.model.create(self.model(**obj_in.dict(exclude_unset=True, exclude_none=True)))

    async def update(
        self,
        *,
        db_obj: DocumentType,
        obj_in: UpdateSchemaType,
    ) -> None:
        return await db_obj.update(Set(obj_in.dict(exclude_unset=True)))

    async def remove(self, *, id: Any) -> Any:
        db_obj = await self.get(id=id)
        return await db_obj.delete()
