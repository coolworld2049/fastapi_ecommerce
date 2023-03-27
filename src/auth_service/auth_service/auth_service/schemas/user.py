import re
from datetime import datetime
from typing import Optional

from pydantic import EmailStr, validator, BaseModel

from auth_service.models import UserRoleEnum


class UserOptional(BaseModel):
    full_name: Optional[str]

    class Config:
        use_enum_values = True


class UserSpec(BaseModel):
    role: UserRoleEnum = UserRoleEnum.guest
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    _verification_code: Optional[str]


# noinspection PyMethodParameters
class UserBase(UserOptional):
    email: Optional[EmailStr]
    username: Optional[str]

    @validator("username", always=True)
    def validate_username(cls, value):
        assert re.match(
            "^[A-Za-z][A-Za-z0-9_]{7,29}$",
            value,
        ), "Invalid username"
        return value


class UserCreateBase(UserBase):
    password: Optional[str]
    password_confirm: Optional[str]


class UserCreate(UserCreateBase, UserSpec):
    pass


class UserCreateOpen(UserCreateBase, UserOptional):
    pass


class UserUpdate(UserCreate, UserSpec):
    pass


class UserUpdateMe(UserOptional):
    pass


class User(UserBase, UserSpec):
    id: Optional[str] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
