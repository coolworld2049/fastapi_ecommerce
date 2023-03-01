import uvicorn

from order_service.core.config import get_app_settings
from order_service.main import project_templates_html_path

if __name__ == "__main__":
    uvicorn.run(
        "main:order_service",
        port=get_app_settings().PORT,
        reload=True,
        reload_dirs=project_templates_html_path.__str__(),
    )
