# -*- coding: utf-8 -*-
"""
Web Search - Tavily 网络检索
用法: python main.py <搜索关键词>
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from tavily import TavilyClient


# API Key (从环境变量获取，更安全)
API_KEY = os.environ.get("TAVILY_API_KEY", "")


def web_search(query: str, max_results: int = 10) -> dict:
    """
    使用 Tavily 进行网络检索

    参数:
        query: 搜索关键词
        max_results: 最大结果数，默认10

    返回:
        {results: [{title, content, url, score}, ...], answer: str}
    """
    client = TavilyClient(api_key=API_KEY)

    try:
        response = client.search(
            query=query,
            max_results=max_results,
            include_answer=True,
            include_raw_content=False,
        )

        if "results" in response or "answer" in response:
            return {"status": "ok", **response}
        else:
            return {"status": "error", "message": "未找到结果", "raw": response}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def format_search_results(results: dict) -> str:
    """格式化搜索结果输出"""

    if results.get("status") != "ok":
        return f"搜索失败: {results.get('message', '未知错误')}"

    output = []
    output.append("=" * 60)
    output.append(f"搜索结果")
    output.append("=" * 60)

    # 优先显示 answer（如果存在）
    if results.get("answer"):
        output.append(f"\n【摘要】{results['answer']}")
        output.append("")

    # 显示详细结果
    items = results.get("results", [])
    if items:
        output.append("【详细信息】")
        for i, item in enumerate(items, 1):
            title = item.get("title", "N/A")
            content = item.get("content", "")[:200]  # 限制长度
            url = item.get("url", "N/A")

            output.append(f"\n[{i}] {title}")
            output.append(f"    {content}...")
            output.append(f"    来源: {url}")

    if not items and not results.get("answer"):
        output.append("\n未找到相关结果")

    return "\n".join(output)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) < 2:
        print("用法: python main.py <搜索关键词>")
        print('示例: python main.py "A股市场 2026"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"正在搜索: {query}")

    results = web_search(query)
    print(format_search_results(results))
