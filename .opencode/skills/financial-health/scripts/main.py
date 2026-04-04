# -*- coding: utf-8 -*-
"""
Financial Health Analyzer - 薄封装层
用法: python main.py <股票代码>
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core import analyze_financial_health


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    stock = sys.argv[1] if len(sys.argv) > 1 else "600519"

    print("=" * 80)
    print(f"股票: {stock} 财务健康分析")
    print("=" * 80)

    try:
        health = analyze_financial_health(stock)

        if health["ratios"]:
            print(
                f"\n{'日期':<12}{'流动比率':>10}{'速动比率':>10}{'资产负债率':>12}{'ROE':>10}"
            )
            print("-" * 60)
            for r in health["ratios"]:
                print(
                    f"{str(r['date']):<12}"
                    f"{r['current_ratio']:>10.2f}"
                    f"{r['quick_ratio']:>10.2f}"
                    f"{r['debt_ratio']:>11.2%}"
                    f"{r['roe']:>10.2%}"
                )

        if health.get("interest_coverage"):
            print(f"\n--- 利息覆盖率 ---")
            for c in health["interest_coverage"]:
                print(f"  {c['date']}: {c['ratio']:.2f}")

        if health.get("cash_flow"):
            print(f"\n--- 自由现金流 ---")
            for c in health["cash_flow"]:
                print(
                    f"  {str(c['date']):<12} 经营: {c['ocf'] / 1e8:>8.1f}亿  自由: {c['fcf'] / 1e8:>8.1f}亿"
                )

        print("\n" + "=" * 80)
        print("参考标准:")
        print("  流动比率: >2 良好 | >1.5 一般 | <1 较差")
        print("  速动比率: >1 良好 | >0.8 一般")
        print("  资产负债率: <50% 安全 | 50%-70% 警戒 | >70% 危险")
        print("  ROE: >15% 优秀 | >10% 良好 | <5% 较差")
        print("  利息覆盖率: >3 安全 | <1.5 危险")
        print("=" * 80)

    except Exception as e:
        print(f"分析失败: {e}")
