import logging
from logging.config import dictConfig

from fastapi import FastAPI
from starlette.responses import JSONResponse

from backend.auth.api import auth_router, users_router
from backend.blog.api import router as blog_router
from backend.core import settings
from backend.core.logging import log_config
from backend.core.middleware import add_process_time_header, set_session


async def health_check():
    return JSONResponse({'status': 'ok'})


class HealthCheckFilter(logging.Filter):

    def filter(self, record) -> bool:
        return record.getMessage().find('/ping/') == -1


dictConfig(log_config)

logging.getLogger('uvicorn.access').addFilter(HealthCheckFilter())

app = FastAPI(debug=settings.DEBUG)

app.middleware('http')(add_process_time_header)
app.middleware('http')(set_session)

app.add_api_route('/ping/', health_check, methods=['GET'], include_in_schema=False)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(blog_router)
