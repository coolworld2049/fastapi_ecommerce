from typing import Optional, Any

from fastapi import APIRouter, HTTPException, Depends
from prisma.models import Category
from prisma.partials import CategoryWithoutRelations, CategoryCreate, CategoryUpdate
from starlette import status

from store_service.api.api_v1.deps import params
from store_service.api.api_v1.deps.base import RoleChecker
from store_service.api.api_v1.deps.params import RequestParams

router = APIRouter()


@router.get(
    "/",
    response_model=list[CategoryWithoutRelations],
    dependencies=[
        Depends(RoleChecker(Category, ["admin", "manager", "customer", "guest"]))
    ],
)
async def read_categories(
    request_params: RequestParams = Depends(params.parse_query_params()),
) -> list[Category]:
    category = await Category.prisma().find_many(
        **request_params.dict(exclude_none=True)
    )
    return category


@router.post(
    "/",
    response_model=CategoryWithoutRelations,
    dependencies=[Depends(RoleChecker(Category, ["admin", "manager"]))],
)
async def create_category(category_in: CategoryCreate) -> Optional[Category]:
    category = await Category.prisma().create(category_in.dict())
    return category


@router.get(
    "/{id}",
    response_model=CategoryWithoutRelations,
    dependencies=[
        Depends(RoleChecker(Category, ["admin", "manager", "customer", "guest"]))
    ],
)
async def read_category_by_id(
    id: str,
) -> Category | None:
    category = await Category.prisma().find_unique(where={"id": id})
    return category


@router.put(
    "/{id}",
    response_model=CategoryWithoutRelations,
    dependencies=[Depends(RoleChecker(Category, ["admin", "manager"]))],
)
async def update_category(id: str, category_in: CategoryUpdate) -> Optional[Category]:
    return await Category.prisma().update(
        where={
            "id": id,
        },
        data=category_in.dict(),
    )


@router.delete(
    "/{id}",
    dependencies=[Depends(RoleChecker(Category, ["admin", "manager"]))],
)
async def delete_category(id: str) -> dict[str, Any]:
    where = {
        "id": id,
    }
    category = await Category.prisma().find_unique(where=where)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await Category.prisma().delete(where=where)
    return {"status": status.HTTP_200_OK}
