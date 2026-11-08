"""
消息模型:Agent 间通信

原理:结构化消息解耦+可追踪——Agent 不直接调用,通过消息通信
"""

from dataclasses import dataclass


@dataclass
class Message:
    """Agent间消息"""

    from_agent: str  # 谁发的
    to_agent: str  # 发给谁
    typr: str  # 消息类型:task/result/approve/reject
    content: dict  # 内容


def task_message(to_agent: str, task: str) -> Message:
    """快捷:创建任务消息"""
    return Message(from_agent="coordinator", to_agent=to_agent, type="task", content={"task": task})


def result_message(from_agent: str, content: str) -> Message:
    """快捷:创建结果消息"""
    return Message(
        from_agent=from_agent, to_agent="coordinator", type="result", content={"content": content}
    )
