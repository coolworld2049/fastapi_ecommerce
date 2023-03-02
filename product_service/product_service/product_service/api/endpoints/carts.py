from typing import Any
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response

from product_service.models.cart import CartCreate
from product_service import crud
from product_service.api.dependencies import auth
from product_service.api.dependencies import params
from product_service.models.cart import Cart
from product_service.models.request_params import RequestParams
from product_service.models.user import User

router = APIRouter()


# noinspection PyUnusedLocal
@router.get("/", response_model=List[Cart])
async def read_carts(
    response: Response,
    
    current_user: User = Depends(auth.get_current_active_user),
    request_params: RequestParams = Depends(
        params.parse_query_params(),
    ),
) -> Any:
    """
    Retrieve carts.
    """
    carts, total = await crud.cart.get_multi(request_params)
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(carts)}/{total}"
    return carts


# noinspection PyUnusedLocal
@router.post("/", response_model=Cart)
async def create_cart(
    *,
    
    cart_in: CartCreate,
    current_user: User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Create new cart.
    """

    cart = await crud.cart.create(obj_in=cart_in)
    return cart


# noinspection PyUnusedLocal
@router.get("/{id}", response_model=Cart)
async def read_cart_by_id(
    id: Any,
    current_user: User = Depends(auth.get_current_active_user),
    
) -> Any:
    """
    Get a specific cart.
    """
    cart = await crud.cart.get(id)
    if not cart:
        raise HTTPException(
            status_code=404,
            detail="The cart does not exist",
        )
    return cart


# noinspection PyUnusedLocal
@router.delete("/{id}")
async def delete_cart(
    *,
    id: Any,
    current_user: User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Delete cart.
    """
    cart = await crud.cart.get(id)
    if not cart:
        raise HTTPException(status_code=404, detail="Item not found")
    cart = await crud.cart.remove(id=id)
    return {"detail": "Successfully deleted"}
