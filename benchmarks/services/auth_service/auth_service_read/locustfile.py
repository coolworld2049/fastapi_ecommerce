import os
import random  # noqa
import string
import uuid  # noqa

from locust import FastHttpUser, task
from locust.runners import logger  # noqa


def rnd_str(n=24):
    return "".join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(n)
    )

class Base(FastHttpUser):
    @task
    def read_users(self):
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
        }
        range_ = [0, random.randint(2, 50)]
        with self.rest(
            "GET",
            f"/api/v1/users/?range=[{range_[0]},{range_[1]}]",
            headers=headers if os.getenv('API_TOKEN') else None
        ) as resp:
            pass
