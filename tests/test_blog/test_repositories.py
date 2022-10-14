import pytest
from sqlalchemy import func, select

from tests.base import BaseRepoTest

from backend.blog.repositories import InvalidPostId
from backend.core.container import post_repository
from backend.models import Post


@pytest.mark.asyncio
class TestPostRepository(BaseRepoTest):

    async def test_create_post_invalid_parent_id(self, async_session, create_user):
        _, user = await create_user(username='username', password='password')
        with pytest.raises(InvalidPostId):
            await post_repository.create_post(owner_id=user.id, text='text', parent_id=10)
        assert not (await async_session.execute(select(func.count(Post.id)))).scalar()

    async def test_create_post_refers_itself(self, async_session, create_user, create_post):
        _, user = await create_user(username='username', password='password')
        post = await create_post(owner_id=user.id, text='text1')
        with pytest.raises(InvalidPostId):
            await post_repository.create_post(owner_id=user.id, text='text2', parent_id=post.id + 1)
        assert (await async_session.execute(select(func.count(Post.id)))).scalar() == 1

    async def test_create_post_user_not_found(self, async_session, create_user, create_post):
        _, user = await create_user(username='username', password='password')
        post = await create_post(owner_id=user.id, text='text1')
        with pytest.raises(InvalidPostId):
            await post_repository.create_post(owner_id=100, text='text2', parent_id=post.id)
        assert (await async_session.execute(select(func.count(Post.id)))).scalar() == 1

    async def test_update_post(self, async_session, create_user, create_post):
        _, user = await create_user(username='username', password='password')
        post = await create_post(owner_id=user.id, text='text1')
        await post_repository.update_post(post_id=post.id, text='text2')

        updated_post = (await async_session.execute(select(Post))).scalar_one()
        assert updated_post.text == 'text2'
        assert updated_post.updated_at != post.updated_at

    async def test_delete_post(self, async_session, create_user, create_post):
        _, user = await create_user(username='username', password='password')
        post = await create_post(owner_id=user.id, text='text')
        assert (await async_session.execute(select(func.count(Post.id)))).scalar() == 1

        await post_repository.delete_post(post_id=post.id)
        assert not (await async_session.execute(select(func.count(Post.id)))).scalar()
