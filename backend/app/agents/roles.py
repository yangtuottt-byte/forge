"""
角色定义:规划者/研究员/执行者/审查员

原理:分工带来专业——每个角色有明确职责,通过协调器组织
通用逻辑(Agent 循环)在 BaseAgent,专业逻辑(拆任务/查资料/干活/审查)在子类
"""

from app.agents.base.agent import BaseAgent
from app.agents.planner import plan


class PlannerAgent(BaseAgent):
    """规划者:拆解任务"""

    name = "planner"

    async def decompose(self, goal: str) -> list[str]:
        """把目标拆解成子任务列表"""
        return await plan(goal)


class ResearcherAgent(BaseAgent):
    """研究员:查资料"""

    name = "researcher"

    async def research(self, task: str) -> str:
        """搜集任务相关信息"""
        messages = [{"role": "user", "content": f"搜集关于'{task}'的相关信息"}]
        return await self.run(messages)


class WorkerAgent(BaseAgent):
    """执行者:干活"""

    name = "worker"

    async def execute(self, task: str) -> str:
        """完成具体任务"""
        messages = [{"role": "user", "content": task}]
        return await self.run(messages)


class ReviewerAgent(BaseAgent):
    """审查员:检查质量"""

    name = "reviewer"

    async def review(self, content: str) -> bool:
        """审查成果:通过 True / 打回 False"""
        messages = [{"role": "user", "content": f"审查以下成果,只回答'通过'或'不通过':\n{content}"}]
        answer = await self.run(messages)
        return "通过" in answer
