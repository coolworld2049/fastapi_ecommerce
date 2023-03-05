from prisma.errors import UniqueViolationError
from prisma.models import User
from prisma.types import UserCreateInput
from pymongo.errors import OperationFailure
from uvicorn.main import logger

from store_service.core.auth import hash_password
from store_service.core.config import settings
from store_service.db.base import dbapp
from store_service.resources.predefined_roles import predefined_roles


async def create_predefined_roles(_roles: list[dict[str, list[str]]]):
    try:
        if _roles:
            for item in _roles:
                try:
                    await dbapp.command(
                        "createRole",
                        item.get("role"),
                        privileges=item.get("privileges"),
                        roles=item.get("roles"),
                    )
                    logger.info(f"predefined role '{item.get('role')}' created")
                except:  # noqa
                    logger.info(f"predefined role '{item.get('role')}' already exist")
    except OperationFailure as e:
        logger.error(e.args)


async def create_first_superuser():
    user_in = UserCreateInput(
        email=settings.FIRST_SUPERUSER_EMAIL,
        username=settings.FIRST_SUPERUSER_USERNAME,
        role="admin",
        password=hash_password(settings.FIRST_SUPERUSER_PASSWORD),
        is_superuser=True,
        full_name="No Name",
    )
    try:
        user = await User.prisma().create(data=user_in)
        await dbapp.command(
            "createUser",
            user_in.get("username"),
            pwd=hash_password(
                user_in.get("password"),
            ),
            roles=[{"role": user_in.get("role"), "db": dbapp.name}],
        )
        logger.info("first superuser created")
        return user
    except UniqueViolationError as e:
        logger.info(f"first superuser already exists")


async def init_db():
    await create_predefined_roles(predefined_roles)
    await create_first_superuser()
