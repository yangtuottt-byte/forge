# 规划 Agent 测试:拆解任务(真实调 LLM)
import pytest

from app.agents.planner import plan
from app.core.config import get_settings

settings = get_settings()


async def test_planner_basic():
    """规划:拆解任务,返回子任务列表"""
    if not settings.llm_api_key:
        pytest.skip("未配置 LLM_API_KEY")
    tasks = await plan("写一个 Python 爬虫抓取某网站")
    assert all(isinstance(t, str) for t in tasks)
    print("\n拆解任务:", tasks)


async def test_planner_bad_input():
    if not settings.llm_api_key:
        pytest.skip("未配置 LLM_API_KEY")
    tasks = await plan("")
    assert len(tasks) >= 1
