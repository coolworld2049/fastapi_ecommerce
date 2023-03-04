import pytest
from faker import Faker
from prisma import Prisma
from prisma.models import User
from prisma.types import UserCreateInput
from uvicorn.main import logger

from store_service.core.auth import hash_password
from store_service.db.base import dbapp

faker = Faker()


async def create_user(count: int = 20):
    roles = {"admin": count // 4, "manager": count // 3, "customer": count, "guest": count * 2}
    counter = 0
    for role, count in roles.items():
        for i in range(count):
            counter += i
            is_superuser = True if role == "admin" else False
            full_name: str = faker.name()
            username = full_name.replace(" ", "")
            user_in = UserCreateInput(
                email=f"{username}_{role}_{i}@gmail.com",
                username=username,
                role=role,
                password=hash_password(role),
                is_superuser=is_superuser,
                full_name=full_name,
            )
            try:
                user = await User.prisma().create(data=user_in)
                db_user = await dbapp.command(
                    "createUser",
                    user_in.get("username"),
                    pwd=hash_password(
                        user_in.get("password"),
                    ),
                    roles=[{"role": user_in.get("role"), "db": dbapp.name}],
                )
                logger.info(f"create_user: {counter}")
            except Exception as e:
                logger.info(e.args)


@pytest.mark.asyncio
async def test_data(prisma_client: Prisma):
    await prisma_client.connect()
    await create_user()
