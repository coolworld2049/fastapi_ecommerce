from typing import Any
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from uvicorn.main import logger

from product_service import crud
from product_service.api.dependencies import auth
from product_service.api.dependencies import params
from product_service.models.enums import OrderStatus
from product_service.models.order import Order, OrderUpdate, OrderCreate
from product_service.models.request_params import RequestParams
from product_service.models.user import User

router = APIRouter()


# noinspection PyUnusedLocal
@router.get("/", response_model=List[Order])
async def read_orders(
    response: Response,

    current_user: User = Depends(auth.get_current_active_user),
    request_params: RequestParams = Depends(
        params.parse_query_params(),
    ),
) -> Any:
    """
    Retrieve orders.
    """
    orders, total = await crud.order.get_multi(request_params)
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(orders)}/{total}"
    return orders


# noinspection PyUnusedLocal
@router.get("/{id}", response_model=Order)
async def read_order_by_id(
    id: Any,
    current_user: User = Depends(auth.get_current_active_user),

) -> Any:
    """
    Get a specific order.
    """
    order = await crud.order.get(id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="The order does not exist",
        )
    return order


# noinspection PyUnusedLocal
@router.post("/", response_model=Order)
async def create_order(
    obj_in: OrderCreate,
    current_user: User = Depends(auth.get_current_active_user),

) -> Any:
    try:
        order = await crud.order.create(obj_in=obj_in)
        return order
    except Exception as e:
        logger.error(e.args)
        raise HTTPException(status_code=400, detail=e.args)


# noinspection PyUnusedLocal
@router.put("/{id}", response_model=Order)
async def update_order(
    *,
    id: Any,
    order_in: OrderUpdate,
    current_user: User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Update a order.
    """
    order = await crud.order.get(id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="The order with this ordername does not exist",
        )
    order = await crud.order.update(db_obj=order, obj_in=order_in)
    return order


# noinspection PyUnusedLocal
@router.patch("/{id}/{status}", response_model=Order)
async def update_order_status(
    *,
    id: Any,
    status: OrderStatus,
    current_user: User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Update a order.
    """
    order = await crud.order.get(id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="The order with this ordername does not exist",
        )
    order_in = OrderUpdate(
        status=status
    )
    order = await crud.order.update(db_obj=order, obj_in=order_in)
    return order


# noinspection PyUnusedLocal
@router.delete("/{id}")
async def delete_order(
    *,
    id: Any,
    current_user: User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Delete order.
    """
    order = await crud.order.get(id)
    if not order:
        raise HTTPException(status_code=404, detail="Item not found")
    order = await crud.order.remove(id=id)
    return {"detail": "Successfully deleted"}
