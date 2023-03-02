import re
from datetime import datetime
from difflib import SequenceMatcher
from typing import Optional

from beanie import Document, Indexed
from loguru import logger
from pydantic import EmailStr, validator, root_validator, BaseModel, Field

from product_service.models.enums import UserRole
from product_service.resources.reserved_username import reserved_usernames_list

password_exp = (
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)
password_conditions = """
Minimum 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character
"""
username_exp = "[A-Za-z_0-9]*"


class UserOptional(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserBase(UserOptional):
    email: Indexed(EmailStr, unique=True)
    username: Indexed(str, unique=True)
    role: UserRole = UserRole.guest
    hashed_password: Optional[str] = None
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
        else:
            return None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str
    password_confirm: str

    class Config:
        orm_mode = True

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
class UserUpdate(UserBase):
    password: str | None = None
    password_confirm: str | None = None


class UserInDBBase(UserBase):
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now)


# Additional properties to return via API
class User(UserInDBBase, Document):
    class Config:
        orm_mode = True


# Additional properties stored in DB but not returned by API
class UserInDB(UserInDBBase):
    pass
