import random
import string

from pydantic import EmailStr


def random_lower_string(n=32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=n))


def random_email(st: str = None) -> EmailStr:
    return EmailStr(
        f"{random_lower_string() if not st else f'{st}_{random_lower_string(6)}'}@gmail.com"
    )


def gen_random_password():
    length = 10
    return (
        f"{''.join(random.choice(string.ascii_letters) for _ in range(length)).capitalize()}"
        f"{random.choice(string.ascii_uppercase)}"
        f"{random.randint(0, 9)}"
        f"{random.choice('@$!%*?&')}"
    )
