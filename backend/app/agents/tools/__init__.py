from app.agents.tools.builtin import calculator
from app.agents.tools.registry import ToolRegistry

default_registry = ToolRegistry()
default_registry.register(
    "calculator",
    calculator,
    description="计算数学表达式,如 2+3*4",
    parameters={
        "type": "object",
        "properties": {"expr": {"type": "string", "description": "数学表达式"}},
        "required": ["expr"],
    },
)
