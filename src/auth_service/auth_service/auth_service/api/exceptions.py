from fastapi import HTTPException, status


class DuplicateUserException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists",
        )


class InactiveUserException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )


class AccountNotVerifiedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not verified",
        )


class InvalidVerificationTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid verification token or account already verified",
        )


class CouldNotValidateCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class AccessTokenHasExpiredException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired",
        )


class PermissionDeniedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
