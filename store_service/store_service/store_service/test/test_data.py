import random
import string
from datetime import datetime

import aiohttp
import faker_commerce
import pytest
from faker import Faker
from prisma import Prisma
from prisma.enums import OrderStatus
from prisma.errors import UniqueViolationError
from prisma.models import Category, Product, Order, OrderProduct
from prisma.types import CategoryCreateInput, ProductCreateInput

from store_service.core.config import settings
from store_service.schemas.user import User

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
                lambda it: it[1] is not None and isinstance(it[1], int),
                data.items(),
            )
        )
        return now_dt.replace(**items)


def rnd_string(length=24):
    return "".join(
        [random.choice(string.ascii_letters) for _ in range(length)]
    )


def rnd_password():
    length = 10
    return (
        f"{''.join(random.choice(string.ascii_letters) for _ in range(length)).capitalize()}"
        f"{random.choice(string.ascii_uppercase)}"
        f"{random.randint(0, 9)}"
        f"{random.choice('@$!%*?&')}"
    )


async def get_token(username: str, password: str):
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = {"username": username, "password": password}
    async with aiohttp.ClientSession(
        settings.AUTH_SERVICE_URL, headers=headers
    ) as session:
        async with session.post(
            "/api/v1/login/access-token", data=body
        ) as resp:
            resp = await resp.json()
            return resp.get("access_token")


async def get_users(count=100, *, token: str):
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    async with aiohttp.ClientSession(
        settings.AUTH_SERVICE_URL, headers=headers
    ) as session:
        async with session.get(
            f"""/api/v1/users?range=[0, {count}]&sort=["id", "ASC"]"""
        ) as resp:
            resp = await resp.json()
            return resp


async def create_category(count=20):
    categories: list[Category] = []
    for i in range(count):
        category = await Category.prisma().create(
            CategoryCreateInput(name=rnd_string(), description=rnd_string()),
        )
        categories.append(category)
    return categories


async def create_product(
    categories: list[Category],
    multiplier: int = 100,
    *,
    created_at: RandomDateTime,
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
                "user_id": user.id,
                "created_at": created_at.datetime(),
                "updated_at": created_at.datetime(),
            }
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
        rnd_products: list[Product] = [
            x for x in random.choices(products, k=k)
        ]
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
                data={"product": {"connect": {"id": p.id}}},
                where={"id": order.id},
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
    if settings.DEBUG:
        await prisma_client.connect()
        token = await get_token(
            settings.FIRST_SUPERUSER_EMAIL, settings.FIRST_SUPERUSER_PASSWORD
        )
        users = await get_users(count=300, token=token)
        users = [User(**x) for x in users]
        categories = await create_category()
        now = datetime.now()
        created_at = RandomDateTime(
            [now.year - 1, now.year],
            [1, datetime.now().month],
        )
        products = await create_product(categories, created_at=created_at)
        for _ in range(3):
            orders = await create_orders(users, created_at=created_at)
            await update_orders(orders, products, created_at=created_at)
