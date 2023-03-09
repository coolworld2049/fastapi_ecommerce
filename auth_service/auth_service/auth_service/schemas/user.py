import re
from datetime import datetime
from difflib import SequenceMatcher
from typing import Optional, Any

from loguru import logger
from pydantic import EmailStr, validator, root_validator, BaseModel
from pydantic.types import UUID

from auth_service.models import UserRole
from auth_service.resources.reserved_username import reserved_usernames_list

password_exp = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
password_conditions = """
Minimum 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character
"""
username_exp = "[A-Za-z_0-9]*"


class UserOptional(BaseModel):
    full_name: Optional[str]
    phone: Optional[str]


class UserBase(UserOptional):
    email: Optional[EmailStr]
    username: Optional[str]
    role: UserRole = UserRole.guest
    is_active: bool = True
    is_superuser: bool = False

    class Config:
        use_enum_values = True

    @validator("username")
    def validate_username(cls, value):  # noqa
        assert re.match(
            username_exp,
            value,
        ), "Invalid characters in username"
        assert value not in reserved_usernames_list, "This username is reserved"
        return value

    @validator("phone")
    def validate_phone(cls, v: str):  # noqa
        if v:
            regex = r"^(\+)[1-9][0-9\-\(\)\.]{9,15}$"
            if v.isdigit() and not re.search(regex, v, re.I):
                raise ValueError("Phone Number Invalid.")
        return v


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str
    password_confirm: str

    @classmethod
    def check_password_strongness(cls, values):
        def values_match_ratio(a, b):
            return SequenceMatcher(None, a, b).ratio() if a and b else None

        if values.get("email") and values.get("username") and values.get("password"):
            username_password_match: float = values_match_ratio(
                values.get("username"),
                values.get("password"),
            )
            assert username_password_match < 0.5, "Password must not match username"

            email_password_match: float = values_match_ratio(
                values.get("email").split("@")[0],
                values.get("password"),
            )
            assert email_password_match < 0.5, "Password must not match email"
        return values

    @root_validator()
    def validate_all_fields(cls, values):
        if values.get("password_confirm"):
            assert values.get("password") == values.get(
                "password_confirm"
            ), "Passwords mismatch."
        if values.get("id") is None:
            try:
                return cls.check_password_strongness(values)
            except AssertionError as e:
                logger.error(e.args)

    @validator("password")
    def validate_password(cls, value):  # noqa
        assert re.match(password_exp, value, flags=re.M), password_conditions
        return value


# Properties to receive via API on update
class UserUpdate(UserCreate):
    pass


class UserInDBBase(UserBase):
    id: Optional[str] = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    class Config:
        use_enum_values = True


# Additional properties stored in DB but not returned by API
class UserInDB(UserInDBBase):
    _hashed_password: str
