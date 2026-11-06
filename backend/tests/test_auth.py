"""认证流程测试:注册→登录→带 token 访问 /me"""

from httpx import ASGITransport, AsyncClient

from app.main import app

email = "test@forge.dev"


async def register_and_login(client: AsyncClient) -> dict:
    """注册 + 登录(注册页直接返回 token)"""
    r = await client.post("/api/v1/auth/register", json={"email": email, "password": "s3cret!"})
    assert r.status_code == 201
    return r.json()


async def test_register_login_flow():
    """注册→登录→带 token 访问 /me"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await register_and_login(client)
        assert "access_token" in token

        # 不带 token:401
        r = await client.get("/api/v1/users/me")
        assert r.status_code == 401

        # 带 token:200 + 自己的用户信息
        r = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        assert r.status_code == 200
        assert r.json()["email"] == email


async def test_login_wrong_password():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 先注册
        await register_and_login(client)
        # 错误密码 → 401
        r = await client.post("/api/v1/auth/login", json={"email": email, "password": "wrong"})
        assert r.status_code == 401
