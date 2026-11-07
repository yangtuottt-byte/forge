# 迭代 6:Redis(缓存 + 分布式锁)(知识笔记)

> 日期:2026-11-06
> 产出:`app/core/redis.py`(redis 客户端)、`app/core/cache.py`(缓存 + 锁工具)、`app/services/user_service.py`(get_user_me 带缓存)、`app/api/v1/users.py`(/me 走缓存)、`tests/test_redis.py`(redis 测试)、`tests/conftest.py`(redis 连接池隔离)
> 对应路线图:阶段 1(后端地基)· 1.6 Redis(缓存 + 分布式锁)
> 提交:`feat(core): Redis 缓存 + 分布式锁(阶段 1 收官)`

---

## 一、学到的核心概念(用自己的话)

### 1. Redis 是什么、为什么需要
- **内存数据库**,读写比 PG 快 100 倍以上
- 两个用途:
  - **缓存**:热点数据放内存,DB 查询变 redis GET(微秒级)
  - **分布式锁**:多服务实例互斥访问同一资源

### 2. 缓存读写流程(cache-aside)⭐
```
读请求 → 查 redis → 命中?返回 ✅
              ↓ miss
        查 DB → 返回 + 回填缓存(带 TTL)
```
- **回填 + TTL**:防止缓存雪崩(DB 全挂时缓存也不永久失效);数据变更时主动删缓存

### 3. 分布式锁 = SET NX EX ⭐
- `SET key value NX EX ttl` 是**单命令原子**(redis 单线程),不用 check-then-set(有竞态窗口)
- NX=只有 key 不存在才设;EX=自动过期防死锁
- 释放:`DEL key`(简单版;生产用 Lua 脚本保证"判断持有者+删除"原子)

### 4. 缓存只优化"读",认证是"写"依赖 ⭐(重要架构观察)
- `/me` 走缓存后,PG 挂了 /me 仍然 500——因为 **get_current_user 校验 token 必须查 DB 确认用户存在**
- **无状态 JWT 的代价**:服务端不存会话,每个请求都要查 DB 确认身份
- 想让 PG 挂了还能用:token 校验不查 DB(JWT 里带用户信息,或用 redis session)
- 教学结论:**缓存优化的是数据读取路径,认证/授权是控制路径,两者要分开看**

### 5. redis.asyncio 连接池也有事件循环绑定问题 ⭐
- 和 SQLAlchemy engine 一模一样:连接池里的连接"记住"第一个 loop
- 解法:conftest 里每个测试前后 `redis_client.aclose()`
- **统一教训:任何异步客户端的连接池都要在测试间清理**

---

## 二、关键代码模式

| 模式 | 代码 | 用在哪 |
|------|------|--------|
| 异步客户端 | `redis.asyncio.from_url(url, decode_responses=True)` | redis.py |
| 读缓存 | `await redis_client.get(key)` | cache.py |
| 写缓存 + TTL | `await redis_client.set(key, value, ex=ttl)` | cache.py |
| 分布式锁 | `redis_client.set(name, "locked", nx=True, ex=expire)` | cache.py |
| 释放锁 | `redis_client.delete(name)` | cache.py |
| cache-aside | 查 redis → miss 查 DB → 回填 | user_service.py |
| 连接池清理 | `await redis_client.aclose()` | conftest.py |

---

## 三、踩坑记录(自己写代码时遇到的)

1. **容器全没了**:`docker compose ps` 空表——PG/Redis 容器被停,所有连库测试 ConnectionRefused。**教训:长时间不操作,docker 容器可能被系统回收**;发现后 `docker compose up -d` 重启即可。
2. **async fixture 不支持 scope="module"**:pytest-asyncio 在 auto 模式下只支持 function scope,`scope="module"` 会 ScopeMismatch。**教训:async fixture 别乱写 scope**。
3. **redis 连接池事件循环绑定**:前两个 redis 测试过、后两个说"Redis 未运行"——同 SQLAlchemy engine 的坑。**解法:conftest 里 redis_client.aclose()**。
4. **JWT 密钥长度告警**:`InsecureKeyLengthWarning: HMAC key 20 bytes < 32 bytes`(RFC 7518 要求 32+ 字节)。**修法:.env.example 和默认值都改长;生产用 `secrets.token_urlsafe(48)` 生成**。

---

## 四、面试可能问

| 问题 | 答案要点 |
|------|---------|
| Redis 为什么快? | 内存存储,单线程避免锁竞争;I/O 多路复用
| 缓存穿透/击穿/雪崩? | 穿透:查不存在的数据(布隆过滤器/空值缓存);击穿:热点 key 过期(互斥锁);雪崩:大量 key 同时过期(随机 TTL)
| 什么是 cache-aside? | 读时先查缓存,miss 查 DB 回填;写时先更新 DB 再删缓存
| 分布式锁怎么实现? | SET key value NX EX ttl 原子;释放用 Lua 脚本保证原子性(检查持有者+删除)
| 为什么用 SET NX EX 而不是先检查再 set? | 两步操作有竞态窗口(check-then-set),单命令原子无窗口 |
| 锁过期了怎么办? | 业务超时没执行完,锁过期被释放,下一个请求拿到锁——两个请求并发(生产用看门狗续期)
| JWT 密钥要多长? | SHA256 至少 32 字节(RFC 7518);生成用 secrets.token_urlsafe(48)
| 缓存只优化什么? | 数据读取路径;认证/授权是控制路径,缓存不影响它(PG 挂了认证仍挂)
| redis.asyncio 和 sync 客户端? | async 不阻塞事件循环,适合 FastAPI;sync 用于脚本/后台任务
| 为什么测试里要 aclose redis? | 连接池绑定事件循环,不清池后续测试连不上 |

---

## 五、实验结果与校准

### 实验 6:Redis 缓存 + 分布式锁
| 命令/操作 | 结果 |
|-----------|------|
| `make test` | ✅ 12 passed(8 原有 + 4 redis:ping/cache/lock/ttl) |
| 注册用户拿 token | ✅ |
| 第一次 /me | ✅ 200 + 用户信息(miss → 回填) |
| `redis-cli KEYS 'user:*'` | ✅ `user:40` 缓存存在 |
| 第二次 /me | ✅ 200(命中缓存) |
| 停 PG 后 /me | ❌ 500(认证查 DB 失败——缓存只优化读路径,教学发现) |

**结论**:
1. ✅ **缓存生效**:cache-aside 全流程(miss → 回填 → 命中)验证通过
2. ✅ **分布式锁验证**:锁互斥(第二个抢不到)、释放后可抢
3. ✅ **测试基础设施**:redis 连接池清理解决事件循环串线
4. ✅ **阶段 1 收官**:脚手架 → 配置 → 数据库 → 分层 → 认证 → Redis 全部闭环

**观察**:
- PG 挂了 /me 500,证明认证是控制路径——这是无状态 JWT 的真实代价,未来阶段可优化(如 redis session 或 token 内嵌用户信息)
- 缓存 key 命名规范 `user:{id}`,TTL 60s——生产按业务调整

---

## 六、下一步

- **阶段 1 完成**:后端地基全部闭环!✅✅✅✅✅✅
- **阶段 2:Agent 核心**(项目灵魂):
  - Agent 基类设计(消息、状态、记忆接口)
  - 单 Agent + Function Calling(让 LLM 调工具)
  - 规划:ReAct / Plan-and-Execute(任务拆解)
  - 记忆:短期(内存) + 长期(PGVector)
  - 流式输出(Agent 过程实时展示)
- 迭代 6 核心已掌握:cache-aside 缓存、SET NX EX 分布式锁、redis.asyncio、连接池隔离、JWT 密钥安全
- 观察点:缓存一致性(DB 更新后删缓存的时机)、锁续期(看门狗)留待后续
