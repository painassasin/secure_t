from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.schemas import User


SESSION: ContextVar[AsyncSession | None] = ContextVar('SESSION', default=None)
USER: ContextVar[User | None] = ContextVar('USER', default=None)
