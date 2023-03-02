from typing import Any
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response

from product_service.models.category import CategoryCreate
from product_service import crud
from product_service.api.dependencies import auth
from product_service.api.dependencies import params
from product_service.models.category import Category
from product_service.models.request_params import RequestParams
from product_service.models.user import User

router = APIRouter()


# noinspection PyUnusedLocal
@router.get("/", response_model=List[Category])
async def read_categories(
    response: Response,

    current_user: User = Depends(auth.get_current_active_user),
    request_params: RequestParams = Depends(
        params.parse_query_params(),
    ),
) -> Any:
    """
    Retrieve categorys.
    """
    categorys, total = await crud.category.get_multi(request_params)
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(categorys)}/{total}"
    return categorys


# noinspection PyUnusedLocal
@router.post("/", response_model=Category)
async def create_category(
    *,

    category_in: CategoryCreate,
    current_user: User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Create new category.
    """

    category = await crud.category.create(obj_in=category_in)
    return category


# noinspection PyUnusedLocal
@router.get("/{id}", response_model=Category)
async def read_category_by_id(
    id: Any,
    current_user: User = Depends(auth.get_current_active_user),

) -> Any:
    """
    Get a specific category.
    """
    category = await crud.category.get(id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="The category does not exist",
        )
    return category


# noinspection PyUnusedLocal
@router.delete("/{name}")
async def delete_category(
    *,
    name: Any,
    current_user: User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Delete category.
    """
    category = await crud.category.get(name)
    if not category:
        raise HTTPException(status_code=404, detail="Item not found")
    category = await crud.category.remove(id=name)
    return {"detail": "Successfully deleted"}
