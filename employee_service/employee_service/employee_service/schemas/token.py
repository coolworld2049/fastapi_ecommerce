from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from employee_service.models import UserRole


class TokenBase(BaseModel):
    access_token: str = Field(None, alias="access_token")
    token_type: Optional[str] = "bearer"

    class Config:
        allow_population_by_field_name = True


class TokenPayload(TokenBase):
    sub: Optional[str]
    role: Optional[UserRole]
    expires_delta: Optional[datetime]

    class Config:
        use_enum_values = True


class Token(TokenPayload):
    pass
