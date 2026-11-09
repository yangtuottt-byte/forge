# Forge 前端(MVP 核心闭环)

为后端补一个前端,打通「提交研发任务 → 多 Agent 协作 → 实时进度 → 交付结果」的完整闭环,
使 Forge 成为一个**可运行、可演示**的旗舰级练手项目。

## 1. 技术栈

| 关注 | 选型 | 理由 |
|------|------|------|
| 框架 | React 18 | 主流、生态成熟,适合展示前端工程化 |
| 构建 | Vite 5 | dev 体验快、配置简洁、原生 ESM |
| 类型 | TypeScript 5 | 与后端一致,类型安全教学 |
| 样式 | Tailwind CSS 3 | 原子类、快速构建统一界面 |
| 数据 | @tanstack/react-query 5 | 缓存/重试/loading/error 行业标准 |
| 路由 | react-router-dom 6 | 受保护路由 + 重定向 |
| 图标 | lucide-react | 轻量图标 |
| 测试 | Vitest + Testing Library | 与 Vite 配套,jsdom 环境 |
| 部署 | nginx:alpine(Docker 多阶段) | 托管静态 + 同源反代 |

> 故意不引 Redux / Socket.io:react-query + Context 已足够;后端 WS 是原生 WebSocket,客户端原生对接即可,不引 socket.io。

## 2. 目录结构

```
frontend/
├── package.json / tsconfig*.json / vite.config.ts / vitest.config.ts
├── tailwind.config.js / postcss.config.js / .eslintrc.cjs
├── Dockerfile / nginx.conf / .dockerignore / .env.example
└── src/
    ├── main.tsx            # 入口:QueryClient + AuthProvider + BrowserRouter
    ├── App.tsx             # 路由表
    ├── api/                # types + client(fetch 封装) + auth + tasks
    ├── lib/                # apiBase(API_BASE/wsBase) + cn(类名合并)
    ├── auth/               # context.ts + useAuth.ts + AuthProvider.tsx + ProtectedRoute
    ├── realtime/           # useTaskProgress(WebSocket hook)
    ├── components/         # Layout / Button / Input / TaskProgress / TaskResult
    ├── pages/              # Login / Register / Dashboard
    └── test/               # vitest setup(jest-dom)
```

## 3. 与后端 API 对接

| 后端端点 | 方法 | 前端实现 | 鉴权 |
|----------|------|----------|------|
| `/api/v1/auth/register` | POST | `api/auth.ts register` | 无 |
| `/api/v1/auth/login` | POST | `api/auth.ts login` | 无 |
| `/api/v1/users/me` | GET | `api/auth.ts getMe` | Bearer |
| `/api/v1/tasks?goal=` | POST | `api/tasks.ts createTask` | 无(当前) |
| `/api/v1/tasks/{id}` | GET | `api/tasks.ts getTask` | 无(当前) |
| `/api/v1/tasks/{id}/ws` | WS | `realtime/useTaskProgress` | query token(当前不校验) |

- `api/client.ts` 统一封装 fetch:自动注入 `Authorization`,JSON 处理,401 清 token,非 2xx 抛 `ApiError`(带后端 detail)。
- API 基础地址 `lib/apiBase.ts`:dev 默认 `http://localhost:8000/api/v1`;prod 经 nginx 设相对 `/api/v1`(Dockerfile 注入)。用 `||` 兜底,空串回退默认。

## 4. 认证

- token 存 `localStorage.forge_token`,user 内存态。
- `AuthProvider` 挂载时若有 token 则 `GET /auth/me` 恢复用户(刷新保持登录态)。
- `ProtectedRoute` 无 token 跳 `/login`;登录/注册成功后跳目标(默认 `/dashboard`)。
- `Layout` 顶栏显示当前邮箱 + 退出登录。

## 5. WebSocket 实时进度

后端链路:Worker `publish_progress` → Redis pub/sub → API 订阅转发 → 前端。
下行帧 JSON `{ status, progress }`,`status ∈ pending/running/done/failed`。

前端 `realtime/useTaskProgress.ts` 是一个原生 WebSocket hook,具备:

- 连接 `/tasks/{id}/ws?token=xxx`(token 走 query,为后续后端强校验留口)
- 异常断开**指数退避重连**(1s → 10s 上限);**完成/失败收口**后关闭不再重连
- `onopen` 时先 `GET /tasks/{id}` 同步一次当前状态,防止任务已先完成而错过订阅
- 与 react-query 分工:REST 数据走 query,WS 推送走独立 hook

## 6. 任务状态机

`pending → running(progress 0→100) → done / failed`

## 7. 开发

```bash
make dev-frontend      # 一键起前端 dev
# 等价于
cd frontend && npm install && npm run dev   # http://localhost:5173
```

`make test-frontend` / `make lint-frontend` / `make build-frontend`。

## 8. 部署(docker)

`frontend` 服务多阶段构建:node 编译 → nginx 托管 `dist` + 同源反代。
`nginx.conf` 路由:

- `location /` SPA 历史路由 fallback 到 `index.html`
- `location /api/` REST 反代到 `api:8000`
- `location /api/v1/tasks/` WebSocket 升级反代(`Upgrade`/`Connection`)

生产 `VITE_API_URL=/api/v1`(相对同源,规避跨域)。

```bash
docker compose up -d --build   # 起 api + worker + pg + redis + frontend
# 前端 http://localhost:5173
docker compose logs -f frontend
docker compose down
```

## 9. 测试

Vitest + jsdom + Testing Library,`build/lint/test` 全绿,共 10 项用例:

- `apiBase`:默认值 / `toWsBase`
- `Login` 表单空提交校验
- `TaskProgress` 渲染
- `useTaskProgress` 状态机(WebSocket mock,5 用例:初始态/URL/流转/onFinished/完成后不重连)

## 10. 后续迭代(明确不做,记入路线)

- 多 Agent 协作阶段可视化(规划→研究→执行→审查)
- 任务历史列表 / workspace 工件查看
- 用户 / 计费页
- WebSocket token 强校验、消息确认(ack)
- Redux(对象状态本就够用,避免过度设计)
