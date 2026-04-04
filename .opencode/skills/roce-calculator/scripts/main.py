# -*- coding: utf-8 -*-
"""
ROCE Calculator - 薄封装层
用法: python main.py <股票代码>
"""

import sys
import os

# 添加项目根目录到 path，确保能导入 analyze 包
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core import calculate_roce


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    stock = sys.argv[1] if len(sys.argv) > 1 else "600519"

    print("=" * 75)
    print(
        f"{'年份':<6}{'ROCE':>10}    {'净利润':>14}    {'EBIT':>14}    {'投入资本':>14}"
    )
    print("-" * 75)

    for year in range(2024, 2014, -1):
        try:
            result = calculate_roce(stock, year)
            roce_str = f"{result['roce']:.2%}"
            print(
                f"{year:<6}{roce_str:>10}    {result['net_profit'] / 1e8:>12.1f}亿    "
                f"{result['ebit'] / 1e8:>12.1f}亿    {result['capital_employed'] / 1e8:>12.1f}亿"
            )
        except Exception as e:
            print(f"{year:<6}  失败: {e}")

    print("=" * 75)
