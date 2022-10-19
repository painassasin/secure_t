import logging

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from backend.core.context_vars import SESSION
from backend.core.database import async_session


logger = logging.getLogger(__name__)


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = JSONResponse(
            content={'error': 'Something went wrong'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

        async with async_session() as db_session:

            SESSION.set(db_session)
            try:
                response = await call_next(request)
                await db_session.commit()
            except Exception as e:  # pragma: no cover
                logger.debug(e)
                await db_session.rollback()
            finally:
                await db_session.close()
                SESSION.set(None)
                return response
