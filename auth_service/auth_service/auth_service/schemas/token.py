from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from auth_service import models


class Token(BaseModel):
    access_token: Optional[str]
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    user: str
    exp: int


class TokenData(TokenPayload):
    sub: str
    user: models.User | str
    exp: int

    class Config:
        arbitrary_types_allowed = True
