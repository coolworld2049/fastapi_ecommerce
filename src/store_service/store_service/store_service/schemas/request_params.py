from typing import Optional

from pydantic import BaseModel


class RequestParams(BaseModel):
    take: Optional[int]
    skip: Optional[int]
    order: Optional[dict]
    where: Optional[dict]
    include: Optional[dict]
