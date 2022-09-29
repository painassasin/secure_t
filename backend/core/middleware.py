from fastapi.openapi.models import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

from backend.core.common import SESSION
from backend.core.database import get_session


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        db_session = await anext(get_session())
        SESSION.set(db_session)
        response = await call_next(request)
        SESSION.set(None)
        return response
