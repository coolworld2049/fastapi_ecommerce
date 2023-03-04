from typing import Optional

from passlib.context import CryptContext
from prisma.models import User

cryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return cryptContext.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return cryptContext.hash(password)


async def authenticate(
    email: str,
    password: str,
) -> Optional[User]:
    user = await User.prisma().find_unique(where={"email": email})
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user
