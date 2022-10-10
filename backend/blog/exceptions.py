from starlette import status

from backend.core.exceptions import BaseAppException


class PostNotFound(BaseAppException):
    message = 'Post not found'
    status_code = status.HTTP_404_NOT_FOUND
