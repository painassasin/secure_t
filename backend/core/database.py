import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.core.config import AppSettings


settings = AppSettings()

Base = declarative_base()

async_engine = create_async_engine(settings.DATABASE_URI, echo=settings.POSTGRES_DB_ECHO, future=True)
async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


class TimestampMixin:
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
