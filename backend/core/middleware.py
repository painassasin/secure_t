from fastapi.openapi.models import Response
from sqlalchemy.exc import DBAPIError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

from backend.core.context_vars import SESSION
from backend.core.database import async_session


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        async with async_session() as db_session:
            SESSION.set(db_session)
            try:
                return await call_next(request)
            except DBAPIError:  # pragma: no cover
                await db_session.rollback()
                raise
            finally:
                await db_session.close()
                SESSION.set(None)
