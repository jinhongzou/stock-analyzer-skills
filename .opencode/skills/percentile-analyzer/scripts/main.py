# -*- coding: utf-8 -*-
"""
Percentile Analyzer - 股票历史分位数分析
用法: python main.py <股票代码> [周期]
周期: 3m (近3月), 1y (近1年), 3y (近3年), 5y (近5年), all (全部)
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import akshare as ak
import pandas as pd


def get_stock_data(stock_code: str) -> pd.DataFrame:
    """获取股票历史数据"""
    df = ak.stock_zh_a_daily(symbol=f"sh{stock_code}" if stock_code.startswith("6") else f"sz{stock_code}", adjust="qfq")
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').set_index('date')
    return df


def calc_percentile(data, current_value):
    """计算分位数"""
    return (data <= current_value).sum() / len(data) * 100


def analyze_period(df: pd.DataFrame, days: int, period_name: str) -> dict:
    """分析指定周期的分位数"""
    start_date = datetime.now() - timedelta(days=days)
    period_df = df[df.index >= start_date]

    if len(period_df) < 10:
        return None

    current = period_df['close'].iloc[-1]
    high = period_df['high'].max()
    low = period_df['low'].min()
    pct = calc_percentile(period_df['close'], current)

    percentiles = {}
    for p in [10, 20, 30, 40, 50, 60, 70, 80, 90, 95]:
        percentiles[p] = round(period_df['close'].quantile(p / 100), 2)

    return {
        'period': period_name,
        'days': len(period_df),
        'current': round(current, 2),
        'percentile': round(pct, 1),
        'high': round(high, 2),
        'low': round(low, 2),
        'percentiles': percentiles
    }


def get_signal(pct: float) -> tuple:
    """根据分位数获取信号和建议"""
    if pct < 10:
        return ("🟢 极低", "强烈买入", "短期极低位建仓机会")
    elif pct < 30:
        return ("🟢 低", "买入", "分批建仓")
    elif pct < 50:
        return ("🟡 偏低", "观望", "可考虑入场")
    elif pct < 70:
        return ("🟡 合理", "持有", "无需操作")
    elif pct < 90:
        return ("🟠 偏高", "减仓", "分批止盈")
    else:
        return ("🔴 极高", "减仓/止损", "不追高，严格止损")


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) < 2:
        print("用法: python main.py <股票代码> [周期]")
        print("周期: 3m (近3月), 1y (近1年), 3y (近3年), 5y (近5年), all (全部，默认)")
        sys.exit(1)

    stock = sys.argv[1]
    period_filter = sys.argv[2] if len(sys.argv) > 2 else "all"

    # 周期配置
    periods_config = {
        "3m": [("近3个月", 90)],
        "1y": [("近1年", 365)],
        "3y": [("近3年", 1095)],
        "5y": [("近5年", 1825)],
        "all": [("近3个月", 90), ("近1年", 365), ("近3年", 1095), ("近5年", 1825)]
    }

    periods = periods_config.get(period_filter, periods_config["all"])

    print("=" * 70)
    print(f"  股票分位数分析 — {stock}")
    print(f"  分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    try:
        # 获取数据
        print("\n获取数据...")
        df = get_stock_data(stock)
        print(f"历史数据: {df.index.min().strftime('%Y-%m-%d')} ~ {df.index.max().strftime('%Y-%m-%d')}")

        # 分析各周期
        results = []
        for name, days in periods:
            result = analyze_period(df, days, name)
            if result:
                results.append(result)

        # 输出结果
        print("\n" + "=" * 70)

        for r in results:
            signal, action, detail = get_signal(r['percentile'])

            print(f"\n--- {r['period']} ({r['days']}交易日) ---")
            print(f"  当前价格: {r['current']}元")
            print(f"  分位数:   {r['percentile']}% {signal}")
            print(f"  区间:     {r['low']} ~ {r['high']}元")
            print(f"  操作:     {action} — {detail}")

            print(f"  价格分位数:")
            for p in [10, 20, 30, 40, 50, 60, 70, 80, 90]:
                val = r['percentiles'][p]
                marker = " ←" if abs(r['percentile'] - p) < 5 else ""
                print(f"    第{p}0%分位: {val}元{marker}")

        print("\n" + "=" * 70)
        print("分位数参考:")
        print("  <30%: 🟢 低估，买入信号")
        print("  30-70%: 🟡 合理，观望持有")
        print("  70-90%: 🟠 偏高，减仓止盈")
        print("  >90%: 🔴 高估，不追高")
        print("=" * 70)

    except Exception as e:
        print(f"分析失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()