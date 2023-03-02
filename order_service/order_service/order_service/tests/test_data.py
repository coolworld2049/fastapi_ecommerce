import json
import random
import string

import pytest
from faker import Faker
from loguru import logger
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from order_service import crud, schemas
from order_service.core.config import get_app_settings
from order_service.db.init_db import (
    init_db,
    create_first_superuser,
    truncate_tables,
)
from order_service.db.session import SessionLocal, pg_database
from order_service.models.enums import UserRole
from order_service.models.user import User
from order_service.tests.utils.utils import gen_random_password

fake = Faker()


async def create_users(users_count=5):
    ration_teachers_to_students = users_count // 2
    users: list[User] = []
    users_cred_list = []
    role = UserRole.admin.name
    for us in range(users_count):
        logger.info(f"UserCreate: {us + 1}/{users_count}")
        us += 2
        if us >= ration_teachers_to_students:
            role = UserRole.customer.name

        password = gen_random_password()
        user_in = schemas.UserCreate(
            email=EmailStr(f"{role}{us}@gmail.com"),
            password=password,
            password_confirm=password,
            username=f"{role}{us}{random.randint(1000, 10000)}",
            full_name=fake.name(),
            age=random.randint(18, 25),
            phone="+7"
            + "".join(random.choice(string.digits) for _ in range(10)),
            role=role,
        )
        users_cred_list.append(
            {
                user_in.role: {
                    "email": user_in.email,
                    "password": user_in.password,
                }
            },
        )
        async with SessionLocal() as db:
            user_in_obj = await crud.user.create(db, obj_in=user_in)
            users.append(user_in_obj)

    with open(f"test_api-users_cred_list.json", "w") as wr:
        wr.write(json.dumps(users_cred_list, indent=4))


@pytest.mark.asyncio
async def test_init_db(db: AsyncSession):
    conn = await pg_database.get_connection()
    await truncate_tables(conn)
    await init_db()
    await create_users(10)
    if get_app_settings().APP_ENV != "test":
        await truncate_tables(conn)
        await create_first_superuser(db)
    await conn.close()
