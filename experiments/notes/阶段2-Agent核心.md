# 阶段 2:Agent 核心(知识笔记)

> 日期:2026-11-07
> 产出:LLM 客户端封装、工具注册表、Agent 基类、短期记忆、规划 Agent(ReAct)
> 对应路线图:阶段 2 Agent 核心
> 提交:`feat(agents): LLM客户端` / `工具注册` / `Agent基类` / `短期记忆` / `规划Agent`(5 个提交)

---

## 一、学到的核心概念(用自己的话)

### 1. Agent 的本质:主动干活 vs 被动回答 ⭐
- 普通 LLM:被动回答,你问它答
- Agent:主动干活,给目标后**自己决定**调哪些工具完成
- Agent = 大脑(LLM) + 手(工具) + 循环(思考-行动-观察)

### 2. Agent 循环(核心中的核心)⭐
```
提问 → 调 LLM(带工具清单) → LLM 说"我要调工具 X"
  → 执行工具 X → 结果喂回 → 再问 LLM → 循环 N 次
  → LLM 说"我做完/答完了" → 结束
```
**为什么是循环**:LLM 一次看不到所有信息,每步决策依赖上步结果。
**max_steps 防死循环**:LLM 可能一直调工具不回答,最多跑 N 轮。

### 3. 消息协议(四个关键细节)⭐
| 细节 | 为什么 |
|------|--------|
| tool_choice="auto" | 让 LLM 自己决定调不调 |
| **assistant 消息存历史** | 下轮 LLM 靠它知道刚才调了什么 |
| **tool 消息 + tool_call_id 配对** | 协议要求,回执单号 |
| **arguments 是 JSON 字符串** | 要 json.loads 解析 |

### 4. 工具注册表:名字→函数映射 ⭐
- 工具 = 函数 + schema(给 LLM 的说明书)
- 注册表 = 名字→函数映射,Agent 循环按名字执行工具
- schema 格式:OpenAI 标准 {type:function, function:{name, description, parameters}}

### 5. 安全计算器:ast 白名单 vs eval ⭐
- `eval("__import__('os').system('rm -rf /')")` = 代码注入
- 安全做法:ast 模块白名单解析,只放行数学运算

### 6. 短期记忆:LLM 无状态 ⭐
- LLM 每次调用独立,不记得上次说过什么
- 多轮对话 = 把历史 messages 一起传
- 短期记忆 = 内存存 user/assistant 问答(快但易失)
- **只存问答不存 tool 消息**:tool 是每轮内部的,存了下轮 LLM 乱

### 7. ReAct:推理 + 行动 ⭐
- 复杂任务拆解成子任务,每步验证可纠错
- LLM 上下文有限,一次太多容易错
- 规划 Agent 输出 JSON 格式子任务列表

### 8. 流式 vs 非流式:generator 不能 return 带值 ⭐
- 函数里有 yield 就变成 generator,不能 return 值
- 所以流式和非流式必须拆成两个函数

---

## 二、关键代码模式

| 模式 | 代码 | 用在哪 |
|------|------|--------|
| 异步 LLM 客户端 | AsyncOpenAI(api_key, base_url) | llm.py |
| 非流式 chat | `await chat(messages, tools=...)` | llm.py |
| 流式 chat_stream | `async for chunk in chat_stream(...)` | llm.py |
| 工具 schema | {type:function, function:{name, description, parameters}} | registry.py |
| 注册表 call | `registry.call(name, arguments)` 执行+容错 | registry.py |
| Agent 循环 | for _ in range(max_steps): chat → tool_calls → call → append | agent.py |
| 消息配对 | tool 消息带 tool_call_id 对应 assistant 的 tc.id | agent.py |
| 短期记忆 | Memory.add/get_all(只存问答) | memory.py |
| 记忆拼接 | `memory.get_all() + messages` | agent.py |
| ReAct 拆解 | planner 输出 JSON tasks 列表 | planner.py |
| JSON 提取 | find("{") / rfind("}") 处理 markdown 包裹 | planner.py |
| 测试 client 重建 | reset_client() 替代 close() | llm.py + conftest |

---

## 三、踩坑记录(自己写代码时遇到的)

1. **密钥写进 config.py**:真实 API key 写进代码文件 → 入库泄露。**教训:密钥走 .env,代码里只留默认空值**。
2. **generator 不能 return 带值**:`async def chat()` 里同时 yield 和 return → SyntaxError。**解法:流式非流式拆两个函数**。
3. **类型注解被当参数**:`def __init__(self, registry, ToolRegistry)` 把类型注解当第二个参数 → TypeError。**正确:`registry: ToolRegistry`**。
4. **OpenAI client close 后不能复用**:conftest 里 close → "client has been closed"。**解法:reset_client() 重建**。
5. **`.format()` 误解析 JSON 示例**:prompt 里 `{"tasks": ...}` 被 format 当占位符 → KeyError。**解法:用 replace 替代 format**。
6. **容器频繁掉线**:docker compose ps 空表,PG/Redis 停了 → ConnectionRefused。**教训:定期 docker compose ps,挂了重启**。

---

## 四、面试可能问

| 问题 | 答案要点 |
|------|---------|
| Agent 和普通 LLM 区别? | Agent 主动干活自己选工具;普通 LLM 被动回答 |
| Agent 循环怎么实现? | 调LLM→有tool_calls执行→喂回→循环→无tool_calls回答 |
| 为什么要 max_steps? | 防死循环:LLM 可能一直调工具不回答 |
| assistant 消息为什么要存历史? | 下轮 LLM 靠它知道刚才调了什么工具、参数 |
| tool_call_id 的作用? | 配对工具结果和 LLM 的调用(回执单号) |
| 工具 schema 格式? | {type:function, function:{name, description, parameters}} |
| 为什么不用 eval 做计算器? | 代码注入风险;用 ast 白名单 |
| 短期记忆为什么只存问答? | tool 消息是每轮内部的,存了下轮 LLM 乱 |
| LLM 无状态是什么意思? | 每次调用独立,不记得上次;多轮=把历史一起传 |
| ReAct 是什么? | Reason+Act,任务拆解,每步验证 |
| 为什么要任务拆解? | LLM 上下文有限,一次太多容易错 |
| 流式和非流式为什么拆函数? | generator 不能 return 带值 |
| OpenAI client close 后能复用吗? | 不能;用 reset/重建 |
| 工具注册表的作用? | 名字→函数映射,Agent 按名字执行工具 |

---

## 五、实验结果与校准

### 实验 2:Agent 核心(25 个测试)
| 命令 | 结果 |
|------|------|
| `make lint` | ✅ All checks passed |
| `make test` | ✅ 25 passed(含真实调 LLM:LLM 客户端/Agent 循环/规划) |
| Agent 循环验证 | ✅ LLM 调 calculator 计算 3*5+2 = 17 |
| 规划验证 | ✅ LLM 拆解任务返回子任务列表 |
| 记忆验证 | ✅ 多轮问答历史正确存储 |

**结论**:
1. ✅ **Agent 全链路跑通**:LLM 客户端 → 工具注册 → Agent 循环 → 记忆 → 规划
2. ✅ **真实调 LLM 验证**:Agent 能自己判断"这题该用 calculator"并调工具
3. ✅ **安全验证**:计算器 ast 白名单拒绝代码注入
4. ✅ **测试基础设施**:reset_client 解决 LLM 连接池事件循环问题

**观察**:
- LLM 测试慢(规划任务 2 分钟),生产可考虑缓存/异步
- 星火模型能正确使用 tool_calls 和 JSON 输出
- 阶段 3 多 Agent 协作可以基于现有基类扩展

---

## 六、下一步

- **阶段 3:多 Agent 协作**:
  - 角色定义(规划者/研究员/执行者/审查员)
  - 协调器(任务分派、消息传递)
  - LangGraph 状态机(对比原生实现)
  - Human-in-the-loop(人工审批节点)
  - 多 Agent 冲突解决
- 阶段 2 核心已掌握:Agent 循环、工具协议、记忆分层、ReAct 拆解
- 观察点:LLM 调用成本、流式输出集成、长期记忆(PGVector)
