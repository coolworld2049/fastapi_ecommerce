import random  # noqa
import string
import uuid  # noqa

from locust import task, FastHttpUser, between
from locust.runners import logger  # noqa


def rnd_str(n=24):
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(n))


class RWUser(FastHttpUser):
    wait_time = between(3, 5)

    # @task
    # def test_read_users(self):
    #     low = random.randint(2, 100)
    #     high = random.randint(2, 100)
    #     pair = [low, high]
    #     if pair[0] == pair[1]:
    #         pair = abs(pair[0] - 1), pair[1]
    #     pair.sort()
    #     with self.rest(
    #         "GET",
    #         f"""/api/v1/users/?range=[{pair[0]},{pair[1]}]
    #         &sort=["id","ASC"]""",
    #     ) as resp:
    #         if resp.js is None:
    #             pass
    #         else:
    #             logger.error(f"{resp.headers} {resp.js}")

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
                pass
            elif not resp.js.get("email"):
                logger.error(f"{resp.headers} {resp.js}")
