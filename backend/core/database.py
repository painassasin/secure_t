import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.core import settings


async_engine = create_async_engine(settings.DB.URI, echo=settings.DB.SQL_ECHO)
async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


class TimestampMixin:
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
