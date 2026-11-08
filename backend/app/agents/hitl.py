"""
HITL(Human-in-the-loop):关键节点暂停,等人工审批

原理:安全/质量/合规——关键决策不能全自动
"""

from collections.abc import Callable


async def approval_gate(
    prompt: str, on_approve: Callable, on_reject: Callable | None = None
) -> bool:
    """
    审批门:暂停,等人工确认

    Args:
        prompt: 给审批人的提示(如"执行者已完成代码,是否继续?")
        on_approve: 通过时调用的回调
        on_reject: 打回时调用的回调
    Returns:
        True=通过, False=打回
    """
    print(f"\n[HITL]{prompt}")
    choice = input("输入 'yes' 通过, 'no' 打回:").strip().lower()
    if choice == "yes":
        if on_approve:
            await on_approve()
        return True
    if on_reject:
        await on_reject()
    return False
