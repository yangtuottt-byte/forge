# 迭代 1:后端脚手架与 CI(知识笔记)

> 日期:2026-11-05
> 产出:`backend/pyproject.toml`(依赖+工具配置)、根 `Makefile`(一键命令)、`.github/workflows/ci.yml`(CI 骨架)、`backend/app/` 目录骨架、`backend/tests/` 占位测试、`backend/.gitignore`
> 对应路线图:阶段 1(后端地基)· 1.1 脚手架 + 阶段 0 欠的 CI/CD
> 提交:`feat(core): 后端脚手架 + CI 骨架`

---

## 一、学到的核心概念(用自己的话)

### 1. pyproject.toml = Python 项目的"身份证 + 依赖清单 + 工具配置"三合一 ⭐
- 以前老项目用 `requirements.txt` + 各种散配置文件;现在 PEP 621 统一到 `pyproject.toml`:
  - `[project]` 管**元信息 + 依赖版本**(谁、什么版本、依赖什么)
  - `[project.optional-dependencies]` 管**可选组**(如 dev 组:只写代码测试需要,不进生产)
  - `[tool.ruff]` / `[tool.pytest.ini_options]` 管**工具配置**(lint 规则、pytest 行为)
- `pip install -e ".[dev]"` 中:
  - `-e` = editable(可编辑安装,改源码直接生效,不用重装)
  - `[dev]` = 安装 dev 可选组
  - **引号必须加**(方括号是 glob 语义,不引号会被 shell 吞)

### 2. Makefile = 命令快捷方式 + 团队约定
- `make dev` 背后是一串命令(建 venv → 装依赖),别人不用再记一遍命令长什么样
- **最关键的坑**:规则行前必须是 **Tab** 不是空格(Make 的语法要求,空格会报 `missing separator`)
- `# 后面的注释是文档字符串`(make 里 `##` 被某些工具当 help 文本)

### 3. CI(GitHub Actions)= 自动化的"守门员"
- push / 发 PR → GitHub 拉干净环境 → 安装依赖 → lint → test → 绿/红
- **五个步骤按顺序**:`checkout`(拉代码)→ `setup-python`(装环境)→ `Install`(装依赖)→ `Lint` → `Test`
- 好处:不用人肉检查"这代码规范吗/测试过吗";**CI 不过 = 不能合并**,这是生产级底线
- CI 里跑的命令 = 根 Makefile 里的命令(**本地和 CI 同一套命令**,避免"我机器上能跑")

### 4. 虚拟环境(venv)隔离依赖
- 项目依赖装到 `backend/.venv/` 里,不污染系统 Python
- `backend/.gitignore` 必须忽略 ``.venv/``——环境是每机器生成的,不入库

### 5. 分层目录骨架的价值
- `app/`, `app/core/`(配置/日志/安全)、`app/api/v1/`(路由)、`app/services/`(业务)、`app/repositories/`(数据访问)、`app/models/`(ORM)、`app/agents/`、`app/tools/`、`app/workers/`、`app/realtime/`、`app/sandbox/`——**现在全是空的 `__init__.py`,但结构先立好,后面每阶段往里填,不会乱**
- **根 `.gitignore` 和 `backend/.gitignore` 双层保险**:根忽略 workspace/、.env 等,backend 忽略 `.venv`、`__pycache__` 等常规 Python 产物

---

## 二、关键代码模式

| 模式 | 代码 | 用在哪 |
|------|------|--------|
| 依赖清单 | `[project] dependencies = ["fastapi>=...", ...]` | pyproject.toml |
| dev 可选组 | `[project.optional-dependencies] dev = ["ruff", "pytest"]` | pyproject.toml |
| 工具配置 | `[tool.ruff] select = ["E","F","I","UP"]` / `[tool.pytest.ini_options] asyncio_mode = "auto"` | pyproject.toml |
| 一键命令 | `dev: cd backend && venv && pip install -e ".[dev]"` | Makefile(**Tab** 缩进) |
| CI 五步 | checkout → setup-python → install deps → lint → test | .github/workflows/ci.yml |
| 占位测试 | `def test_placeholder(): assert True` | tests/(DB 没做前先保证 CI 不空转) |

---

## 三、踩坑记录(自己写代码时遇到的)

1. **⭐ Makefile 缩进必须是 Tab 而不是空格**——手写编辑器里的空格缩进,`make` 秒报 `missing separator`;**检查方法**:`cat -A Makefile` 看有没有 `^I` 标记(没有就是空格)
2. **⭐ `.github/workflows/` 必须在仓库根目录**,放在 `backend/.github/` 里 GitHub 永远不会触发(CI 是"看不见"的)
3. **`test` vs `tests` 目录命名不一致**:pyproject `testpaths = ["tests"]`,pytest 找不到就报错——**配置和目录名必须一致**
4. **ruff 格式化检查会报"需要重排空行"**:写占位测试时两行空行、格式不标准,`make format` 自动修——**格式让工具管,别手写较劲**
5. **`pip install -e ".[dev]"` 引号不能少**(方括号是 glob 语义)
6. **CI 命令 = Make 命令**(本地 `make lint` 过不了,CI 一定过不了——两边共用一套命令)
7. **`backend/.gitignore` 别忽略自己的 `ruff.toml`**(项目从 pyproject.toml 读 ruff 配置,忽略 ruff.toml 是多余但无害的)

> CI 的价值在这里体现:**任何一次改动,本地和 CI 跑同一套命令**,红就是红,不存在"我机器上能跑"。

---

## 四、面试可能问

| 问题 | 答案要点 |
|------|---------|
| pyproject.toml 有什么用?为什么不用 requirements.txt? | 统一管理元信息+依赖+工具配置(PEP 621);requirements 只管依赖,工具配置散落在多个文件 |
| `pip install -e ".[dev]"` 里 -e 和 [dev] 是什么? | -e 可编辑安装(改源码即生效);[dev] 选装 dev 可选组 |
| 为什么要 Makefile? | 一键命令、团队约定、CI 复用同一套命令 |
| Makefile 为什么缩进不能用空格? | GNU Make 语法规定规则行前必须是 Tab;空格报 missing separator |
| CI 的作用和流程? | 自动化守门:push/PR 触发 → checkout → setup 环境 → 装依赖 → lint → test;绿=能合,红=禁止合并 |
| 为什么 .env 不能进 Git? | 密钥(数据库密码、API Key)入库 = 泄露;用 .gitignore 拦住 |
| 为什么 CI 里跑的命令要和本地一致? | 避免"我机器上能跑"的经典坑;本地 make lint 过不了,CI 也过不了 |
| venv 为什么要忽略? | 依赖是每机器生成的,直接从环境生成 .venv 各种系统/Python 版本不一致 |
| ruff 和 flake8+black 的区别? | 同一工具做 lint+format,配置一套搞定;不用在两个工具间对齐版本 |

---

## 五、实验结果与校准

### 实验 1:脚手架(`make dev` / `make lint` / `make test`)
| 命令 | 结果 |
|------|------|
| `make dev`(建 venv + 装依赖 48+ 包) | ✅ 成功(清华镜像,快) |
| `make lint`(ruff check) | ✅ All checks passed |
| `make format`(自动修格式) | ✅ 1 file reformatted,17 unchanged |
| `make test`(pytest) | ✅ 1 passed in 0.01s |

**结论**:
1. ✅ **脚手架可跑**:创建虚拟环境 → 安装 48+ 依赖 → lint/format/test 全绿
2. ✅ **CI 骨架就绪**:GitHub Actions 五步流程(装环境 → lint → format check → test)
3. ✅ **目录骨架立起来**:`app/` 下 13 个子目录空 `__init__.py`,后续阶段直接往里填代码

**观察**:
- 版本锁 log 里 fastapi-0.162.0、pydantic-2.14.2、ruff-0.17.3 —— `>=` 不锁精确版本,生产项目要 `pip lock` 或用 constraints 锁死
- .ruff_cache 会被忽略(.gitignore 里有),egg-info 也是

---

## 六、下一步

- **迭代 2:配置注入**(阶段 1.2)
  - `.env` + `pydantic-settings`,把配置从硬编码改为环境注入
  - `app/core/config.py` 写配置对象,分层 dev/prod
  - 把数据库连接、JWT 密钥等交给配置管
- 迭代 1 核心已掌握:pyproject(依赖+工具)、Makefile(一键命令)、CI(自动化守门)、目录分层,脚手架可跑、CI 全绿
