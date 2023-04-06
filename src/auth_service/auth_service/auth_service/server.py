import uvicorn

from auth_service.core.config import get_app_settings

if __name__ == "__main__":
    uvicorn.run("main:auth_service", port=get_app_settings().APP_PORT)
