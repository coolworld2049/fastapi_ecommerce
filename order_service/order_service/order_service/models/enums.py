from order_service.mixins.base import EnumMixin


class UserRole(str, EnumMixin):
    admin = "admin"
    manager = "manager"
    user = "user"
    guest = "guest"


class OrderStatus(str, EnumMixin):
    pending = "pending"
    accepted = "accepted"
    completed = "completed"
    terminated = "terminated"
