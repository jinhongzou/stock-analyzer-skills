# -*- coding: utf-8 -*-
"""
财务分析器

合并自原 financial.py + roce.py
数据源: 新浪财经 (akshare) — stock_financial_report_sina
"""
import akshare as ak
import pandas as pd
import time


class FinancialAnalyzer:
    """深度财务分析（财务健康指标 + 资本回报率 ROCE）"""

    # ══════════════════════════════════════════
    # 财务健康指标（原 financial.py）
    # ══════════════════════════════════════════

    def get_financial_data(self, stock_code: str) -> dict:
        """
        获取三大财务报表原始数据。

        Returns:
            {balance_sheet, profit_sheet, cash_flow} 各为 DataFrame
        """
        return {
            "balance_sheet": ak.stock_financial_report_sina(stock=stock_code, symbol="资产负债表"),
            "profit_sheet": ak.stock_financial_report_sina(stock=stock_code, symbol="利润表"),
            "cash_flow": ak.stock_financial_report_sina(stock=stock_code, symbol="现金流量表"),
        }

    def analyze_financial_health(self, stock_code: str) -> dict:
        """
        分析财务健康指标（最近 5 期）。

        Returns:
            {ratios: [{date, current_ratio, quick_ratio, debt_ratio, roe}, ...],
             interest_coverage: [{date, ratio}, ...],
             cash_flow: [{date, ocf, fcf}, ...]}
        """
        result = {"ratios": [], "cash_flow": [], "interest_coverage": []}

        data = self.get_financial_data(stock_code)
        balance = data["balance_sheet"]
        profit = data["profit_sheet"]
        cashflow = data["cash_flow"]

        col_ca = self._safe_get_col(balance, "流动资产合计")
        col_cl = self._safe_get_col(balance, "流动负债合计")
        col_inv = self._safe_get_col(balance, "存货")
        col_ta = self._safe_get_col(balance, "资产总计")
        col_tl = self._safe_get_col(balance, "负债合计")
        col_eq = self._safe_get_col(balance, "归属于母公司股东权益合计") or self._safe_get_col(
            balance, "所有者权益"
        )
        col_np = self._safe_get_col(profit, "净利润")
        col_ebit = self._safe_get_col(profit, "利润总额")
        col_int = self._safe_get_col(profit, "利息费用")
        col_ocf = self._safe_get_col(cashflow, "经营活动产生的现金流量净额")
        col_capex = self._safe_get_col(cashflow, "购建固定资产")
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

            result["ratios"].append({
                "date": balance[date_col].iloc[i],
                "current_ratio": ca / cl if cl else 0,
                "quick_ratio": (ca - inv) / cl if cl else 0,
                "debt_ratio": tl / ta if ta else 0,
                "roe": np_val / eq if eq else 0,
            })

            if interest > 0:
                result["interest_coverage"].append({
                    "date": balance[date_col].iloc[i],
                    "ratio": ebit / interest,
                })

            result["cash_flow"].append({
                "date": cashflow["报告日"].iloc[i] if "报告日" in cashflow.columns else balance[date_col].iloc[i],
                "ocf": ocf,
                "fcf": ocf - capex,
            })

        return result

    # ══════════════════════════════════════════
    # ROCE 计算（原 roce.py）
    # ══════════════════════════════════════════

    def calculate_roce(self, stock_code: str, year: int, retries: int = 5, delay: int = 3) -> dict:
        """
        计算单年 ROCE（资本回报率）。

        公式: ROCE = EBIT ÷ 投入资本
              EBIT = 净利润 + 利息费用 + 所得税
              投入资本 = 总资产 - 流动负债

        Returns:
            {stock_code, year, roce, ebit, capital_employed,
             net_profit, total_assets, current_liabilities}
        """
        for attempt in range(retries):
            try:
                income = ak.stock_financial_report_sina(stock=stock_code, symbol="利润表")
                balance = ak.stock_financial_report_sina(stock=stock_code, symbol="资产负债表")

                date_col = [c for c in income.columns if "报告日" in str(c)][0]

                # 优先匹配年报（12月31日）
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

                def _sg(df, col):
                    """safe_get: 从 DataFrame 提取数值"""
                    if col in df.columns:
                        v = df[col].values[0]
                        try:
                            return float(v) if pd.notna(v) and v != "" else 0
                        except (ValueError, TypeError):
                            return 0
                    return 0

                net_profit = _sg(inc_y, "净利润")
                interest_expense = _sg(inc_y, "利息费用")
                tax_expense = _sg(inc_y, "所得税费用")
                total_assets = _sg(bal_y, "资产总计")
                current_liabilities = _sg(bal_y, "流动负债合计")

                ebit = net_profit + interest_expense + tax_expense
                capital_employed = total_assets - current_liabilities

                if capital_employed == 0:
                    raise ValueError("投入资本为0，无法计算ROCE")

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
        self, stock_code: str, start_year: int = 2015, end_year: int = 2025
    ) -> list:
        """
        计算多年 ROCE 历史趋势。

        Returns:
            [{year, roce, net_profit, ebit, capital}, ...]
            从最近年份开始降序排列。
        """
        results = []
        for year in range(end_year, start_year - 1, -1):
            try:
                r = self.calculate_roce(stock_code, year)
                results.append({
                    "year": r["year"],
                    "roce": r["roce"],
                    "net_profit": r["net_profit"],
                    "ebit": r["ebit"],
                    "capital": r["capital_employed"],
                })
            except Exception:
                continue
        return results

    # ──────────────────────────────────────────
    # 内部工具
    # ──────────────────────────────────────────

    @staticmethod
    def _safe_get_col(df: pd.DataFrame, keyword: str):
        """模糊匹配列名（新浪财经返回中文列名，可能存在细微差异）"""
        matches = [c for c in df.columns if keyword in str(c)]
        return matches[0] if matches else None
