from datetime import datetime
from typing import Optional

from pydantic import EmailStr, BaseModel


class UserBase(BaseModel):
    email: Optional[EmailStr]
    username: Optional[str]
    full_name: Optional[str]
    role: Optional[str]
    is_active: bool = True
    is_superuser: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class User(UserBase):
    id: str

