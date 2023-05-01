import random
from datetime import datetime
from typing import Optional

from loguru import logger
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.crud.base import CRUDBase
from auth_service.models.user import User
from auth_service.schemas import UserCreate
from auth_service.schemas import UserUpdate
from auth_service.services.email import Email
from auth_service.services.security import (
    get_password_hash,
)
from auth_service.services.security import verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(
        self, db: AsyncSession, *, email: EmailStr | str
    ) -> Optional[User]:
        return await self.get_by_attr(db, User.email == email)

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        obj_in.password = get_password_hash(obj_in.password)
        del obj_in.password_confirm
        return await super().create(db, obj_in=obj_in)

    async def authenticate(
        self,
        *,
        email: str,
        password: str,
        db: AsyncSession,
    ) -> Optional[User]:
        db_obj = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, db_obj.password):
            return None
        return db_obj

    async def send_email_for_verif(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        email: Email,
    ):
        try:
            db_obj.verification_token = random.randbytes(24).hex()
            email_data = {
                "full_name": db_obj.full_name,
                "token": db_obj.verification_token,
            }
            await email.send_verification_code(
                subject="Verification",
                recipients=[EmailStr(db_obj.email)],
                data=email_data,
            )
        except Exception as e:
            await super().remove(db, id=db_obj.id)
            logger.error(e)
            return False
        await super().update(
            db, db_obj=db_obj, obj_in=UserUpdate(**db_obj.__dict__)
        )
        return True

    async def verify_token_from_email(
        self,
        db: AsyncSession,
        db_obj: User,
        token: str,
    ) -> Optional[User]:
        if not db_obj.verification_token == token:
            return None
        db_obj.is_verified = True
        db_obj.verified_at = datetime.now()
        db_obj = await super().update(
            db, db_obj=db_obj, obj_in=UserUpdate(**db_obj.__dict__)
        )
        return db_obj


user = CRUDUser(User)
