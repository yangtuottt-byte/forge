"""LLM 客户端测试"""

import pytest

from app.agents.llm import chat_text
from app.core.config import get_settings

settings = get_settings()


async def test_llm_basic():
    if not settings.llm_api_key:
        pytest.skip("未配置 llm_api_key")
    # 问一个简单问题,验证能调通
    answer = await chat_text([{"role": "user", "content": "用一句话介绍什么是Agent"}])
    assert len(answer) > 0
    print("\nLLM 回答:", answer)
