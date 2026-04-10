# -*- coding: utf-8 -*-
"""
Valuation Anchor Method - 估值锚点法入口
用法: python main.py <股票代码>
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# 设置输出编码
sys.stdout.reconfigure(encoding="utf-8")

from core import (
    get_stock_profile,
    get_historical_data,
    calculate_price_distribution,
    calculate_buy_strategy,
    calculate_ma,
    calculate_rsi,
)


def format_valuation_report(stock_code: str) -> str:
    """生成估值锚点法分析报告"""

    print(f"正在分析 {stock_code} 估值锚点...")

    # 获取基本信息
    profile = get_stock_profile(stock_code)
    if not profile:
        print("无法获取股票信息")
        return

    name = profile.get("名称", "未知")
    current_price = float(profile.get("现价", 0))
    eps = float(profile.get("每股收益", 0))
    dps = float(profile.get("每股分红", 0))
    pb = float(profile.get("市净率", 0))

    print(f"股票: {name} ({stock_code})")
    print(f"现价: {current_price} 元")
    print(f"EPS: {eps} 元")
    print(f"每股分红: {dps} 元")
    print(f"PB: {pb}")
    print("-" * 50)

    # 52周价格分布
    price_dist = calculate_price_distribution(stock_code)

    print("\n【维度1: 52周价格分布】")
    if price_dist.get("high_52w"):
        print(f"  52周高点: {price_dist['high_52w']:.2f} 元")
        print(f"  52周低点: {price_dist['low_52w']:.2f} 元")
        print(f"  中位数: {price_dist['median']:.2f} 元")
        print(f"  Q1(25%): {price_dist['q1']:.2f} 元")
        print(f"  Q3(75%): {price_dist['q3']:.2f} 元")
        print(f"  当前位置: {price_dist['position_pct']:.1f}%分位")

        # 价格分布买入策略
        print(f"\n  价格分布买入策略:")
        print(f"    激进: {price_dist['q1']:.2f} ~ {price_dist['median']:.2f} 元")
        low_quartile = (
            price_dist["low_52w"] + (price_dist["median"] - price_dist["low_52w"]) * 0.2
        )
        print(f"    稳健: {low_quartile:.2f} ~ {price_dist['q1']:.2f} 元")
        print(f"    理想: ~{price_dist['low_52w']:.2f} 元")

    # 买入点策略（综合多维，包含行业信息）
    industry = profile.get("行业") if profile else None
    buy_strategy = calculate_buy_strategy(
        stock_code,
        eps=eps,
        dps=dps,
        revenue_growth=None,
        pb=pb,
        industry=industry,
    )

    print("\n【买入点策略（多维交叉验证）】")
    if buy_strategy:
        # 显示估值方法提示
        valuation_note = buy_strategy.get("valuation_note")
        if valuation_note:
            print(f"  {valuation_note}")

        pe_strategy = buy_strategy.get("pe_strategy", {})
        if pe_strategy:
            print(f"  PE估值:")
            for level, price in pe_strategy.items():
                print(f"    {level}: {price} 元")

        final_strategy = buy_strategy.get("final_strategy", {})
        if final_strategy:
            strategy = final_strategy.get("strategy", {})
            multi_price = strategy.get("综合", {})
            if multi_price:
                print(f"\n  综合价格（多维交叉）:")
                for level, price in multi_price.items():
                    print(f"    {level}: {price} 元")

            print(f"\n  推荐: {final_strategy.get('recommendation', 'N/A')}")
            print(f"  原因: {final_strategy.get('reason', 'N/A')}")

    # 技术面验证
    print("\n【维度4: 技术面验证】")
    try:
        df = get_historical_data(stock_code)
        ma_result = calculate_ma(df)
        rsi_result = calculate_rsi(df)

        if "ma50" in ma_result:
            print(f"  MA50: {ma_result['ma50']:.2f} 元")
            print(f"  MA200: {ma_result['ma200']:.2f} 元")
            print(f"  均线信号: {ma_result['signal']}")

        if rsi_result.get("rsi"):
            print(f"  RSI(14): {rsi_result['rsi']:.2f} ({rsi_result['signal']})")
    except Exception as e:
        print(f"  技术面数据获取失败: {e}")

    print("\n" + "=" * 50)
    print("【透明化推理说明】")
    print("=" * 50)
    print("• 52周价格分布: 客观数据，基于实际交易价格计算")
    print("• PE估值法: 经验判断，合理PE区间因行业而异")
    print("• 股息率锚定: 客观计算，但目标股息率门槛是经验值")
    print("• 技术面: 客观数据，但支撑位解读有主观成分")
    print("\n建议仅作为参考，投资需自行判断风险。")

    return ""


if __name__ == "__main__":
    stock = sys.argv[1] if len(sys.argv) > 1 else "600519"

    format_valuation_report(stock)
