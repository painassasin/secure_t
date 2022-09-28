import time

from fastapi.openapi.models import Response
from starlette.requests import Request

from backend.core import settings
from backend.core.common import SESSION
from backend.core.database import get_db


async def add_process_time_header(request: Request, call_next) -> Response:
    if settings.PROCESS_TIME:
        start_time = time.time()
        response = await call_next(request)
        response.headers['X-Process-Time'] = '%.4f' % (time.time() - start_time)
    else:
        response = await call_next(request)
    return response


async def set_session(request: Request, call_next) -> Response:
    db_session = await anext(get_db())
    SESSION.set(db_session)
    response = await call_next(request)
    SESSION.set(None)
    return response
