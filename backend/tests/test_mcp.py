from app.agents.mcp import MCPServer


def test_mcp_list_tools():
    """list_tools 返回所有工具 schema"""
    server = MCPServer()
    tools = server.list_tools()
    assert len(tools) >= 5  # calculator + search + run_code + read_file + write_file
    names = [t["function"]["name"] for t in tools]
    assert "calculator" in names
    assert "search" in names


def test_mcp_call_tool():
    """call_tool 调用工具"""
    server = MCPServer()
    result = server.call_tool("calculator", {"expr": "2+3"})
    assert result == "5"


def test_mcp_health():
    """健康检查"""
    server = MCPServer()
    h = server.health()
    assert h["status"] == "ok"
    assert h["tools"] >= 5
