import re
from difflib import SequenceMatcher
from typing import Any

from prisma.models import User
from prisma.partials import UserCreate, UserUpdate, UserCreateOpen, UserUpdateMe
from starlette.exceptions import HTTPException
from uvicorn.main import logger

password_exp = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
password_conditions = (
    "Minimum 8 characters, at least one uppercase letter, one lowercase letter, one number and one "
    "special character"
)
username_exp = "[A-Za-z_0-9]*"


class UserValidator:
    def __init__(self, user: Any | User):
        if isinstance(user, dict):
            self.user = UserCreate(**user)
        else:
            self.user = user

    def _check_password_strongness(self):
        def values_match_ratio(a, b):
            return SequenceMatcher(None, a, b).ratio() if a and b else None

        if self.user.email and self.user.username and self.user.password:
            username_password_match: float = values_match_ratio(
                self.user.username,
                self.user.password,
            )
            assert username_password_match < 0.5, "Password must not match username"

            email_password_match: float = values_match_ratio(
                self.user.email.split("@")[0],
                self.user.password,
            )
            assert email_password_match < 0.5, "Password must not match email"

    def _validate_email(self):
        if self.user.email:
            assert self.user.email.find("@") != -1, "email invalid"

    def _validate_username(self):
        if self.user.username:
            assert re.match(
                username_exp,
                self.user.username,
            ), "Invalid characters in username"

    def _validate_password(self):
        if self.user.password:
            assert re.match(
                password_exp, self.user.password, flags=re.M
            ), password_conditions

    def validate(self):
        try:
            self._validate_email()
            self._validate_password()
            self._validate_username()
            self._check_password_strongness()
            return self.user
        except AssertionError as e:
            logger.error(e.args)
            raise HTTPException(status_code=402, detail=str(*e.args))
