from employee_service.core.config import get_app_settings
from celery import Celery

celery_app = Celery(
    "worker",
    broker=get_app_settings().rabbitmq_dsn,
    backend=get_app_settings().redis_dsn,
)

celery_app.conf.task_routes = {
    "employee_service.worker.*": "main-queue",
    "employee_service.tasks.*": "main-queue",
}
