import uvicorn

from store_service.core.config import get_app_settings

if __name__ == "__main__":
    uvicorn.run("main:store_service", port=get_app_settings().APP_PORT)
