from fastapi import APIRouter

from auth_service.api.api_v1.endpoints import (
    login,
    signup,
)
from auth_service.api.api_v1.endpoints import users

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(signup.router, tags=["signup"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
