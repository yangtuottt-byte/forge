"""
文件操作工具:读写文件
安全:路径白名单,只允许 workspace 下
"""

from pathlib import Path

WORKSPACE = Path("/home/yangtuot/python-learning/forge/workspace")


def _safe_path(path: str) -> Path | None:
    """路径安全检查:必须在workspace下"""
    p = (WORKSPACE / path).resolve()
    if not str(p).startswith(str(WORKSPACE)):
        return None
    return p


def read_file(path: str) -> str:
    """读文件"""
    p = _safe_path(path)
    if p is None:
        return f"错误:路径不在工作区:{path}"
    try:
        return p.read_text(encoding="utf-8")
    except Exception as e:
        return f"读文件错误:{e}"


def write_file(path: str, content: str) -> str:
    """写文件"""
    p = _safe_path(path)
    if p is None:
        return f"错误:路径不在工作区:{path}"
    try:
        return p.write_text(encoding="utf-8")
    except Exception as e:
        return f"写文件错误:{e}"
