from starlette import status

from backend.core.exceptions import BaseAppException


class InvalidCredentials(BaseAppException):
    message = 'Invalid username or password'
    status_code = status.HTTP_401_UNAUTHORIZED
    headers = {'WWW-Authenticate': 'Bearer'}


class UserAlreadyExists(BaseAppException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'The user with this username already exists'
