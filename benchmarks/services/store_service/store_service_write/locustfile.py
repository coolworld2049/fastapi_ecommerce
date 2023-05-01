import random  # noqa
import string
import uuid  # noqa

from locust import task, FastHttpUser
from locust.runners import logger  # noqa


def rnd_str(n=24):
    return "".join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(n)
    )


class RWUser(FastHttpUser):
    @task
    def test_create_product(self):
        full_name = rnd_str(random.randint(5, 18))
        json = {
            "name": rnd_str(128),
            "description": rnd_str(64),
        }
        with self.rest(
            "POST",
            "/api/v1/categories",
            json=json,
        ) as resp:
            pass
