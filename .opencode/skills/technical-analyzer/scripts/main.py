# -*- coding: utf-8 -*-
"""
Technical Analyzer - 薄封装层
用法: python main.py <股票代码>
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core import get_historical_data, calculate_ma, calculate_rsi, calculate_beta


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    stock = sys.argv[1] if len(sys.argv) > 1 else "600519"

    print("=" * 60)
    print(f"股票: {stock} 技术分析")
    print("=" * 60)

    try:
        df = get_historical_data(stock)
        print(
            f"\n数据范围: {df['日期'].iloc[0]} ~ {df['日期'].iloc[-1]} (共 {len(df)} 个交易日)"
        )

        ma_result = calculate_ma(df)
        print(f"\n--- 均线系统 ---")
        if "ma50" in ma_result:
            print(f"  MA50:  {ma_result['ma50']:.2f}")
            print(f"  MA200: {ma_result['ma200']:.2f}")
        else:
            print(f"  MA短期: {ma_result['ma_short']:.2f}")
            print(f"  MA长期: {ma_result['ma_long']:.2f}")
        print(f"  信号:  {ma_result['signal']}")
        if ma_result.get("note"):
            print(f"  备注:  {ma_result['note']}")

        rsi_result = calculate_rsi(df)
        print(f"\n--- RSI (14日) ---")
        if rsi_result["rsi"] is not None:
            print(f"  RSI:   {rsi_result['rsi']:.2f}")
        print(f"  信号:  {rsi_result['signal']}")

        # 计算 Beta
        print(f"\n--- Beta (相对沪深300) ---")
        beta_result = calculate_beta(stock)
        if beta_result["beta"] is not None:
            print(f"  Beta:  {beta_result['beta']:.4f}")
            print(f"  交易日: {beta_result['trading_days']}")
            print(f"  区间:  {beta_result['date_range']}")
            print(f"  解读:  {beta_result['interpretation']}")
        else:
            print(f"  {beta_result['interpretation']}")

        print("\n" + "=" * 60)
        print("参考标准:")
        print("  均线: Bullish(金叉) = MA50 > MA200 | Bearish(死叉) = MA50 < MA200")
        print("  RSI:  >70 超买 | <30 超卖 | 30-70 中性")
        print("  Beta: >1.2 高波动 | 0.8-1.2 同步 | <0.8 低波动")
        print("=" * 60)

    except Exception as e:
        print(f"分析失败: {e}")
