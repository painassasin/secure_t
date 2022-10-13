import pytest

from backend.blog.schemas import PostInDB
from backend.models import Post


@pytest.fixture
def create_post(create_obj_in_db):
    async def _create_post(text: str, owner_id: int) -> PostInDB:
        return PostInDB.from_orm(await create_obj_in_db(
            obj=Post(text=text, owner_id=owner_id)
        ))

    return _create_post


@pytest.fixture
def create_comment(create_obj_in_db):
    async def _create_comment(text: str, owner_id: int, parent_id: int) -> PostInDB:
        return PostInDB.from_orm(await create_obj_in_db(
            obj=Post(text=text, owner_id=owner_id, parent_id=parent_id)
        ))

    return _create_comment
