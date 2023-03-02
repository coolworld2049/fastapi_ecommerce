import json
from collections.abc import Callable
from typing import Optional

from fastapi import HTTPException
from fastapi import Query

from product_service.models.request_params import RequestParams


def parse_query_params() -> Callable[[str | None, str | None], RequestParams]:
    def inner(
        range_: Optional[str] = Query(
            None,
            alias="range",
            description="Format: `[skip, limit]`",
            example="[0, 10]",
        ),
        sort_: Optional[str] = Query(
            None,
            alias="sort",
            description='Format: `{"field_name", "ASC/DESC"}`'
        ),
        filter_: Optional[str] = Query(
            None,
            alias="filter",
            description='Format: `{"field_name": "value"}`',
        ),
    ):
        skip, limit = 0, 50
        if range_:
            start, end = json.loads(range_)
            skip, limit = start, (end - start + 1)

        sort = None
        if sort_:
            sort = []
            sort_by: dict = json.loads(sort_)
            if len(sort_by) > 0:
                for k, v in sort_by.items():
                    try:
                        if v.lower() == "asc":
                            sort.append(f"+{k}")
                        elif v.lower() == "desc":
                            sort.append(f"-{k}")
                    except:
                        raise HTTPException(400, f"Invalid sort direction '{k}': '{v}'")

        filter_by = None
        if filter_:
            filter_by = {}
            filters: dict = json.loads(filter_)
            if len(filters) > 0:
                for k, v in filters.items():
                    try:
                        if v is None:
                            filter_by.update({k: None})
                        else:
                            filter_by.update({k: v})
                    except:
                        raise HTTPException(
                            400, f"Invalid filters {filters}"
                        )

        rp = RequestParams(
            skip=skip,
            limit=limit,
            sort=sort,
            filter_by=filter_by,
        )
        return rp

    return inner
