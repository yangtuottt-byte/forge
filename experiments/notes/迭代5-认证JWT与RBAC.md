# 迭代 5:认证(JWT + RBAC)(知识笔记)

> 日期:2026-11-05
> 产出:`app/core/security.py`(bcrypt 哈希 + JWT)、`app/schemas/user.py`、`app/repositories/user_repo.py`、`app/services/user_service.py`(register/login)、`app/api/deps.py`(get_current_user + require_roles)、`app/api/v1/auth.py`(register/login 路由)、`app/api/v1/users.py`(/me 路由)、`tests/test_auth.py`(认证流程测试)
> 对应路线图:阶段 1(后端地基)· 1.5 认证(JWT + RBAC)
> 提交:`feat(core): 认证(JWT + bcrypt + RBAC)`

---

## 一、学到的核心概念(用自己的话)

### 1. 密码哈希:只存哈希,不存明文 ⭐
- 数据库泄露 ≠ 用户密码泄露,因为哈希不可逆(bcrypt 天然加盐 + 慢)
- **旧写法 passlib + bcrypt 5.x 不兼容**(passlib 探测 `bcrypt.__about__` 已不存在)→ **现代实践:直接用 bcrypt 库**,代码更短:
```python
bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
bcrypt.checkpw(password.encode(), hash.encode())
```

### 2. JWT(JSON Web Token)⭐
- 结构:`header.payload.signature`,Base64 编码
- **无状态**:服务端不存 session,校验靠签名 + exp(过期时间)
- `sub` 必须是**字符串**(JWT 规范),所以 `{"sub": str(user.id)}`
- payload 里放业务数据(role),供路由做 RBAC

### 3. RBAC(基于角色访问控制)⭐
- 用户带 `role` 字段(user/admin)
- **依赖工厂模式**:`require_roles("admin")` 生成一个依赖函数,在路由参数上 `Depends(...)` 使用
- 不满足角色 → 403,不满足认证 → 401

### 4. FastAPI 依赖注入的"全家桶"
- `Depends(get_db)` → 每请求一个 session(1.3 就绪)
- `Depends(http_bearer)` → 自动从 Authorization 头提取 Bearer token
- `Depends(get_current_user)` → 校验 token + 查用户,返回当前用户对象
- **组合方式**:`Depends(require_roles("admin"))` 自动嵌套 `get_current_user`

### 5. HTTPBearer 的语义
- `HTTPBearer()` 实例作为依赖:**自动提取 + 校验 Authorization 头**,缺失时 401 "Not authenticated"
- `Depends(http_bearer)` 传入 `HTTPAuthorizationCredentials`(含 credentials=token 字符串)

---

## 二、关键代码模式

| 模式 | 代码 | 用在哪 |
|------|------|--------|
| bcrypt 哈希 | `bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()` | security.py |
| JWT 签发 | `jwt.encode(payload, secret, algorithm)` | security.py |
| JWT 校验 | `jwt.decode(token, secret, algorithms=[...])` | security.py |
| 过期时间 | `datetime.now(timezone.utc) + (expires_delta or default)` | security.py |
| 解析 Bearer 头 | `Depends(HTTPBearer())` | deps.py |
| 认证守卫 | `async def get_current_user(creds=Depends(http_bearer), session=Depends(get_db))` | deps.py |
| RBAC 工厂 | `def require_roles(*roles): async def dep(user=Depends(get_current_user))` | deps.py |
| 注册即登录 | register 成功 → 直接签发 token 返回 | user_service.py |
| 异常吞掉细节 | `except Exception: raise HTTPException(401, ...) from None` | deps.py |

---

## 三、踩坑记录(自己写代码时遇到的)

1. **⭐ passlib + bcrypt 5.x 不兼容**:passlib 1.7.4(2020 年后停更)探测 bcrypt 版本用 `bcrypt.__about__.__version__`,bcrypt 5.0 移除了 `__about__` → 探测失败 → 后端 fallback 逻辑崩 → `ValueError: password cannot be longer than 72 bytes`(明明密码才 7 字节!)。**教训:查依赖版本兼容性,老教程的 passlib 已死**。
2. **⭐ 运算符优先级:`+` 比 `or` 优先级高**:`datetime + expires_delta or default` 实际是 `(datetime + expires_delta) or default`,expires_delta=None 时直接 TypeError。**正确:加括号** `datetime + (expires_delta or default)`。
3. **路由前缀挂载不一致**:include_router 不带 prefix 时,路由路径是"挂载点前缀 + 路由定义",文档承诺 `/api/v1/auth/register` 实际挂成 `/api/v1/register`。**route 文档和挂载代码要同步**。
4. **测试数据隔离**:测试表残留数据 → 下一次测试邮箱冲突 400。**每个测试结束后清空测试表**(conftest fixture),这是测试隔离的标准做法。
5. **测试事件循环复用**(延续 1.4):conftest 里既有 engine.dispose() 又有清表,两个都要在同一个 async fixture 里做。
6. **ruff B904:raise from**:except 里 raise 必须显式 `from err` 或 `from None`。**`from None` = 故意吞掉原始异常细节**(不把签名错误细节暴露给调用方,安全上有意义)。
7. **ruff B008 vs FastAPI Depends**:`Depends(...)` 写在参数默认值里是 FastAPI 标准惯用法,ruff 规则冲突 → `extend-immutable-calls = ["fastapi.Depends"]` 精确放行(pyproject 配置)。

---

## 四、面试可能问

| 问题 | 答案要点 |
|------|---------|
| 密码为什么要哈希? | 单向函数不可逆,库泄露不等于密码泄露;bcrypt 加盐 + 慢(抗暴力破解) |
| bcrypt vs md5? | md5 快→暴力破解易;bcrypt 慢 + 加盐→抗 GPU/ASIC 暴力;md5 只用于校验完整性 |
| passlib 为什么不用? | 停更,与 bcrypt 5.x 不兼容;现代直接用 bcrypt 库 |
| JWT 原理? | header.payload.signature;无状态,校验靠签名+exp;服务端不存 session |
| JWT 有什么坑? | 无法主动注销(过期前一直有效);payload 不能放敏感数据(可解码);sub 必须是字符串 |
| RBAC 实现方式? | 依赖工厂:`require_roles(*roles)` 生成校验函数,在路由参数上 Depends;401 vs 403 语义 |
| HTTPBearer 的作用? | 自动从 Authorization: Bearer xxx 提取 token,缺失抛 401 |
| get_current_user 设计? | 解析 token → 查用户 → 返回 ORM 对象;异常统一 401,不暴露细节 |
| `from None` 的意义? | 抑制异常链显示——调用方看不到原始异常细节(签名错误具体信息),防信息泄露 |
| 注册为什么要直接返回 token? | 注册即登录,前端少一次请求;用户体验更好 |
| 测试数据隔离怎么做? | conftest 夹具:测试前后清空测试表;或每个测试用唯一数据 + 清理 |
| 测试时 bcrypt 慢怎么办? | bcrypt cost 参数可调低(测试环境用低 cost,生产 12-14) |

---

## 五、实验结果与校准

### 实验 5:认证全流程(`make test` + 手动 curl)
| 命令/操作 | 结果 |
|-----------|------|
| `make lint` | ✅ All checks passed(format 后) |
| `make test`(8 个测试) | ✅ 8 passed(含 auth 全流程 + DB + health + config) |
| 注册 `POST /api/v1/auth/register` | ✅ 201 + `{"access_token": "...", "token_type": "bearer"}` |
| 登录 `POST /api/v1/auth/login` | ✅ 200 + access_token |
| 错误密码登录 | ✅ 401 `{"detail": "邮箱或密码错误"}`(不暴露具体哪个错了,安全) |
| 带 token `GET /api/v1/users/me` | ✅ 200 + `{"id":33, "email":"e2e@forge.dev", "role":"user"}` |
| 不带 token 访问 /me | ✅ 401 `{"detail": "Not authenticated"}` |
| 伪造 token 访问 /me | ✅ 401 `{"detail": "无效或过期令牌"}` |

**结论**:
1. ✅ **认证全链路跑通**:注册→登录→带 token 访问受保护资源
2. ✅ **安全验证到位**:错误密码 401、缺失 token 401、伪造 token 401、不暴露具体错误细节
3. ✅ **测试隔离生效**:8 passed 全绿,测试间不再互相污染

**观察**:
- 密码哈希在测试中很快(bcrypt 默认 cost=12,约 0.2s 一次),生产可按需调
- JWT payload 里 role 允许客户端自证"我是 admin"——**生产环境绝不能信任 payload 里的角色,必须服务端重查数据库**(本迭代简化,后续阶段加)

---

## 六、下一步

- **迭代 6:Redis(缓存 + 分布式锁)**(阶段 1.6)
  - redis 客户端连接(redis 容器已起)
  - 缓存:给 /api/v1/users/me 加缓存(同一用户信息缓存 60s)
  - 分布式锁:用 `SET NX EX` 实现(防重复注册/防重复任务)
  - 测试:Redis 不可用时降级(和 DB 一样,环境感知)
- 阶段 1 后端地基全部闭环:脚手架 → 配置 → 数据库 → 分层 → 认证 → Redis
- 阶段 2 开始:Agent 核心(Agent 基类、Function Calling、规划、记忆)
- 迭代 5 核心已掌握:bcrypt 哈希、JWT 签发校验、RBAC 权限依赖、HTTPBearer 提取、注册即登录
