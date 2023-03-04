from prisma.models import *

common_excluded = ["created_at", "updated_at"]

# User
User.create_partial(
    "UserWithoutRelations",
    exclude_relational_fields=True,
    exclude=["password", "is_superuser", *common_excluded],
)

User.create_partial(
    "UserCreate",
    exclude_relational_fields=True,
    exclude=["id", "is_active", *common_excluded],
    required=["email", "username", "role", "password"],
)

User.create_partial(
    "UserCreateOpen",
    exclude_relational_fields=True,
    exclude=["id", "role", "is_active", "is_superuser", *common_excluded],
    required=["email", "username", "password"],
)

User.create_partial(
    "UserUpdate",
    exclude_relational_fields=True,
    exclude=["id", "password", "username", *common_excluded]
)

User.create_partial(
    "UserUpdateMe",
    exclude_relational_fields=True,
    exclude=[
        "id",
        "password",
        "username",
        "email",
        "role",
        "is_active",
        "is_superuser",
        *common_excluded
    ],
)

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
    "ProductCreate", exclude_relational_fields=True, exclude=["id", "order_ids"]
)

Product.create_partial(
    "ProductUpdate",
    exclude_relational_fields=True,
    exclude=["id", "category_id"],
)

# Order
Order.create_partial("OrderWithoutRelations", exclude_relational_fields=True)

Order.create_partial(
    "OrderCreate",
    exclude_relational_fields=True,
    required=["user_id", "status"],
    exclude=["cost", "tax", "total", "currency", *common_excluded],
)

Order.create_partial(
    "OrderUpdate",
    exclude_relational_fields=True,
    exclude=[*common_excluded],
    required=["user_id", "status"]
)
