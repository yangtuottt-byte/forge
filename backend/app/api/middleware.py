"""限流中间件:限制每个客户端请求频率(纯 ASGI)"""
from collections import defaultdict
from time import time

from fastapi.responses import JSONResponse

# 滑动窗口限流:记录每个客户端的请求时间戳
_requests: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware:
    """简单限流:每客户端每秒最多 N 次(纯 ASGI 中间件)

    ⭐ FastAPI add_middleware 期望纯 ASGI:__call__(scope, receive, send)
    Starlette 风格(__call__(request, call_next))要用 BaseHTTPMiddleware
    """

    def __init__(self, app, max_requests: int = 10, window: int = 1):
        self.app = app
        self.max_requests = max_requests
        self.window = window

    async def __call__(self, scope, receive, send):
        # 非 HTTP 请求(如 websocket)直接放行
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        client = scope.get("client", (None, 0))[0]
        now = time()
        # ⭐ 滑动窗口:只保留 window 秒内的请求
        _requests[client] = [t for t in _requests[client] if now - t < self.window]
        if len(_requests[client]) >= self.max_requests:
            # 返回 429
            response = JSONResponse({"error": "Too Many Requests"}, status_code=429)
            await response(scope, receive, send)
            return
        _requests[client].append(now)
        await self.app(scope, receive, send)
