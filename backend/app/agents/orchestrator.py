"""
协调器:分派任务、管理流程、汇总结果

原理:协调器是中心节点——Agent 不直接调用,通过协调器流转
状态机:planning → researching → executing → reviewing → done
"""

from app.agents.hitl import approval_gate
from app.agents.roles import PlannerAgent, ResearcherAgent, ReviewerAgent, WorkerAgent


class Orchestrator:
    """协调器:管理多Agent协作"""

    def __init__(self):
        self.planner = PlannerAgent()
        self.researcher = ResearcherAgent()
        self.worker = WorkerAgent()
        self.reviewer = ReviewerAgent()

    async def run(self, goal: str, hitl: bool = False) -> str:
        """完整流程:规划→研究→执行→审查→汇总"""
        # 规划:拆任务
        tasks = await self.planner.decompose(goal)
        if not tasks:  # ⭐ 规划返回空兜底:用目标本身作为唯一任务
            tasks = [goal]

        # 对每个任务:研究-执行-审查
        results = []
        for task in tasks:
            # 研究员查资料
            research = await self.researcher.research(task)
            # 执行者干活
            result = await self.worker.execute(f"{task}\n\n相关资料:\n{research}")
            # HITL:执行者完成后,人工审批
            if hitl:
                approved = await approval_gate(f"任务'{task}'已完成,是否继续审查?", on_approve=None)
                if not approved:
                    result = await self.worker.execute(f"{task}(打回重做)")

            # 审查员检查
            if not await self.reviewer.review(result):
                result = await self.worker.execute(f"{task}(重新做,上次被打回)")
            results.append(result)  # ✅ 每次循环都 append

        # 汇总(循环外 return)
        return "\n\n---\n\n".join(results)
