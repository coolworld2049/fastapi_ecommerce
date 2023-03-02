from product_service.mixins.base import EnumMixin


class UserRole(str, EnumMixin):
    admin = "admin"
    manager = "manager"
    customer = "customer"
    guest = "guest"


class OrderStatus(str, EnumMixin):
    pending = "pending"
    awaiting_payment = "awaiting_payment"
    awaiting_fulfilment = "awaiting_fulfilment"
    completed = "completed"
    canceled = "canceled"
    declined = "declined"
    refunded = "refunded"
    disputed = "disputed"
    partially_refunded = "partially_refunded"


class CartStatus(str, EnumMixin):
    active = 'active'
    inactive = 'inactive'
