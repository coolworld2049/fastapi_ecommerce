from auth_service.mixins.base import EnumMixin


class UserRole(str, EnumMixin):
    admin = "admin"
    manager = "manager"
    customer = "customer"
    guest = "guest"
