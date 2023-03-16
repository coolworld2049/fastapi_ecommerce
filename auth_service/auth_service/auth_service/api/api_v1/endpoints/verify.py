from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from auth_service import crud, models
from auth_service.api.deps import database
from auth_service.api.errors.custom_exception import (
    InvalidVerificationCodeException,
)

router = APIRouter()


@router.get("/email/{token}")
async def verify_me(token: str, db: AsyncSession = Depends(database.get_db)):
    user = await crud.user.get_by_col(
        db, col=models.User.verification_code, val=token
    )
    if not user or user.is_verified:
        raise InvalidVerificationCodeException
    await crud.user.verify_token(db, db_obj=user, token=token)
    return Response(
        status_code=status.HTTP_200_OK, content="Account verified successfully"
    )
