# -*- coding: utf-8 -*-
"""
分红历史模块
数据源: 东方财富 (akshare)
"""

import akshare as ak
import pandas as pd


def get_dividend_history(stock_code: str) -> pd.DataFrame:
    """
    获取历年分红数据

    返回:
        DataFrame with columns: 年份, 每股分红, 股息率, 送转比例, 每股收益, 每股净资产
    """
    try:
        df = ak.stock_fhps_detail_em(symbol=stock_code)
        df["年份"] = pd.to_datetime(df["报告期"]).dt.year
        cols = [
            "年份",
            "现金分红-现金分红比例",
            "现金分红-股息率",
            "送转股份-送转总比例",
            "每股收益",
            "每股净资产",
        ]
        available = [c for c in cols if c in df.columns]
        result = df[available].copy()
        result.columns = [
            "年份",
            "每股分红",
            "股息率",
            "送转比例",
            "每股收益",
            "每股净资产",
        ]
        result = result.sort_values("年份", ascending=False).head(10)
        return result
    except:
        return pd.DataFrame()


def calculate_dividend_metrics(stock_code: str, profile: dict) -> dict:
    """
    计算分红相关指标：
    1. 股息率 = (每股年度分红 ÷ 当前股价) × 100%
       注：akshare的"现金分红-现金分红比例"单位是"每10股派X元"，需÷10
    2. 股利支付率 = (年度分红总额 ÷ 年度净利润) × 100%
       = 每股分红 ÷ 每股收益 × 100%
    3. 派现融资比 = (上市以来累计分红总额 ÷ 上市以来累计融资总额) × 100%
    """
    result = {
        "股息率": None,
        "股息率解读": None,
        "股利支付率": None,
        "股利支付率解读": None,
        "派现融资比": None,
        "派现融资比解读": None,
    }

    try:
        # 获取分红历史
        df = ak.stock_fhps_detail_em(symbol=stock_code)
        if df.empty:
            return result

        # 获取当前股价
        current_price = None
        try:
            current_price = float(profile.get("现价", 0))
        except:
            pass

        # 最新一年的数据
        latest = df.iloc[-1] if len(df) > 0 else None
        if latest is None:
            return result

        # "现金分红-现金分红比例" 单位是"每10股派X元"，需要÷10得到每股分红
        cash_per_10 = latest.get("现金分红-现金分红比例", None)
        if cash_per_10 and pd.notna(cash_per_10) and cash_per_10 > 0:
            cash_per_share = cash_per_10 / 10.0  # 转换为每股分红

            # 1. 股息率 = 每股分红 / 当前股价
            if current_price and current_price > 0:
                dividend_yield = (cash_per_share / current_price) * 100
                result["股息率"] = dividend_yield
                if dividend_yield >= 5:
                    result["股息率解读"] = (
                        f"{dividend_yield:.2f}% — 高股息，远超银行定存(<3%)和国债(2-3%)"
                    )
                elif dividend_yield >= 3:
                    result["股息率解读"] = (
                        f"{dividend_yield:.2f}% — 中等股息，高于银行定存"
                    )
                else:
                    result["股息率解读"] = f"{dividend_yield:.2f}% — 低股息"

            # 2. 股利支付率 = 每股分红 / 每股收益
            eps = latest.get("每股收益", None)
            if eps and pd.notna(eps) and eps > 0:
                payout_ratio = (cash_per_share / eps) * 100
                result["股利支付率"] = payout_ratio
                if payout_ratio >= 70:
                    result["股利支付率解读"] = (
                        f"{payout_ratio:.1f}% — 高分红，大部分利润用于分红"
                    )
                elif payout_ratio >= 30:
                    result["股利支付率解读"] = (
                        f"{payout_ratio:.1f}% — 合理分红，兼顾发展和回报"
                    )
                else:
                    result["股利支付率解读"] = (
                        f"{payout_ratio:.1f}% — 低分红，利润多用于再投资"
                    )

            # 3. 派现融资比 = 累计分红总额 / 累计融资总额
            total_dividend_per_share = 0
            for _, row in df.iterrows():
                cash = row.get("现金分红-现金分红比例", None)
                if cash and pd.notna(cash) and cash > 0:
                    total_dividend_per_share += cash / 10.0

            total_shares = latest.get("总股本", None)
            if total_shares and pd.notna(total_shares) and total_shares > 0:
                total_dividend_amount = total_dividend_per_share * total_shares
            else:
                total_dividend_amount = total_dividend_per_share

            try:
                ipo_info = ak.stock_ipo_summary_cninfo()
                stock_row = ipo_info[ipo_info["代码"] == stock_code]
                if not stock_row.empty:
                    total_finance = stock_row.iloc[0].get("实际募资金额", None)
                    if total_finance and pd.notna(total_finance) and total_finance > 0:
                        total_finance_yuan = total_finance * 1e8
                        finance_ratio = (
                            total_dividend_amount / total_finance_yuan
                        ) * 100
                        result["派现融资比"] = finance_ratio
                        if finance_ratio >= 100:
                            result["派现融资比解读"] = (
                                f"{finance_ratio:.1f}% — 分红已超过融资，真正回报股东"
                            )
                        elif finance_ratio >= 50:
                            result["派现融资比解读"] = (
                                f"{finance_ratio:.1f}% — 分红接近融资额，回报良好"
                            )
                        else:
                            result["派现融资比解读"] = (
                                f"{finance_ratio:.1f}% — 分红低于融资，仍在投入期"
                            )
                    else:
                        result["派现融资比解读"] = "无融资数据"
                else:
                    result["派现融资比解读"] = "无IPO数据"
            except:
                result["派现融资比解读"] = "暂无融资数据"

    except Exception as e:
        pass

    return result
