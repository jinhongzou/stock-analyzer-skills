#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
行业成分股详情采集脚本
对应指南: guides/03-industry-valuation.md + guides/04-industry-rotation.md

对涨幅榜/跌幅榜/成交额榜的主要行业，获取成分股中的领涨/领跌股详情

数据源: akshare stock_board_industry_cons_em（东方财富行业成分股）
代码只提供原始数据，不做分析判断

用法:
    python .opencode/skills/core/src/skills/industry-analysis/collect_industry_detail.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import akshare as ak
import pandas as pd
import time


def collect_industry_detail() -> dict:
    """采集行业估值 + 成分股详情数据"""
    result = {}

    # ── 1. 行业估值（巨潮行业PE/PB） ──
    try:
        df = ak.stock_industry_pe_ratio_cninfo()
        if not df.empty:
            sectors = []
            for _, row in df.iterrows():
                sectors.append({
                    "industry": str(row.iloc[0]),
                    "pe": round(float(row.iloc[3]), 2) if row.iloc[3] != "-" else None,
                    "pe_median": round(float(row.iloc[4]), 2) if row.iloc[4] != "-" else None,
                    "pb": round(float(row.iloc[5]), 2) if row.iloc[5] != "-" else None,
                    "pb_median": round(float(row.iloc[6]), 2) if row.iloc[6] != "-" else None,
                })
            result["valuation_sectors"] = sectors
            result["valuation_count"] = len(sectors)

            # PE最高/最低 Top 5
            valid_pe = [s for s in sectors if s["pe"] is not None and s["pe"] > 0]
            valid_pe.sort(key=lambda x: x["pe"], reverse=True)
            result["pe_highest_top5"] = valid_pe[:5]
            result["pe_lowest_top5"] = valid_pe[-5:] if len(valid_pe) >= 5 else valid_pe

        time.sleep(1)
    except Exception as e:
        result["valuation_error"] = str(e)

    # ── 2. 热门行业成分股（从行业排行取领头行业） ──
    try:
        spot_df = ak.stock_sector_spot()
        if not spot_df.empty:
            sorted_by_change = spot_df.sort_values(by=spot_df.columns[5], ascending=False)
            sorted_by_volume = spot_df.sort_values(by=spot_df.columns[6], ascending=False)

            # 取涨幅前3 + 跌幅前3 + 成交额前3（去重）
            target = []
            seen = set()
            for _, row in sorted_by_change.head(3).iterrows():
                name = str(row.iloc[1])
                if name not in seen:
                    target.append({"name": name, "reason": "涨幅榜"})
                    seen.add(name)
            for _, row in sorted_by_change.tail(3).iloc[::-1].iterrows():
                name = str(row.iloc[1])
                if name not in seen:
                    target.append({"name": name, "reason": "跌幅榜"})
                    seen.add(name)
            for _, row in sorted_by_volume.head(3).iterrows():
                name = str(row.iloc[1])
                if name not in seen:
                    target.append({"name": name, "reason": "成交额榜"})
                    seen.add(name)

            sectors_detail = []
            for t in target:
                try:
                    cons = ak.stock_board_industry_cons_em(symbol=t["name"])
                    if not cons.empty:
                        cons_sorted = cons.sort_values(by=cons.columns[7], ascending=False)
                        top5 = []
                        for _, row in cons_sorted.head(5).iterrows():
                            top5.append({
                                "code": str(row.iloc[1]),
                                "name": str(row.iloc[2]),
                                "change_pct": round(float(row.iloc[7]), 2),
                                "price": round(float(row.iloc[5]), 2),
                            })
                        sectors_detail.append({
                            "name": t["name"],
                            "reason": t["reason"],
                            "stock_count": len(cons),
                            "top5_stocks": top5,
                        })
                    time.sleep(0.5)
                except Exception:
                    pass

            result["sectors_detail"] = sectors_detail
            result["detail_count"] = len(sectors_detail)

        time.sleep(1)
    except Exception as e:
        result["detail_error"] = str(e)

    return result


def main():
    print("=" * 60)
    print("行业详情数据采集（估值 + 成分股）")
    print("=" * 60)

    data = collect_industry_detail()

    # 输出估值数据
    print(f"\n[行业估值]")
    if data.get("valuation_error"):
        print(f"  [错误] {data['valuation_error']}")
    else:
        print(f"  有估值数据的行业数: {data.get('valuation_count', 0)}")
        print(f"\n  PE最高 Top 5:")
        for s in data.get('pe_highest_top5', []):
            print(f"    {s['industry']}: PE={s['pe']} PB={s['pb']}")
        print(f"\n  PE最低 Top 5:")
        for s in data.get('pe_lowest_top5', []):
            print(f"    {s['industry']}: PE={s['pe']} PB={s['pb']}")

    # 输出成分股数据
    print(f"\n[热门行业成分股]")
    if data.get("detail_error"):
        print(f"  [错误] {data['detail_error']}")
    else:
        for s in data.get('sectors_detail', []):
            print(f"\n  {s['name']}（{s['reason']}，共{s['stock_count']}只成分股）:")
            for stk in s['top5_stocks']:
                print(f"    {stk['name']}({stk['code']}): {stk['change_pct']}% 现价={stk['price']}")

    print(f"\n{'=' * 60}")
    print(f"共采集 {len(data)} 项数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
