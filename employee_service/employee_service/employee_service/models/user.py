from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import ENUM

from employee_service.db.session import Base
from employee_service.mixins.base import TimestampsMixin
from employee_service.models.enums import UserRole

user_role_enum = ENUM(
    *UserRole.to_list(), name=UserRole.snake_case_name(), metadata=Base.metadata
)


class User(Base, TimestampsMixin):
    __tablename__ = "user"
    id = Column(BigInteger, primary_key=True)
    email = Column(Text, nullable=False, unique=True)
    hashed_password = Column(Text)
    role = Column(user_role_enum, nullable=False)
    full_name = Column(Text)
    username = Column(Text, nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    is_superuser = Column(Boolean, nullable=False, server_default=text("false"))
