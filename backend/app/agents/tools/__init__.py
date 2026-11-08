from app.agents.tools.builtin import calculator
from app.agents.tools.code_exec import run_code
from app.agents.tools.file_ops import read_file, write_file
from app.agents.tools.registry import ToolRegistry
from app.agents.tools.search import search

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
default_registry.register(
    "search",
    search,
    description="搜索网络资料",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索关键词"},
            "max_results": {"type": "integer", "description": "结果数量,默认3"},
        },
        "required": ["query"],
    },
)

default_registry.register(
    "run_code",
    run_code,
    description="执行python代码(沙箱,10s超时)",
    parameters={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python代码"},
            "timeout": {"type": "integer", "description": "超时秒数,默认10"},
        },
        "required": ["code"],
    },
)

default_registry.register(
    "read_file",
    read_file,
    description="读取 workspace 下的文件",
    parameters={
        "type": "object",
        "properties": {"path": {"type": "string", "description": "文件路径(相对 workspace)"}},
        "required": ["path"],
    },
)
default_registry.register(
    "write_file",
    write_file,
    description="写入 workspace 下的文件",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件路径(相对 workspace)"},
            "content": {"type": "string", "description": "文件内容"},
        },
        "required": ["path", "content"],
    },
)
