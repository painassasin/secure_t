from typing import AsyncGenerator

import sqlalchemy as sa
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.core import settings


Base = declarative_base()

async_engine = create_async_engine(settings.DATABASE_URI, echo=settings.POSTGRES_DB_ECHO, future=True)
async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except DBAPIError:
            await session.rollback()
            raise
        finally:
            await session.close()


class TimestampMixin:
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
