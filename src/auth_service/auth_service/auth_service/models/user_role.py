from sqlalchemy import Column, SmallInteger, String, Sequence

from auth_service.db.session import Base
from auth_service.models.mixins import EnumMixin


class UserRoleEnum(str, EnumMixin):
    admin = "admin"
    manager = "manager"
    client = "client"
    guest = "guest"


class UserRole(Base):
    __tablename__ = "user_role"
    id = Column(SmallInteger, Sequence('user_role_id_seq'), primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
