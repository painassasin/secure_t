import time

from fastapi.openapi.models import Response
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp

from backend.core.common import SESSION
from backend.core.database import get_session


class ProcessTimeMiddleware(BaseHTTPMiddleware):

    def __init__(
        self, app: ASGIApp, use: bool, dispatch: DispatchFunction | None = None
    ) -> None:
        self.app = app
        self.dispatch_func = self.dispatch if dispatch is None else dispatch
        super().__init__(app, dispatch)
        self.use = use

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if self.use:
            start_time = time.time()
            response = await call_next(request)
            response.headers['X-Process-Time'] = '%.4f' % (time.time() - start_time)
        else:
            response = await call_next(request)
        return response


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        db_session = await anext(get_session())
        SESSION.set(db_session)
        response = await call_next(request)
        SESSION.set(None)
        return response
