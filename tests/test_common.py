import pytest


@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get('/ping/')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
