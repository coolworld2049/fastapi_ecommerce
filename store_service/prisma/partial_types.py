from prisma.models import *

# Category
Category.create_partial("CategoryWithoutRelations", exclude_relational_fields=True)

Category.create_partial(
    "CategoryCreate", exclude_relational_fields=True, exclude=["id"]
)

Category.create_partial(
    "CategoryUpdate", exclude_relational_fields=True, exclude=["id"]
)

# Product
Product.create_partial("ProductWithoutRelations", exclude_relational_fields=True)

Product.create_partial(
    "ProductCreate", exclude_relational_fields=True, exclude=["id", "cart_ids"]
)

Product.create_partial(
    "ProductUpdate",
    exclude_relational_fields=True,
    exclude=["id", "cart_ids", "category_id"],
)

# Cart
Cart.create_partial("CartWithoutRelations", exclude_relational_fields=True)

Cart.create_partial(
    "CartCreate",
    exclude_relational_fields=True,
    exclude=["id", "status", "expires_at", "product_ids"],
)

Cart.create_partial(
    "CartUpdate",
    exclude_relational_fields=True,
    exclude=["id", "expires_at", "product_ids"],
)

Cart.create_partial(
    "CartProductInput",
    exclude_relational_fields=True,
    exclude=["id", "expires_at", "status"],
)

# Order
Order.create_partial("OrderWithoutRelations", exclude_relational_fields=True)

Order.create_partial(
    "OrderCreate",
    exclude_relational_fields=True,
    required=["cart_id", "status"],
    exclude=["cost", "tax", "total", "currency"],
)

Order.create_partial(
    "OrderUpdate", exclude_relational_fields=True, required=["cart_id", "status"]
)

# User
User.create_partial(
    "UserWithoutRelations",
    exclude_relational_fields=True,
    exclude=["password", "is_superuser"],
)

User.create_partial(
    "UserCreate",
    exclude_relational_fields=True,
    exclude=["id", "is_active"],
    required=["email", "username", "role", "password"],
)

User.create_partial(
    "UserCreateOpen",
    exclude_relational_fields=True,
    exclude=["id", "role", "is_active", "is_superuser"],
    required=["email", "username", "password"],
)

User.create_partial(
    "UserUpdate", exclude_relational_fields=True,
    exclude=["id", "password", "username"]
)

User.create_partial(
    "UserUpdateMe", exclude_relational_fields=True,
    exclude=["id", "password", "username", "is_active", "is_superuser"]
)
