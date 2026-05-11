#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
行业资金流向采集脚本
对应指南: guides/02-industry-fundflow.md

数据源: akshare stock_sector_fund_flow_rank（东方财富行业资金流）
代码只提供原始数据，不做分析判断

用法:
    python .opencode/skills/core/src/skills/industry-analysis/collect_industry_fundflow.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import akshare as ak
import pandas as pd
import time


def collect_industry_fundflow() -> dict:
    """采集行业资金流向数据，返回原始数值"""
    result = {}

    try:
        df = ak.stock_sector_fund_flow_rank(indicator="今日")
        if df.empty:
            result["note"] = "东方财富资金流接口暂不可用"
            return result

        # 按主力净流入排序
        sorted_df = df.sort_values(by=df.columns[2], ascending=False)

        result["total_sectors"] = len(df)

        # 资金流整体统计
        inflows = [float(v) for v in df.iloc[:, 2] if float(v) > 0]
        outflows = [float(v) for v in df.iloc[:, 2] if float(v) < 0]
        result["inflow_sectors_count"] = len(inflows)
        result["outflow_sectors_count"] = len(outflows)
        result["total_main_net_inflow"] = round(sum(inflows) + sum(outflows), 2)

        # 流入榜 Top 10
        inflow_top = []
        for _, row in sorted_df.head(10).iterrows():
            inflow_top.append({
                "name": str(row.iloc[1]),
                "main_net_inflow": round(float(row.iloc[2]), 2),
                "change_pct": round(float(row.iloc[4]), 2),
            })
        result["inflow_top10"] = inflow_top

        # 流出榜 Top 10
        outflow_top = []
        for _, row in sorted_df.tail(10).iloc[::-1].iterrows():
            outflow_top.append({
                "name": str(row.iloc[1]),
                "main_net_inflow": round(float(row.iloc[2]), 2),
                "change_pct": round(float(row.iloc[4]), 2),
            })
        result["outflow_top10"] = outflow_top

        time.sleep(1)

    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    print("=" * 60)
    print("行业资金流向数据采集")
    print("=" * 60)

    data = collect_industry_fundflow()

    if data.get("error"):
        print(f"\n[错误] {data['error']}")
        return

    print(f"\n[资金流概况]")
    print(f"  分析行业数: {data.get('total_sectors', 'N/A')}")
    print(f"  主力净流入/流出行业数: {data.get('inflow_sectors_count', 0)}/{data.get('outflow_sectors_count', 0)}")
    print(f"  全市场主力净流入合计: {data.get('total_main_net_inflow', 'N/A')}亿元")

    print(f"\n[主力净流入榜 Top 10]")
    for i, s in enumerate(data.get('inflow_top10', []), 1):
        print(f"  {i}. {s['name']}: {s['main_net_inflow']}亿元 涨跌幅={s['change_pct']}%")

    print(f"\n[主力净流出榜 Top 10]")
    for i, s in enumerate(data.get('outflow_top10', []), 1):
        print(f"  {i}. {s['name']}: {s['main_net_inflow']}亿元 涨跌幅={s['change_pct']}%")

    print(f"\n{'=' * 60}")
    print(f"共采集 {len(data)} 项数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
