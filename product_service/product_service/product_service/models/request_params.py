from typing import Any
from typing import Optional

from pydantic.main import BaseModel


class RequestParams(BaseModel):
    skip: Optional[int]
    limit: Optional[int]
    sort: Optional[Any]
    filter_by: Optional[Any]
