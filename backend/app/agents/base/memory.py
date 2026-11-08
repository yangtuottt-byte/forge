"""
短期记忆:内存里存每轮的 user/assistant 问答

为什么只存问答不存 tool 消息?
tool 消息是每轮循环内部的(assistant调工具→tool结果→assistant回答),
存进 memory 下轮 LLM 看到会乱(不知道是哪个用户问的)
"""


class Memory:
    """短期记忆:add 存, get_all 取, clear 清"""

    def __init__(self):
        self._messages: list[dict] = []

    def add(self, role: str, content: str) -> None:
        """存一条消息(只存 user/assistant,不存 tool)"""
        self._messages.append({"role": role, "content": content})

    def get_all(self) -> list[dict]:
        """取全部历史(拼到下轮 messages 前面)"""
        return list(self._messages)

    def clear(self) -> None:
        """清空(新会话/重置用)"""
        self._messages.clear()
