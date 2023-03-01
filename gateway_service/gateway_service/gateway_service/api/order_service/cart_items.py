from typing import Any
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from order_service import crud
from order_service import schemas
from order_service import models
from order_service.api.dependencies import auth
from order_service.api.dependencies import database
from order_service.api.dependencies import params
from order_service.models import CartItem

router = APIRouter()


# noinspection PyUnusedLocal
@router.get("/", response_model=List[schemas.CartItem])
async def read_cart_items(
    response: Response,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
    request_params: models.RequestParams = Depends(
        params.parse_react_admin_params(CartItem),
    ),
) -> Any:
    """
    Retrieve cart_items.
    """
    cart_items, total = await crud.cart_item.get_multi(db, request_params)
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(cart_items)}/{total}"
    return cart_items


# noinspection PyUnusedLocal
@router.post("/", response_model=schemas.CartItem)
async def create_cart_item(
    *,
    db: AsyncSession = Depends(database.get_db),
    cart_item_in: schemas.CartItemCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Create new cart_item.
    """
    try:
        cart_item_in = schemas.CartItemCreate(
            **cart_item_in.dict(exclude_none=True)
        )
        new_cart_item = await crud.cart_item.create(db, obj_in=cart_item_in)
    except SQLAlchemyError as ie:
        raise HTTPException(status_code=400, detail=ie.args)
    return new_cart_item


# noinspection PyUnusedLocal
@router.get("/{id}", response_model=schemas.CartItem)
async def read_cart_item_by_id(
    id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: AsyncSession = Depends(database.get_db),
) -> Any:
    """
    Get a specific cart_item.
    """
    cart_item = await crud.cart_item.get(db, id)
    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="The cart_item does not exist",
        )
    return cart_item


# noinspection PyUnusedLocal
@router.put("/{id}", response_model=schemas.CartItem)
async def update_cart_item(
    *,
    id: int,
    db: AsyncSession = Depends(database.get_db),
    cart_item_in: schemas.CartItemUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Update a cart_item.
    """
    cart_item_in = schemas.CartItemCreate(
        **cart_item_in.dict(exclude_none=True)
    )
    cart_item = await crud.cart_item.get(db, id)
    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="The cart_item with this cart_itemname does not exist",
        )
    cart_item = await crud.cart_item.update(
        db, db_obj=cart_item, obj_in=cart_item_in
    )
    return cart_item


# noinspection PyUnusedLocal
@router.delete("/{id}", response_model=schemas.CartItem)
async def delete_cart_item(
    *,
    id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Delete cart_item.
    """
    cart_item = await crud.cart_item.get(db, id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found")
    cart_item = await crud.cart_item.remove(db=db, id=id)
    return cart_item
