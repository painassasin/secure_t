import pytest
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from backend.blog.models import Post
from backend.blog.schemas import PostInDB


@pytest.fixture
def create_post(async_session: AsyncSession):
    async def _create_post(text: str, owner_id: int) -> PostInDB:
        cursor: CursorResult = await async_session.execute(
            insert(Post).values(text=text, owner_id=owner_id).returning(Post)
        )
        await async_session.commit()
        return PostInDB.parse_obj(cursor.mappings().one())

    return _create_post


@pytest.fixture
def create_comment(async_session: AsyncSession):
    async def _create_comment(text: str, owner_id: int, parent_id: int) -> PostInDB:
        cursor: CursorResult = await async_session.execute(
            insert(Post).values(text=text, owner_id=owner_id, parent_id=parent_id).returning(Post)
        )
        await async_session.commit()
        return PostInDB.parse_obj(cursor.mappings().one())

    return _create_comment
