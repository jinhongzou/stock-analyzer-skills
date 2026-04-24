# -*- coding: utf-8 -*-
"""
News Risk Analyzer - 薄封装层
用法: python main.py <股票代码> [新闻数量]
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core import analyze_news_risk


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    stock = sys.argv[1] if len(sys.argv) > 1 else "600519"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    print("=" * 80)
    print(f"股票: {stock}")
    from datetime import datetime

    print(f"获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"新闻数量: {limit}条")
    print("=" * 80)

    try:
        news = analyze_news_risk(stock, limit)

        print(
            f"\n风险统计: 🔴高风险 {news['high']}条 | 🟡中风险 {news['medium']}条 | 🟢低风险 {news['low']}条"
        )
        if news["integrity"] > 0:
            print(f"⚠️  诚信风险提醒: {news['integrity']}条新闻涉及诚信相关风险!")
        print("=" * 80)

        for i, alert in enumerate(news.get("alerts", []), 1):
            print(f"\n[{i}] {alert['level']}风险 | {alert['type']}")
            print(f"     标题: {alert['title']}")
            print(f"     日期: {alert['date']}")
            print(f"     关键词: {', '.join(alert['keywords'])}")

        print("\n" + "=" * 80)
        print("风险等级说明:")
        print("  🔴 高风险: 可能严重影响股价（财务造假、监管处罚、诚信问题等）")
        print("  🟡 中风险: 可能影响股价（业绩下滑、股东减持、行业政策变化等）")
        print("  🟢 低风险: 影响较小（日常经营、正面新闻等）")
        print("  ⚠️ 诚信风险: 涉及财务真实性、信披合规、高管诚信等核心信任问题")
        print("=" * 80)

    except Exception as e:
        print(f"分析失败: {e}")
