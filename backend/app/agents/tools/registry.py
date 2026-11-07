"""工具注册表:名字→函数的映射,Agent 循环靠它执行工具"""


class ToolRegistry:
    """注册表:register 注册,get_schemas 给 LLM,call 执行"""

    def __init__(self):
        self._tools: dict[str, dict] = {}

    def register(self, name: str, fn, description: str, parameters: dict) -> None:
        """注册一个工具:名字、函数、说明书"""
        schema = {
            "type": "function",
            "function": {"name": name, "description": description, "parameters": parameters},
        }

        self._tools[name] = {"fn": fn, "schema": schema}

    def get_schemas(self) -> list[dict]:
        """给 LLM 的工具清单"""
        return [t["schema"] for t in self._tools.values()]

    def get_function(self, name: str):
        """按名字查函数"""
        tool = self._tools.get(name)
        return tool["fn"] if tool else None

    def call(self, name: str, arguments: dict) -> str:
        """执行工具:查函数 -> 调 -> 结果转字符串"""
        fn = self.get_function(name)
        if fn is None:
            return f"错误:工具 {name} 不存在"
        try:
            return str(fn(**arguments))
        except Exception as e:
            return f"工具执行错误:{e}"
