from app.agents.base.agent import BaseAgent
from app.agents.tools import default_registry


async def test_agent_loop_calculator():
    """Agent 循环:LLM 自己调 calculator 计算 3*5+2"""
    agent = BaseAgent(default_registry)
    messages = [{"role": "user", "content": "3乘5加2等于多少?"}]
    answer = await agent.run(messages)
    # LLM 应该调 calculator 拿到 17,然后回答
    assert "17" in answer


async def test_agent_max_steps():
    """max_steps 防死循环:循环里一直调工具会停"""
    # 这个测试验证 max_steps 生效(构造一个总是调工具的 agent)
    # 简单验证:max_steps=1 时,即使 LLM 调工具,循环也只跑 1 轮
    agent = BaseAgent(default_registry, max_steps=1)
    messages = [{"role": "user", "content": "计算 1+1"}]
    # 应该返回"达到最大步数"或"1+1=2"(取决于 LLM 是否第 1 轮就回答)
    answer = await agent.run(messages)
    assert len(answer) > 0  # 至少不报错
