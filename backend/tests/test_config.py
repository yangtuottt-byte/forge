from app.core.config import Settings


def test_defaults():
    """没设置任何环境变量时,取代码默认值"""
    s = Settings()
    assert s.app_name == "Forge"
    assert s.db_port == 5432
    assert "postgresql+asyncpg://" in s.database_url


def test_env_override_wins(monkeypatch):
    """环境变量 > 默认值"""
    monkeypatch.setenv("APP_ENV", "prod")
    monkeypatch.setenv("DB_HOST", "prod-host")
    s = Settings()
    assert s.app_env == "prod"
    assert "prod-host" in s.database_url


def test_url_contains_credentials(monkeypatch):
    """URL 拼接把用户密码带进去(阶段1.3 可直接用)"""
    monkeypatch.setenv("DB_USER", "admin")
    monkeypatch.setenv("DB_PASSWORD", "s3cret")
    s = Settings()
    assert "admin:s3cret@" in s.database_url
