import asyncio
from typing import Coroutine, Generator

import pytest
import pytest_asyncio
import sqlalchemy as sa
from httpx import AsyncClient
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app import app
from backend.auth.models import User
from backend.auth.schemas import TokenData, UserInDB
from backend.auth.utils import get_access_token, get_password_hash
from backend.core.database import async_engine
from backend.core.database import async_session as async_session_maker
from backend.models import Base


@pytest.fixture(scope='session')
def event_loop():
    return asyncio.get_event_loop()


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url='http://0.0.0.0') as ac:
        yield ac


@pytest_asyncio.fixture(scope='session', autouse=True)
async def make_migrations():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture
async def async_session():
    async with async_session_maker() as db_session:
        try:
            yield db_session
        except DBAPIError:
            await db_session.rollback()
            raise
        finally:
            await db_session.close()


@pytest_asyncio.fixture(autouse=True)
async def delete_data():
    async with async_engine.begin() as conn:
        tasks: Generator[Coroutine] = (
            conn.execute(sa.text(f'DELETE FROM {table_name}'))
            for table_name in ['posts', 'users']
        )
        await asyncio.gather(*tasks)


@pytest.fixture
def create_user(async_session: AsyncSession):
    async def _create_user(username: str, password: str) -> tuple[str, UserInDB]:
        cursor: CursorResult = await async_session.execute(
            insert(User).values(username=username, password=get_password_hash(password)).returning(User)
        )
        user: UserInDB = UserInDB.parse_obj(cursor.mappings().one())
        await async_session.commit()
        access_token: str = get_access_token(token_data=TokenData.parse_obj(user))
        return f'Bearer {access_token}', user

    return _create_user
