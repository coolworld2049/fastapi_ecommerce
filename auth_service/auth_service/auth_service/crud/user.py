from typing import Any
from typing import Optional

from loguru import logger
from pydantic import EmailStr
from sqlalchemy import and_, select
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from auth_service.crud.base import CRUDBase
from auth_service.models.user import User
from auth_service.schemas import UserCreate
from auth_service.schemas import UserUpdate
from auth_service.services.security import get_password_hash
from auth_service.services.security import verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_id(
        self,
        db: AsyncSession,
        *,
        id: str,
    ) -> Optional[User]:
        q: Select = select(self.model).where(User.id == id)
        result: Result = await db.execute(q)
        return result.scalar()

    async def get_by_email(
        self, db: AsyncSession, *, email: EmailStr | str
    ) -> Optional[User]:
        q: Select = select(self.model).where(User.email == email)
        result: Result = await db.execute(q)
        return result.scalar()

    # noinspection PyArgumentList
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        obj_in_data = obj_in.dict(exclude_none=True)
        obj_in_data.update(
            {"hashed_password": get_password_hash(obj_in.password)}
        )
        obj_in_data.pop("password")
        obj_in_data.pop("password_confirm")
        db_obj = self.model(**obj_in_data)
        try:
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(e.args)
            raise
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: UserUpdate | dict[str, Any],
    ) -> User:
        obj_in_data = obj_in.dict(exclude_none=True)
        db_obj.hashed_password = get_password_hash(obj_in_data.get("password"))
        result = await super().update(db, db_obj=db_obj, obj_in=obj_in)
        return result

    async def constr_user_role_filter(
        self, roles: list[str], column: Any = None
    ):
        c_filter = None
        if roles:
            if column is None:
                c_filter = and_(self.model.role.in_(tuple(roles)))
            else:
                c_filter = and_(column.in_(tuple(roles)))
        return c_filter

    async def authenticate(
        self,
        *,
        email: str,
        password: str,
        db: AsyncSession,
    ) -> Optional[User]:
        user_obj = await self.get_by_email(db, email=email)
        if not user or not verify_password(password, user_obj.hashed_password):
            return None
        return user_obj


user = CRUDUser(User)
