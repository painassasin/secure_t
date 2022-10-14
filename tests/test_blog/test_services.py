from datetime import datetime
from unittest.mock import patch

import pytest

from backend.blog.exceptions import PostNotFound
from backend.blog.repositories import InvalidPostId, PostRepository
from backend.blog.schemas import Comment, PostInDB, UpdatePost
from backend.core.container import blog_service
from backend.core.exceptions import Forbidden


@pytest.mark.asyncio
class TestBlogService:

    @pytest.fixture
    def post_in_db(self):
        now = datetime.now()
        return PostInDB(
            id=1,
            created_at=now,
            updated_at=now,
            owner_id=1,
            text='text',
            parent_id=1,
        )

    @patch.object(PostRepository, 'create_post', side_effect=InvalidPostId)
    async def test_create_comment_invalid_post_id(self, create_post_mock):
        assert not await blog_service.create_comment(owner_id=1, text='text', parent_id=1)
        create_post_mock.assert_awaited_once_with(owner_id=1, text='text', parent_id=1)

    @patch.object(PostRepository, 'create_post')
    async def test_create_comment_success(self, create_post_mock, post_in_db):
        create_post_mock.return_value = post_in_db
        obj = await blog_service.create_comment(owner_id=1, text='text', parent_id=1)
        create_post_mock.assert_awaited_once_with(owner_id=1, text='text', parent_id=1)
        assert obj == Comment.parse_obj(post_in_db)

    @patch.object(PostRepository, 'get_post_or_comment_in_db', return_value=None)
    async def test_update_post_not_found(self, get_post_or_comment_in_db_mock):
        with pytest.raises(PostNotFound):
            await blog_service.update_post(post_id=1, user_id=2, data={})
        get_post_or_comment_in_db_mock.assert_awaited_once_with(post_id=1, for_update=True)

    @patch.object(PostRepository, 'update_post')
    @patch.object(PostRepository, 'get_post_or_comment_in_db')
    async def test_update_post_not_owner(self, get_post_or_comment_in_db_mock, update_post_mock, post_in_db):
        get_post_or_comment_in_db_mock.return_value = post_in_db
        post_in_db.owner_id = 1

        with pytest.raises(Forbidden):
            await blog_service.update_post(post_id=1, user_id=2, data=UpdatePost(text='text'))
        get_post_or_comment_in_db_mock.assert_awaited_once_with(post_id=1, for_update=True)
        update_post_mock.assert_not_awaited()

    @patch.object(PostRepository, 'update_post')
    @patch.object(PostRepository, 'get_post_or_comment_in_db')
    async def test_update_post_success(self, get_post_or_comment_in_db_mock, update_post_mock, post_in_db):
        get_post_or_comment_in_db_mock.return_value = post_in_db
        post_in_db.owner_id = 5

        await blog_service.update_post(post_id=1, user_id=5, data=UpdatePost(text='new_text'))
        get_post_or_comment_in_db_mock.assert_awaited_once_with(post_id=1, for_update=True)
        update_post_mock.assert_awaited_once_with(post_id=1, text='new_text')

    @patch.object(PostRepository, 'get_post_or_comment_in_db', return_value=None)
    async def test_delete_post_not_found(self, get_post_or_comment_in_db_mock):
        with pytest.raises(PostNotFound):
            await blog_service.delete_post(post_id=1, user_id=2)
        get_post_or_comment_in_db_mock.assert_awaited_once_with(post_id=1)

    @patch.object(PostRepository, 'delete_post')
    @patch.object(PostRepository, 'get_post_or_comment_in_db')
    async def test_delete_post_not_owner(self, get_post_or_comment_in_db_mock, delete_post_mock, post_in_db):
        get_post_or_comment_in_db_mock.return_value = post_in_db
        post_in_db.owner_id = 1

        with pytest.raises(Forbidden):
            await blog_service.delete_post(post_id=1, user_id=2)
        get_post_or_comment_in_db_mock.assert_awaited_once_with(post_id=1)
        delete_post_mock.assert_not_awaited()

    @patch.object(PostRepository, 'delete_post')
    @patch.object(PostRepository, 'get_post_or_comment_in_db')
    async def test_delete_post_success(self, get_post_or_comment_in_db_mock, delete_post_mock, post_in_db):
        get_post_or_comment_in_db_mock.return_value = post_in_db
        post_in_db.owner_id = 5

        await blog_service.delete_post(post_id=1, user_id=5)
        get_post_or_comment_in_db_mock.assert_awaited_once_with(post_id=1)
        delete_post_mock.assert_awaited_once_with(post_id=1)
