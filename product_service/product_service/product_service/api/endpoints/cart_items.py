from typing import Any
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from sqlalchemy.exc import SQLAlchemyError

from product_service.models.cart_item import CartItemCreate, CartItemUpdate
from product_service import crud
from product_service.api.dependencies import auth
from product_service.api.dependencies import params
from product_service.models.cart_item import CartItem
from product_service.models.request_params import RequestParams
from product_service.models.user import User

router = APIRouter()


# noinspection PyUnusedLocal
@router.get("/", response_model=List[CartItem])
async def read_cart_items(
    response: Response,
    
    current_user: User = Depends(auth.get_current_active_user),
    request_params: RequestParams = Depends(
        params.parse_query_params(),
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
@router.post("/", response_model=CartItem)
async def create_cart_item(
    *,
    cart_item_in: CartItemCreate,
    current_user: User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Create new cart_item.
    """
    try:
        cart_item_in = CartItemCreate(
            **cart_item_in.dict(exclude_none=True)
        )
        new_cart_item = await crud.cart_item.create(db, obj_in=cart_item_in)
    except SQLAlchemyError as ie:
        raise HTTPException(status_code=400, detail=ie.args)
    return new_cart_item


# noinspection PyUnusedLocal
@router.get("/{id}", response_model=CartItem)
async def read_cart_item_by_id(
    id: Any,
    current_user: User = Depends(auth.get_current_active_user),
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
@router.put("/{id}", response_model=CartItem)
async def update_cart_item(
    *,
    id: Any,
    cart_item_in: CartItemUpdate,
    current_user: User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Update a cart_item.
    """
    cart_item_in = CartItemCreate(
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
@router.delete("/{id}")
async def delete_cart_item(
    *,
    id: Any,
    current_user: User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Delete cart_item.
    """
    cart_item = await crud.cart_item.get(db, id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found")
    cart_item = await crud.cart_item.remove(db=db, id=id)
    return {"detail": "Successfully deleted"}
