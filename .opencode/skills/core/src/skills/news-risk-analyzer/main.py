# -*- coding: utf-8 -*-
"""
新闻风险评估 - 诚信风险 / 经营风险关键词检测
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from core import analyze_news_risk


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py <股票代码> [新闻条数]")
        sys.exit(1)

    stock_code = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 15

    print("=" * 60)
    print(f"股票: {stock_code} 新闻风险评估")
    print("=" * 60)

    result = analyze_news_risk(stock_code, limit)
    print(f"\n分析新闻: {result['total']} 条")

    if result["high"] > 0:
        print(f"\n高风险: {result['high']} 条")
    if result["medium"] > 0:
        print(f"中风险: {result['medium']} 条")
    if result["low"] > 0:
        print(f"低风险: {result['low']} 条")

    if result.get("alerts"):
        print(f"\n--- 风险明细 ---")
        for a in result["alerts"][:10]:
            print(f"  [{a['level']}] {a['title']}")
            print(f"    关键词: {', '.join(a['keywords'])}")

    print(f"\n{'=' * 60}")
    print("诚信风险: 财务造假/信披违规/立案调查等关键词")
    print("=" * 60)


if __name__ == "__main__":
    main()
