# -*- coding: utf-8 -*-
"""
技术分析 - MA50/MA200 金叉死叉 / RSI
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from core import get_historical_data, calculate_ma, calculate_rsi
from datetime import datetime


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py <股票代码>")
        sys.exit(1)

    stock_code = sys.argv[1]
    print("=" * 60)
    print(f"股票: {stock_code} 技术分析")
    print("=" * 60)

    df = get_historical_data(stock_code, start_date="20240101")
    if df.empty:
        print("\n[X] 获取数据失败")
        return

    print(f"\n数据范围: {df['日期'].iloc[0]} ~ {df['日期'].iloc[-1]} (共 {len(df)} 个交易日)")

    ma = calculate_ma(df)
    print(f"\n--- 均线系统 ---")
    if "ma50" in ma:
        print(f"  MA50:  {ma['ma50']:.2f}")
        print(f"  MA200: {ma['ma200']:.2f}")
    else:
        print(f"  MA短期: {ma['ma_short']:.2f}")
        print(f"  MA长期: {ma['ma_long']:.2f}")
    print(f"  信号:  {ma['signal']}")

    rsi = calculate_rsi(df)
    print(f"\n--- RSI (14日) ---")
    if rsi["rsi"] is not None:
        print(f"  RSI:   {rsi['rsi']:.2f}")
    else:
        print(f"  RSI:   N/A")
    print(f"  信号:  {rsi['signal']}")

    print(f"\n{'=' * 60}")
    print("参考标准:")
    print("  均线: Bullish(金叉) = MA50 > MA200 | Bearish(死叉) = MA50 < MA200")
    print("  RSI:  >70 超买 | <30 超卖 | 30-70 中性")
    print("=" * 60)


if __name__ == "__main__":
    main()
