# -*- coding: utf-8 -*-
"""
ROCE 计算 - 近10年资本回报率趋势
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from core import calculate_roce_history


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py <股票代码>")
        sys.exit(1)

    stock_code = sys.argv[1]
    print("=" * 60)
    print(f"股票: {stock_code} ROCE 分析")
    print("=" * 60)

    data = calculate_roce_history(stock_code)
    if not data:
        print("\n[X] 获取数据失败")
        return

    print(f"\n{'年份':<8} {'ROCE':<10} {'净利润':<14} {'EBIT':<14} {'投入资本':<14}")
    print("-" * 60)
    for r in data:
        print(f"{r['year']:<8} {r['roce']:<10.2%} {r['net_profit']/1e8:<14.1f}亿 {r['ebit']/1e8:<14.1f}亿 {r['capital']/1e8:<14.1f}亿")

    # 趋势总结
    if len(data) >= 2:
        latest = data[0]["roce"]
        earliest = data[-1]["roce"]
        trend = "上升" if latest > earliest else "下降"
        print(f"\n趋势: {trend} (近 {len(data)} 年)")

    print(f"\n{'=' * 60}")
    print("ROCE > 20% 优秀 | 15-20% 良好 | 10-15% 一般 | <10% 较差")
    print("=" * 60)


if __name__ == "__main__":
    main()
