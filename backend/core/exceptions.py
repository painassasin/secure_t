from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse


class BaseAppException(Exception):
    message: str = 'Something went wrong'
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, *args):
        if args:
            self.message = str(args[0])


class BadRequest(BaseAppException):
    status_code: int = status.HTTP_400_BAD_REQUEST


class Forbidden(BaseAppException):
    status_code: int = status.HTTP_403_FORBIDDEN


async def base_app_exception_handler(request: Request, exc: BaseAppException):
    return JSONResponse(status_code=exc.status_code, content={'error': exc.message})
