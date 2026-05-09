# -*- coding: utf-8 -*-
"""
Shareholder Deep Analyzer - 可复用的深度股东分析
带完整分析推理过程的版本
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from core import (
    get_top_circulating_holders,
    get_holder_changes,
    detect_selling_risk,
    get_pledge_data,
    get_repurchase_data,
)
from core.src.analyzers.shareholder import _normalize_ts_code
import tushare as ts
import pandas as pd
import datetime


DEFAULT_YEARS = 5
MAX_HOLDERS_SHOWN = 10


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py <股票代码>")
        sys.exit(1)

    stock_code = sys.argv[1]
    print("=" * 70)
    print(f"  {stock_code} 深度股东分析")
    print("=" * 70)

    # Step 1: 股东结构
    print("\n[Step 1] 获取股东结构...")
    holders = get_top_circulating_holders(stock_code)
    if holders.get("holders"):
        print(f"  十大股东合计持股: {sum(h['\u5360\u6d41\u901a\u80a1\u6bd4\u4f8b'] for h in holders['holders'][:10]):.1f}%")
        for h in holders["holders"][:5]:
            print(f"    {h['\u80a1\u4e1c\u540d\u79f0'][:25]}: {h['\u6301\u80a1\u6570\u91cf']/1e4:.1f}万股 ({h['\u5360\u6d41\u901a\u80a1\u6bd4\u4f8b']:.2f}%)")

    # Step 2: 增减持
    print("\n[Step 2] 分析增减持变动...")
    changes = get_holder_changes(stock_code)
    print(f"  有变动的股东: {len(changes) if changes else 0} 家")

    # Step 3: 股权质押
    print("\n[Step 3] 查询股权质押...")
    pledge = get_pledge_data(stock_code)
    if pledge.get("summary", {}).get("\u603b\u8d28\u62bc\u6bd4\u4f8b"):
        print(f"  总质押比例: {pledge['summary']['\u603b\u8d28\u62bc\u6bd4\u4f8b']}")
    else:
        print("  无质押数据")

    # Step 4: 股份回购
    print("\n[Step 4] 查询股份回购...")
    repurchase = get_repurchase_data(stock_code)
    print(f"  回购次数: {repurchase['summary'].get('\u56de\u8d2d\u6b21\u6570', 0)}")
    print(f"  进行中: {repurchase['summary'].get('\u662f\u5426\u6b63\u5728\u8fdb\u884c\u56de\u8d2d', '\u5426')}")

    # Step 5: 综合判断
    print("\n[Step 5] 综合判断")
    signals_pos = 0
    signals_neg = 0
    if holders.get("holders"):
        top_holder = holders["holders"][0]
        if top_holder["\u5360\u6d41\u901a\u80a1\u6bd4\u4f8b"] > 30:
            signals_pos += 1
    if changes:
        decreasing = sum(1 for c in changes if any(
            r.get("\u53d8\u52a8\u65b9\u5411") == "\u51cf\u6301"
            for r in c.get("\u53d8\u52a8\u8bb0\u5f55", [])
        ))
        signals_neg += decreasing

    print(f"\n  积极信号: {signals_pos}")
    print(f"  消极信号: {signals_neg}")
    print(f"\n{'=' * 70}")
    print("声明: 以上分析仅供参考，不构成投资建议。")
    print("=" * 70)


if __name__ == "__main__":
    main()
