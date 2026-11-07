"""工具注册表测试:注册/查 schema/执行"""

from app.agents.tools import default_registry


def test_calculator_basic():
    """calculator:2+3*4 = 14(运算优先级)"""
    assert default_registry.call("calculator", {"expr": "2+3*4"}) == "14"


def test_calculator_complex():
    """calculator:幂运算 + 除法"""
    assert default_registry.call("calculator", {"expr": "2**3 + 10/2"}) == "13.0"


def test_calculator_safe():
    """⭐ 安全测试:eval 能注入的,白名单 eval 必须拒绝"""
    # 恶意输入:__import__ 应该被拒(不是数学表达式)
    result = default_registry.call("calculator", {"expr": "__import__('os').system('echo hacked')"})
    assert "错误" in result or "不允许" in result


def test_registry_unknown_tool():
    """调用不存在的工具:返回错误信息,不抛异常"""
    assert "不存在" in default_registry.call("nonexistent", {})


def test_registry_schemas():
    """get_schemas 返回所有工具的 schema"""
    schemas = default_registry.get_schemas()
    assert len(schemas) >= 1
    assert schemas[0]["function"]["name"] == "calculator"
