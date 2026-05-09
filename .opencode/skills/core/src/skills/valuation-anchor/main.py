# -*- coding: utf-8 -*-
"""
估值锚点分析 - 52周价格分布 / PE估值 / 技术面验证
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from core import (
    calculate_price_distribution,
    calculate_buy_strategy,
    get_stock_profile_tushare,
)
from core import get_historical_data, calculate_ma, calculate_rsi
from datetime import datetime, timedelta


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py <股票代码>")
        sys.exit(1)

    stock_code = sys.argv[1]
    print(f"正在分析 {stock_code} 估值锚点...")

    # 获取基本数据
    profile = get_stock_profile_tushare(stock_code)
    if not profile or not profile.get("\u73b0\u4ef7"):
        print("[X] 获取数据失败")
        return

    name = profile.get("\u540d\u79f0", stock_code)
    price = profile["\u73b0\u4ef7"]
    eps = profile.get("\u6bcf\u80a1\u6536\u76ca", 0)
    dps = profile.get("\u6bcf\u80a1\u5206\u7ea2", 0)
    pb = profile.get("\u5e02\u51c0\u7387", 0)

    print(f"股票: {name} ({stock_code})")
    print(f"现价: {price} 元")
    print(f"EPS: {eps} 元")
    print(f"每股分红: {dps} 元")
    print(f"PB: {pb}")
    print("-" * 50)

    # 价格分布
    dist = calculate_price_distribution(stock_code)
    if dist:
        print(f"\n【维度1: 52周价格分布】")
        print(f"  52周高点: {dist['high_52w']:.2f} 元")
        print(f"  52周低点: {dist['low_52w']:.2f} 元")
        print(f"  中位数: {dist['median']:.2f} 元")
        print(f"  Q1(25%): {dist['q1']:.2f} 元")
        print(f"  Q3(75%): {dist['q3']:.2f} 元")
        print(f"  当前位置: {dist['position_pct']:.1f}%分位")

    # PE估值
    if eps and eps > 0:
        print(f"\n【买入点策略】")
        strategy = calculate_buy_strategy(stock_code, eps=eps, pb=pb)
        print(f"  PE估值: {strategy['pe_strategy']}")
        print(f"  建议: {strategy['final_strategy']['recommendation']}")

    # 技术面
    start = (datetime.now() - timedelta(days=400)).strftime("%Y%m%d")
    df = get_historical_data(stock_code, start_date=start)
    if not df.empty:
        ma = calculate_ma(df)
        rsi = calculate_rsi(df)
        print(f"\n【技术面验证】")
        print(f"  MA50: {ma.get('ma50', 0):.2f} 元")
        print(f"  MA200: {ma.get('ma200', 0):.2f} 元")
        print(f"  均线信号: {ma.get('signal', 'N/A')}")
        print(f"  RSI(14): {rsi.get('rsi', 0):.2f}")


if __name__ == "__main__":
    main()
