import random  # noqa
import string
import uuid  # noqa

from locust import task, FastHttpUser, between
from locust.runners import logger  # noqa


def rnd_str(n=24):
    return "".join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(n)
    )


class RWUser(FastHttpUser):
    wait_time = between(3, 5)

    @task
    def test_signup_client(self):
        full_name = rnd_str(random.randint(5, 18))
        json = {
            "full_name": full_name,
            "email": f"{rnd_str()}@{rnd_str()}.com",
            "username": rnd_str(),
            "password": full_name,
            "password_confirm": full_name,
        }
        with self.rest(
            "POST",
            "/api/v1/signup/client",
            json=json,
        ) as resp:
            if resp.js is None:
                resp.failure(resp.text)
