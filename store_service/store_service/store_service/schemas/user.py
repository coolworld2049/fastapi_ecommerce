from datetime import datetime
from typing import Optional

from pydantic import EmailStr, BaseModel


class UserBase(BaseModel):
    email: Optional[EmailStr]
    username: Optional[str]
    full_name: Optional[str]
    role: Optional[str]
    is_active: Optional[bool]
    is_superuser: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class User(UserBase):
    id: str
