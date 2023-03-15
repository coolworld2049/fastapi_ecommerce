import json
from collections.abc import Callable
from json import JSONDecodeError
from typing import Optional, Any

from fastapi import HTTPException
from fastapi import Query
from pydantic import BaseModel, Field


class RequestParams(BaseModel):
    take: Optional[int] = None
    skip: Optional[int] = None
    order: Optional[dict] = None
    where: Optional[dict] = None
    include: Optional[dict] = None


def parse_query_params(
    use_range=True,
    use_order=True,
    use_where=True,
    range_example="[0,50]",
    order_example='{"id": "ASC"}',
    where_example: Any = None,
    range_description: str = "",
    where_add_description: str = "",
    include_example: str = None,
) -> Callable[[str | None, str | None], RequestParams]:
    def inner(
        range_: Optional[str] = Query(
            None,
            alias="range",
            description="Format: `[start, end]`, infinity: `[start, null]` "
            + range_description,
            example=range_example,
            include_in_schema=use_range,
        ),
        sort_: Optional[str] = Query(
            None,
            alias="sort",
            description='Format: `{"field_name", "ASC/DESC"}`',
            example=order_example,
            include_in_schema=use_order,
        ),
        where_: Optional[str] = Query(
            None,
            alias="filter",
            description='Format: `{"field_name": "value"}`, '
            + where_add_description,
            example=where_example,
            include_in_schema=use_where,
        ),
        include_: Optional[str] = Query(
            None,
            alias="include",
            description='Format: `{"field_name": true}`, `{"field_name": false}`',
            example=include_example,
        ),
    ):
        try:
            skip, limit = 0, 50
            if range_:
                start, end = json.loads(range_)
                if end is None:
                    skip, limit = start, None
                else:
                    skip, limit = start, (end - start + 1)

            order = None
            if sort_:
                order = {}
                order_by: dict = json.loads(sort_)
                if len(order_by) > 0:
                    for k, v in order_by.items():
                        try:
                            if v.lower() == "asc":
                                order.update({k: "asc"})
                            elif v.lower() == "desc":
                                order.update({k: "desc"})
                        except:
                            raise HTTPException(
                                400, f"Invalid order direction '{k}': '{v}'"
                            )
            where_by = None
            if where_:
                where_by = {}
                wheres: dict = json.loads(where_)
                if len(wheres) > 0:
                    for k, v in wheres.items():
                        try:
                            if v is None:
                                where_by.update({k: None})
                            else:
                                where_by.update({k: v})
                        except:
                            raise HTTPException(
                                400, f"Invalid where param {k}: {v}"
                            )
            include = None
            if include_:
                include = {}
                includes: dict = json.loads(include_)
                if len(includes) > 0:
                    for k, v in includes.items():
                        try:
                            if v is None:
                                include.update({k: None})
                            else:
                                include.update({k: v})
                        except:
                            raise HTTPException(
                                400, f"Invalid include param {k}: {v}"
                            )

        except JSONDecodeError as jse:
            raise HTTPException(400, f"Invalid query params. {jse}")
        _rp = {
            "skip": skip,
            "take": limit,
            "order": order,
            "where": where_by,
            "include": include,
        }

        return RequestParams(**_rp)

    return inner
