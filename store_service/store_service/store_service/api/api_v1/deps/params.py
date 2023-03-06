import ast
import json
from collections.abc import Callable
from json import JSONDecodeError
from typing import Optional, Any

from fastapi import HTTPException
from fastapi import Query
from pydantic import BaseModel


class RequestParams(BaseModel):
    take: Optional[int] = None
    skip: Optional[int] = None
    order: Optional[dict] = None
    where: Optional[dict] = None


def parse_query_params(
        use_range=True,
        use_order=True,
        use_where=True,
        range_example="[0,50]",
        order_example='{"id": "asc"}',
        where_example: Any = None,
        range_description: str = "",
        where_add_description: str = "",
) -> Callable[[str | None, str | None], RequestParams]:
    def inner(
            range_: Optional[str] = Query(
                None,
                alias="range",
                description="Format: `[skip, limit]`, infinity: `[skip, null]` " + range_description,
                example=range_example,
                include_in_schema=use_range,
            ),
            order_: Optional[str] = Query(
                None,
                alias="order",
                description='Format: `{"field_name", "asc/desc"}`',
                example=order_example,
                include_in_schema=use_order,
            ),
            where_: Optional[str] = Query(
                None,
                alias="where",
                description='Format: `{"field_name": "value"}`, ' + where_add_description,
                example=where_example,
                include_in_schema=use_where,
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
            if order_:
                order = {}
                order_by: dict = json.loads(order_)
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
            assert ast.literal_eval(where_example)
            where_by = ast.literal_eval(where_example)
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
                            raise HTTPException(400, f"Invalid where param {k}: {v}")
        except JSONDecodeError as jse:
            raise HTTPException(400, f"Invalid query params. {jse}")
        _rp = {"skip": skip, "take": limit, "order": order, "where": where_by}

        return RequestParams(**_rp)

    return inner
