from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

import auth_service.api.deps.db
from auth_service import crud, models
from auth_service.api.exceptions import (
    InvalidVerificationTokenException,
)
from auth_service.db import session

router = APIRouter()


@router.get("/email/{token}")
async def verify_me(
    token: str,
    db: AsyncSession = Depends(auth_service.api.deps.db.get_db),
):
    user = await crud.user.get_by_attr(
        db, where_clause=models.User.verification_token == token
    )
    if not user or user.is_verified:
        raise InvalidVerificationTokenException
    await crud.user.verify_token_from_email(db, db_obj=user, token=token)
