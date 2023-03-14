import json
import random
import string

import pytest
from asyncpg import UniqueViolationError
from faker import Faker
from loguru import logger
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service import crud, schemas
from auth_service.core.config import get_app_settings
from auth_service.db.init_db import (
    init_db,
    drop_all_models,
)
from auth_service.db.session import SessionLocal, engine
from auth_service.models.user_role import UserRole
from auth_service.models.user import User
from auth_service.test.utils.utils import (
    gen_random_password,
    random_lower_string,
)

fake = Faker()


async def create_users(count=100):
    roles = {
        UserRole.admin: count // 10,
        UserRole.manager: count // 5,
        UserRole.customer: count,
    }
    users: list[User] = []
    users_cred_list = []
    for r, c in roles.items():
        for i in range(c):
            logger.info(f"UserCreate: role: {r.name}, {i + 1}/{c}")
            password = gen_random_password()
            user_in = schemas.UserCreate(
                email=EmailStr(
                    f"{r.name}{i}{random_lower_string(8)}@gmail.com"
                ),
                password=password,
                password_confirm=password,
                username=f"{r.name}{i}{random.randint(1000, 10000)}",
                full_name=fake.name(),
                age=random.randint(18, 25),
                phone="+7"
                + "".join(random.choice(string.digits) for _ in range(10)),
                role=r.name,
            )
            users_cred_list.append(
                {
                    user_in.role: {
                        "email": user_in.email,
                        "username": user_in.username,
                        "password": user_in.password,
                    }
                },
            )
            async with SessionLocal() as db:
                user_in_obj = await crud.user.create(db, obj_in=user_in)
                users.append(user_in_obj)

    with open(f"test_user_creds.json", "w") as wr:
        wr.write(json.dumps(users_cred_list, indent=4))


@pytest.mark.asyncio
async def test_init_db(db: AsyncSession):
    await drop_all_models(engine)
    await init_db()
    await create_users(30 if get_app_settings().APP_ENV == "dev" else 10)
