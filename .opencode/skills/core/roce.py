# -*- coding: utf-8 -*-
"""
ROCE 计算模块
数据源: 新浪财经 (akshare)
"""

import akshare as ak
import pandas as pd
import time
from .joblibartifactstore import get_cache


def calculate_roce(
    stock_code: str, year: int, retries: int = 5, delay: int = 3
) -> dict:
    """
    计算单年 ROCE

    参数:
        stock_code: 股票代码，如 "600519"
        year: 年份，如 2024
        retries: 重试次数
        delay: 重试间隔（秒）

    返回:
        {stock_code, year, roce, ebit, capital_employed, net_profit, total_assets, current_liabilities}
    """
    for attempt in range(retries):
        try:
            income = ak.stock_financial_report_sina(stock=stock_code, symbol="利润表")
            balance = ak.stock_financial_report_sina(
                stock=stock_code, symbol="资产负债表"
            )

            date_col = [c for c in income.columns if "报告日" in str(c)][0]

            # 仅匹配年报（12月31日）
            inc_y = income[
                income[date_col].astype(str).str.startswith(str(year) + "12")
            ]
            bal_y = balance[
                balance[date_col].astype(str).str.startswith(str(year) + "12")
            ]

            if inc_y.empty or bal_y.empty:
                inc_y = income[income[date_col].astype(str).str.startswith(str(year))]
                bal_y = balance[balance[date_col].astype(str).str.startswith(str(year))]
                if not inc_y.empty:
                    dates = inc_y[date_col].astype(str).values
                    annual = [d for d in dates if d.endswith("1231")]
                    if not annual:
                        raise ValueError(f"未找到 {year} 年年报数据")
                    inc_y = inc_y[inc_y[date_col].astype(str) == annual[0]]
                    bal_y = bal_y[bal_y[date_col].astype(str) == annual[0]]
                else:
                    raise ValueError(f"未找到 {year} 年财报数据")

            def sg(df, col):
                if col in df.columns:
                    v = df[col].values[0]
                    try:
                        return float(v) if pd.notna(v) and v != "" else 0
                    except:
                        return 0
                return 0

            net_profit = sg(inc_y, "净利润")
            interest_expense = sg(inc_y, "利息费用")
            tax_expense = sg(inc_y, "所得税费用")
            total_assets = sg(bal_y, "资产总计")
            current_liabilities = sg(bal_y, "流动负债合计")

            ebit = net_profit + interest_expense + tax_expense
            capital_employed = total_assets - current_liabilities

            if capital_employed == 0:
                raise ValueError("投入资本为0")

            return {
                "stock_code": stock_code,
                "year": year,
                "roce": ebit / capital_employed,
                "ebit": ebit,
                "capital_employed": capital_employed,
                "net_profit": net_profit,
                "total_assets": total_assets,
                "current_liabilities": current_liabilities,
            }

        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e


def calculate_roce_history(
    stock_code: str, start_year: int = 2015, end_year: int = 2025
) -> list:
    """
    计算多年 ROCE 历史（带缓存，168小时=7天有效）

    参数:
        stock_code: 股票代码
        start_year: 起始年份
        end_year: 结束年份

    返回:
        [{year, roce, net_profit, ebit, capital}, ...]
    """
    # 尝试从缓存获取
    cache = get_cache()
    cache_key = f"roce_history_{stock_code}_{start_year}_{end_year}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    results = []
    for year in range(end_year, start_year - 1, -1):
        try:
            r = calculate_roce(stock_code, year)
            results.append(
                {
                    "year": r["year"],
                    "roce": r["roce"],
                    "net_profit": r["net_profit"],
                    "ebit": r["ebit"],
                    "capital": r["capital_employed"],
                }
            )
        except:
            continue

    # 缓存结果
    cache.set(cache_key, results)
    return results
