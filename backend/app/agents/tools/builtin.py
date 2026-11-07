"""内置工具:calculator"""

import ast
import operator

# 白名单:只允许这些运算符
_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval(node):
    """递归求值(白名单模式,防代码注入)"""
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        left = _eval(node.left)
        right = _eval(node.right)
        op = _ALLOWED_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"不允许的操作: {type(node.op).__name__}")
        return op(left, right)
    if isinstance(node, ast.UnaryOp):
        operand = _eval(node.operand)
        op = _ALLOWED_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"不允许的操作: {type(node.op).__name__}")
        return op(operand)
    raise ValueError(f"不允许的表达式结构: {type(node).__name__}")


def calculator(expr: str) -> str:
    """计算数学表达式:2+3*4 → 14"""
    try:
        result = _eval(ast.parse(expr, mode="eval"))
        return str(result)
    except Exception as e:
        return f"计算错误:{e}"
