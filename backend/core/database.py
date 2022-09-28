from asyncio import current_task
from typing import AsyncGenerator

import sqlalchemy as sa
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.core import settings


Base = declarative_base()

engine = create_async_engine(
    settings.DATABASE_URI,
    echo=settings.POSTGRES_DB_ECHO,
    future=True,
    json_serializer=jsonable_encoder,
)

async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
AsyncScopedSession = async_scoped_session(async_session_factory, scopefunc=current_task)


async def get_db() -> AsyncGenerator:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class TimestampMixin:
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False)
