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
from auth_service.core.settings.base import StageType
from auth_service.db.init_db import (
    init_db,
)
from auth_service.models.user_role import UserRoleEnum
from auth_service.test.utils.random_data import (
    gen_random_password,
    random_lower_string,
)

fake = Faker()


async def create_users(db: AsyncSession, count=100, out_user_creds=None):
    roles = {
        UserRoleEnum.admin: count // 10,
        UserRoleEnum.manager: count // 5,
        UserRoleEnum.client: count,
        UserRoleEnum.guest: count // 15,
    }
    users: list[schemas.User] = []
    test_users: dict[str, dict] = {}
    for r, c in roles.items():
        for i in range(c):
            password = gen_random_password()
            random_phone = "+7" + "".join(
                random.choice(string.digits) for _ in range(10)
            )
            user_in = schemas.UserCreate(
                email=EmailStr(
                    f"{r.name}{i}{random_lower_string(8)}@gmail.com"
                ),
                password=password,
                password_confirm=password,
                username=f"{r.name}{i}{random.randint(1000, 10000)}",
                full_name=fake.name(),
                age=random.randint(18, 25),
                phone=random_phone,
                role=r.name,
            )
            user_in_obj = await crud.user.create(db, obj_in=user_in)
            user_in_data = schemas.User(**user_in_obj.__dict__).dict()
            users.append(user_in_data)
            test_users.update({r.name: user_in_data})
    if out_user_creds and len(users) > 0:
        with open(out_user_creds, "w") as wr:
            wr.write(
                json.dumps(
                    test_users,
                    indent=4,
                    default=str,
                ),
            )
    return users


@pytest.mark.asyncio
async def test_fake_data(db: AsyncSession):
    await init_db()
    if get_app_settings().STAGE != StageType.prod:
        count = 20
        out_user_creds = "test_users_creds.json"
        users = await create_users(
            db=db, count=count, out_user_creds=out_user_creds
        )
        logger.info(
            f"users_count - {len(users)}, "
            f"fake user credentials stored in {pathlib.Path().absolute()}/{out_user_creds}"
        )
