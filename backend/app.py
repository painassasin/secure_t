from logging.config import dictConfig

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.auth.api import router as auth_router
from backend.blog.api import router as blog_router
from backend.core import settings
from backend.core.exceptions import BaseAppException
from backend.core.logging.config import log_config
from backend.core.middleware import SessionMiddleware


dictConfig(log_config)


async def health_check():
    return JSONResponse({'status': 'ok'})


async def base_app_exception_handler(request: Request, exc: BaseAppException):
    return JSONResponse(status_code=exc.status_code, content={'error': exc.message}, headers=exc.headers)


def create_app() -> FastAPI:
    app = FastAPI(debug=settings.DEBUG)

    app.add_middleware(SessionMiddleware)

    app.exception_handler(BaseAppException)(base_app_exception_handler)

    app.add_api_route('/ping/', health_check, methods=['GET'], include_in_schema=False)
    app.include_router(auth_router)
    app.include_router(blog_router)

    return app
