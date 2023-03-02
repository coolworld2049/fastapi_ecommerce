from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import ENUM

from order_service.db.session import Base
from order_service.mixins.base import TimestampsMixin
from order_service.models.enums import UserRole

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
    age = Column(SmallInteger, server_default=None)
    phone = Column(String(20))
    avatar = Column(Text)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    is_superuser = Column(Boolean, nullable=False, server_default=text("false"))

