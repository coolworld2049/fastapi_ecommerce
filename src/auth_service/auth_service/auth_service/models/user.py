from sqlalchemy import (
    Boolean,
    String,
    BigInteger,
    ForeignKey,
)
from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import TIMESTAMP

from auth_service.db.session import Base
from auth_service.models.mixins import TimestampsMixin


class User(Base, TimestampsMixin):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True)
    email = Column(Text, nullable=False, unique=True)
    password = Column(Text)
    role = Column(ForeignKey("user_role.name"), nullable=False)
    full_name = Column(String(128))
    username = Column(String(128), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    is_superuser = Column(
        Boolean, nullable=False, server_default=text("false")
    )
    verification_token = Column(String(255))
    is_verified = Column(Boolean, nullable=False, server_default=text("false"))
    verified_at = Column(TIMESTAMP(timezone=True), default=None)
