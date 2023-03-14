import re
from datetime import datetime
from difflib import SequenceMatcher
from typing import Optional

from loguru import logger
from pydantic import EmailStr, validator, root_validator, BaseModel

from auth_service.models import UserRole
from auth_service.resources.reserved_username import reserved_usernames_list

PASSWORD_REGEXP = (
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)
PASSWORD_REGEXP_DESCRIPTION = """
Minimum 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character
"""
USERNAME_REGEXP = "[A-Za-z_0-9]*"


class UserOptional(BaseModel):
    full_name: Optional[str]
    phone: Optional[str]


class UserSpec(BaseModel):
    role: UserRole = UserRole.guest
    is_active: bool = True
    is_superuser: bool = False


class UserBase(UserOptional):
    email: Optional[EmailStr]
    username: Optional[str]

    class Config:
        use_enum_values = True

    @validator("username")
    def validate_username(cls, value):
        assert re.match(
            USERNAME_REGEXP,
            value,
        ), "Invalid characters in username"
        assert (
            value not in reserved_usernames_list
        ), "This username is reserved"
        return value

    @validator("phone")
    def validate_phone(cls, v: str):
        if v:
            regex = r"^(\+)[1-9][0-9\-\(\)\.]{9,15}$"
            if v.isdigit() and not re.search(regex, v, re.I):
                raise ValueError("Phone Number Invalid.")
        return v


# Properties to receive via API on creation
class UserCreateBase(UserBase):
    password: str
    password_confirm: str

    @classmethod
    def check_password_strongness(cls, values):
        def values_match_ratio(a, b):
            return SequenceMatcher(None, a, b).ratio() if a and b else None

        if (
            values.get("email")
            and values.get("username")
            and values.get("password")
        ):
            username_password_match: float = values_match_ratio(
                values.get("username"),
                values.get("password"),
            )
            assert (
                username_password_match < 0.5
            ), "Password must not match username"

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
            ), "Passwords mismatch"
        if values.get("id") is None:
            try:
                return cls.check_password_strongness(values)
            except AssertionError as e:
                logger.error(e.args)

    @validator("password")
    def validate_password(cls, value):
        assert re.match(
            PASSWORD_REGEXP, value, flags=re.M
        ), PASSWORD_REGEXP_DESCRIPTION
        return value


class UserCreate(UserCreateBase, UserSpec):
    pass


class UserCreateOpen(UserCreate, UserOptional):
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
