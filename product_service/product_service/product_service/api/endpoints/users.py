from typing import Any
from typing import List

from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr

from product_service.models.user import UserCreate
from product_service import crud
from product_service.api.dependencies import auth
from product_service.api.dependencies import params
from product_service.models.request_params import RequestParams
from product_service.models.user import User, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[User])
async def read_users(
    response: Response,
    request_params: RequestParams = Depends(
        params.parse_query_params(),
    ),
) -> Any:
    """
    Retrieve users.
    """
    users, total = await crud.user.get_multi(request_params)
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(users)}/{total}"
    return users


@router.post("/", response_model=User)
async def create_user(
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """

    user = await crud.user.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    new_user = await crud.user.create(obj_in=user_in)
    return new_user


@router.put("/me", response_model=User)
async def update_user_me(
    email: EmailStr = Body(None),
    password: str = Body(None),
    password_confirm: str = Body(None),
    current_user: User = Depends(auth.get_current_active_user)
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = UserUpdate(**current_user_data)
    if email:
        user_in.email = email
    if password:
        user_in.password = password
        if password_confirm:
            user_in.password_confirm = password_confirm

    await crud.user.update_me(db_obj=current_user, obj_in=user_in)
    return current_user


@router.get("/me", response_model=User)
async def read_user_me(
    response: Response,
    current_user: User = Depends(auth.get_current_active_user)
) -> Any:
    """
    Get current user.
    """
    user = await crud.user.get(current_user.id)
    response.headers["Content-Range"] = f"{0}-{1}/{1}"
    return user


@router.get("/{id}", response_model=User)
async def read_user_by_id(
    id: Any,
) -> Any:
    """
    Get a specific user.
    """
    user = await crud.user.get(id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user does not exist",
        )
    return user


@router.put("/{id}", response_model=User)
async def update_user(
    *,
    id: Any,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    user = await crud.user.get(id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist",
        )
    user = await crud.user.update(db_obj=user, obj_in=user_in)
    return user


@router.delete("/{id}")
async def delete_user(
    *,
    id: Any,
) -> Any:
    """
    Delete user.
    """
    user = await crud.user.get(id)
    if not user:
        raise HTTPException(status_code=404, detail="Item not found")
    if user.is_active:
        raise HTTPException(
            status_code=404, detail="Acive user cannot be removed"
        )
    if user.is_superuser:
        raise HTTPException(
            status_code=404, detail="Superuser cannot be removed"
        )
    await crud.user.remove(id=id)
    return {"detail": "Successfully deleted"}
