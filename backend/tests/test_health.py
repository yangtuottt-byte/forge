"""health 端点测试:ASGITransport 不发真实网络"""

from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_health_ok():
    """GET /api/v1/health -> 200 + ok"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "db": True}
