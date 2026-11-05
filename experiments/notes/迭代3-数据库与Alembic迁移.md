# 迭代 3:数据库 + Alembic(知识笔记)

> 日期:2026-11-05
> 产出:`docker-compose.yml`(pg+redis)、`backend/app/db/session.py`(async 引擎+Session)、`backend/app/models/base.py`(基类)、`backend/app/models/user.py`(users 表)、`backend/alembic/`(迁移)、`backend/tests/test_db.py`(集成测试)
> 对应路线图:阶段 1(后端地基)· 1.3 数据库 + Alembic
> 提交:`feat(core): 数据库 + Alembic(async SQLAlchemy + asyncpg)`

---

## 一、学到的核心概念(用自己的话)

### 1. ORM = 对象关系映射
- `User` 类 ↔ `users` 表;`user.email` ↔ `users.email` 列
- 你写 Python 对象,SQLAlchemy 翻译 SQL、管理连接池

### 2. async 引擎 + asyncpg
- PostgreSQL 驱动 `asyncpg` 是异步的;`create_async_engine(url, pool_pre_ping=True, ...)`
- **海死连接**:pool 是连接池,连接可能因超时被 PG 掐掉;`pool_pre_ping=True` 取连接前先 ping 一下,防"server gone away"

### 3. Session = 会话(对话窗口)
- `async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)`
- 每个操作一个 session;FastAPI 用 `yield` 注入,请求结束归还池里

### 4. 三层架构:Model → migration → 真实表
- **Model**(Python 类)↔ **migration**(版本文件)↔ **数据库表**(PG)
- 三方必须一致:改模型 → `alembic revision --autogenerate` → `alembic upgrade head` → 表结构更新

### 5. Alembic 原理
- 每次模型变化生成**版本文件** (`versions/xxx.py`,中文内容 `upgrade()`/`downgrade()`对称)
- `alembic upgrade head`:按版本链升级;`alembic downgrade -1`:回退
- 库中 `alembic_version` 表记录当前版本号
- **生产意义**:代码版本和 DB 版本永远同步,不会"忘了哪台机器改过哪张表"

---

## 二、关键代码模式

| 模式 | 代码 | 用在哪 |
|------|------|--------|
| async 引擎 | `create_async_engine(settings.database_url, pool_pre_ping=True, pool_size=5, max_overflow=10)` | db/session.py |
| Session 工厂 | `async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)` | db/session.py |
| 依赖注入 | `async def get_db()` 里 `yield session`(FastAPI 生命周期) | db/session.py |
| DeclarativeBase | `class Base(DeclarativeBase)` 作所有模型基类 | models/base.py |
| 模型字段 | `Mapped[int] = mapped_column(primary_key=True)`(2.0 类型注解写法) | models/user.py |
| 自动建表(migration) | `alembic revision --autogenerate -m "..."`(Autogenerate 生成版本文件) | alembic/ |
| 测试环境感知 | `try: connect → except: pytest.skip("...")`(CI 没有 PG 时跳过) | tests/test_db.py |
| 测试自己收拾 | 插入后 `delete(row)` + commit,保证可重复跑 | tests/test_db.py |

---

## 三、踩坑记录(自己写代码时遇到的)

1. **save 后 lint 仍报 W293 空行带空格**:编辑器(如 vscode)空行可能被填了空格 → `make format` 修(空行不要留空格,工具会管)
2. **`alembic env.py` 默认同步**:生成的 env.py 用同步引擎写法,要换成 async(`connection.run_sync(do_run_migrations)`),否则 PG 迁移报错(原模板我改好了)
3. **pg 镜像白名单**:conda 的镜像源 DaoCloud 有白名单机制,`postgres:16-alpine` 被拒,但 `postgres:16` 放行——tag 粒度挡,改 tag 解决
4. **测试直接操作真实库**:写库后如果没清理,第二次跑测试会撞车(唯一约束/残留数据);解决:测试里**先探测连接,失败就 skip**;跑完自己 delete 清理
5. **`make test` 与 docker 权限**:编辑 shell 没有 Docker 成员资格时跑 docker 命令报 permission denied → 用 `sg docker -c "docker compose ps"` 或 `sudo docker`(处理方式:改 /etc/group 加 docker 用户组 + 重启 shell)
6. **Alembic 版本文件中文注释**:alembic autogenerate 生成的代码带阿里注释的真实 PG 提交(create date / revision id / down_revision(Must be None for initial revision),正常)

---

## 四、面试可能问

| 问题 | 答案要点 |
|------|---------|
| ORM 是什么? | Python 对象 ↔ 数据库表,框架自动翻译 SQL |
| SQLAlchemy async 与 sync 区别? | 驱动不同(asyncpg vs psycopg2);async 可配合 FastAPI 的 async context |
| Session 的作用? | 管理事务(commit/rollback)、连接池、生命周期;每请求一个 session |
| create_async_engine 为什么设 pool_size/pool_pre_ping? | 连接池防创建太勤;pre_ping 防 server gone away |
| pool_size 和 max_overflow? | pool_size=常驻连接数;max_overflow=最多临时扩到 pool_size + max_overflow |
| Alembic 的原理? | 模型变化 → autogenerate 生成迁移文件 → upgrade 链式应用 + alembic_version 记录版本 |
| 什么是 autogenerate? | 对比模型 schema 与当前库 schema 三代差异生成 DDL(自动控制升降攻击) |
| 为什么用 versioned revision 而不是手动 DDL? | 可靠版本管理,团队协同不变、可调尧、可回滚 |
| 如何回滚迁移? | `alembic downgrade -1` 回退一个版本 |
| 集成测试为什么会假红? | 依赖外部服务;解决:环境探测 + skip;测试跑完删除自己立的河 |
| 测试里的 alice 为什么每次 id 不同? | `id` 是自增主键(primary_key=True),每次自增 |

---

## 五、实验结果与校准

### 实验 3:数据库 + Alembic(`make test`)
| 命令 | 结果 |
|------|------|
| `docker compose up -d`(pg + redis) | ✅ forge-pg-1 Up (healthy),forge-redis-1 Up(运行中 redis) |
| `docker compose ps` | ✅ pg healthy,redis running |
| `alembic upgrade head`(执行迁移) | ✅ Running upgrade -> 4ccdaa4dddf4 |
| `docker compose exec pg psql "\dt"`(看表) | ✅ `alembic_version` + `users`(5 列 id/email/password_hash/role/created_at) |
| `alembic revision --autogenerate -m "..."` | ✅ "Detected added table 'users'",生成 `versions/4ccdaa4dddf4_create_users_table.py` |
| `make lint` | ✅ All checks passed |
| `make test`(5 个测试:test_db+config) | ✅ 5 passed(含 DB 集成:插入→读出→删除) |

**结论**:
1. ✅ **async ORM 工作**:User(email+role)真实写 PG、自增主键、UUID 读回
2. ✅ **Alembic 全过程跑通**:生成迁移→升级→真实表里 alembic_version=版本号一致
3. ✅ **migration 文件对称**:`upgrade()` 建表 + `downgrade()` 删表,可回滚

**观察**:
- 多个环境下迁移链可移植:任一台机器 clone 代码 + `alembic upgrade head`,表结构与 models 一致
- `make format` 每次都报 editor 的尾随空格;以后**写完一个文件先跑 `make format`**(自己定的纪律)

---

## 六、下一步

- **迭代 4:分层架构 + 首个路由**(阶段 1.4)
  - FastAPI 入口 `main.py` + 生命周期管理(`async def lifespan`)
  - `api/v1/` 路由层 + `services/` 业务层 + `repositories/`(数据访问层)
  - 第一个路由 `GET /api/v1/health`,通过 testclient 验证
  - 依赖注入:get_db 作为服务依赖注入 router(async 请求挂一个 session)
- 迭代3 核心已掌握:engine/session 分层、Alembic 版本管理、集成测试环境感知 + 自免
