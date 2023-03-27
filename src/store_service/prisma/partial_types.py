from prisma.models import Category, Product, Order

common_excluded = ["created_at", "updated_at"]

# Category
Category.create_partial(
    "CategoryWithoutRelations", exclude_relational_fields=True
)

Category.create_partial(
    "CategoryCreate",
    exclude_relational_fields=True,
    exclude=["id", *common_excluded],
)

Category.create_partial(
    "CategoryUpdate",
    exclude_relational_fields=True,
    exclude=["id", *common_excluded],
)

# Product
Product.create_partial(
    "ProductWithoutRelations", exclude_relational_fields=True
)

Product.create_partial(
    "ProductCreate",
    exclude_relational_fields=True,
    exclude=["id", *common_excluded],
)

Product.create_partial(
    "ProductUpdate",
    exclude_relational_fields=True,
    exclude=["id", "category_id", *common_excluded],
)

# Order
Order.create_partial("OrderWithoutRelations", exclude=["order_products"])

Order.create_partial(
    "OrderCreate",
    exclude_relational_fields=True,
    required=["user_id", "status"],
    exclude=["cost", "order_products", *common_excluded],
)

Order.create_partial(
    "OrderUpdate",
    exclude_relational_fields=True,
    exclude=[*common_excluded],
    required=["user_id", "status"],
)
