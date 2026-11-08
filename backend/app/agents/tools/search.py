"""搜索工具:查资料"""

import re

import httpx


def search(query: str, max_results: int = 3) -> str:
    """搜索网络,返回前N个结果标题"""
    try:
        resp = httpx.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        results = re.findall(r'class="result__a"[^>]*>([^<]+)</a>', resp.text)
        if not results:
            return f"搜索 '{query}' 无结果"
        top = results[:max_results]
        return "\n".join(f"{i + 1}.{r.strip()}" for i, r in enumerate(top))
    except Exception as e:
        return f"搜索错误:{e}"
