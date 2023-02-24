import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api.dependencies.database import get_session_user, reset_session_user, is_rolname_exist, create_user_in_role, \
    set_session_user
from app.core.config import get_app_settings


@pytest.mark.asyncio
async def test_auth_in_db(db: AsyncSession):
    current_user = await crud.user.get_by_email(db, email=get_app_settings().FIRST_SUPERUSER_EMAIL)
    await get_session_user(db)
    await reset_session_user(db)
    await get_session_user(db)
    if not await is_rolname_exist(db, current_user):
        await create_user_in_role(db, current_user)
    await reset_session_user(db)
    await get_session_user(db)
    await set_session_user(db, current_user)
    await get_session_user(db)
