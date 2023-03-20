import random
from datetime import datetime

import faker_commerce
import pytest
from aiohttp import ClientSession
from faker import Faker
from loguru import logger
from prisma import Prisma
from prisma.enums import OrderStatus
from prisma.errors import UniqueViolationError
from prisma.models import Category, Product, Order, OrderProduct
from prisma.types import CategoryCreateInput, ProductCreateInput

from store_service.core.config import get_app_settings
from store_service.schemas.user import User
from store_service.test.auth_service.test_users import get_users
from store_service.test.utils import RandomDateTime, rnd_string

fake = Faker()
fake.add_provider(faker_commerce.Provider)


async def create_category(count=20):
    categories: list[Category] = []
    for i in range(count):
        category = await Category.prisma().create(
            CategoryCreateInput(name=rnd_string(), description=rnd_string()),
        )
        categories.append(category)
    logger.info(len(categories))
    return categories


async def create_product(
    categories: list[Category],
    multiplier: int = 100,
    *,
    created_at: RandomDateTime,
):
    if multiplier <= 0:
        raise ValueError(multiplier)

    products: list[Product] = []
    count = len(categories) * multiplier
    for i in range(count):
        product_in = ProductCreateInput(
            title=fake.ecommerce_name(),
            category_id=random.choice(categories).id,
            price=random.randint(100, 100000),
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
    logger.info(len(products))
    return products


async def create_orders(users: list[User], created_at: RandomDateTime):
    orders: list[Order] = []
    for i, user in enumerate(users):
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
    for i, order in enumerate(orders):
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
            await OrderProduct.prisma().update(
                data={"product": {"connect": {"id": p.id}}},
                where={"id": order.id},
            )
        _orders.append(order)
        data = None
        if order.status == OrderStatus.completed:
            data = {"stock": {"decrement": 1}}
        if data:
            for p in rnd_products:
                await Product.prisma().update(
                    data=data,
                    where={"id": p.id},
                )
    return _orders


@pytest.mark.asyncio
async def test_data(prisma_client: Prisma, auth_service_client: ClientSession):
    await prisma_client.connect()
    degree = 2 if get_app_settings().APP_ENV == "dev" else 1
    users = await get_users(
        count=10**degree, auth_service_client=auth_service_client
    )
    if get_app_settings().APP_ENV == "test":
        categories = await create_category(count=10 * degree)
        now = datetime.now()
        created_at = RandomDateTime(
            [now.year - 1, now.year],
            [1, datetime.now().month],
        )
        products = await create_product(
            categories, multiplier=10**degree, created_at=created_at
        )
        orders_count = 0
        for _ in range(degree):
            orders = await create_orders(users, created_at=created_at)
            orders_count += len(orders)
            await update_orders(orders, products, created_at=created_at)
        logger.info(f"orders_count - {orders_count}")
