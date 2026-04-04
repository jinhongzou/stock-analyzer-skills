# -*- coding: utf-8 -*-
"""
Market Analyzer - 薄封装层
用法: python main.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core import analyze_market_overview, analyze_market_trend


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 60)
    print("A 股市场整体分析")
    print("=" * 60)

    try:
        overview = analyze_market_overview()
        if overview:
            print(f"\n--- 市场概览 ---")
            print(f"  平均市盈率:   {overview['average_pe']:.2f}")
            print(f"  指数值:       {overview['index_value']:.2f}")
            print(f"  数据日期:     {overview['date']}")

        trend = analyze_market_trend()
        print(f"\n--- 市场趋势 (上证指数) ---")
        print(f"  最新日期:     {trend['latest_date']}")
        print(f"  最新收盘:     {trend['latest_close']:.2f}")
        print(f"  MA20:         {trend['ma20']:.2f}")
        print(f"  MA50:         {trend['ma50']:.2f}")
        print(f"  市场状态:     {trend['trend']}")
        print(f"  信号:         {trend['signal']}")

        print("\n" + "=" * 60)
        print("趋势判断: MA20 > MA50 → 牛市 | MA20 < MA50 → 熊市")
        print("=" * 60)

    except Exception as e:
        print(f"分析失败: {e}")
