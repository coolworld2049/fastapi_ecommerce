from typing import Optional

from fastapi import APIRouter
from prisma.models import User
from prisma.partials import UserWithoutRelations, UserCreateOpen

from store_service.core.auth import hash_password
from store_service.db.base import dbapp

router = APIRouter()


@router.post(
    "/guest",
    response_model=UserWithoutRelations,
)
async def sign_up_guest(user_in: UserCreateOpen) -> Optional[User]:
    user = await User.prisma().create(user_in.dict())
    await dbapp.command(
        "createUser",
        user_in.username,
        pwd=hash_password(user_in.password),
        roles=[{"role": "customer", "db": dbapp.name}],
    )
    return user
