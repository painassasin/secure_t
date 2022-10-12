from typing import Any

from starlette import status


class BaseAppException(Exception):
    message: str = 'Something went wrong'
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    headers: dict[str, Any] = {}

    def __init__(self, *args):
        if args:
            self.message = str(args[0])


class BadRequest(BaseAppException):
    status_code: int = status.HTTP_400_BAD_REQUEST


class Forbidden(BaseAppException):
    status_code: int = status.HTTP_403_FORBIDDEN
