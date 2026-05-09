# -*- coding: utf-8 -*-
"""
Percentile Analyzer - 股票历史分位数分析
计算股票在近3月/1年/3年/5年周期中的价格分位数
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import akshare as ak
import pandas as pd


MIN_DATA_DAYS = 10
PERIODS = {
    "3m": ("近3个月", 90),
    "1y": ("近1年", 365),
    "3y": ("近3年", 1095),
    "5y": ("近5年", 1825),
}
PERIOD_ALIAS = {v[0]: k for k, v in PERIODS.items()}  # "近3个月" -> "3m"


def get_stock_data(stock_code: str) -> pd.DataFrame:
    """获取股票历史日线数据（前复权）"""
    prefix = "sh" if stock_code.startswith("6") else "sz"
    df = ak.stock_zh_a_daily(symbol=f"{prefix}{stock_code}", adjust="qfq")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")
    return df


def calc_percentile(data: pd.Series, current_value: float) -> float:
    """计算当前值在历史序列中的分位数"""
    return (data <= current_value).sum() / len(data) * 100


def analyze_period(df: pd.DataFrame, days: int, period_name: str) -> dict:
    """分析指定周期的分位数并返回结构化结果"""
    start_date = datetime.now() - timedelta(days=days)
    period_df = df[df.index >= start_date]

    if len(period_df) < MIN_DATA_DAYS:
        return None

    close = period_df["close"]
    current = close.iloc[-1]
    pct = calc_percentile(close, current)

    percentiles = {p: round(close.quantile(p / 100), 2) for p in [10, 20, 30, 40, 50, 60, 70, 80, 90]}

    return {
        "period": period_name,
        "days": len(period_df),
        "current": round(current, 2),
        "percentile": round(pct, 1),
        "high": round(period_df["high"].max(), 2),
        "low": round(period_df["low"].min(), 2),
        "percentiles": percentiles,
    }


def get_signal(pct: float) -> tuple:
    """根据分位数返回信号等级和操作建议"""
    if pct < 10:
        return ("🟢 极低", "强烈买入", "极低位建仓机会")
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

    stock_code = sys.argv[1]
    period_filter = sys.argv[2] if len(sys.argv) > 2 else "all"

    if period_filter == "all":
        selected = list(PERIODS.values())
    elif period_filter in PERIODS:
        selected = [PERIODS[period_filter]]
    elif period_filter in PERIOD_ALIAS:
        selected = [PERIODS[PERIOD_ALIAS[period_filter]]]
    else:
        print(f"无效周期: {period_filter}")
        sys.exit(1)

    print("=" * 70)
    print(f"  股票分位数分析 — {stock_code}")
    print(f"  分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Step 1: 获取数据
    print(f"\n[Step 1] 获取历史行情数据...")
    try:
        df = get_stock_data(stock_code)
    except Exception as e:
        print(f"  数据获取失败: {e}")
        sys.exit(1)
    print(f"  数据范围: {df.index.min().strftime('%Y-%m-%d')} ~ {df.index.max().strftime('%Y-%m-%d')}")
    print(f"  总交易日: {len(df)}")

    # Step 2: 计算分位数
    print(f"\n[Step 2] 计算各周期分位数...")
    results = []
    for name, days in selected:
        result = analyze_period(df, days, name)
        if result:
            results.append(result)

    for r in results:
        signal, action, _ = get_signal(r["percentile"])
        print(f"  {r['period']:8s} ({r['days']:4d}日)  当前价 {r['current']:>8}元  "
              f"分位 {r['percentile']:5.1f}%  {signal}")

    # Step 3: 输出分位数明细表
    print(f"\n[Step 3] 价格分位数明细")
    print(f"\n{'分位':>6} |", end="")
    for r in results:
        print(f" {r['period']:>10}", end="")
    print()
    print("-" * (8 + 12 * len(results)))

    for p in [10, 20, 30, 50, 70, 90]:
        print(f" 第{p}0%分位 |", end="")
        for r in results:
            val = r["percentiles"][p]
            marker = " ◀" if abs(r["percentile"] - p) < 5 else ""
            print(f" {val:>8}元{marker}", end="")
        print()

    # Step 4: 操作建议
    print(f"\n[Step 4] 操作建议")
    for r in results:
        signal, action, detail = get_signal(r["percentile"])
        print(f"  {r['period']:8s}: {signal} → {action}（{detail}）")

    # 综合判断
    print(f"\n[综合判断]")
    avg_pct = sum(r["percentile"] for r in results) / len(results)
    print(f"  平均分位: {avg_pct:.1f}%")
    _, avg_action, _ = get_signal(avg_pct)
    print(f"  建议: {avg_action}")
    print(f"\n{'=' * 70}")
    print("声明: 本分析仅供参考，不构成投资建议。分位数需结合基本面综合判断。")
    print("=" * 70)


if __name__ == "__main__":
    main()
