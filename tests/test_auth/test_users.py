import pytest


@pytest.mark.asyncio
class TestUser:
    url = '/users/'

    async def test_auth_required(self, async_client):
        response = await async_client.get(self.url)
        assert response.status_code == 401

    async def test_success(self, async_client, create_user):
        token, user = await create_user('test_user', 'test_password')
        response = await async_client.get(self.url, headers={'Authorization': token})
        assert response.status_code == 200
