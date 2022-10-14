from unittest.mock import patch

import pytest
from sqlalchemy import select

from backend.core.security import create_access_token
from backend.models import User


@pytest.mark.asyncio
class TestSignIn:
    url = '/auth/signin/'

    async def test_user_not_found(self, async_client):
        response = await async_client.post(self.url, data={'username': 'test_user', 'password': 'test_password'})
        assert response.status_code == 401

    @pytest.mark.parametrize('username, password', [
        ('invalid_username', 'test_password'),
        ('test_user', 'invalid_password'),
    ], ids=['invalid username', 'invalid password'])
    async def test_invalid_username_or_password(self, async_client, create_user, username, password):
        await create_user('test_user', 'test_password')
        response = await async_client.post(self.url, data={'username': username, 'password': password})
        assert response.status_code == 401

    @patch('backend.core.security._create_token', return_value='fake_access_token')
    async def test_success(self, mock_create_token, async_client, create_user):
        await create_user('test_user', 'test_password')
        response = await async_client.post(self.url, data={'username': 'test_user', 'password': 'test_password'})
        assert response.status_code == 200
        assert mock_create_token.called
        assert response.json() == {'access_token': 'fake_access_token', 'token_type': 'bearer'}


@pytest.mark.asyncio
class TestSignUp:
    url = '/auth/signup/'

    async def test_success(self, async_client, async_session):
        response = await async_client.post(self.url, json={'username': 'test_user', 'password': 'test_password'})
        assert response.status_code == 201

        user_in_db: User = (await async_session.execute(select(User))).scalar_one()
        assert response.json() == {'id': user_in_db.id, 'username': 'test_user'}
        assert user_in_db.username == 'test_user'
        assert user_in_db.password != 'test_password'

    async def test_user_already_exists(self, async_client, create_user):
        await create_user('test_user', 'test_password')
        response = await async_client.post(self.url, json={'username': 'test_user', 'password': 'test_password'})
        assert response.status_code == 400


@pytest.mark.asyncio
class TestGetUser:
    url = '/auth/me/'

    async def test_auth_required(self, async_client):
        response = await async_client.get(self.url)
        assert response.status_code == 401

    @pytest.mark.parametrize('access_token', ['Bearer token', 'token'])
    async def test_invalid_token_format(self, async_client, create_user, access_token):
        response = await async_client.get(self.url, headers={'Authorization': access_token})
        assert response.status_code == 401

    async def test_user_not_found(self, async_client):
        token = create_access_token(username='invalid_user')
        response = await async_client.get(self.url, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 401

    async def test_success(self, async_client, create_user):
        token, user = await create_user('test_user', 'test_password')
        response = await async_client.get(self.url, headers={'Authorization': token})
        assert response.status_code == 200
