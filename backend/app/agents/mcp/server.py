"""
MCP Server:标准工具接口(概念实现)
MCP = Model Context Protocol,统一工具调用协议
工具可以是本地函数或远程服务,LLM 通过统一接口调用
"""

from app.agents.tools import default_registry
from app.agents.tools.registry import ToolRegistry


class MCPServer:
    """MCP Server:提供工具列表 + 调用接口"""

    def __init__(self, registry: ToolRegistry = default_registry):
        self.registry = registry

    def list_tools(self) -> list[dict]:
        """工具列表"""
        return self.registry.get_schemas()

    def call_tool(self, name: str, arguments: dict) -> str:
        """调用工具(MCP 的 tools/call)"""
        return self.registry.call(name, arguments)

    def health(self) -> dict:
        """健康检查"""
        return {"status": "ok", "tools": len(self.registry.get_schemas())}
