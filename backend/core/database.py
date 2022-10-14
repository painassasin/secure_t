from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.core import settings


async_engine = create_async_engine(settings.DB.URI, echo=settings.DB.SQL_ECHO)
async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


class TimestampMixin:
    created_at = Column(DateTime, server_default=func.statement_timestamp(), nullable=False)
    updated_at = Column(DateTime, server_default=func.statement_timestamp(), onupdate=func.now(), nullable=False)

    # Если сделать несколько изменений в одной транзакции, они все будут иметь одну и ту же метку времени.
    # Это потому, что стандарт SQL указывает, что CURRENT_TIMESTAMP возвращает значения,
    # основанные на начале транзакции.
    # PG обеспечивает не-SQL стандарта statement_timestamp() и clock_timestamp(),
    # которые меняются в рамках транзакции.
    # Документы здесь:
    # https://www.postgresql.org/docs/current/static/functions-datetime.html#FUNCTIONS-DATETIME-CURRENT
