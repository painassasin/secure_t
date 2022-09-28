import logging
from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.schemas import User


SESSION: ContextVar[AsyncSession | None] = ContextVar('SESSION', default=None)
USER: ContextVar[User | None] = ContextVar('USER', default=None)


class BaseRepository:
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    @property
    def _db_session(self) -> AsyncSession:
        if _session := SESSION.get():
            return _session
        raise RuntimeError
