from typing import Any
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from employee_service import crud
from employee_service import schemas
from employee_service import models
from employee_service.api.dependencies import auth
from employee_service.api.dependencies import database
from employee_service.api.dependencies import params
from employee_service.models import Cart

router = APIRouter()


# noinspection PyUnusedLocal
@router.get("/", response_model=List[schemas.Cart])
async def read_carts(
    response: Response,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
    request_params: models.RequestParams = Depends(
        params.parse_react_admin_params(Cart),
    ),
) -> Any:
    """
    Retrieve carts.
    """
    carts, total = await crud.cart.get_multi(db, request_params)
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(carts)}/{total}"
    return carts


# noinspection PyUnusedLocal
@router.get("/{id}", response_model=schemas.Cart)
async def read_cart_by_id(
    id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(database.get_db),
) -> Any:
    """
    Get a specific cart.
    """
    cart = await crud.cart.get(db, id)
    if not cart:
        raise HTTPException(
            status_code=404,
            detail="The cart does not exist",
        )
    return cart


# noinspection PyUnusedLocal
@router.delete("/{id}", response_model=schemas.Cart)
async def delete_cart(
    *,
    id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Delete cart.
    """
    cart = await crud.cart.get(db, id)
    if not cart:
        raise HTTPException(status_code=404, detail="Item not found")
    cart = await crud.cart.remove(db=db, id=id)
    return cart
