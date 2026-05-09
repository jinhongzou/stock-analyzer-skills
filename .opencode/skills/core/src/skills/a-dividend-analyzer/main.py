# -*- coding: utf-8 -*-
"""
A股分红配送详情 - 送转/现金分红/股息率
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from core import get_a_dividend_detail, analyze_dividend_consistency


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py <股票代码>")
        sys.exit(1)

    stock_code = sys.argv[1]
    print("=" * 60)
    print(f"股票: {stock_code} 分红配送分析")
    print("=" * 60)

    df = get_a_dividend_detail(stock_code)
    if df.empty:
        print("\n[X] 获取分红数据失败")
        return

    # 显示关键列
    cols = ["报告期", "现金分红-现金分红比例", "现金分红-股息率", "送转股份-送转总比例"]
    available = [c for c in cols if c in df.columns]
    print(f"\n共 {len(df)} 条分红记录\n")
    print(df[available].head(10).to_string(index=False))

    # 连续性分析
    consistency = analyze_dividend_consistency(df)
    if "error" not in consistency:
        print(f"\n--- 分红连续性 ---")
        print(f"  现金分红年份: {consistency['years_with_cash_dividend']}")
        print(f"  送股年份: {consistency['years_with_stock_dividend']}")
        print(f"  转股年份: {consistency['years_with_transfer']}")
        print(f"  评价: {consistency['consistency']}")

    print(f"\n{'=' * 60}")
    print("数据来源: 东方财富")
    print("=" * 60)


if __name__ == "__main__":
    main()
