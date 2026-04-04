# -*- coding: utf-8 -*-
"""
Stock Analyzer - 薄封装层
用法: python main.py <股票代码>
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core import get_stock_profile, analyze_sector


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    stock = sys.argv[1] if len(sys.argv) > 1 else "600519"

    print("=" * 60)
    print(f"股票: {stock} 个股分析")
    print("=" * 60)

    try:
        profile = get_stock_profile(stock)
        if profile:
            print(f"\n--- 基本信息 ---")
            print(f"  股票名称:   {profile.get('名称', 'N/A')}")
            print(f"  所属行业:   {profile.get('行业', 'N/A')}")
            print(f"  现价:       {profile.get('现价', 'N/A')}")
            print(f"  涨跌幅:     {profile.get('涨幅', 'N/A')}%")

            print(f"\n--- 估值指标 ---")
            print(f"  市盈率(动): {profile.get('市盈率(动)', 'N/A')}")
            print(f"  市盈率(静): {profile.get('市盈率(静)', 'N/A')}")
            print(f"  市盈率(TTM):{profile.get('市盈率(TTM)', 'N/A')}")
            print(f"  市净率:     {profile.get('市净率', 'N/A')}")
            print(f"  股息率(TTM):{profile.get('股息率(TTM)', 'N/A')}%")
            print(f"  总市值:     {profile.get('资产净值/总市值', 'N/A')}")
            print(f"  每股收益:   {profile.get('每股收益', 'N/A')}")
            print(f"  每股净资产: {profile.get('每股净资产', 'N/A')}")

        sector = analyze_sector(stock)
        if sector["行业"] != "未知":
            print(f"\n--- 行业分析 ---")
            print(f"  行业趋势:   {sector['趋势']}")
            print(f"  行业表现:   {sector['表现']:.2f}%")
            print(f"  波动性:     {sector['波动性']:.2f}%")

        try:
            pe = float(profile.get("市盈率(动)", 0))
            change = float(profile.get("涨幅", 0))
            if pe < 15 and change > 0:
                rec = "买入"
            elif pe > 50 or change < -5:
                rec = "卖出"
            else:
                rec = "持有"
            print(f"\n--- 投资建议 ---")
            print(f"  建议: {rec}")
        except (ValueError, TypeError):
            pass

        print("\n" + "=" * 60)
        print("建议逻辑: PE<15 且上涨 → 买入 | PE>50 或大跌>5% → 卖出 | 其他 → 持有")
        print("=" * 60)

    except Exception as e:
        print(f"分析失败: {e}")
