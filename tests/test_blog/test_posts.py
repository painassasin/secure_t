import pytest
from sqlalchemy import func, select

from backend.blog.models import Post
from backend.blog.schemas import PostInDB


@pytest.mark.asyncio
class TestCreatePost:
    url = '/posts/'

    async def test_auth_required(self, async_client):
        response = await async_client.post(self.url, json={'text': 'new_post'})
        assert response.status_code == 401

    async def test_success(self, async_client, create_user, async_session):
        token, user = await create_user('user_1', 'password')
        response = await async_client.post(
            url=self.url,
            json={'text': 'new_post'},
            headers={'Authorization': token}
        )
        assert response.status_code == 201
        new_post: Post = (await async_session.execute(select(Post))).scalar_one()
        assert new_post.parent_id is None
        assert new_post.post_id is None
        assert response.json() == {
            'id': new_post.id,
            'created_at': new_post.created_at.isoformat(),
            'owner_id': user.id,
            'text': 'new_post'
        }


@pytest.mark.asyncio
class TestGetAllPosts:
    url = '/posts/'

    async def test_without_comments_belongs_current_user(self, create_user, create_post, async_client):
        _, user = await create_user('user', 'password')
        posts: list[PostInDB] = [
            await create_post(text=f'post_{i}', owner_id=user.id)
            for i in range(3)
        ]
        response = await async_client.get(self.url, params={'limit': 2})
        assert response.status_code == 200
        assert response.json() == {
            'limit': 2,
            'offset': 0,
            'total': len(posts),
            'items': [
                {
                    'id': posts[-1].id,
                    'text': posts[-1].text,
                    'created_at': posts[-1].created_at.isoformat(),
                    'comments_count': 0,
                    'owner': {'id': user.id, 'username': user.username}
                },
                {
                    'id': posts[-2].id,
                    'text': posts[-2].text,
                    'created_at': posts[-2].created_at.isoformat(),
                    'comments_count': 0,
                    'owner': {'id': user.id, 'username': user.username}
                },
            ]
        }

    async def test_without_comments_belongs_different_users(self, create_user, create_post, async_client):
        _, user_1 = await create_user('user_1', 'password')
        _, user_2 = await create_user('user_2', 'password')

        post_1 = await create_post(text='post_1', owner_id=user_1.id)
        post_2 = await create_post(text='post_2', owner_id=user_2.id)

        response = await async_client.get(self.url)
        assert response.status_code == 200
        assert response.json() == {
            'limit': 10,
            'offset': 0,
            'total': 2,
            'items': [
                {
                    'id': post_2.id,
                    'text': post_2.text,
                    'created_at': post_2.created_at.isoformat(),
                    'comments_count': 0,
                    'owner': {'id': user_2.id, 'username': user_2.username}
                },
                {
                    'id': post_1.id,
                    'text': post_1.text,
                    'created_at': post_1.created_at.isoformat(),
                    'comments_count': 0,
                    'owner': {'id': user_1.id, 'username': user_1.username}
                },
            ]
        }


@pytest.mark.asyncio
class TestGetPostDescription:
    url = '/posts/{post_id}/'

    async def test_post_without_comments(self, create_user, create_post, async_client):
        _, user = await create_user('user', 'password')

        post = await create_post(text='post', owner_id=user.id)
        response = await async_client.get(self.url.format(post_id=post.id))
        assert response.status_code == 200
        assert response.json() == {
            'id': post.id,
            'text': post.text,
            'created_at': post.created_at.isoformat(),
            'comments_count': 0,
            'owner': {'id': user.id, 'username': user.username},
            'comments': []
        }

    async def test_post_with_comments(self, create_user, create_post, create_comment, async_client):
        """
        post
         |_ comment_1
            |_ comment 2
         |_ comment_3
             |_ comment_4
                |_ comment 5
             |_ comment_6
        """
        _, user_1 = await create_user('user_1', 'password')
        _, user_2 = await create_user('user_2', 'password')

        post = await create_post(text='post', owner_id=user_1.id)
        comment_1 = await create_comment(text='comment_1', owner_id=user_2.id, parent_id=post.id, post_id=post.id)
        comment_2 = await create_comment(text='comment_2', owner_id=user_1.id, parent_id=comment_1.id, post_id=post.id)
        comment_3 = await create_comment(text='comment_3', owner_id=user_2.id, parent_id=post.id, post_id=post.id)
        comment_4 = await create_comment(text='comment_4', owner_id=user_1.id, parent_id=comment_3.id, post_id=post.id)
        comment_5 = await create_comment(text='comment_5', owner_id=user_2.id, parent_id=comment_4.id, post_id=post.id)
        comment_6 = await create_comment(text='comment_6', owner_id=user_1.id, parent_id=comment_3.id, post_id=post.id)

        response = await async_client.get(self.url.format(post_id=post.id))
        assert response.status_code == 200
        assert response.json() == {
            'id': post.id,
            'text': post.text,
            'created_at': post.created_at.isoformat(),
            'comments_count': 6,
            'owner': {'id': user_1.id, 'username': user_1.username},
            'comments': [
                {
                    'id': comment_3.id,
                    'created_at': comment_3.created_at.isoformat(),
                    'owner': {'id': user_2.id, 'username': user_2.username},
                    'text': comment_3.text,
                    'comments': [
                        {
                            'id': comment_6.id,
                            'created_at': comment_6.created_at.isoformat(),
                            'text': comment_6.text,
                            'owner': {'id': user_1.id, 'username': user_1.username},
                            'comments': []
                        },
                        {
                            'id': comment_4.id,
                            'created_at': comment_4.created_at.isoformat(),
                            'text': comment_4.text,
                            'owner': {'id': user_1.id, 'username': user_1.username},
                            'comments': [
                                {
                                    'id': comment_5.id,
                                    'created_at': comment_5.created_at.isoformat(),
                                    'text': comment_5.text,
                                    'owner': {'id': user_2.id, 'username': user_2.username},
                                    'comments': []
                                }
                            ]
                        }
                    ]
                },
                {
                    'id': comment_1.id,
                    'created_at': comment_1.created_at.isoformat(),
                    'owner': {'id': user_2.id, 'username': user_2.username},
                    'text': comment_1.text,
                    'comments': [
                        {
                            'id': comment_2.id,
                            'created_at': comment_2.created_at.isoformat(),
                            'text': comment_2.text,
                            'owner': {'id': user_1.id, 'username': user_1.username},
                            'comments': []
                        }
                    ]
                }
            ]
        }


@pytest.mark.asyncio
class TestUpdatePost:
    url = '/posts/{post_id}/'

    async def test_not_owner(self, create_user, create_post, async_client):
        _, user_1 = await create_user('user_1', 'password')
        token, user_2 = await create_user('user_2', 'password')

        post = await create_post(text='post', owner_id=user_1.id)

        response = await async_client.patch(
            url=self.url.format(post_id=post.id),
            json={'text': 'new_post'},
            headers={'Authorization': token}
        )
        assert response.status_code == 403

    async def test_post_not_found(self, create_user, async_client):
        token, user_1 = await create_user('user', 'password')

        response = await async_client.patch(
            url=self.url.format(post_id=1),
            json={'text': 'new_post'},
            headers={'Authorization': token}
        )
        assert response.status_code == 404

    async def test_success(self, create_user, create_post, async_client):
        token, user = await create_user('user', 'password')

        post = await create_post(text='post', owner_id=user.id)

        response = await async_client.patch(
            url=self.url.format(post_id=post.id),
            json={'text': 'new_post'},
            headers={'Authorization': token}
        )

        assert response.status_code == 200
        assert response.json() == {
            'id': post.id,
            'created_at': post.created_at.isoformat(),
            'owner_id': user.id,
            'text': 'new_post'
        }


@pytest.mark.asyncio
class TestDeletePost:
    url = '/posts/{post_id}/'

    async def test_post_not_found(self, create_user, async_client, async_session):
        token, user = await create_user('user', 'password')

        assert not (await async_session.execute(select(func.count(Post.id)))).scalar()

        response = await async_client.delete(
            url=self.url.format(post_id=1),
            headers={'Authorization': token}
        )
        assert response.status_code == 404

    async def test_not_owner(self, create_user, create_post, async_client, async_session):
        _, user_1 = await create_user('user_1', 'password')
        token, user_2 = await create_user('user_2', 'password')

        post = await create_post(text='post', owner_id=user_1.id)

        response = await async_client.delete(
            url=self.url.format(post_id=post.id),
            headers={'Authorization': token}
        )
        assert response.status_code == 403
        assert (await async_session.execute(select(func.count(Post.id)))).scalar() == 1

    @pytest.mark.parametrize('with_comments', [False, True], ids=['without comments', 'with comments'])
    async def test_success(self, create_user, create_post, create_comment, async_client, async_session, with_comments):
        token, user = await create_user('user', 'password')

        post = await create_post(text='post', owner_id=user.id)

        if with_comments:
            _, user2 = await create_user('user2', 'password')
            comment_1 = await create_comment(text='comment_1', owner_id=user2.id, parent_id=post.id, post_id=post.id)
            _ = await create_comment(text='comment_2', owner_id=user.id, parent_id=comment_1.id, post_id=post.id)

        response = await async_client.delete(
            url=self.url.format(post_id=post.id),
            headers={'Authorization': token}
        )
        assert response.status_code == 204

        assert not (await async_session.execute(select(func.count(Post.id)))).scalar()
