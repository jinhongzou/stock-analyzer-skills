# -*- coding: utf-8 -*-
"""
分红分析器

合并自原 dividend.py + a_dividend.py
数据源: 东方财富 (akshare) — stock_fhps_detail_em
"""
import akshare as ak
import pandas as pd


class DividendAnalyzer:
    """A 股分红配送全维度分析（历史分红 / 配送详情 / 连续性 / 质量指标）"""

    # ──────────────────────────────────────────
    # 分红历史（原 dividend.py）
    # ──────────────────────────────────────────

    def get_dividend_history(self, stock_code: str) -> pd.DataFrame:
        """
        获取历年分红数据（最近 10 年）。

        Returns:
            DataFrame: 年份, 每股分红, 股息率, 送转比例, 每股收益, 每股净资产
        """
        try:
            df = self._fetch_dividend_data(stock_code)
            if df.empty:
                return pd.DataFrame()

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
                "年份", "每股分红", "股息率", "送转比例", "每股收益", "每股净资产",
            ]
            return result.sort_values("年份", ascending=False).head(10)
        except Exception:
            return pd.DataFrame()

    def calculate_dividend_metrics(self, stock_code: str, profile: dict) -> dict:
        """
        计算分红质量指标：
          1. 股息率 = 每股年度分红 ÷ 当前股价 × 100%
             (akshare 的"现金分红-现金分红比例"单位是"每10股派X元"，需 ÷10)
          2. 股利支付率 = 每股分红 ÷ 每股收益 × 100%
          3. 派现融资比 = 累计分红总额 ÷ 累计融资总额 × 100%

        Returns:
            {股息率, 股息率解读, 股利支付率, 股利支付率解读, 派现融资比, 派现融资比解读}
        """
        result = {
            "股息率": None, "股息率解读": None,
            "股利支付率": None, "股利支付率解读": None,
            "派现融资比": None, "派现融资比解读": None,
        }

        try:
            df = self._fetch_dividend_data(stock_code)
            if df.empty:
                return result

            # 当前股价
            current_price = None
            try:
                current_price = float(profile.get("现价", 0))
            except (ValueError, TypeError):
                pass

            latest = df.iloc[-1] if len(df) > 0 else None
            if latest is None:
                return result

            cash_per_10 = latest.get("现金分红-现金分红比例", None)
            if cash_per_10 is not None and pd.notna(cash_per_10) and cash_per_10 > 0:
                cash_per_share = cash_per_10 / 10.0  # 每10股→每股

                # 1. 股息率
                if current_price and current_price > 0:
                    dividend_yield = (cash_per_share / current_price) * 100
                    result["股息率"] = dividend_yield
                    if dividend_yield >= 5:
                        result["股息率解读"] = f"{dividend_yield:.2f}% — 高股息，远超银行定存(<3%)和国债(2-3%)"
                    elif dividend_yield >= 3:
                        result["股息率解读"] = f"{dividend_yield:.2f}% — 中等股息，高于银行定存"
                    else:
                        result["股息率解读"] = f"{dividend_yield:.2f}% — 低股息"

                # 2. 股利支付率
                eps = latest.get("每股收益", None)
                if eps is not None and pd.notna(eps) and eps > 0:
                    payout_ratio = (cash_per_share / eps) * 100
                    result["股利支付率"] = payout_ratio
                    if payout_ratio >= 70:
                        result["股利支付率解读"] = f"{payout_ratio:.1f}% — 高分红，大部分利润用于分红"
                    elif payout_ratio >= 30:
                        result["股利支付率解读"] = f"{payout_ratio:.1f}% — 合理分红，兼顾发展和回报"
                    else:
                        result["股利支付率解读"] = f"{payout_ratio:.1f}% — 低分红，利润多用于再投资"

                # 3. 派现融资比
                total_dividend_per_share = sum(
                    row.get("现金分红-现金分红比例", 0) / 10.0
                    for _, row in df.iterrows()
                    if row.get("现金分红-现金分红比例") is not None
                    and pd.notna(row.get("现金分红-现金分红比例"))
                    and row.get("现金分红-现金分红比例", 0) > 0
                )
                total_shares = latest.get("总股本", None)
                if total_shares is not None and pd.notna(total_shares) and total_shares > 0:
                    total_dividend_amount = total_dividend_per_share * total_shares
                else:
                    total_dividend_amount = total_dividend_per_share

                try:
                    ipo_info = ak.stock_ipo_summary_cninfo()
                    stock_row = ipo_info[ipo_info["代码"] == stock_code]
                    if not stock_row.empty:
                        total_finance = stock_row.iloc[0].get("实际募资金额", None)
                        if total_finance is not None and pd.notna(total_finance) and total_finance > 0:
                            finance_ratio = (total_dividend_amount / (total_finance * 1e8)) * 100
                            result["派现融资比"] = finance_ratio
                            if finance_ratio >= 100:
                                result["派现融资比解读"] = f"{finance_ratio:.1f}% — 分红已超过融资，真正回报股东"
                            elif finance_ratio >= 50:
                                result["派现融资比解读"] = f"{finance_ratio:.1f}% — 分红接近融资额，回报良好"
                            else:
                                result["派现融资比解读"] = f"{finance_ratio:.1f}% — 分红低于融资，仍在投入期"
                        else:
                            result["派现融资比解读"] = "无融资数据"
                    else:
                        result["派现融资比解读"] = "无IPO数据"
                except Exception:
                    result["派现融资比解读"] = "暂无融资数据"

        except Exception:
            pass

        return result

    # ──────────────────────────────────────────
    # 分红配送详情（原 a_dividend.py）
    # ──────────────────────────────────────────

    def get_dividend_detail(self, stock_code: str) -> pd.DataFrame:
        """
        获取 A 股历年分红配送完整详情。

        Returns:
            DataFrame 包含报告期、送转比例、现金分红、股息率、每股指标、方案进度等
        """
        try:
            return self._fetch_dividend_data(stock_code)
        except Exception as e:
            print(f"⚠️  获取A股分红数据失败: {e}")
            return pd.DataFrame()

    def analyze_dividend_consistency(self, stock_code: str = None, df: pd.DataFrame = None) -> dict:
        """
        分析分红连续性和趋势。

        Args:
            stock_code: 股票代码（与 df 二选一）
            df: 分红数据 DataFrame

        Returns:
            {total_records, years_with_cash_dividend, years_with_stock_dividend,
             years_with_transfer, avg_dividend_yield, consistency, ...}
        """
        if df is None and stock_code:
            df = self._fetch_dividend_data(stock_code)
        if df is None or df.empty:
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

        # 现金分红
        if "现金分红-现金分红比例" in df.columns:
            cash_div = pd.to_numeric(df["现金分红-现金分红比例"], errors="coerce")
            result["years_with_cash_dividend"] = int(cash_div.notna().sum())

            if "现金分红-股息率" in df.columns:
                yield_vals = pd.to_numeric(df["现金分红-股息率"], errors="coerce").dropna()
                if len(yield_vals) > 0:
                    result["avg_dividend_yield"] = round(float(yield_vals.mean()), 4)

        # 送股
        if "送转股份-送股比例" in df.columns:
            stock_div = pd.to_numeric(df["送转股份-送股比例"], errors="coerce")
            result["years_with_stock_dividend"] = int(stock_div.notna().sum())

        # 转股
        if "送转股份-转股比例" in df.columns:
            transfer = pd.to_numeric(df["送转股份-转股比例"], errors="coerce")
            result["years_with_transfer"] = int(transfer.notna().sum())

        # 最新年份
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

    # ──────────────────────────────────────────
    # 内部工具
    # ──────────────────────────────────────────

    @staticmethod
    def _fetch_dividend_data(stock_code: str) -> pd.DataFrame:
        """统一获取东方财富分红数据"""
        return ak.stock_fhps_detail_em(symbol=stock_code)
