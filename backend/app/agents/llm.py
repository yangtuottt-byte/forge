"""
LLM 客户端封装:调 OpenAI 兼容 API
为什么封装:每个 Agent 都要调 LLM,把"怎么调"集中一处
换模型/换 API 只改配置,Agent 代码不动
"""

from openai import AsyncOpenAI

from app.core.config import get_settings

settings = get_settings()

# 全局客户端:避免反复连接,复用连接池
client = AsyncOpenAI(
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
)

MODEL = settings.llm_model


def reset_client() -> None:
    """重建全局 client(测试用:每个测试前重置,避免事件循环串线)

    ⭐ 为什么不用 close():close 是永久关闭,后续请求报错"client has been closed"
       重建 = 每个测试拿全新 client,连接池空,绑定当前 loop
    """
    global client
    client = AsyncOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )


async def chat(
    messages: list[dict],
    tools: list[dict] | None = None,
    temperature: float = 0.7,
):
    """非流式调用:一次性返回完整回复

    Args:
        messages: 对话历史 [{"role": "user", "content": "..."}, ...]
        tools: 工具清单(None = 不启用工具)
        temperature: 创造性(0=严谨,1=发散)
    Returns:
        完整回复对象(含 content / tool_calls)
    """
    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        tools=tools,
        stream=False,
    )
    return response.choices[0].message


async def chat_stream(
    messages: list[dict],
    tools: list[dict] | None = None,
    temperature: float = 0.7,
):
    """流式调用:逐段 yield(async generator)

    ⭐ 为什么和 chat 拆开:函数里一旦有 yield 就变成 generator,
       generator 不能 return 带值——所以流式和非流式不能混在一个函数
    """
    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        tools=tools,
        stream=True,
    )
    async for chunk in response:
        yield chunk


async def chat_text(messages: list[dict], **kwargs) -> str:
    """便捷方法:只要文本内容(非流式)"""
    msg = await chat(messages, **kwargs)
    return msg.content or ""
