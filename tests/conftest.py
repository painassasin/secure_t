import asyncio
from typing import Type, TypeVar
from unittest.mock import AsyncMock, patch

import asyncpg
import pytest
import pytest_asyncio
from asyncpg import Connection
from httpx import AsyncClient
from pydantic import PostgresDsn
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, AsyncTransaction, create_async_engine
from sqlalchemy.orm import Session, SessionTransaction, sessionmaker

from backend.app import create_app
from backend.auth.schemas import UserInDB
from backend.core import settings
from backend.core.context_vars import SESSION
from backend.core.security import create_access_token, get_password_hash
from backend.models import Base, User


T = TypeVar('T', bound=Base)


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def app():
    return create_app()


@pytest.fixture(scope='session')
def database_url() -> str:
    return PostgresDsn.build(
        scheme='postgresql+asyncpg',
        user=settings.DB.USER,
        password=settings.DB.PASSWORD,
        host=settings.DB.HOST,
        path=f'/{settings.DB.DB_TEST}',
    )


@pytest.fixture(scope='session')
def test_engine(database_url) -> AsyncEngine:
    engine = create_async_engine(database_url, echo=True)
    yield engine
    engine.sync_engine.dispose()


@pytest_asyncio.fixture
async def async_session(test_engine):
    async with test_engine.connect() as conn:
        trans: AsyncTransaction = await conn.begin()

        async with sessionmaker(
            bind=conn, expire_on_commit=False, class_=AsyncSession
        )() as db_session:
            nested: AsyncTransaction = await conn.begin_nested()

            @event.listens_for(db_session.sync_session, 'after_transaction_end')
            def end_savepoint(session: Session, transaction: SessionTransaction):
                if not nested.is_active:
                    conn.sync_connection.begin_nested()

            yield db_session

        await trans.rollback()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def make_migrations(test_engine):
    sync_conn: Connection = await asyncpg.connect(
        host=settings.DB.URI.host,
        user=settings.DB.URI.user,
        password=settings.DB.URI.password,
        database=settings.DB.URI.path.lstrip('/'),
    )
    await sync_conn.execute(f'DROP DATABASE IF EXISTS {settings.DB.DB_TEST}')
    await sync_conn.execute(f'CREATE DATABASE {settings.DB.DB_TEST}')
    await sync_conn.close()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await test_engine.dispose()


@pytest.fixture(autouse=True)
def mock_session_middleware(async_session):
    with patch('backend.core.middleware.async_session') as mock:
        mock.return_value = AsyncMock(
            __aenter__=AsyncMock(return_value=async_session),
            __aexit__=AsyncMock(return_value=None)
        )
        yield mock


@pytest_asyncio.fixture
async def async_client(app) -> AsyncClient:
    async with AsyncClient(app=app, base_url='http://0.0.0.0') as ac:
        yield ac


@pytest.fixture
def create_obj_in_db(async_session: AsyncSession):
    async def _create_obj_in_db(obj: T) -> T:
        values = vars(obj)
        values.pop('_sa_instance_state')

        obj_class: Type[T] = obj.__class__
        cursor: CursorResult = await async_session.execute(
            insert(obj_class).values(**values).returning(obj_class)
        )
        await async_session.commit()
        return obj_class(**cursor.mappings().one())

    return _create_obj_in_db


@pytest.fixture
def set_session(async_session):
    SESSION.set(async_session)
    yield
    SESSION.set(None)


@pytest.fixture
def create_user(create_obj_in_db):
    async def _create_user(username: str, password: str) -> tuple[str, UserInDB]:
        user = UserInDB.from_orm(await create_obj_in_db(
            obj=User(username=username, password=get_password_hash(password))
        ))
        access_token: str = create_access_token(username=user.username)
        return f'Bearer {access_token}', user

    return _create_user
