from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: Optional[str]
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    user: str
    expires_delta: str
