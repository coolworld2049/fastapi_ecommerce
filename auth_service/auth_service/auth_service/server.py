import uvicorn

from auth_service.core.config import get_app_settings
from auth_service.main import project_templates_html_path

if __name__ == "__main__":
    uvicorn.run(
        "main:auth_service",
        port=get_app_settings().PORT,
        reload=True,
        reload_dirs=project_templates_html_path.__str__(),
    )
