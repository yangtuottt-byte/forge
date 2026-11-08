"""
Agent基类:实现Agent循环(调llm -> 看tool_calls -> 执行 -> 喂回 -> 循环)
核心:Agent = 循环, LLM一次看不到所有消息,每步决策依赖上步结果
"""

import json

from app.agents.base.memory import Memory
from app.agents.llm import chat
from app.agents.tools.registry import ToolRegistry


class BaseAgent:
    """所有 Agent 的基类:会调 LLM、会调工具、会循环"""

    def __init__(self, registry: ToolRegistry, max_steps: int = 10):
        self.registry = registry  # 工具注册表
        self.max_steps = max_steps  # 防死循环

    async def run(self, messages: list[dict], memory: Memory | None = None) -> str:
        """
        Agent 循环:直到 LLM 不再调工具,返回最终回答
        Args:
            messages: 本轮消息(可含 user 提问)
            memory: 短期记忆(可选),会把历史拼到 messages 前面
        """

        if memory:
            messages = memory.get_all() + messages

        for _ in range(self.max_steps):
            # 1.调llm
            msg = await chat(messages, tools=self.registry.get_schemas())
            # 2.存 assistant 消息(含 tool_calls)
            assistant_smg = {"role": "assistant", "content": msg.content or ""}
            # 3.有 tool_calls → 执行工具
            if msg.tool_calls:
                assistant_smg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in msg.tool_calls
                ]
            messages.append(assistant_smg)
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    # arguments 是 JSON 字符串,要解析
                    arguments = json.loads(tc.function.arguments) if tc.function.arguments else {}
                    # 4.执行工具,结果存回(role:"tool" + tool_call_id 配对)
                    result = self.registry.call(tc.function.name, arguments)
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
                # 5.继续循环
                continue
            if memory:
                memory.add("assistant", msg.content or "")
            # 6.没 tool_calls → 最终回答
            return msg.content or ""
        # 达到 max_steps 还没结束
        return "达到最大步数,Agent 停止"
