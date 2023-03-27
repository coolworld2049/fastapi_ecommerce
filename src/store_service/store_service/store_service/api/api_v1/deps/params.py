import json
from collections.abc import Callable
from json import JSONDecodeError
from typing import Optional, Any

from fastapi import HTTPException
from fastapi import Query

from store_service.schemas.request_params import RequestParams


def sort_query_param(param: dict):
    sorted_ = {}
    if len(param) > 0:
        for k, v in param.items():
            # noinspection PyPep8
            try:
                if v is None:
                    sorted_.update({k: None})
                else:
                    sorted_.update({k: v})
            except Exception:
                raise HTTPException(400, f"Invalid param {k}: {v}")
    return sorted_


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
            include_in_schema=True if include_example else False,
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
                        except Exception:
                            raise HTTPException(
                                400, f"Invalid order direction '{k}': '{v}'"
                            )
            where = None
            if where_:
                where = sort_query_param(json.loads(where_))
            include = None
            if include_:
                include = sort_query_param(json.loads(include_))

        except JSONDecodeError as jse:
            raise HTTPException(400, f"Invalid query params. {jse}")
        return RequestParams(
            skip=skip, take=limit, order=order, where=where, include=include
        )

    return inner
