# Forge — 多智能体协作研发平台

> 一个"AI 研发团队"平台:用户提交研发任务(写代码 / 做研究 / 分析),**多个 Agent 分工协作**完成,全程生产级后端支撑。旗舰场景 = 自主编程(类比 Devin / Cursor 的简化版)。
>
> 本项目为**旗舰级练手项目**,目标是把 Agent 开发的全部内容 + 后端工程能力(计算机基础、语言深度、数据库、分布式、架构、排障、工程化、业务)全部串起来充分展示。

---

## 一、项目主题

**Forge — 多智能体协作研发平台**:用户提交研发任务,平台拆解成子任务,分派给不同 Agent(规划者 / 研究员 / 执行者 / 审查员)协作完成,实时展示进度,产出可交付成果。

### 为什么选这个主题

| 要展示的能力 | 在这个项目中怎么体现 |
|--------------|-------------------|
| 计算机基础 | 代码沙箱(进程/namespace 隔离)、Agent 间网络通信、文件系统 workspace、并发异步 |
| 语言深度(Python) | async/await、context manager、装饰器、类型系统、元编程、并发原语 |
| 数据库能力 | PostgreSQL 复杂状态机、PGVector 记忆、Redis 缓存、事务、Alembic 迁移 |
| 分布式系统 | Celery 队列、多 worker、任务调度、幂等、分布式锁、消息可靠投递 |
| 系统架构 | 微服务拆分、API 网关、分层架构(router/service/repo/model)、可扩展设计 |
| 排查问题 | 分布式调试、链路追踪、日志聚合、性能分析、故障注入 |
| 工程化素养 | 单元/集成测试、CI/CD、代码规范、文档、版本管理、可观测 |
| 业务能力 | 真实产品:提交任务→交付成果,领域建模(任务/工件/审批/计费) |
| Agent 开发全部 | 多 Agent、规划、记忆、工具生态、MCP、Human-in-the-loop、评估、流式 |

---

## 二、项目框架

生产级分层结构,`api → services → repositories → models`,Agent 层(`agents/`)是业务核心,挂在 services 之上。

```
forge/
├── README.md
├── docker-compose.yml          # 多服务编排(api/worker/redis/pg/sandbox)
├── Makefile                    # 一键命令(dev/test/build/up)
├── .github/workflows/ci.yml    # CI/CD
├── deploy/                     # 部署(k8s/helm 可选)
├── docs/                       # 架构文档、ADR、设计文档
│   └── architecture/
├── backend/
│   ├── pyproject.toml          # 依赖 + 工具配置
│   ├── alembic/                # DB 迁移
│   ├── app/
│   │   ├── main.py             # FastAPI 入口
│   │   ├── core/               # 配置、日志、安全、依赖注入
│   │   ├── api/v1/             # 路由层(/tasks /agents /workspace /realtime)
│   │   ├── schemas/            # pydantic 请求/响应模型
│   │   ├── services/           # 业务逻辑层
│   │   ├── repositories/       # 数据访问层(DB/Redis)
│   │   ├── models/             # SQLAlchemy ORM
│   │   ├── agents/             # Agent 实现
│   │   │   ├── orchestrator/   # 协调器(规划/分派)
│   │   │   ├── planner/        # 规划者
│   │   │   ├── researcher/     # 研究员
│   │   │   ├── worker/         # 执行者(写代码/跑工具)
│   │   │   ├── reviewer/       # 审查员
│   │   │   └── base/           # Agent 基类、消息、记忆接口
│   │   ├── tools/              # 工具生态(search/code_exec/file/mcp)
│   │   ├── memory/             # 短期/长期/向量记忆
│   │   ├── mcp/                # MCP server(标准工具接口)
│   │   ├── workers/            # Celery 异步任务
│   │   ├── realtime/           # WebSocket 进度推送
│   │   ├── sandbox/            # 代码执行沙箱(隔离)
│   │   └── utils/
│   └── tests/                  # 测试(unit/integration/e2e)
├── frontend/                   # 简单前端(实时进度展示,可选)
├── workspace/                  # Agent 代码执行工作区(动态生成,不提交)
└── data/
```

---

## 三、Git 仓库方案

- **仓库位置**:`/home/yangtuot/python-learning/forge`
- **默认分支**:`main`(稳定主干,永远可部署)

### 分支策略(trunk-based + 短分支)
- `main` — 稳定主干
- `feat/xxx`、`fix/xxx`、`refactor/xxx` — 短生命周期功能分支,做完 PR 合并

### 提交规范(Conventional Commits)
```
feat(agents): 实现规划者任务拆解
fix(sandbox): 修复代码沙箱进程隔离逃逸
refactor(api): 拆分 /tasks 路由到独立 router
test(workers): 补充 Celery 任务幂等测试
docs(architecture): 补充多 Agent 协调 ADR
chore(prod): 生产化配置
```

### 仓库初始化内容
- `.gitignore`(Python + 密钥 + workspace + 缓存)
- `README.md`(本文件)
- `data/docs/项目迭代路径.md`(迭代路线图)

---

## 四、后续代码提交计划

| 阶段 | 内容 | 提交组 |
|------|------|--------|
| **0 初始化** | 仓库骨架、CI、Makefile、目录占位 | `chore: 初始化项目骨架` |
| **1 后端地基** | pyproject、配置注入、PostgreSQL+Alembic、JWT+RBAC、Redis、分层架构 | `feat(core): 后端地基` 系列 |
| **1.1 脚手架** | pyproject.toml(依赖+工具)、Makefile(一键命令)、目录骨架、CI 骨架、占位测试 | `feat(core): 后端脚手架 + CI 骨架` |
| **1.2 配置注入** | .env.example + Settings 类(三层优先级)+ 测试 | `feat(core): 配置注入(pydantic-settings + .env)` |
| **1.3 数据库 + Alembic** | docker compose(pg+redis)、async SQLAlchemy 引擎、User 模型、alembic 迁移、DB 集成测试 | `feat(core): 数据库 + Alembic(async SQLAlchemy + asyncpg)` |
| **1.4 分层架构 + 首个路由** | main.py(app+lifespan)、api/v1 + schema/service/repository 四层落地、GET /api/v1/health、ASGI 测试 | `feat(core): 分层架构 + 首个路由(FastAPI app + /api/v1/health)` |
| **1.5 认证(JWT + RBAC)** | bcrypt 密码哈希、JWT 签发/校验、登录/注册/me 路由、get_current_user + require_roles RBAC 依赖 | `feat(core): 认证(JWT + bcrypt + RBAC)` |
| **1.6 Redis** | redis 客户端、cache-aside 缓存、/me 走缓存、SET NX EX 分布式锁 | `feat(core): Redis 缓存 + 分布式锁(阶段 1 收官)` |
| **2 Agent 核心** | Agent 基类、消息、单 Agent+Function Calling、规划、记忆 | `feat(agents): Agent 核心` 系列 |
| **3 多 Agent 协作** | 角色定义、协调器、消息传递、LangGraph、Human-in-the-loop | `feat(agents): 多 Agent 协作` 系列 |
| **4 工具生态+MCP** | 工具注册、MCP server、搜索/代码执行/文件工具、代码沙箱 | `feat(tools): 工具生态` 系列 |
| **5 异步+实时** | Celery 队列、多 worker、任务持久化、WebSocket、分布式锁 | `feat(workers): 异步实时` 系列 |
| **6 生产化** | 可观测、限流、测试补全、CI/CD、Docker Compose、文档 | `chore(prod): 生产化` 系列 |

每个阶段结束打一个 tag,便于回溯。

> 详细迭代路线(含每阶段知识点、产出、达标)见 `data/docs/项目迭代路径.md`。

---

## 快速开始

> 骨架搭建中,后续补充。

```bash
# 克隆后
cd forge
make dev        # 安装依赖 + 启动开发环境
make test       # 跑测试
make up         # docker compose 启动全部服务
```
