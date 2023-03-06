import random
import string
from datetime import datetime

import faker_commerce
import pytest
from faker import Faker
from prisma import Prisma
from prisma.enums import OrderStatus
from prisma.errors import UniqueViolationError
from prisma.models import User, Category, Product, Order, OrderProduct
from prisma.types import UserCreateInput, CategoryCreateInput, ProductCreateInput
from uvicorn.main import logger

from store_service.core.auth import hash_password
from store_service.db.base import dbapp
from store_service.validator.user import UserValidator

fake = Faker()
fake.add_provider(faker_commerce.Provider)


class RandomDateTime:
    def __init__(
        self,
        year: list[int, int] = None,
        month: list[int, int] = None,
        day: list[int, int] = None,
    ):
        self.year = year
        self.month = month
        self.day = day

    def datetime(self, now_dt: datetime = datetime.now()):
        data = {
            "year": random.choice(self.year) if self.year else None,
            "month": random.choice(self.month) if self.month else None,
            "day": random.choice(self.day) if self.day else None,
        }
        items = dict(
            filter(  # noqa
                lambda it: it[1] is not None and isinstance(it[1], int), data.items()
            )
        )
        return now_dt.replace(**items)


def rnd_string(length=24):
    return "".join([random.choice(string.ascii_letters) for _ in range(length)])


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
    for role, _count in roles_count.items():
        for i in range(_count):
            counter += i
            is_superuser = True if role == "admin" else False
            full_name: str = f"{fake.name()}-{rnd_string()}"
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


async def create_category(count=20):
    categories: list[Category] = []
    for i in range(count):
        category = await Category.prisma().create(
            CategoryCreateInput(name=rnd_string(), description=rnd_string()),
        )
        categories.append(category)
    return categories


async def create_product(
    categories: list[Category], multiplier: int = 100, *, created_at: RandomDateTime
):
    products: list[Product] = []
    count = len(categories) * multiplier
    for i in range(count):
        product_in = ProductCreateInput(
            title=fake.ecommerce_name(),
            category_id=random.choice(categories).id,
            price=random.randint(1000, 100000),
            description=rnd_string(),
            stock=multiplier * 10,
            created_at=created_at.datetime(),
            updated_at=created_at.datetime(),
        )
        try:
            product = await Product.prisma().create(
                product_in, include={"category": True}
            )
            products.append(product)
        except UniqueViolationError:
            pass
    return products


async def create_orders(users: list[User], created_at: RandomDateTime):
    orders: list[Order] = []
    for user in users:
        order = await Order.prisma().create(
            data={
                "status": OrderStatus.pending,
                "cost": 0.0,
                "user": {"connect": {"id": user.id}},
                "created_at": created_at.datetime(),
                "updated_at": created_at.datetime(),
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
    k = random.randint(1, products_choice_weight)
    for order in orders:
        rnd_products: list[Product] = [x for x in random.choices(products, k=k)]
        rnd_products_cost = sum(list(map(lambda x: x.price, rnd_products)))
        order = await Order.prisma().update(
            data={
                "status": random.choice([x for x in OrderStatus]),
                "order_products": {
                    "create": [
                        {
                            "product_id": x.id,
                        }
                        for x in rnd_products
                    ],
                },
                "cost": {"set": rnd_products_cost},
                "updated_at": created_at.datetime(),
            },
            where={"id": order.id},
            include={"order_products": True},
        )
        for p in rnd_products:
            order_product = await OrderProduct.prisma().update(
                data={"product": {"connect": {"id": p.id}}}, where={"id": order.id}
            )
        _orders.append(order)
        data = None
        if order.status == OrderStatus.completed:
            data = {"stock": {"decrement": 1}}
        if data:
            for p in rnd_products:
                product = await Product.prisma().update(
                    data=data,
                    where={"id": p.id},
                )
    return _orders


@pytest.mark.asyncio
async def test_data(prisma_client: Prisma):
    await prisma_client.connect()
    us = await create_user(count=100)
    cat = await create_category()
    now = datetime.now()
    created_at = RandomDateTime(
        [now.year - 1, now.year],
        [1, datetime.now().month],
    )
    prod = await create_product(cat, created_at=created_at)
    for _ in range(3):
        orders = await create_orders(us, created_at=created_at)
        await update_orders(orders, prod, created_at=created_at)
