import uuid

from bson import ObjectId
from sqlalchemy import Boolean, String, func
from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import ENUM, UUID

from auth_service.db.session import Base
from auth_service.mixins.base import TimestampsMixin
from auth_service.models.enums import UserRole

user_role_enum = ENUM(
    *UserRole.to_list(),
    name=UserRole.snake_case_name(),
    metadata=Base.metadata
)


def uuid_to_object_id():
    return ObjectId(uuid.uuid4().hex[:24]).__str__()


class User(Base, TimestampsMixin):
    __tablename__ = "user"
    id = Column(String(24), primary_key=True, default=uuid_to_object_id)
    email = Column(Text, nullable=False, unique=True)
    hashed_password = Column(Text)
    phone = Column(Text)
    role = Column(user_role_enum, nullable=False)
    full_name = Column(Text)
    username = Column(Text, nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    is_superuser = Column(
        Boolean, nullable=False, server_default=text("false")
    )
