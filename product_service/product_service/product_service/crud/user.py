from typing import Optional

from pydantic import EmailStr

from product_service.crud.base import CRUDBase
from product_service.models.user import User, UserCreate, UserUpdate
from product_service.services.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    # noinspection PyMethodMayBeStatic
    async def get_by_email(
        self, email: EmailStr | str
    ) -> Optional[User]:
        return await self.model.find_one(self.model.email == email)

    async def create(self, obj_in: UserCreate) -> User:
        obj_in_data = obj_in.dict(exclude_none=True)
        obj_in_data.update(
            {"hashed_password": get_password_hash(obj_in.password)}
        )
        obj_in_data.pop("password")
        obj_in_data.pop("password_confirm")
        return await super().create(obj_in=User(**obj_in_data))

    async def update_me(
        self,
        db_obj: User,
        obj_in: UserUpdate,
    ) -> None:
        obj_in_data = obj_in.dict(exclude_none=True)
        obj_in_data.update(
            {"hashed_password": get_password_hash(obj_in.password)}
        )
        obj_in_data.pop("password")
        obj_in_data.pop("password_confirm")
        return await super().update(db_obj=db_obj, obj_in=UserUpdate(**obj_in_data))

    # noinspection PyShadowingNames
    async def authenticate(
        self,
        email: EmailStr | str,
        password: str,

    ) -> Optional[User]:
        user = await self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    # noinspection PyShadowingNames,PyMethodMayBeStatic
    def is_active(self, user: User) -> bool:
        return user.is_active

    # noinspection PyShadowingNames,PyMethodMayBeStatic
    def is_superuser(self, user: User) -> bool:
        return user.is_superuser


user = CRUDUser(User)
