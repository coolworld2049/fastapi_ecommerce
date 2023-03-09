import random
import string

from locust import HttpUser, task, between

from auth_service import schemas
from auth_service.core.config import get_app_settings
from auth_service.tests.test_data import fake
from auth_service.tests.utils.utils import (
    random_email,
    random_lower_string,
    gen_random_password,
)


class PerformanceTests(HttpUser):
    wait_time = between(0.5, 1)

    base_url = f"http://{get_app_settings().DOMAIN}:{get_app_settings().PORT}{get_app_settings().api_v1}"

    @task(7)
    def test_create_user(self):
        email = random_email()
        username = random_lower_string()
        password = gen_random_password()
        user_in = schemas.UserCreate(
            email=email,
            username=username,
            password=password,
            password_confirm=password,
            full_name=fake.name(),
            age=random.randint(18, 25),
            phone="+7" + "".join(random.choice(string.digits) for _ in range(10)),
        )
        self.client.post(f"{self.base_url}/signup", data=user_in.json())
