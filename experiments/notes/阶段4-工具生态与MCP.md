# 阶段 4:工具生态 + MCP(知识笔记)

> 日期:2026-11-08
> 产出:search/run_code/read_file/write_file 工具 + MCP Server + 沙箱加固文档
> 对应路线图:阶段 4 工具生态 + MCP
> 提交:`feat(tools): 工具扩展` / `MCP Server`(2 个提交)

---

## 一、学到的核心概念(用自己的话)

### 1. 工具扩展:每个工具 = 函数 + schema ⭐
- 阶段 2 只有 calculator,阶段 4 加了 search/run_code/read_file/write_file
- 扩展方式不变:加函数 + 注册 schema
- **工具 = 函数 + 说明书(schema),注册到 ToolRegistry**

### 2. 代码沙箱:subprocess + 超时 ⭐
- Agent 执行代码 = 运行任意 Python 代码,必须隔离
- **进程隔离**:subprocess 子进程执行,主进程不受影响
- **超时限制**:timeout 参数防死循环
- **沙箱层次**:subprocess+超时(基础) → namespace+seccomp(生产防逃逸)

### 3. 文件操作:路径白名单 ⭐
- 防越权:只允许 workspace 下的文件
- **路径安全**:`resolve()` + `startswith` 防路径穿越(`../../etc/passwd`)

### 4. MCP = 标准工具接口 ⭐
- MCP(Model Context Protocol):统一工具调用协议
- 工具可以是本地函数或远程服务,LLM 通过统一接口调用
- 三组件:Server(提供工具)/ Client(调用)/ 协议(JSON-RPC)
- **教学实现**:MCPServer 概念实现,阶段 6 引入完整 MCP

### 5. 容错设计
- 工具出错返回错误信息,不抛异常
- LLM 能看到错误并纠正(如"工具不存在""路径越权")

---

## 二、关键代码模式

| 模式 | 代码 | 用在哪 |
|------|------|--------|
| 搜索工具 | httpx.get(DuckDuckGo) + 正则解析 | search.py |
| 代码沙箱 | subprocess.run([python, -c, code], timeout=N) | code_exec.py |
| 超时处理 | except TimeoutExpired: return "超时" | code_exec.py |
| 路径白名单 | resolve() + startswith(WORKSPACE) | file_ops.py |
| 工具注册 | registry.register(name, fn, schema) | __init__.py |
| MCP Server | list_tools / call_tool / health | mcp/server.py |

---

## 三、踩坑记录(自己写代码时遇到的)

1. **search.py 的 results 未赋值**:`re.findall(...)` 没赋值给变量 → F821 未定义。**修复:`results = re.findall(...)`**。
2. **容器频繁掉线**:PG 容器多次停止 → ConnectionRefused。**教训:长时间不操作 docker 容器会被回收,定期检查**。
3. **LLM 测试限流**:星火 API 免费版有限流,LLM 测试频繁触发。**教训:测试要限流感知,CI 用 skip**。
4. **搜索工具联网依赖**:DuckDuckGo 需要网络,网络不通返回错误(容错处理)。

---

## 四、面试可能问

| 问题 | 答案要点 |
|------|---------|
| Agent 为什么要工具? | 让 Agent 能感知/操作外部世界,不只靠 LLM 知识 |
| 代码执行工具为什么需要沙箱? | 防代码注入/死循环/资源耗尽,主进程安全 |
| 沙箱有哪些层次? | 进程隔离+超时(基础)→ namespace+seccomp(生产防逃逸) |
| 路径白名单怎么实现? | resolve() + startswith 防路径穿越 |
| MCP 是什么? | Model Context Protocol,统一工具调用协议 |
| MCP 三组件? | Server(提供)/ Client(调用)/ 协议(JSON-RPC) |
| 工具出错怎么办? | 返回错误信息不抛异常,LLM 能看到并纠正 |
| 工具 schema 格式? | {type:function, function:{name, description, parameters}} |
| 沙箱能防逃逸吗? | subprocess+超时不能防逃逸(能访问文件系统);生产要 namespace+seccomp |

---

## 五、实验结果与校准

### 实验 4:工具生态 + MCP
| 命令 | 结果 |
|------|------|
| `make lint` | ✅ All checks passed |
| `make test` | ✅ 29 passed(26 + 3 MCP) |
| 工具数量 | ✅ 5 个(calculator/search/run_code/read_file/write_file) |
| MCP Server | ✅ list_tools/call_tool/health |

**结论**:
1. ✅ **工具扩展成功**:5 个工具注册,Agent 能搜索/执行代码/读写文件
2. ✅ **沙箱工作**:代码执行在子进程 + 超时,主进程安全
3. ✅ **MCP 概念实现**:标准工具接口,阶段 6 引入完整 MCP

**观察**:
- 搜索工具依赖网络,网络不通时容错返回错误
- 沙箱是基础隔离,生产要 namespace+seccomp 防逃逸
- LLM 测试限流是环境问题,CI 用 skip 避免变红

---

## 六、下一步

- **阶段 5:异步 + 实时**:
  - Celery 队列 + 多 worker
  - 任务状态持久化(PostgreSQL)
  - WebSocket 实时进度推送
  - 分布式锁(防任务重复执行)
  - 任务幂等、重试、死信队列
- 阶段 4 核心已掌握:工具扩展、沙箱隔离、路径安全、MCP 概念
- 观察点:完整 MCP 引入、沙箱生产化加固、工具权限粒度
