from fastapi import APIRouter

from employee_service.api.api_v1.endpoints import (
    login,
    signup,
)
from employee_service.api.api_v1.endpoints import users
from employee_service.api.api_v1.endpoints import utils

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(signup.router, tags=["signup"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
