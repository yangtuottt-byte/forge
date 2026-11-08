# 阶段 3:多 Agent 协作(知识笔记)

> 日期:2026-11-08
> 产出:角色定义(Planner/Researcher/Worker/Reviewer)、消息模型、协调器(Orchestrator)、HITL 审批门
> 对应路线图:阶段 3 多 Agent 协作
> 提交:`feat(agents): 角色定义+消息模型` / `协调器` / `HITL`(3 个提交)

---

## 一、学到的核心概念(用自己的话)

### 1. 为什么需要多 Agent ⭐
- 单 Agent:一个 LLM 干所有事,上下文有限,容易"偏科"
- 多 Agent:分工合作,各司其职——**分工带来专业,协调带来效率**
- 类比:单 Agent=一个人开公司;多 Agent=一个公司(项目经理/调研员/程序员/测试员)

### 2. 四种角色 ⭐
| 角色 | 职责 | 类比 | 方法 |
|------|------|------|------|
| 规划者 | 拆任务 | 项目经理 | decompose(goal) → 子任务列表 |
| 研究员 | 查资料 | 调研员 | research(task) → 资料 |
| 执行者 | 干活 | 程序员 | execute(task) → 成果 |
| 审查员 | 检查 | 测试员 | review(content) → 通过/打回 |

对应"做一件事"的完整流程:**想→查→做→验**。

### 3. 协调器 = 中心节点 ⭐
- Agent 之间不直接调用,通过协调器流转
- 三个职责:**分派**(给对角色)、**流转**(状态机顺序)、**汇总**(拼结果)
- 状态机:planning → researching → executing → reviewing → done

### 4. 消息模型:结构化通信 ⭐
- 消息 = {from, to, type, content}
- **为什么结构化**:解耦(Agent 不直接调)、可追踪(日志/审计)、可异步(排队/重试)
- 协调器是"路由器"

### 5. LangGraph vs 原生实现 ⭐
| | 原生 | LangGraph |
|------|------|-----------|
| 流程 | if/for 写死 | 节点+边声明 |
| 状态 | 局部变量 | 全局 state dict |
| 可视化 | ❌ | ✅ |

**原则:先懂原理再用框架**——原生实现理解状态流转,LangGraph 是声明式重写。

### 6. HITL(Human-in-the-loop)⭐
- 关键节点暂停,等人工审批
- **为什么**:安全(关键操作不全自动)、质量(人判断更可靠)、合规(必须人工)
- 实现:协调器在审查前 `approval_gate()` 暂停,等确认

---

## 二、关键代码模式

| 模式 | 代码 | 用在哪 |
|------|------|--------|
| 角色子类 | class PlannerAgent(BaseAgent): name/decompose | roles.py |
| 角色方法 | decompose/research/execute/review | roles.py |
| 消息模型 | Message(from/to/type/content) | messages.py |
| 协调器 | Orchestrator.run: 规划→研究→执行→审查→汇总 | orchestrator.py |
| 状态机 | for task in tasks: 循环流转 | orchestrator.py |
| 打回重做 | if not review: execute(retry) | orchestrator.py |
| HITL 门 | approval_gate(prompt, on_approve) | hitl.py |
| 规划兜底 | if not tasks: tasks = [goal] | orchestrator.py |

---

## 三、踩坑记录(自己写代码时遇到的)

1. **角色类缺 __init__**:BaseAgent 需要 registry 参数,子类没传 → TypeError。**修复:每个角色加 `__init__` 传 default_registry**。
2. **append 在循环分支里**:`results.append` 只在审查不通过分支,通过时没 append → 结果空。**修复:append 提到循环体末尾**。
3. **return 在循环里**:return 在 for 内 → 只处理第一个任务。**修复:return 移到循环外**。
4. **规划返回空列表**:LLM 返回 `{"tasks": []}` → 协调器循环 0 次 → 结果空。**修复:planner 和 orchestrator 双重兜底**。
5. **API 限流(RateLimitError)**:LLM 测试调用频繁触发星火 API 限流。**教训:免费 API 有频率限制,测试要限流感知**。
6. **HITL 的 input() 测试阻塞**:input() 在测试环境阻塞。**修复:hitl 参数默认 False,测试关闭**。

---

## 四、面试可能问

| 问题 | 答案要点 |
|------|---------|
| 为什么多 Agent 而不是单 Agent? | 分工带来专业,协调带来效率;单 Agent 上下文有限易偏科 |
| 四种角色怎么分工? | 规划拆任务/研究查资料/执行干活/审查检查,对应想查做验 |
| 协调器的作用? | 中心节点:分派+流转+汇总,Agent 不直接调用 |
| Agent 间怎么通信? | 结构化消息(from/to/type/content),解耦+可追踪 |
| LangGraph 是什么? | 声明式状态图(State/Node/Edge),可视化流程 |
| 为什么先原生再 LangGraph? | 先懂原理(状态流转)再用框架,避免框架魔法 |
| HITL 是什么? | 关键节点暂停等人工审批,安全/质量/合规 |
| HITL 怎么实现? | 协调器在关键节点调用 approval_gate 等待确认 |
| 打回重做怎么实现? | 审查不通过,执行者重新执行(可加重试上限) |
| 协调器的状态机流程? | planning→researching→executing→reviewing→done |

---

## 五、实验结果与校准

### 实验 3:多 Agent 协作
| 命令 | 结果 |
|------|------|
| `make lint` | ✅ All checks passed |
| `make test` | ✅ 26 passed(含协调器完整流程,真实调 LLM) |
| 协调器流程 | ✅ 规划4子任务→研究→执行→审查(全通过)→汇总 |
| HITL | ✅ approval_gate 实现,默认关闭不影响测试 |

**结论**:
1. ✅ **多 Agent 协作跑通**:规划→研究→执行→审查→汇总全流程
2. ✅ **角色分工生效**:每个角色有明确职责和方法
3. ✅ **协调器状态机工作**:中心节点管理流转
4. ✅ **HITL 可插拔**:默认关闭,需要时启用

**观察**:
- 协调器完整流程 11 分钟(LLM 调用成本),生产可并行/缓存
- 星火 API 免费版有限流,测试要限流感知
- 阶段 4 工具生态可以给 Agent 装更多"手"(搜索/代码执行/文件)

---

## 六、下一步

- **阶段 4:工具生态 + MCP**:
  - 工具注册机制扩展(搜索/代码执行/文件操作)
  - MCP(Model Context Protocol)标准接口
  - 代码沙箱(进程/namespace 隔离,防逃逸)
  - 工具权限与安全
- 阶段 3 核心已掌握:多 Agent 分工、协调器状态机、消息通信、HITL
- 观察点:协调器并行执行、LangGraph 引入时机、HITL 生产化(外部审批 API)
