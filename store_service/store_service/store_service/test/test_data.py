import random
import string
from datetime import datetime

import pytest
from faker import Faker
from prisma import Prisma
from prisma.enums import OrderStatus
from prisma.models import User, Category, Product, Order
from prisma.types import UserCreateInput, CategoryCreateInput, ProductCreateInput
from uvicorn.main import logger

from store_service.core.auth import hash_password
from store_service.db.base import dbapp
from store_service.validator.user import UserValidator

faker = Faker()


class RandomDateTime:
    def __init__(self, year: int = None, month: int = None, day: int = None):
        self.year = year
        self.month = month
        self.day = day

    def datetime(self, now_dt: datetime):
        items = dict(
            filter(  # noqa
                lambda it: it[1] is not None and isinstance(it[1], int),
                self.__dict__.items(),
            )
        )
        return now_dt.replace(**items)


def rnd_string():
    return "".join(
        [random.choice(string.ascii_letters) for _ in range(random.randint(5, 10))]
    )


def rnd_password():
    length = 10
    return (
        f"{''.join(random.choice(string.ascii_letters) for _ in range(length)).capitalize()}"
        f"{random.choice(string.ascii_uppercase)}"
        f"{random.randint(0, 9)}"
        f"{random.choice('@$!%*?&')}"
    )


async def create_user(count: int = 100):
    roles_count = {
        "admin": count // 4,
        "manager": count // 3,
        "customer": count,
        "guest": count // 2,
    }
    counter = 0
    users: list[User] = []
    for role, count in roles_count.items():
        for i in range(count):
            counter += i
            is_superuser = True if role == "admin" else False
            full_name: str = f"{faker.name()}-{rnd_string()}"
            username = full_name.replace(" ", "")
            user_in = UserCreateInput(
                email=f"{username}_{role}_{i}@gmail.com",
                username=username,
                role=role,
                password=rnd_password(),
                is_superuser=is_superuser,
                full_name=full_name,
            )
            try:
                UserValidator(user_in).validate()
                user_in.update({"password": hash_password(user_in.get("password"))})
                user = await User.prisma().create(data=user_in)
                users.append(user)
                db_user = await dbapp.command(  # noqa
                    "createUser",
                    user_in.get("username"),
                    pwd=hash_password(
                        user_in.get("password"),
                    ),
                    roles=[{"role": user_in.get("role"), "db": dbapp.name}],
                )
            except Exception as e:
                logger.info(e.args)
                raise
    return users


async def create_category(count=10):
    categories: list[Category] = []
    for i in range(count):
        category = await Category.prisma().create(
            CategoryCreateInput(name=rnd_string(), description=rnd_string())
        )
        categories.append(category)
    return categories


async def create_product(
    categories: list[Category], multiplier: int = 10, *, created_at: RandomDateTime
):
    products: list[Product] = []
    count = len(categories) * multiplier
    for i in range(count):
        product_in = ProductCreateInput(
            title=rnd_string(),
            category_id=random.choice(categories).id,
            price=random.randint(multiplier * 10, count),
            description=rnd_string(),
            stock=multiplier * 10,
            created_at=created_at.datetime(datetime.now()),
            updated_at=created_at.datetime(datetime.now()),
        )
        product = await Product.prisma().create(product_in, include={"category": True})
        products.append(product)
    return products


async def create_orders(users: list[User], created_at: RandomDateTime):
    orders: list[Order] = []
    for user in users:
        order = await Order.prisma().create(
            data={
                "user": {"connect": {"id": user.id}},
                "created_at": created_at.datetime(datetime.now()),
            },
            include={"user": True},
        )
        orders.append(order)
    return orders


async def update_orders(
    orders: list[Order],
    products: list[Product],
    created_at: RandomDateTime,
    products_choice_weight=10,
):
    _orders: list[Order] = []
    for order in orders:
        rnd_products: list[Product] = [
            x
            for x in random.choices(
                products, k=random.randint(1, products_choice_weight)
            )
        ]
        rnd_products_ids = [{"id": x.id} for x in rnd_products]
        rnd_products_cost = sum(list(map(lambda x: x.price, rnd_products)))
        order = await Order.prisma().update(
            data={
                "status": random.choice([OrderStatus.completed, OrderStatus.canceled]),
                "products": {"set": rnd_products_ids},
                "cost": {"set": rnd_products_cost},
                "updated_at": created_at.datetime(datetime.now()),
            },
            where={"id": order.id},
            include={"products": True},
        )
        _orders.append(order)
        if order.status == OrderStatus.completed:
            product = await Product.prisma().update_many(
                data={"stock": {"decrement": 1}},
                where={"id": {"in": order.product_ids}},
            )
            if not product:
                raise
        if order.status == OrderStatus.canceled:
            for p in rnd_products:
                product_ = await Product.prisma().update(
                    data={"orders": {"disconnect": [{"id": order.id}]}},
                    where={"id": p.id},
                )
                if not product_:
                    raise
    return _orders


async def delete_orders(orders: list[Order]):
    for order in orders:
        await Order.prisma().delete(where={"id": order.id}, include={"user": True})


async def delete_product(products: list[Product]):
    for product in products:
        await Product.prisma().delete(
            where={"id": product.id}, include={"category": True, "carts": True}
        )


async def delete_category(categories: list[Category]):
    for category in categories:
        await Product.prisma().delete(where={"id": category.id})


@pytest.mark.asyncio
async def test_data(prisma_client: Prisma):
    await prisma_client.connect()
    us = await create_user(count=100)
    cat = await create_category()
    now = datetime.now()
    created_at = RandomDateTime(
        random.choice([x for x in range(now.year - 3, now.year)]),
        random.randint(1, 12),
    )
    prod = await create_product(cat, created_at=created_at)
    for _ in range(3):
        orders = await create_orders(us, created_at=created_at)
        await update_orders(orders, prod, created_at=created_at)
