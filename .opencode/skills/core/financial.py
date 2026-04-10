# -*- coding: utf-8 -*-
"""
财务健康分析模块
数据源: 新浪财经 (akshare)
"""

import akshare as ak
import pandas as pd
from .joblibartifactstore import get_cache


def safe_get_col(df: pd.DataFrame, keyword: str) -> str:
    """模糊匹配列名"""
    matches = [c for c in df.columns if keyword in str(c)]
    return matches[0] if matches else None


def get_financial_data(stock_code: str) -> dict:
    """
    获取三大财务报表

    返回:
        {balance_sheet, profit_sheet, cash_flow}
    """
    balance_sheet = ak.stock_financial_report_sina(
        stock=stock_code, symbol="资产负债表"
    )
    profit_sheet = ak.stock_financial_report_sina(stock=stock_code, symbol="利润表")
    cash_flow = ak.stock_financial_report_sina(stock=stock_code, symbol="现金流量表")
    return {
        "balance_sheet": balance_sheet,
        "profit_sheet": profit_sheet,
        "cash_flow": cash_flow,
    }


def analyze_financial_health(stock_code: str) -> dict:
    """
    分析财务健康指标（带缓存，24小时有效）

    返回:
        {
            ratios: [{date, current_ratio, quick_ratio, debt_ratio, roe}, ...],
            interest_coverage: [{date, ratio}, ...],
            cash_flow: [{date, ocf, fcf}, ...],
        }
    """
    # 尝试从缓存获取
    cache = get_cache()
    cache_key = f"financial_health_{stock_code}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    result = {"ratios": [], "cash_flow": [], "interest_coverage": []}

    data = get_financial_data(stock_code)
    balance = data["balance_sheet"]
    profit = data["profit_sheet"]
    cashflow = data["cash_flow"]

    col_ca = safe_get_col(balance, "流动资产合计")
    col_cl = safe_get_col(balance, "流动负债合计")
    col_inv = safe_get_col(balance, "存货")
    col_ta = safe_get_col(balance, "资产总计")
    col_tl = safe_get_col(balance, "负债合计")
    col_eq = safe_get_col(balance, "归属于母公司股东权益合计") or safe_get_col(
        balance, "所有者权益"
    )
    col_np = safe_get_col(profit, "净利润")
    col_ebit = safe_get_col(profit, "利润总额")
    col_int = safe_get_col(profit, "利息费用")
    col_ocf = safe_get_col(cashflow, "经营活动产生的现金流量净额")
    col_capex = safe_get_col(cashflow, "购建固定资产")
    date_col = [c for c in balance.columns if "报告日" in str(c)][0]

    n = min(5, len(balance))
    for i in range(n):
        ca = float(balance[col_ca].iloc[i] or 0) if col_ca else 0
        cl = float(balance[col_cl].iloc[i] or 0) if col_cl else 0
        inv = float(balance[col_inv].iloc[i] or 0) if col_inv else 0
        ta = float(balance[col_ta].iloc[i] or 0) if col_ta else 0
        tl = float(balance[col_tl].iloc[i] or 0) if col_tl else 0
        eq = float(balance[col_eq].iloc[i] or 0) if col_eq else 0
        np_val = float(profit[col_np].iloc[i] or 0) if col_np else 0
        ebit = float(profit[col_ebit].iloc[i] or 0) if col_ebit else 0
        interest = float(profit[col_int].iloc[i] or 0) if col_int else 0
        ocf = float(cashflow[col_ocf].iloc[i] or 0) if col_ocf else 0
        capex = float(cashflow[col_capex].iloc[i] or 0) if col_capex else 0

        result["ratios"].append(
            {
                "date": balance[date_col].iloc[i],
                "current_ratio": ca / cl if cl else 0,
                "quick_ratio": (ca - inv) / cl if cl else 0,
                "debt_ratio": tl / ta if ta else 0,
                "roe": np_val / eq if eq else 0,
            }
        )

        if interest > 0:
            result["interest_coverage"].append(
                {
                    "date": balance[date_col].iloc[i],
                    "ratio": ebit / interest,
                }
            )

        result["cash_flow"].append(
            {
                "date": cashflow["报告日"].iloc[i]
                if "报告日" in cashflow.columns
                else balance[date_col].iloc[i],
                "ocf": ocf,
                "fcf": ocf - capex,
            }
        )

    # 缓存结果
    cache.set(cache_key, result)
    return result
