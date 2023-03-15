import random
import string
from datetime import datetime

import faker_commerce
from faker import Faker


class RandomDateTime:
    def __init__(
        self,
        year: list[int, int] = None,
        month: list[int, int] = None,
        day: list[int, int] = None,
    ):
        self.year = year
        self.month = month
        self.day = day

    def datetime(self, now_dt: datetime = datetime.now()):
        data = {
            "year": random.choice(self.year) if self.year else None,
            "month": random.choice(self.month) if self.month else None,
            "day": random.choice(self.day) if self.day else None,
        }
        items = dict(
            filter(  # noqa
                lambda it: it[1] is not None and isinstance(it[1], int),
                data.items(),
            )
        )
        return now_dt.replace(**items)


def rnd_string(length=24):
    return "".join(
        [random.choice(string.ascii_letters) for _ in range(length)]
    )


def rnd_password():
    length = 10
    return (
        f"{''.join(random.choice(string.ascii_letters) for _ in range(length)).capitalize()}"
        f"{random.choice(string.ascii_uppercase)}"
        f"{random.randint(0, 9)}"
        f"{random.choice('@$!%*?&')}"
    )


fake = Faker()
fake.add_provider(faker_commerce.Provider)
