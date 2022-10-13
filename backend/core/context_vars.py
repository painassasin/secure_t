from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession


SESSION: ContextVar[AsyncSession | None] = ContextVar('SESSION', default=None)
