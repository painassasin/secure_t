from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession


SESSION: ContextVar[AsyncSession | None] = ContextVar('SESSION', default=None)


class BaseRepository:

    @property
    def session(self) -> AsyncSession:
        if _session := SESSION.get():
            return _session
        raise RuntimeError
