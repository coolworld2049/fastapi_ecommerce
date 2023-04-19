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
    def test_read_users(self):
        range_ = [0, random.randint(2, 50)]

        with self.rest(
            "GET",
            f'/api/v1/users/?range=[{range_[0]},{range_[1]}]',
        ) as resp:
            if resp.js is None:
                resp.failure(resp.text)
