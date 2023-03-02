from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import EmailStr
from uvicorn.main import logger

from product_service import crud
from product_service.core.config import settings
from product_service.models.enums import UserRole
from product_service.models.user import UserCreate


async def create_first_superuser():
    super_user = await crud.user.get_by_email(
        email=settings.FIRST_SUPERUSER_EMAIL,
    )
    if not super_user:
        user_in_admin = UserCreate(
            email=EmailStr(settings.FIRST_SUPERUSER_EMAIL),
            username=settings.FIRST_SUPERUSER_USERNAME,
            role=UserRole.admin,
            full_name="No Name",
            phone='+799988877714',
            password=settings.FIRST_SUPERUSER_PASSWORD,
            password_confirm=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        super_user = await crud.user.create(obj_in=user_in_admin)
        logger.info("created")
    else:
        logger.info("first superuser already exists")
    return super_user


async def init_db(client: AsyncIOMotorClient, document_models: list):
    await init_beanie(database=client.app, document_models=document_models)
    await create_first_superuser()
