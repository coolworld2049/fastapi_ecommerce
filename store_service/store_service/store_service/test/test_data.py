import random
import string
from logging import Logger

import pytest
from faker import Faker
from prisma import Prisma
from prisma.models import User, Category, Product, Cart, Order
from prisma.types import UserCreateInput, CategoryCreateInput, ProductCreateInput
from uvicorn.main import logger

from store_service.core.auth import hash_password
from store_service.core.config import settings
from store_service.db.base import dbapp
from store_service.validator.user import UserValidator

faker = Faker()


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


async def create_user(count: int = 20):
    roles = {
        "admin": count // 4,
        "manager": count // 3,
        "customer": count,
        "guest": count * 2,
    }
    counter = 0
    users: list[User] = []
    for role, count in roles.items():
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


async def create_product(count=10, *, categories: list[Category]):
    products: list[Product] = []
    for i in range(count):
        product_in = ProductCreateInput(
            title=rnd_string(),
            category_id=random.choice(categories).id,
            price=random.randint(100, 100000),
            description=rnd_string(),
        )
        product = await Product.prisma().create(product_in)
        products.append(product)
    return products


async def create_carts(users: list[User], products: list[Product]):
    carts: list[Cart] = []
    users = list(filter(lambda x: x.role == 'customer', users))
    for user in users:
        data = {
            "expires_at": settings.cart_expires_timestamp,
            "user": {"connect": {"id": user.id}},
        }
        cart = await Cart.prisma().create(data=data)

        product_ids = [{"id": x.id} for x in random.choices(products, k=random.randint(1, 3))]
        new_data = {
            "products": {"set": product_ids, "connect": product_ids}
        }
        new_cart = await Cart.prisma().update(data=new_data, where={"id": cart.id})
        carts.append(new_cart)
    return carts


async def create_orders(carts: list[Cart]):
    orders: list[Order] = []
    for cart in carts:
        order = await Order.prisma().create(data={"cart": {"connect": {"id": cart.id}}})
        orders.append(order)
    return orders


async def delete_orders(orders: list[Order]):
    for order in orders:
        await Order.prisma().delete(where={"cart_id": order.cart_id}, include={"cart": True})


async def delete_cart(carts: list[Cart]):
    for cart in carts:
        await Cart.prisma().delete(where={"id": cart.id}, include={"products": True})


async def delete_product(products: list[Product]):
    for product in products:
        await Product.prisma().delete(where={"id": product.id}, include={"category": True, "carts": True})


async def delete_category(categories: list[Category]):
    for category in categories:
        await Product.prisma().delete(where={"id": category.id})


@pytest.mark.asyncio
async def test_data(prisma_client: Prisma):
    await prisma_client.connect()
    us = await create_user()
    cat = await create_category()
    prod = await create_product(categories=cat)
    carts = await create_carts(us, prod)
    orders = await create_orders(carts)
    await delete_orders(orders)
    await delete_cart(carts)
    await delete_product(prod)
    await delete_category(cat)
