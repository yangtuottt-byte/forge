"""应用配置:从环境变量/.env 注入,全项目共享。

优先级(高→低):
  1. 真实环境变量(export / Docker compose 注入)
  2. .env 文件
  3. 代码默认值(开发快速起跑用,生产必须被覆盖)

  记忆点:字段名 = 环境变量名大写
  db_host  ↔  DB_HOST      app_name ↔  APP_NAME
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # env_file:读哪个 .env;extra="ignore":多余变量不报错(生产环境变量很多)
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )
    # ---- 应用 ----
    app_name: str = "Forge"
    app_env: str = "dev"  # dev / prod

    # ----数据库----
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "forge"
    db_user: str = "forge"
    db_password: str = "forge"

    # ---- 认证 ----
    jwt_secret: str = "dev-secret-change-me-32-bytes-minimum-for-hmac-sha256"  # 生产必须改
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 24 * 60  # 1 天

    # ---- Redis ----
    redis_host: str = "localhost"
    redis_port: int = 6379

    # ---- LLM ----
    llm_api_key: str = ""  # ⚠️ 必须填,从 .env 注入,不能写代码里
    llm_base_url: str = "https://maas-api.cn-huabei-1.xf-yun.com/v1"
    llm_model: str = "spark-x2.6"

    @property
    def database_url(self) -> str:
        """拼 SQLAlchemy async 连接串"""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def redis_url(self) -> str:
        """拼 Redis 连接串"""
        return f"redis://{self.redis_host}:{self.redis_port}/0"


@lru_cache
def get_settings() -> Settings:
    """全局配置单例:进程内只构造一次(只读一次 .env)"""
    return Settings()
