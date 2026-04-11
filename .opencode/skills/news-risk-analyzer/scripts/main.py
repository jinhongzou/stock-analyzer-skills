# -*- coding: utf-8 -*-
"""
News Risk Analyzer - 薄封装层
用法: python main.py <股票代码> [新闻数量] [--web]
选项:
  --web  同时使用Tavily网络检索获取更多舆情（更全面但更慢）
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core import analyze_news_risk, analyze_news_with_web


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    # 解析参数
    use_web = "--web" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    stock = args[0] if len(args) > 0 else "600519"
    limit = int(args[1]) if len(args) > 1 else 20

    # 获取股票名称
    from core import get_stock_profile

    profile = get_stock_profile(stock)
    stock_name = profile.get("名称", "") if profile else ""

    print("=" * 80)
    print(f"股票: {stock} {f'({stock_name})' if stock_name else ''}")
    from datetime import datetime

    print(f"获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"新闻数量: {limit}条")
    if use_web:
        print("网络检索: 已启用（Tavily）")
    print("=" * 80)

    try:
        if use_web and stock_name:
            # 使用综合分析（含网络检索）
            news = analyze_news_with_web(stock, stock_name, limit)
            print(f"\n【本地新闻（东方财富）】")
            print(
                f"风险统计: 🔴高风险 {news['high']}条 | 🟡中风险 {news['medium']}条 | 🟢低风险 {news['low']}条"
            )

            print(f"\n【网络舆情（Tavily）】")
            print(f"获取到 {news['total_web']} 条网络新闻")
            web_high = sum(1 for r in news.get("web_results", []) if r["level"] == "高")
            web_med = sum(1 for r in news.get("web_results", []) if r["level"] == "中")
            print(f"风险统计: 🔴高风险 {web_high}条 | 🟡中风险 {web_med}条")

            # 显示网络风险新闻
            if news.get("web_results"):
                print("\n网络风险新闻详情:")
                for i, alert in enumerate(news.get("web_results", [])[:10], 1):
                    print(f"\n[{i}] {alert['level']}风险 | {alert['type']}")
                    print(f"     标题: {alert['title'][:60]}...")
                    print(f"     关键词: {', '.join(alert['keywords'])}")
                    print(f"     来源: {alert['source'][:50]}...")
        else:
            # 仅使用本地新闻
            news = analyze_news_risk(stock, limit)
            print(
                f"\n风险统计: 🔴高风险 {news['high']}条 | 🟡中风险 {news['medium']}条 | 🟢低风险 {news['low']}条"
            )

        if news.get("integrity", 0) > 0 or (use_web and web_high > 0):
            total_integrity = news.get("integrity", 0) + (web_high if use_web else 0)
            print(f"\n⚠️  诚信风险提醒: {total_integrity}条新闻涉及诚信相关风险!")

        print("=" * 80)

        if not use_web:
            # 显示本地风险新闻
            for i, alert in enumerate(news.get("alerts", []), 1):
                print(f"\n[{i}] {alert['level']}风险 | {alert['type']}")
                print(f"     标题: {alert['title']}")
                print(f"     日期: {alert['date']}")
                print(f"     关键词: {', '.join(alert['keywords'])}")

        print("\n" + "=" * 80)
        print("风险等级说明:")
        print("  🔴 高风险: 可能严重影响股价（财务造假、监管处罚、诚信问题等）")
        print(
            "  🟡 中风险: 可能影响股价（业绩下滑、股东减持、行业政策变化、舆情投诉等）"
        )
        print("  🟢 低风险: 影响较小（日常经营、正面新闻等）")
        print("  ⚠️ 诚信风险: 涉及财务真实性、信披合规、高管诚信等核心信任问题")
        print("=" * 80)

    except Exception as e:
        print(f"分析失败: {e}")
