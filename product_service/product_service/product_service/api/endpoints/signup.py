from fastapi import APIRouter
from fastapi import HTTPException
from starlette import status

from product_service import crud
from product_service.models.user import UserCreate, User

router = APIRouter()


@router.post(
    "/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_defaults=True,
)
async def signup(
    user_in: UserCreate
):
    user_in = user_in.dict(exclude={"role", "is_superuser", "is_active"})
    user = await crud.user.get_by_email(db, email=user_in.get("email"))
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists.",
        )
    new_user = await crud.user.create(obj_in=UserCreate(**user_in))
    return new_user
