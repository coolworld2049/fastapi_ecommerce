from app.models import EnumMixin


class UserRole(str, EnumMixin):
    admin = "admin"
    user = "user"


