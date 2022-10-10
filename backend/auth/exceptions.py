from starlette import status

from backend.core.exceptions import BaseAppException


class InvalidCredentials(BaseAppException):
    message = 'Invalid username or password'
    status_code = status.HTTP_401_UNAUTHORIZED
