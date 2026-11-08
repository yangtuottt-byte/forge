"""
规划 Agent:ReAct 拆解任务

原理:LLM 上下文有限,复杂任务拆解成子任务,每步验证可纠错
"""

import json

from app.agents.llm import chat

PLANNER_PROMPT = """你是一个任务规划专家。把用户的目标拆解成 3-5 个可执行的子任务。

严格输出 JSON 格式(不要其他内容):
{"tasks": ["子任务1", "子任务2", "子任务3"]}

用户目标:{goal}
"""


async def plan(goal: str) -> list[str]:
    """
    把目标拆解成子任务列表

    Args:
        goal:用户目标

    Returns:
        子任务列表
    """

    msg = await chat(
        [
            {
                "role": "user",
                "content": PLANNER_PROMPT.replace("{goal}", goal),  # ⭐ 用 replace 不用 format
            }
        ]
    )
    content = msg.content or ""

    # LLM 输出可能带 markdown 代码块或额外文本,要提取 JSON
    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end == -1:
        return [goal]
    try:
        data = json.loads(content[start : end + 1])
        return data.get("tasks", [goal])
    except json.JSONDecodeError:
        return [goal]
