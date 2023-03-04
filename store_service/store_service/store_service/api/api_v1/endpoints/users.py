from typing import Optional, Any

from fastapi import APIRouter, HTTPException, Depends
from prisma.models import User
from prisma.partials import UserWithoutRelations, UserCreate, UserUpdate, UserUpdateMe
from starlette import status

from store_service.api.api_v1.deps import params
from store_service.api.api_v1.deps.base import RoleChecker, get_current_active_user
from store_service.api.api_v1.deps.params import RequestParams

router = APIRouter()


@router.get(
    "/",
    response_model=list[UserWithoutRelations],
    dependencies=[Depends(RoleChecker(User, ["admin"]))],
)
async def read_users(
    request_params: RequestParams = Depends(params.parse_query_params()),
) -> list[User]:
    user = await User.prisma().find_many(**request_params.dict())
    return user


@router.post(
    "/",
    response_model=UserWithoutRelations,
    dependencies=[Depends(RoleChecker(User, ["admin"]))],
)
async def create_user(user_in: UserCreate) -> Optional[User]:
    user = await User.prisma().create(user_in.dict())
    return user


@router.get(
    "/{id}",
    response_model=UserWithoutRelations,
    dependencies=[Depends(RoleChecker(User, ["admin"]))],
)
async def read_user_by_id(
    id: str,
) -> User | None:
    user = await User.prisma().find_unique(where={"id": id})
    return user


@router.put(
    "/{id}",
    response_model=UserWithoutRelations,
    dependencies=[Depends(RoleChecker(User, ["admin"]))],
)
async def update_user(id: str, user_in: UserUpdate) -> Optional[User]:
    return await User.prisma().update(
        where={
            "id": id,
        },
        data=user_in.dict(),
    )


@router.get(
    "/me",
    response_model=UserWithoutRelations,
    dependencies=[Depends(RoleChecker(User, ["admin", "manager", "customer"]))],
)
async def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> User | None:
    user = await User.prisma().find_unique(where={"id": current_user.id})
    return user


@router.put(
    "/me",
    response_model=UserWithoutRelations,
    dependencies=[
        Depends(RoleChecker(User, ["admin", "manager", "customer"])),
    ],
)
async def update_user_me(
    user_in: UserUpdateMe, current_user: User = Depends(get_current_active_user)
) -> Optional[User]:
    return await User.prisma().update(
        where={
            "id": current_user.id,
        },
        data=user_in.dict(),
    )


@router.delete(
    "/{id}",
    dependencies=[Depends(RoleChecker(User, ["admin"]))],
)
async def delete_user(id: str) -> dict[str, Any]:
    where = {
        "id": id,
    }
    user = await User.prisma().find_unique(where=where)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await User.prisma().delete(where=where)
    return {"status": status.HTTP_200_OK}
