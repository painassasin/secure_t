import pytest

from tests.base import BaseRepoTest

from backend.auth.repositories import UsernameAlreadyExists
from backend.core.container import user_repository


@pytest.mark.asyncio
class TestUserRepository(BaseRepoTest):

    async def test_create_user_if_already_exists(self, create_user):
        await create_user('test_user', 'test_password')
        with pytest.raises(UsernameAlreadyExists):
            await user_repository.create_user('test_user', 'hashed_password')

    async def test_create_user_success(self, create_user):
        user = await user_repository.create_user('test_user', 'hashed_password')
        assert user.username == 'test_user'
        assert user.password == 'hashed_password'

    @pytest.mark.parametrize('user_exists', [True, False], ids=['user exists', 'user not found'])
    async def test_get_user_by_username(self, create_user, user_exists: bool):
        if user_exists:
            await create_user('test_user', 'test_password')

        result = await user_repository.get_user_by_username('test_user')
        assert bool(result) is user_exists
