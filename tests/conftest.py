import asyncio
from datetime import datetime
from typing import TypeVar
from unittest.mock import AsyncMock, Mock, patch

import asyncpg
import pytest
import pytest_asyncio
from httpx import AsyncClient
from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.app import app
from backend.auth.models import User
from backend.auth.schemas import TokenData, UserInDB
from backend.auth.utils import get_access_token, get_password_hash
from backend.core.config import AppSettings
from backend.core.context_vars import SESSION
from backend.core.database import TimestampMixin
from backend.models import Base


settings = AppSettings()

T = TypeVar('T')


@pytest.fixture(scope='session')
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope='session')
def test_db_name():
    return f'{settings.POSTGRES_DB}_test'


@pytest.fixture(scope='session')
def test_engine(test_db_name):
    test_dsn = PostgresDsn.build(
        scheme='postgresql+asyncpg',
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        path=f'/{test_db_name}',
    )
    return create_async_engine(test_dsn, echo=True)


@pytest_asyncio.fixture
async def async_session(test_engine):
    session_maker = sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as db_session:
        db_session.begin = Mock(
            return_value=Mock(
                __aenter__=AsyncMock(),
                __aexit__=AsyncMock(return_value=None)
            )
        )
        db_session.commit = AsyncMock()
        db_session.close = AsyncMock()
        SESSION.set(db_session)

        yield db_session
        await db_session.rollback()
        SESSION.set(None)


@pytest_asyncio.fixture(scope='session', autouse=True)
async def make_migrations(test_db_name, test_engine):
    conn = await asyncpg.connect(
        host=settings.POSTGRES_HOST,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
    )
    await conn.execute(f'DROP DATABASE IF EXISTS {test_db_name}')
    await conn.execute(f'CREATE DATABASE {test_db_name}')
    await conn.close()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(autouse=True)
def mock_session_middleware(async_session):
    with patch('backend.core.middleware.async_session') as mock:
        mock.return_value = AsyncMock(
            __aenter__=AsyncMock(return_value=async_session),
            __aexit__=AsyncMock(return_value=None)
        )
        yield mock


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url='http://0.0.0.0') as ac:
        yield ac


@pytest.fixture()
def create_obj_in_db(async_session):
    async def _create_obj_in_db(obj: T) -> T:
        if isinstance(obj, TimestampMixin):
            now = datetime.utcnow()
            obj.created_at = now
            obj.updated_at = now
        async_session.add(obj)
        await async_session.flush()
        await async_session.refresh(obj)
        return obj

    return _create_obj_in_db


@pytest.fixture
def create_user(create_obj_in_db):
    async def _create_user(username: str, password: str) -> tuple[str, UserInDB]:
        user = UserInDB.from_orm(await create_obj_in_db(
            obj=User(username=username, password=get_password_hash(password))
        ))
        access_token: str = get_access_token(token_data=TokenData.parse_obj(user))
        return f'Bearer {access_token}', user

    return _create_user
