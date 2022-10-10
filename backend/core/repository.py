import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.context_vars import SESSION


class BaseRepository:
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    @property
    def _db_session(self) -> AsyncSession:
        if _session := SESSION.get():
            return _session
        raise RuntimeError  # pragma: no cover
