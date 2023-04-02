import json
import pathlib
import random
import string

import pytest
from faker import Faker
from loguru import logger
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service import crud, schemas
from auth_service.core.config import get_app_settings
from auth_service.core.settings.base import AppEnvTypes
from auth_service.db.init_db import (
    init_db,
    base_metadata,
)
from auth_service.db.session import engines, SessionLocal
from auth_service.models.user import User
from auth_service.models.user_role import UserRoleEnum
from auth_service.test.utils.utils import (
    gen_random_password,
    random_lower_string,
)

fake = Faker()


async def create_users(db: AsyncSession, count=100, out_user_creds=None):
    roles = {
        UserRoleEnum.admin: count // 10,
        UserRoleEnum.manager: count // 5,
        UserRoleEnum.client: count,
    }
    users: list[User] = []
    users_cred_list = []
    for r, c in roles.items():
        for i in range(c):
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
            if out_user_creds:
                users_cred_list.append(
                    {
                        user_in.role: {
                            "email": user_in.email,
                            "username": user_in.username,
                            "password": user_in.password,
                        }
                    },
                )
            user_in_obj = await crud.user.create(db, obj_in=user_in)
            users.append(user_in_obj)
    if out_user_creds and len(users_cred_list) > 0:
        with open(out_user_creds, "w") as wr:
            wr.write(json.dumps(users_cred_list, indent=4))
    return users


@pytest.mark.asyncio
async def test_fake_data():
    await base_metadata(engines, drop=True)
    await init_db()
    if get_app_settings().APP_ENV != AppEnvTypes.prod:
        count = 30
        out_user_creds = "test_users_creds.json"
        async with SessionLocal() as db:
            users = await create_users(
                db=db, count=count, out_user_creds=out_user_creds
            )
            logger.info(
                f"users_count - {len(users)}, "
                f"fake user credentials stored in {pathlib.Path().absolute()}/{out_user_creds}"
            )
