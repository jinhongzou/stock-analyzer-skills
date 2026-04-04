# -*- coding: utf-8 -*-
"""
A股分红配送详情模块
数据源: 东方财富 (akshare)
接口: stock_fhps_detail_em
"""

import akshare as ak
import pandas as pd


def get_a_dividend_detail(symbol: str) -> pd.DataFrame:
    """
    获取A股历年分红配送详情

    Args:
        symbol: A股股票代码，如 "300073"

    Returns:
        DataFrame with columns:
            - 报告期
            - 业绩披露日期
            - 送转股份-送转总比例
            - 送转股份-送股比例
            - 送转股份-转股比例
            - 现金分红-现金分红比例
            - 现金分红-现金分红比例描述
            - 现金分红-股息率
            - 每股收益
            - 每股净资产
            - 每股公积金
            - 每股未分配利润
            - 净利润同比增长
            - 总股本
            - 预案公告日
            - 股权登记日
            - 除权除息日
            - 方案进度
            - 最新公告日期
    """
    try:
        df = ak.stock_fhps_detail_em(symbol=symbol)
        return df
    except Exception as e:
        print(f"⚠️  获取A股分红数据失败: {e}")
        return pd.DataFrame()


def analyze_dividend_consistency(df: pd.DataFrame) -> dict:
    """
    分析分红连续性和趋势

    Args:
        df: 分红数据 DataFrame

    Returns:
        分红趋势分析结果字典
    """
    if df.empty:
        return {"error": "无分红数据"}

    result = {
        "total_records": len(df),
        "years_with_cash_dividend": 0,
        "years_with_stock_dividend": 0,
        "years_with_transfer": 0,
        "latest_year": None,
        "latest_cash_ratio": None,
        "avg_dividend_yield": 0.0,
        "consistency": "unknown",
    }

    # 统计有现金分红的年份
    if "现金分红-现金分红比例" in df.columns:
        cash_div = pd.to_numeric(df["现金分红-现金分红比例"], errors="coerce")
        result["years_with_cash_dividend"] = int(cash_div.notna().sum())

        # 平均股息率
        if "现金分红-股息率" in df.columns:
            yield_vals = pd.to_numeric(df["现金分红-股息率"], errors="coerce").dropna()
            if len(yield_vals) > 0:
                result["avg_dividend_yield"] = round(float(yield_vals.mean()), 4)

    # 统计有送股的年份
    if "送转股份-送股比例" in df.columns:
        stock_div = pd.to_numeric(df["送转股份-送股比例"], errors="coerce")
        result["years_with_stock_dividend"] = int(stock_div.notna().sum())

    # 统计有转股的年份
    if "送转股份-转股比例" in df.columns:
        transfer = pd.to_numeric(df["送转股份-转股比例"], errors="coerce")
        result["years_with_transfer"] = int(transfer.notna().sum())

    # 最新年份和分红比例
    if len(df) > 0 and "报告期" in df.columns:
        result["latest_year"] = str(df.iloc[0].get("报告期", ""))
        result["latest_cash_ratio"] = df.iloc[0].get("现金分红-现金分红比例", None)

    # 连续性评估
    cash_years = result["years_with_cash_dividend"]
    if cash_years >= 10:
        result["consistency"] = "优秀（连续10年以上分红）"
    elif cash_years >= 5:
        result["consistency"] = "良好（连续5-10年分红）"
    elif cash_years >= 3:
        result["consistency"] = "一般（连续3-5年分红）"
    elif cash_years > 0:
        result["consistency"] = "较短（不足3年）"
    else:
        result["consistency"] = "无现金分红记录"

    return result
