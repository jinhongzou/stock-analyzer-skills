# -*- coding: utf-8 -*-
"""
A股分红配送分析 - 薄封装层
用法: python main.py <A股代码>
示例: python main.py 600519
"""

import sys
import os

# 添加项目根目录到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core import get_a_dividend_detail, analyze_dividend_consistency


def format_ratio(val):
    """格式化送转比例（如 10.0 -> '10转10'）"""
    if val is None or (isinstance(val, float) and str(val) == "nan"):
        return "-"
    try:
        v = float(val)
        if v > 0:
            return f"10转{v:.1f}"
        return "-"
    except (ValueError, TypeError):
        return "-"


def format_cash(val):
    """格式化现金分红（如 1.5 -> '10派1.5元'）"""
    if val is None or (isinstance(val, float) and str(val) == "nan"):
        return "-"
    try:
        v = float(val)
        if v > 0:
            return f"10派{v:.2f}元"
        return "-"
    except (ValueError, TypeError):
        return "-"


def format_pct(val):
    """格式化百分比"""
    if val is None or (isinstance(val, float) and str(val) == "nan"):
        return "-"
    try:
        return f"{float(val):.2f}%"
    except (ValueError, TypeError):
        return "-"


def format_num(val, decimals=2):
    """格式化数值"""
    if val is None or (isinstance(val, float) and str(val) == "nan"):
        return "-"
    try:
        return f"{float(val):.{decimals}f}"
    except (ValueError, TypeError):
        return "-"


def format_date(val):
    """格式化日期"""
    if val is None or (isinstance(val, float) and str(val) == "nan"):
        return "-"
    return str(val)[:10]


def print_dividend_table(df):
    """格式化输出分红配送表格"""
    if df.empty:
        print("\n⚠️  暂无分红数据")
        return

    print(f"\n{'=' * 130}")
    print(
        f"{'报告期':<12} {'预案公告日':<12} {'股权登记日':<12} {'除权除息日':<12} {'方案进度':<8} "
        f"{'送转':<10} {'现金分红':<14} {'股息率':<8} {'每股收益':<8} {'每股净资产':<10} "
        f"{'净利润同比':<10}"
    )
    print(f"{'-' * 130}")

    for _, row in df.iterrows():
        report = format_date(row.get("报告期", ""))
        pre_date = format_date(row.get("预案公告日", ""))
        reg_date = format_date(row.get("股权登记日", ""))
        ex_date = format_date(row.get("除权除息日", ""))
        progress = str(row.get("方案进度", "-"))[:6]

        # 送转总比例
        total_transfer = row.get("送转股份-送转总比例", None)
        transfer_str = format_ratio(total_transfer)

        # 现金分红
        cash_ratio = row.get("现金分红-现金分红比例", None)
        cash_str = format_cash(cash_ratio)

        # 股息率
        yield_str = format_pct(row.get("现金分红-股息率", None))

        # 每股指标
        eps_str = format_num(row.get("每股收益", None))
        nav_str = format_num(row.get("每股净资产", None))

        # 净利润同比
        profit_growth = format_pct(row.get("净利润同比增长", None))

        print(
            f"{report:<12} {pre_date:<12} {reg_date:<12} {ex_date:<12} {progress:<8} "
            f"{transfer_str:<10} {cash_str:<14} {yield_str:<8} {eps_str:<8} {nav_str:<10} "
            f"{profit_growth:<10}"
        )

    print(f"{'=' * 130}")


def print_detail_table(df):
    """输出详细指标表格"""
    if df.empty:
        return

    print(f"\n{'=' * 100}")
    print(f"{'详细每股指标'}")
    print(f"{'=' * 100}")
    print(
        f"{'报告期':<12} {'每股公积金':<10} {'每股未分配利润':<14} {'总股本(亿)':<12} "
        f"{'送股比例':<10} {'转股比例':<10}"
    )
    print(f"{'-' * 100}")

    for _, row in df.iterrows():
        report = format_date(row.get("报告期", ""))
        reserve = format_num(row.get("每股公积金", None))
        undistributed = format_num(row.get("每股未分配利润", None))
        total_shares = format_num(row.get("总股本", None), decimals=0)
        if total_shares != "-":
            total_shares = f"{float(total_shares) / 1e8:.2f}亿"
        stock_div = format_ratio(row.get("送转股份-送股比例", None))
        transfer = format_ratio(row.get("送转股份-转股比例", None))

        print(
            f"{report:<12} {reserve:<10} {undistributed:<14} {total_shares:<12} "
            f"{stock_div:<10} {transfer:<10}"
        )

    print(f"{'=' * 100}")


def print_consistency_analysis(analysis):
    """输出分红连续性分析"""
    if "error" in analysis:
        print(f"\n⚠️  {analysis['error']}")
        return

    print(f"\n{'=' * 60}")
    print("📊 分红连续性分析")
    print(f"{'=' * 60}")
    print(f"  总记录数：{analysis['total_records']} 条")
    print(f"  现金分红年份：{analysis['years_with_cash_dividend']} 年")
    print(f"  送股年份：{analysis['years_with_stock_dividend']} 年")
    print(f"  转股年份：{analysis['years_with_transfer']} 年")
    print(f"  平均股息率：{analysis['avg_dividend_yield']:.2f}%")
    print(f"  连续性评价：{analysis['consistency']}")

    if analysis.get("latest_year"):
        print(f"\n  最新报告期：{analysis['latest_year']}")
        if analysis.get("latest_cash_ratio") is not None:
            cash = analysis["latest_cash_ratio"]
            if not (isinstance(cash, float) and str(cash) == "nan"):
                print(f"  最新现金分红：{format_cash(cash)}")

    print(f"{'=' * 60}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    stock = sys.argv[1] if len(sys.argv) > 1 else "600519"

    print("=" * 60)
    print(f"💰 A股分红配送分析 - {stock}")
    print("=" * 60)

    # 获取分红数据
    df = get_a_dividend_detail(stock)

    if df.empty:
        print("\n⚠️  未获取到分红数据，请检查股票代码是否正确")
        sys.exit(1)

    # 输出分红表格
    print_dividend_table(df)

    # 输出详细指标
    print_detail_table(df)

    # 输出连续性分析
    analysis = analyze_dividend_consistency(df)
    print_consistency_analysis(analysis)
