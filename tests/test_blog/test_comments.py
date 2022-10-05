import pytest
from sqlalchemy import func, select

from backend.blog.models import Post


@pytest.mark.asyncio
class TestCreateComment:
    url = '/comments/'

    async def test_auth_required(self, async_client):
        response = await async_client.post(self.url.format(post_id=1), json={'text': 'new_comment'})
        assert response.status_code == 401

    async def test_post_not_found(self, async_client, async_session, create_user):
        assert not (await async_session.execute(select(func.count(Post.id)))).scalar()

        token, _ = await create_user('user', 'password')

        response = await async_client.post(
            url=self.url,
            json={'text': 'new_comment', 'parent_id': 1},
            headers={'Authorization': token}
        )
        assert response.status_code == 400

    @pytest.mark.parametrize('increase', [1, 2])
    async def test_invalid_parent_id(self, async_client, create_post, create_user, increase, async_session):
        token, user = await create_user('user', 'password')
        post = await create_post('post', owner_id=user.id)

        assert (await async_session.execute(select(func.count(Post.id)))).scalar() == 1

        response = await async_client.post(
            url=self.url,
            json={'text': 'new_comment', 'parent_id': post.id + increase},
            headers={'Authorization': token}
        )
        assert response.status_code == 400

        assert (await async_session.execute(select(func.count(Post.id)))).scalar() == 1

    async def test_success(self, async_client, create_post, create_user, async_session):
        token, user = await create_user('user', 'password')
        post = await create_post('post', owner_id=user.id)

        response = await async_client.post(
            url=self.url,
            json={'text': 'new_comment', 'parent_id': post.id},
            headers={'Authorization': token}
        )
        assert response.status_code == 201

        new_comment: Post = (await async_session.execute(select(Post).filter(Post.text == 'new_comment'))).scalar_one()
        assert response.json() == {
            'id': new_comment.id,
            'created_at': new_comment.created_at.isoformat(),
            'owner_id': user.id,
            'text': new_comment.text,
            'parent_id': post.id,
        }
