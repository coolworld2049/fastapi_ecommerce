from typing import Any
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from auth_service import crud
from auth_service import models
from auth_service import schemas
from auth_service.api.deps import auth
from auth_service.api.deps import params
from auth_service.api.deps.auth import RoleChecker
from auth_service.api.deps.db import get_db
from auth_service.api.exceptions import DuplicateUserException
from auth_service.core.config import get_app_settings
from auth_service.core.settings.base import StageType
from auth_service.models.user import User
from auth_service.schemas import RequestParams

router = APIRouter()


@cache(expire=60)
@router.get(
    "/",
    response_model=List[schemas.User],
    dependencies=None
    if get_app_settings().STAGE == StageType.test
    else [Depends(RoleChecker(["admin"]))],
)
async def read_users(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    request_params: RequestParams = Depends(
        params.parse_react_admin_params(User),
    ),
) -> Any:
    """
    Retrieve users.
    """
    users = await crud.user.get_multi(response, db, request_params)
    return users


@router.post(
    "/",
    response_model=schemas.User,
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise DuplicateUserException
    user = await crud.user.create(db, obj_in=user_in)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return user


@router.put(
    "/me",
    response_model=schemas.User,
    dependencies=[
        Depends(RoleChecker(["admin", "manager", "client", "guest"]))
    ],
)
async def update_user_me(
    user_in: schemas.UserUpdateMe,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_active_current_user),
) -> Any:
    """
    Update own user.
    """
    user = await crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get(
    "/me",
    response_model=schemas.User,
    dependencies=[
        Depends(RoleChecker(["admin", "manager", "client", "guest"]))
    ],
)
async def read_user_me(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_active_current_user),
) -> Any:
    """
    Get current user.
    """
    user = await crud.user.get(db, current_user.id)
    return user


@router.get(
    "/{id}",
    response_model=schemas.User,
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def read_user_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get a specific user.
    """
    user = await crud.user.get(db, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user


@router.put(
    "/{id}",
    response_model=schemas.User,
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def update_user(
    *,
    id: int,
    db: AsyncSession = Depends(get_db),
    user_in: schemas.UserUpdate,
) -> Any:
    """
    Update a user.
    """
    user = await crud.user.get(db, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    user = await crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete(
    "/{id}",
    response_model=schemas.User,
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def delete_user(
    *,
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_active_current_user),
) -> Any:
    """
    Delete user
    """
    user = await crud.user.get(db, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if (
        id == current_user.id
        or user.email == get_app_settings().FIRST_SUPERUSER_EMAIL
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forbidden to delete",
        )
    user = await crud.user.remove(db=db, id=id)
    return user
