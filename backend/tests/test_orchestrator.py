"""协调器测试:多 Agent 协作"""

import pytest

from app.agents.orchestrator import Orchestrator
from app.core.config import get_settings

settings = get_settings()


async def test_orchestratop_basic():
    """完整流程:规划→研究→执行→审查→汇总"""
    if not settings.llm_api_key:
        pytest.skip("未配置 LLM_API_KEY")
    orch = Orchestrator()
    result = await orch.run("用一句话介绍什么是Agent")
    assert len(result) > 0
    print("\n协调器结果:", result)
