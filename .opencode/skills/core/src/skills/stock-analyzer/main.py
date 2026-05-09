# -*- coding: utf-8 -*-
"""
个股分析 - 行业归属 / 估值 / 买卖建议
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from core import get_stock_profile, analyze_sector


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py <股票代码>")
        sys.exit(1)

    stock_code = sys.argv[1]
    print("=" * 60)
    print(f"股票: {stock_code} 个股分析")
    print("=" * 60)

    profile = get_stock_profile(stock_code)
    if not profile:
        print("\n[X] 获取数据失败")
        sys.exit(1)

    name = profile.get("\u540d\u79f0", stock_code)
    price = profile.get("\u73b0\u4ef7", "N/A")
    change = profile.get("\u6da8\u5e45", "N/A")
    pe_dynamic = profile.get("\u5e02\u76c8\u7387(\u52a8)", "N/A")
    pe_ttm = profile.get("\u5e02\u76c8\u7387(TTM)", "N/A")
    pb = profile.get("\u5e02\u51c0\u7387", "N/A")
    dy = profile.get("\u80a1\u606f\u7387(TTM)", "N/A")
    mkt_cap = profile.get("\u8d44\u4ea7\u51c0\u503c/\u603b\u5e02\u503c", "N/A")
    eps = profile.get("\u6bcf\u80a1\u6536\u76ca", "N/A")
    bvps = profile.get("\u6bcf\u80a1\u51c0\u8d44\u4ea7", "N/A")
    industry = profile.get("\u884c\u4e1a", "N/A")

    print(f"\n  \u540d\u79f0:     {name}")
    print(f"  \u884c\u4e1a:     {industry}")
    print(f"  \u73b0\u4ef7:     {price}")
    print(f"  \u6da8\u5e45:     {change}%")
    print(f"  \u5e02\u76c8\u7387(\u52a8):{pe_dynamic}")
    print(f"  \u5e02\u76c8\u7387(TTM):{pe_ttm}")
    print(f"  \u5e02\u51c0\u7387:     {pb}")
    print(f"  \u80a1\u606f\u7387(TTM):{dy}%")
    print(f"  \u603b\u5e02\u503c:   {mkt_cap}")
    print(f"  \u6bcf\u80a1\u6536\u76ca:   {eps}")
    print(f"  \u6bcf\u80a1\u51c0\u8d44\u4ea7: {bvps}")

    # 买卖建议
    sector = analyze_sector(stock_code)
    print(f"\n--- \u6295\u8d44\u5efa\u8bae ---")
    try:
        pe_val = float(pe_dynamic)
        change_val = float(change) if change != "N/A" else 0
        if 0 < pe_val < 15 and change_val > 2:
            advice = "\u4e70\u5165"
        elif pe_val > 50 or change_val < -5:
            advice = "\u5356\u51fa"
        else:
            advice = "\u6301\u6709"
    except:
        advice = "\u6301\u6709"
    print(f"  \u5efa\u8bae: {advice}")

    print(f"\n{'=' * 60}")
    print(f"\u5efa\u8bae\u903b\u8f91: PE<15 \u4e14\u4e0a\u6da8 \u2192 \u4e70\u5165 | PE>50 \u6216\u5927\u8dcc>5% \u2192 \u5356\u51fa | \u5176\u4ed6 \u2192 \u6301\u6709")
    print("=" * 60)


if __name__ == "__main__":
    main()
