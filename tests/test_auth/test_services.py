from unittest.mock import patch

import pytest
from fastapi.security import OAuth2PasswordRequestForm

from backend.auth.exceptions import InvalidCredentials, UserAlreadyExists
from backend.auth.repositories import UsernameAlreadyExists, UserRepository
from backend.auth.schemas import UserCreate
from backend.core.container import auth_service
from backend.core.security import get_password_hash
from backend.models import User


@pytest.mark.asyncio
class TestAuthService:
    @pytest.fixture
    def request_form(self):
        return OAuth2PasswordRequestForm(
            grant_type='password',
            username='test_user',
            password='test_password',
            scope='',
            client_id=None,
            client_secret=None
        )

    @patch.object(UserRepository, 'get_user_by_username', return_value=None)
    async def test_authenticate_user_not_found(self, _, request_form):
        with pytest.raises(InvalidCredentials):
            await auth_service.authenticate(request_form)

    @pytest.mark.parametrize('password', [
        'invalid_password', get_password_hash('invalid password')
    ], ids=['unknown hash', 'valid hash'])
    @patch.object(UserRepository, 'get_user_by_username')
    async def test_authenticate_invalid_password(self, get_user_by_username_mock, password, request_form):
        get_user_by_username_mock.return_value = User(
            username=request_form.username,
            password=password,
        )

        with pytest.raises(InvalidCredentials):
            await auth_service.authenticate(request_form)

    @patch.object(UserRepository, 'get_user_by_username')
    async def test_authenticated_success(self, get_user_by_username_mock, request_form):
        get_user_by_username_mock.return_value = User(
            username=request_form.username,
            password=get_password_hash(request_form.password),
        )
        user = await auth_service.authenticate(request_form)
        assert user.username == 'test_user'

    @patch.object(UserRepository, 'create_user', side_effect=UsernameAlreadyExists)
    async def test_create_user_already_exists(self, _):
        with pytest.raises(UserAlreadyExists):
            await auth_service.create_user(user_in=UserCreate(username='test_user', password='test_password'))

    @patch('backend.auth.services.get_password_hash', return_value='hashed_password')
    @patch.object(UserRepository, 'create_user')
    async def test_create_user_success(self, create_user_mock, get_password_hash_mock):
        assert await auth_service.create_user(user_in=UserCreate(username='test_user', password='test_password'))
        create_user_mock.assert_awaited_once_with(
            username='test_user',
            hashed_password='hashed_password'
        )
        get_password_hash_mock.assert_called_once_with('test_password')
