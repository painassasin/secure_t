from logging.config import dictConfig

from fastapi import FastAPI
from starlette.responses import JSONResponse

from backend.auth.api import auth_router, users_router
from backend.blog.api import comments_router, posts_router
from backend.core.config import AppSettings
from backend.core.logging.config import log_config
from backend.core.middleware import SessionMiddleware


async def health_check():
    return JSONResponse({'status': 'ok'})


dictConfig(log_config)

settings = AppSettings()

app = FastAPI(debug=settings.DEBUG)

app.add_middleware(SessionMiddleware)

app.add_api_route('/ping/', health_check, methods=['GET'], include_in_schema=False)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(comments_router)
app.include_router(posts_router)
