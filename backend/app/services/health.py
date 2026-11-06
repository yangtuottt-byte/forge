"""service 层:业务逻辑编排(路由层不碰 DB,全部调 service)"""

from app.repositories.health_repo import check_database


async def health_status() -> dict:
    """健康 = 数据库就绪(service 把 repo 的结果组装成"业务语义")"""
    db_ok = await check_database()
    status = "ok" if db_ok else "degraded"
    return {"status": status, "db": db_ok}
