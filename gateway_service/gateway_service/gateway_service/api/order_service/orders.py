from typing import Any
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from employee_service import crud
from employee_service import models
from employee_service import schemas
from employee_service.api.dependencies import auth
from employee_service.api.dependencies import database
from employee_service.api.dependencies import params
from employee_service.models.order import Order

router = APIRouter()


# noinspection PyUnusedLocal
@router.get("/", response_model=List[schemas.Order])
async def read_orders(
    response: Response,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
    request_params: models.RequestParams = Depends(
        params.parse_react_admin_params(Order),
    ),
) -> Any:
    """
    Retrieve orders.
    """
    orders, total = await crud.order.get_multi(db, request_params)
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(orders)}/{total}"
    return orders


# noinspection PyUnusedLocal
@router.post("/", response_model=schemas.Order)
async def create_order(
    *,
    db: AsyncSession = Depends(database.get_db),
    order_in: schemas.OrderCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Create new order.
    """

    user = await crud.user.is_exists(db, id=order_in.user_id)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="User with this id does not exist",
        )
    new_order = await crud.order.create(db, obj_in=order_in)
    return new_order


# noinspection PyUnusedLocal
@router.get("/{id}", response_model=schemas.Order)
async def read_order_by_id(
    id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(database.get_db),
) -> Any:
    """
    Get a specific order.
    """
    order = await crud.order.get(db, id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="The order does not exist",
        )
    return order


# noinspection PyUnusedLocal
@router.get("/{user_id}", response_model=schemas.Order)
async def read_order_by_user_id(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(database.get_db),
) -> Any:
    """
    Get a specific order by user_id.
    """
    order = await crud.order.get_by_user_id(db, id=user_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="The order with this user_id does not exist",
        )
    return order


# noinspection PyUnusedLocal
@router.put("/{id}", response_model=schemas.Order)
async def update_order(
    *,
    id: int,
    db: AsyncSession = Depends(database.get_db),
    order_in: schemas.OrderUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Update a order.
    """
    order = await crud.order.get(db, id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="The order with this ordername does not exist",
        )
    order = await crud.order.update(db, db_obj=order, obj_in=order_in)
    return order


# noinspection PyUnusedLocal
@router.delete("/{id}", response_model=schemas.Order)
async def delete_order(
    *,
    id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Delete order.
    """
    order = await crud.order.get(db, id)
    if not order:
        raise HTTPException(status_code=404, detail="Item not found")
    order = await crud.order.remove(db=db, id=id)
    return order
