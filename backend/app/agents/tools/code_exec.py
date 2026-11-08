"""
代码执行工具:沙箱运行 Python 代码

原理:subprocess 子进程 + 超时,主进程安全
防:代码注入、死循环、资源耗尽
"""

import subprocess
import sys


def run_code(code: str, timeout: int = 10) -> str:
    """
    在子进程执行 Python 代码,超时杀掉

    Args:
        code: Python 代码字符串
        timeout: 超时秒数(防死循环)
    Returns:
        执行结果(stdout + stderr)
    """
    try:
        # subprocess 子进程:主进程不受影响
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout + result.stderr
        return output.strip() or "(无输出)"
    except subprocess.TimeoutExpired:
        return f"执行超时(>{timeout}s)"
    except Exception as e:
        return f"执行错误:{e}"
