from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth_service import crud, schemas
from auth_service.api.dependencies import database
from auth_service.models import UserRole

router = APIRouter()


@router.post(
    "/signup/customer",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_defaults=True,
)
async def signup_customer(
    user_in: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)
):
    user_in.role = UserRole.customer.name
    user_in = user_in.dict(exclude={"role", "is_superuser", "is_active"})
    user = await crud.user.get_by_email(db, email=user_in.get("email"))
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists.",
        )
    new_user = await crud.user.create(db, obj_in=schemas.UserCreate(**user_in))
    return new_user
