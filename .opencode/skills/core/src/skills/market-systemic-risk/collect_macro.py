#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
宏观经济数据采集脚本
对应指南: guides/01-macro-analysis.md

数据源策略: Tushare Pro 优先，取不到用 akshare 替补
代码只提供原始数据，不做分析判断

用法:
    python .opencode/skills/core/src/skills/market-systemic-risk/collect_macro.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import akshare as ak
import tushare as ts
import pandas as pd


# ── Tushare 初始化 ──
def _get_ts_api():
    token = os.environ.get("TUSHARE_TOKEN", "")
    if not token:
        env_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", ".env")
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TUSHARE_TOKEN") and "=" in line:
                        token = line.split("=", 1)[1].strip()
                        break
        except Exception:
            pass
    if token:
        ts.set_token(token)
        return ts.pro_api()
    return None


def collect_macro_data() -> dict:
    """采集宏观经济数据，返回原始数值"""
    result = {}

    # ── 1. 市场PE历史（akshare 乐咕数据） ──
    try:
        pe_df = ak.stock_market_pe_lg()
        if not pe_df.empty:
            latest_pe = pe_df.iloc[-1]["平均市盈率"]
            pe_values = pe_df["平均市盈率"].dropna()
            total = len(pe_values)

            result["pe_current"] = round(latest_pe, 2)
            result["pe_percentile_1y"] = round((pe_values.tail(12) < latest_pe).sum() / 12 * 100, 1)
            result["pe_percentile_3y"] = round((pe_values.tail(36) < latest_pe).sum() / 36 * 100, 1)
            result["pe_percentile_5y"] = round((pe_values.tail(60) < latest_pe).sum() / 60 * 100, 1)
            result["pe_min"] = round(pe_values.min(), 2)
            result["pe_max"] = round(pe_values.max(), 2)
            result["pe_median"] = round(pe_values.median(), 2)
        time.sleep(1)
    except Exception as e:
        result["pe_error"] = str(e)

    # ── 2. GDP（Tushare cn_gdp 优先） ──
    pro = _get_ts_api()
    if pro:
        try:
            df = pro.cn_gdp()
            if not df.empty:
                r = df.iloc[0]
                result["gdp_quarter"] = str(r["quarter"])
                result["gdp_value"] = round(float(r["gdp"]), 2)
                result["gdp_yoy"] = round(float(r["gdp_yoy"]), 2)
                result["gdp_trend"] = [
                    {"quarter": str(row["quarter"]), "gdp_yoy": round(float(row["gdp_yoy"]), 2)}
                    for _, row in df.head(8).iterrows()
                ]
            time.sleep(1)
        except Exception:
            pass

    # ── 3. CPI（Tushare cn_cpi 优先） ──
    if pro:
        try:
            df = pro.cn_cpi()
            if not df.empty:
                r = df.iloc[0]
                result["cpi_month"] = str(r["month"])
                result["cpi_yoy"] = round(float(r["nt_yoy"]), 2)
                result["cpi_mom"] = round(float(r.get("nt_mom", 0) or 0), 2)
                result["cpi_accu"] = round(float(r.get("nt_accu", 0) or 0), 2)
            time.sleep(1)
        except Exception:
            pass

    # ── 4. PPI（Tushare cn_ppi 优先） ──
    if pro:
        try:
            df = pro.cn_ppi()
            if not df.empty:
                r = df.iloc[0]
                result["ppi_month"] = str(r["month"])
                result["ppi_yoy"] = round(float(r["ppi_yoy"]), 2)
                result["ppi_mom"] = round(float(r.get("ppi_mom", 0) or 0), 2)
            time.sleep(1)
        except Exception:
            pass

    # ── 5. PMI（akshare，替补Tushare 65列编码） ──
    try:
        df = ak.macro_china_pmi()
        if not df.empty:
            result["pmi_month"] = str(df.iloc[0].iloc[0])
            result["pmi_manufacturing"] = round(float(df.iloc[0].iloc[1]), 2)
            result["pmi_non_manufacturing"] = round(float(df.iloc[0].iloc[3]), 2)
            result["pmi_trend"] = [
                {"month": str(row.iloc[0]), "manufacturing": round(float(row.iloc[1]), 2)}
                for _, row in df.head(12).iterrows()
            ]
        time.sleep(1)
    except Exception:
        pass

    # ── 6. 失业率（akshare，Tushare无此接口） ──
    try:
        df = ak.macro_china_urban_unemployment()
        if not df.empty:
            r = df.iloc[-1]
            result["unemployment_date"] = str(r["date"])
            result["unemployment_value"] = round(float(r["value"]), 2)
        time.sleep(1)
    except Exception:
        pass

    # ── 7. M2货币供应量（akshare，Tushare无此权限） ──
    try:
        df = ak.macro_china_money_supply()
        if not df.empty:
            result["m2_month"] = str(df.iloc[0].iloc[0])
            result["m2_yoy"] = round(float(df.iloc[0].iloc[2]), 2)
            result["m1_yoy"] = round(float(df.iloc[0].iloc[5]), 2)
        time.sleep(1)
    except Exception:
        pass

    return result


def main():
    print("=" * 60)
    print("宏观经济数据采集")
    print("=" * 60)

    data = collect_macro_data()

    print(f"\n[PE估值]")
    print(f"  当前PE: {data.get('pe_current', 'N/A')}")
    print(f"  PE分位(1年): {data.get('pe_percentile_1y', 'N/A')}%")
    print(f"  PE分位(3年): {data.get('pe_percentile_3y', 'N/A')}%")
    print(f"  PE分位(5年): {data.get('pe_percentile_5y', 'N/A')}%")

    print(f"\n[GDP]")
    print(f"  最新: {data.get('gdp_quarter', 'N/A')}, 同比: {data.get('gdp_yoy', 'N/A')}%")
    gdp_trend = data.get('gdp_trend', [])
    if gdp_trend:
        parts = [f'{t["quarter"]}={t["gdp_yoy"]}%' for t in gdp_trend[:4]]
        print(f"  近4期GDP同比: {' | '.join(parts)}")

    print(f"\n[CPI]")
    print(f"  最新: {data.get('cpi_month', 'N/A')}, 同比: {data.get('cpi_yoy', 'N/A')}%, 环比: {data.get('cpi_mom', 'N/A')}%")

    print(f"\n[PPI]")
    print(f"  最新: {data.get('ppi_month', 'N/A')}, 同比: {data.get('ppi_yoy', 'N/A')}%")

    print(f"\n[PMI]")
    print(f"  最新: {data.get('pmi_month', 'N/A')}, 制造业: {data.get('pmi_manufacturing', 'N/A')}")
    pmi_trend = data.get('pmi_trend', [])
    if pmi_trend:
        parts = [f'{t["month"]}={t["manufacturing"]}' for t in pmi_trend[:3]]
        print(f"  近3期PMI: {' | '.join(parts)}")

    print(f"\n[失业率]")
    print(f"  最新: {data.get('unemployment_date', 'N/A')}, 值: {data.get('unemployment_value', 'N/A')}%")

    print(f"\n[货币供应M2]")
    print(f"  最新: {data.get('m2_month', 'N/A')}, M2同比: {data.get('m2_yoy', 'N/A')}%, M1同比: {data.get('m1_yoy', 'N/A')}%")

    print(f"\n{'=' * 60}")
    print(f"共采集 {len(data)} 项数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
