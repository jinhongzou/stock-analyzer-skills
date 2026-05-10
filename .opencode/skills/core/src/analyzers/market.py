# -*- coding: utf-8 -*-
"""
市场分析器

数据源: 乐咕 (市场PE) + 新浪 (上证指数)
"""
import akshare as ak
import pandas as pd
import time
import os


class MarketAnalyzer:
    """A 股市场整体状况分析（市盈率、指数趋势、牛熊判断）"""

    def analyze_market_overview(self) -> dict:
        """
        获取 A 股整体市场数据（平均市盈率）。

        Returns:
            {average_pe, date, index_value} 或空 dict（失败时）
        """
        try:
            df = ak.stock_market_pe_lg()
            latest = df.iloc[-1]
            return {
                "average_pe": latest["平均市盈率"],
                "date": latest["日期"],
                "index_value": latest["指数"],
            }
        except Exception:
            return {}

    def analyze_market_trend(self) -> dict:
        """
        基于上证指数 MA20/MA50 判断牛熊趋势。

        Returns:
            {latest_date, latest_close, ma20, ma50, trend, signal}
        """
        df = ak.stock_zh_index_daily(symbol="sh000001")
        df["MA20"] = df["close"].rolling(window=20).mean()
        df["MA50"] = df["close"].rolling(window=50).mean()

        latest_ma20 = df["MA20"].iloc[-1]
        latest_ma50 = df["MA50"].iloc[-1]
        latest_close = df["close"].iloc[-1]
        latest_date = df["date"].iloc[-1]

        if latest_ma20 > latest_ma50:
            trend = "牛市"
            signal = "短期趋势强于长期趋势"
        else:
            trend = "熊市"
            signal = "短期趋势弱于长期趋势"

        return {
            "latest_date": latest_date,
            "latest_close": latest_close,
            "ma20": latest_ma20,
            "ma50": latest_ma50,
            "trend": trend,
            "signal": signal,
        }


class MarketSystemicRiskAnalyzer:
    """市场系统性风险分析 - 多维度数据采集"""

    def __init__(self):
        self.results = {}
        self._ts_api = None

    # ══════════════════════════════════════════
    # Tushare 初始化
    # ══════════════════════════════════════════

    def _get_ts_api(self):
        """获取 Tushare Pro API 实例"""
        if self._ts_api is not None:
            return self._ts_api
        token = self._get_token()
        if token:
            import tushare as ts
            ts.set_token(token)
            self._ts_api = ts.pro_api()
        return self._ts_api

    @staticmethod
    def _get_token() -> str:
        """从环境变量读取 TUSHARE_TOKEN"""
        token = os.environ.get("TUSHARE_TOKEN", "")
        if token:
            return token
        # 兜底：从 .env 文件读取
        env_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TUSHARE_TOKEN") and "=" in line:
                        return line.split("=", 1)[1].strip()
        except Exception:
            pass
        return ""

    def analyze_all(self) -> dict:
        """执行完整的数据采集"""
        print("\n[Step 1/6] 获取宏观经济数据...")
        macro = self.analyze_macro()
        print(f"  已获取 {len(macro.get('details', {}))} 项数据")

        print("[Step 2/6] 分析市场结构...")
        structure = self.analyze_market_structure()
        print(f"  已获取 {len(structure.get('details', {}))} 项数据")

        print("[Step 3/6] 追踪资金流动...")
        capital = self.analyze_capital_flow()
        print(f"  已获取 {len(capital.get('details', {}))} 项数据")

        print("[Step 4/6] 检测技术面信号...")
        technical = self.analyze_technical_signals()
        print(f"  已获取 {len(technical.get('details', {}))} 项数据")

        print("[Step 5/6] 历史案例对比...")
        history = self.analyze_historical_cases()
        print(f"  已获取 {len(history.get('details', {}))} 项数据")

        print("[Step 6/6] 数据汇总...")

        self.results = {
            "macro": macro,
            "structure": structure,
            "capital": capital,
            "technical": technical,
            "history": history,
        }
        return self.results

    def analyze_macro(self) -> dict:
        """Step 1: 宏观经济数据采集

        数据源策略: Tushare Pro 优先，取不到用 akshare 替补
        代码只提供原始数据，不做任何分析判断
        """
        result = {"details": {}}

        # ── 1. 市场PE历史数据（akshare 乐咕数据） ──
        try:
            pe_df = ak.stock_market_pe_lg()
            if not pe_df.empty:
                latest_pe = pe_df.iloc[-1]["平均市盈率"]
                pe_values = pe_df["平均市盈率"].dropna()
                total_count = len(pe_values)

                if total_count > 0:
                    pe_1y = pe_values.tail(12)
                    pe_3y = pe_values.tail(36)
                    pe_5y = pe_values.tail(60)

                    result["details"]["pe_current"] = round(latest_pe, 2)
                    result["details"]["total_data_points"] = total_count
                    result["details"]["pe_percentile_1y"] = round((pe_1y < latest_pe).sum() / len(pe_1y) * 100, 1) if len(pe_1y) > 0 else None
                    result["details"]["pe_percentile_3y"] = round((pe_3y < latest_pe).sum() / len(pe_3y) * 100, 1) if len(pe_3y) > 0 else None
                    result["details"]["pe_percentile_5y"] = round((pe_5y < latest_pe).sum() / len(pe_5y) * 100, 1) if len(pe_5y) > 0 else None
                    result["details"]["pe_percentile_all"] = round((pe_values < latest_pe).sum() / total_count * 100, 1)

                    pe_trend = []
                    for _, row in pe_df.tail(12).iterrows():
                        pe_trend.append({"date": str(row["日期"]), "pe": round(row["平均市盈率"], 2)})
                    result["details"]["pe_trend"] = pe_trend

                result["details"]["pe_min"] = round(pe_values.min(), 2)
                result["details"]["pe_max"] = round(pe_values.max(), 2)
                result["details"]["pe_median"] = round(pe_values.median(), 2)

            time.sleep(1)
        except Exception as e:
            result["details"]["pe_error"] = str(e)

        # ── 2. GDP 数据（Tushare cn_gdp 优先） ──
        pro = self._get_ts_api()
        if pro:
            try:
                df = pro.cn_gdp()
                if not df.empty:
                    # 最新季度GDP数据（索引0是最新）
                    latest = df.iloc[0]
                    result["details"]["gdp_quarter"] = str(latest["quarter"])
                    result["details"]["gdp_value"] = round(float(latest["gdp"]), 2)
                    result["details"]["gdp_yoy"] = round(float(latest["gdp_yoy"]), 2)
                    # 近 8 个季度趋势
                    gdp_trend = []
                    for _, row in df.head(8).iterrows():
                        gdp_trend.append({
                            "quarter": str(row["quarter"]),
                            "gdp_yoy": round(float(row["gdp_yoy"]), 2),
                        })
                    result["details"]["gdp_trend"] = gdp_trend
                time.sleep(1)
            except Exception:
                pass

        # 替补：akshare GDP
        if "gdp_quarter" not in result["details"]:
            try:
                df = ak.macro_china_gdp()
                if not df.empty:
                    latest = df.iloc[0]
                    result["details"]["gdp_quarter"] = str(latest.iloc[0])
                    result["details"]["gdp_value"] = round(float(latest.iloc[1]), 2)
                    result["details"]["gdp_yoy"] = round(float(latest.iloc[2]), 2)
                    # 近 8 期趋势
                    gdp_trend = []
                    for _, row in df.head(8).iterrows():
                        gdp_trend.append({
                            "quarter": str(row.iloc[0]),
                            "gdp_yoy": round(float(row.iloc[2]), 2),
                        })
                    result["details"]["gdp_trend"] = gdp_trend
                time.sleep(1)
            except Exception:
                pass

        # ── 3. CPI 数据（Tushare cn_cpi 优先） ──
        if pro:
            try:
                df = pro.cn_cpi()
                if not df.empty:
                    latest = df.iloc[0]
                    result["details"]["cpi_month"] = str(latest["month"])
                    result["details"]["cpi_yoy"] = round(float(latest["nt_yoy"]), 2)
                    result["details"]["cpi_mom"] = round(float(latest.get("nt_mom", 0) or 0), 2) if "nt_mom" in df.columns else None
                    result["details"]["cpi_accu"] = round(float(latest.get("nt_accu", 0) or 0), 2) if "nt_accu" in df.columns else None
                    # 近 12 个月趋势
                    cpi_trend = []
                    for _, row in df.head(12).iterrows():
                        cpi_trend.append({
                            "month": str(row["month"]),
                            "cpi_yoy": round(float(row["nt_yoy"]), 2),
                        })
                    result["details"]["cpi_trend"] = cpi_trend
                time.sleep(1)
            except Exception:
                pass

        # 替补：akshare CPI
        if "cpi_yoy" not in result["details"]:
            try:
                df = ak.macro_china_cpi()
                if not df.empty:
                    result["details"]["cpi_month"] = str(df.iloc[0].iloc[0])
                    result["details"]["cpi_yoy"] = round(float(df.iloc[0].iloc[2]), 2)
                    result["details"]["cpi_mom"] = round(float(df.iloc[0].iloc[3]), 2)
                    result["details"]["cpi_accu"] = round(float(df.iloc[0].iloc[4]), 2)
                    # 近 12 个月趋势
                    cpi_trend = []
                    for _, row in df.head(12).iterrows():
                        cpi_trend.append({
                            "month": str(row.iloc[0]),
                            "cpi_yoy": round(float(row.iloc[2]), 2),
                        })
                    result["details"]["cpi_trend"] = cpi_trend
                time.sleep(1)
            except Exception:
                pass

        # ── 4. PPI 数据（Tushare cn_ppi 优先） ──
        if pro:
            try:
                df = pro.cn_ppi()
                if not df.empty:
                    latest = df.iloc[0]
                    result["details"]["ppi_month"] = str(latest["month"])
                    result["details"]["ppi_yoy"] = round(float(latest["ppi_yoy"]), 2)
                    result["details"]["ppi_mom"] = round(float(latest.get("ppi_mom", 0) or 0), 2) if "ppi_mom" in df.columns else None
                    # 近 12 个月趋势
                    ppi_trend = []
                    for _, row in df.head(12).iterrows():
                        ppi_trend.append({
                            "month": str(row["month"]),
                            "ppi_yoy": round(float(row["ppi_yoy"]), 2),
                        })
                    result["details"]["ppi_trend"] = ppi_trend
                time.sleep(1)
            except Exception:
                pass

        # ── 5. PMI 数据（Tushare cn_pmi 有65列编码太复杂，直接用 akshare） ──
        try:
            df = ak.macro_china_pmi()
            if not df.empty:
                result["details"]["pmi_month"] = str(df.iloc[0].iloc[0])
                result["details"]["pmi_manufacturing"] = round(float(df.iloc[0].iloc[1]), 2)
                result["details"]["pmi_non_manufacturing"] = round(float(df.iloc[0].iloc[3]), 2)
                # 近 12 个月趋势
                pmi_trend = []
                for _, row in df.head(12).iterrows():
                    pmi_trend.append({
                        "month": str(row.iloc[0]),
                        "manufacturing": round(float(row.iloc[1]), 2),
                        "non_manufacturing": round(float(row.iloc[3]), 2),
                    })
                result["details"]["pmi_trend"] = pmi_trend
            time.sleep(1)
        except Exception:
            pass

        # ── 6. 失业率（akshare，Tushare 无此接口） ──
        try:
            df = ak.macro_china_urban_unemployment()
            if not df.empty:
                # 筛选"全国城镇调查失业率"
                latest = df.iloc[-1]
                result["details"]["unemployment_date"] = str(latest["date"])
                result["details"]["unemployment_value"] = round(float(latest["value"]), 2)
                result["details"]["unemployment_item"] = str(latest["item"])
                # 近 12 个月趋势
                unemployment_trend = []
                for _, row in df.tail(12).iterrows():
                    unemployment_trend.append({
                        "date": str(row["date"]),
                        "unemployment": round(float(row["value"]), 2),
                    })
                result["details"]["unemployment_trend"] = unemployment_trend
            time.sleep(1)
        except Exception:
            pass

        # ── 7. 货币供应量 M2（akshare，Tushare 无此权限） ──
        try:
            df = ak.macro_china_money_supply()
            if not df.empty:
                result["details"]["m2_month"] = str(df.iloc[0].iloc[0])
                result["details"]["m2_value"] = round(float(df.iloc[0].iloc[1]), 2)
                result["details"]["m2_yoy"] = round(float(df.iloc[0].iloc[2]), 2)
                result["details"]["m1_yoy"] = round(float(df.iloc[0].iloc[5]), 2)
                result["details"]["m0_yoy"] = round(float(df.iloc[0].iloc[8]), 2)
            time.sleep(1)
        except Exception:
            pass

        return result

    def analyze_market_structure(self) -> dict:
        """Step 2: 市场结构数据采集"""
        result = {"details": {}}

        # ── 1. PB历史估值（akshare 乐咕数据） ──
        try:
            pb_df = ak.stock_market_pb_lg()
            if not pb_df.empty:
                pb_values = pb_df.iloc[:, 2].dropna()
                latest_pb = pb_values.iloc[-1]
                result["details"]["pb_current"] = round(latest_pb, 2)
                result["details"]["pb_weighted"] = round(float(pb_df.iloc[-1].iloc[3]), 2)
                result["details"]["pb_median"] = round(float(pb_df.iloc[-1].iloc[4]), 2)
                result["details"]["pb_percentile_1y"] = round((pb_values.tail(250) < latest_pb).sum() / 250 * 100, 1)
                result["details"]["pb_percentile_3y"] = round((pb_values.tail(750) < latest_pb).sum() / 750 * 100, 1)
                result["details"]["pb_percentile_5y"] = round((pb_values.tail(1250) < latest_pb).sum() / 1250 * 100, 1)
                result["details"]["pb_min"] = round(pb_values.min(), 2)
                result["details"]["pb_max"] = round(pb_values.max(), 2)
            time.sleep(1)
        except Exception:
            pass

        # ── 2. 行业板块分布（akshare stock_sector_spot） ──
        try:
            df = ak.stock_sector_spot()
            if not df.empty:
                sorted_df = df.sort_values(by=df.columns[6], ascending=False)
                result["details"]["sector_total"] = len(df)

                top_sectors = []
                for _, row in sorted_df.head(5).iterrows():
                    top_sectors.append({
                        "name": str(row.iloc[1]),
                        "change": round(float(row.iloc[5]), 2),
                        "volume": int(row.iloc[6]),
                    })
                result["details"]["sector_top5"] = top_sectors

                total_volume = df.iloc[:, 6].sum()
                top3_volume = sorted_df.head(3).iloc[:, 6].sum()
                result["details"]["sector_top3_ratio"] = round(float(top3_volume) / float(total_volume) * 100, 2) if total_volume > 0 else 0
                result["details"]["sector_total_volume"] = int(total_volume)

            time.sleep(1)
        except Exception:
            pass

        # ── 3. 产业资本增减持（akshare stock_shareholder_change_ths） ──
        try:
            df = ak.stock_shareholder_change_ths()
            if not df.empty:
                changes = []
                for _, row in df.iterrows():
                    changes.append({
                        "date": str(row.iloc[0]),
                        "shareholder": str(row.iloc[1]),
                        "action": str(row.iloc[2]),
                        "change_volume": str(row.iloc[3]),
                    })
                result["details"]["shareholder_changes"] = changes
                result["details"]["shareholder_change_count"] = len(changes)
            time.sleep(1)
        except Exception:
            pass

        return result

    def analyze_capital_flow(self) -> dict:
        """Step 3: 资金流动数据采集"""
        result = {"details": {}}

        try:
            # 融资融券数据 - 上交所（索引0为最新）
            margin_sse = ak.stock_margin_sse()
            if not margin_sse.empty:
                latest = margin_sse.iloc[0]
                result["details"]["margin_sse_balance"] = round(float(latest.iloc[1]) / 1e8, 2)  # 融资余额
                result["details"]["margin_sse_total"] = round(float(latest.iloc[-1]) / 1e8, 2)   # 融资融券余额
                result["details"]["margin_sse_date"] = str(latest.iloc[0])

                # 融资余额历史 (近10日)
                margin_history = []
                for _, row in margin_sse.head(10).iterrows():
                    margin_history.append({
                        "date": str(row.iloc[0]),
                        "balance": round(float(row.iloc[1]) / 1e8, 2),
                        "total": round(float(row.iloc[-1]) / 1e8, 2)
                    })
                result["details"]["margin_sse_history"] = margin_history

            time.sleep(1)

            # 深交所融资融券 - 用位置索引避免编码问题
            try:
                margin_szse = ak.stock_margin_szse()
                if not margin_szse.empty:
                    result["details"]["margin_szse_balance"] = round(float(margin_szse.iloc[0].iloc[1]), 2) if len(margin_szse.columns) > 1 else 0
            except Exception:
                pass

            time.sleep(1)
        except Exception:
            pass

        return result

    def analyze_technical_signals(self) -> dict:
        """Step 4: 技术面数据采集"""
        result = {"details": {}}

        try:
            # 上证指数数据
            df = ak.stock_zh_index_daily(symbol="sh000001")
            df["MA20"] = df["close"].rolling(window=20).mean()
            df["MA50"] = df["close"].rolling(window=50).mean()
            df["MA200"] = df["close"].rolling(window=200).mean()

            latest = df.iloc[-1]
            result["details"]["index_close"] = round(latest["close"], 2)
            result["details"]["ma20"] = round(latest["MA20"], 2) if pd.notna(latest["MA20"]) else None
            result["details"]["ma50"] = round(latest["MA50"], 2) if pd.notna(latest["MA50"]) else None
            result["details"]["ma200"] = round(latest["MA200"], 2) if pd.notna(latest.get("MA200")) else None

            # 各周期涨跌幅
            if len(df) >= 5:
                result["details"]["change_5d"] = round((latest["close"] - df["close"].iloc[-5]) / df["close"].iloc[-5] * 100, 2)
            if len(df) >= 20:
                result["details"]["change_20d"] = round((latest["close"] - df["close"].iloc[-20]) / df["close"].iloc[-20] * 100, 2)
            if len(df) >= 60:
                result["details"]["change_60d"] = round((latest["close"] - df["close"].iloc[-60]) / df["close"].iloc[-60] * 100, 2)
            if len(df) >= 250:
                result["details"]["change_1y"] = round((latest["close"] - df["close"].iloc[-250]) / df["close"].iloc[-250] * 100, 2)

            # 成交量
            if len(df) >= 60:
                avg_volume = df["volume"].iloc[-60:].mean()
                result["details"]["volume_current"] = int(latest["volume"])
                result["details"]["volume_avg_60d"] = int(avg_volume)
                result["details"]["volume_ratio"] = round(latest["volume"] / avg_volume, 2) if avg_volume > 0 else 1.0

            # 近期价格走势 (近20日)
            price_trend = []
            for _, row in df.tail(20).iterrows():
                price_trend.append({
                    "date": str(row["date"]),
                    "close": round(row["close"], 2),
                    "volume": int(row["volume"])
                })
            result["details"]["price_trend"] = price_trend

            time.sleep(1)
        except Exception as e:
            result["details"]["error"] = str(e)

        return result

    def analyze_historical_cases(self) -> dict:
        """Step 5: 历史数据对比"""
        result = {"details": {}}

        try:
            # 获取历史PE数据用于对比
            pe_df = ak.stock_market_pe_lg()
            if not pe_df.empty:
                pe_df["日期"] = pe_df["日期"].astype(str)

                # 2015年股灾前后PE区间
                pe_2015 = pe_df[(pe_df["日期"] >= "2015-01-01") & (pe_df["日期"] <= "2015-12-31")]
                if not pe_2015.empty:
                    result["details"]["pe_2015_avg"] = round(pe_2015["平均市盈率"].mean(), 2)
                    result["details"]["pe_2015_max"] = round(pe_2015["平均市盈率"].max(), 2)
                    result["details"]["pe_2015_min"] = round(pe_2015["平均市盈率"].min(), 2)

                # 2018年贸易战PE区间
                pe_2018 = pe_df[(pe_df["日期"] >= "2018-01-01") & (pe_df["日期"] <= "2018-12-31")]
                if not pe_2018.empty:
                    result["details"]["pe_2018_avg"] = round(pe_2018["平均市盈率"].mean(), 2)
                    result["details"]["pe_2018_min"] = round(pe_2018["平均市盈率"].min(), 2)
                    result["details"]["pe_2018_max"] = round(pe_2018["平均市盈率"].max(), 2)

                # 2020年疫情底PE
                pe_2020 = pe_df[(pe_df["日期"] >= "2020-02-01") & (pe_df["日期"] <= "2020-04-30")]
                if not pe_2020.empty:
                    result["details"]["pe_2020_min"] = round(pe_2020["平均市盈率"].min(), 2)
                    result["details"]["pe_2020_avg"] = round(pe_2020["平均市盈率"].mean(), 2)

                # 2024-2026 当前周期PE
                pe_recent = pe_df[pe_df["日期"] >= "2024-01-01"]
                if not pe_recent.empty:
                    result["details"]["pe_current_range_min"] = round(pe_recent["平均市盈率"].min(), 2)
                    result["details"]["pe_current_range_max"] = round(pe_recent["平均市盈率"].max(), 2)

            time.sleep(1)
        except Exception as e:
            result["details"]["error"] = str(e)

        return result

    def get_results(self) -> dict:
        """获取分析结果"""
        return self.results