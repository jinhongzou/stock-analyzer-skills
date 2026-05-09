# -*- coding: utf-8 -*-
"""
个股分析器

合并自原 stock.py + valuation.py
数据源: 雪球 (akshare) + Tushare Pro
"""
import akshare as ak
import tushare as ts
import pandas as pd
import time
import os
from datetime import datetime, timedelta


class StockAnalyzer:
    """个股全维度分析（行情估值 / 行业归属 / 52周价格分布 / PE估值锚点）"""

    # ══════════════════════════════════════════
    # 行情 & 估值（原 stock.py）
    # ══════════════════════════════════════════

    def get_stock_profile(self, stock_code: str) -> dict:
        """
        获取股票基本信息和估值数据。

        数据源: Tushare Pro（替换原雪球 API）

        Returns:
            {名称, 现价, 涨幅, 市盈率(动), 市盈率(TTM),
             市净率, 股息率(TTM), 资产净值/总市值, 每股收益, 每股净资产, 行业}
        """
        api = self._get_ts_api()
        code = self._normalize_code(stock_code)

        try:
            profile = {}
            today = datetime.now().strftime("%Y%m%d")
            start = (datetime.now() - timedelta(days=10)).strftime("%Y%m%d")

            # 1. 股票名称和行业
            try:
                basic = api.stock_basic(ts_code=code)
                if not basic.empty:
                    row = basic.iloc[0]
                    profile["名称"] = str(row.get("name", stock_code))
                    profile["行业"] = str(row.get("industry", ""))
            except Exception:
                pass

            # 2. 估值数据 (daily_basic)
            try:
                daily_basic = api.daily_basic(ts_code=code, start_date=start, end_date=today)
                if not daily_basic.empty:
                    latest = daily_basic.iloc[0]
                    profile["现价"] = float(latest.get("close", 0))
                    profile["市盈率(动)"] = float(latest.get("pe", 0))
                    profile["市盈率(TTM)"] = float(latest.get("pe_ttm", 0))
                    profile["市净率"] = float(latest.get("pb", 0))
                    profile["股息率(TTM)"] = float(latest.get("dv_ratio", 0))
                    # total_mv 单位为 万元, 转为 亿元
                    total_mv = float(latest.get("total_mv", 0))
                    profile["资产净值/总市值"] = round(total_mv / 10000, 2)
            except Exception:
                pass

            # 3. 涨幅：用最近 2 个交易日收盘价计算
            try:
                df_daily = api.daily(ts_code=code, start_date=start, end_date=today)
                if not df_daily.empty and len(df_daily) >= 2:
                    df_daily = df_daily.sort_values("trade_date", ascending=True)
                    close_series = df_daily["close"].tail(2)
                    change_pct = (close_series.iloc[-1] - close_series.iloc[-2]) / close_series.iloc[-2] * 100
                    profile["涨幅"] = round(float(change_pct), 2)
                elif not df_daily.empty:
                    profile["涨幅"] = 0.0
            except Exception:
                pass

            # 4. 财务指标：每股收益和每股净资产
            try:
                fina = api.fina_indicator(ts_code=code, start_date=f"{datetime.now().year-1}0101", end_date=today, limit=1)
                if not fina.empty:
                    latest_f = fina.iloc[0]
                    eps = latest_f.get("eps")
                    bps = latest_f.get("bps")
                    if eps is not None:
                        profile["每股收益"] = round(float(eps), 4)
                    if bps is not None:
                        profile["每股净资产"] = round(float(bps), 4)
            except Exception:
                pass

            # 行业兜底：如果 stock_basic 未取到行业，用备选方法
            if not profile.get("行业"):
                profile["行业"] = self._get_stock_industry(stock_code)

            return profile

        except Exception:
            return {}

    def analyze_sector(self, stock_code: str) -> dict:
        """
        分析股票所属行业表现。

        Returns:
            {行业, 趋势, 表现, 波动性}
        """
        try:
            industry_data = ak.stock_industry_info()
            stock_industry = industry_data[industry_data["股票代码"] == stock_code]["行业"].values
            if len(stock_industry) == 0:
                return {"行业": "未知", "趋势": "N/A", "表现": "N/A", "波动性": "N/A"}

            sector = stock_industry[0]
            sector_data = industry_data[industry_data["行业"] == sector]
            performance = sector_data["涨跌幅"].mean()
            volatility = sector_data["涨跌幅"].std()
            trend = "积极" if performance > 0 else "消极"

            return {"行业": sector, "趋势": trend, "表现": performance, "波动性": volatility}
        except Exception:
            return {"行业": "未知", "趋势": "N/A", "表现": "N/A", "波动性": "N/A"}

    # ══════════════════════════════════════════
    # 估值锚点（原 valuation.py）
    # ══════════════════════════════════════════

    def get_stock_profile_tushare(self, stock_code: str) -> dict:
        """
        使用 Tushare Pro 获取股票基本信息和估值数据。

        Returns:
            {名称, 现价, 每股收益, 每股分红, 市净率, 行业, 股息率}
            失败返回 {}
        """
        try:
            api = self._get_ts_api()
            code = self._normalize_code(stock_code)

            profile = {}

            # 1. 股票名称和行业
            try:
                basic = api.stock_basic(ts_code=code)
                if not basic.empty:
                    row = basic.iloc[0]
                    profile["名称"] = str(row.get("name", "未知"))
                    profile["行业"] = str(row.get("industry", ""))
            except Exception:
                pass

            # 2. 最新行情和估值 (close, pe, pb, dv_ratio)
            today = datetime.now().strftime("%Y%m%d")
            start = (datetime.now() - timedelta(days=10)).strftime("%Y%m%d")
            try:
                daily = api.daily_basic(ts_code=code, start_date=start, end_date=today)
                if not daily.empty:
                    latest = daily.iloc[0]
                    profile["现价"] = float(latest.get("close", 0))
                    profile["市净率"] = float(latest.get("pb", 0))
                    dv_ratio = float(latest.get("dv_ratio", 0))
                    close_price = float(latest.get("close", 0))
                    # 每股分红 = 股息率(%) × 现价 / 100
                    profile["每股分红"] = round(dv_ratio * close_price / 100, 2) if dv_ratio and close_price else 0
                    profile["股息率"] = dv_ratio
            except Exception:
                pass

            # 3. 最新每股收益
            try:
                income = api.income(ts_code=code, start_date=f"{datetime.now().year-1}0101", end_date=today, limit=1)
                if not income.empty:
                    eps = income.iloc[0].get("basic_eps")
                    if eps is not None:
                        profile["每股收益"] = float(eps)
            except Exception:
                pass

            return profile
        except Exception:
            return {}

    def get_historical_data_tushare(self, stock_code: str, days: int = 365) -> pd.DataFrame:
        """
        获取股票历史数据（Tushare）。

        Returns:
            DataFrame: trade_date, close, high, low
        """
        api = self._get_ts_api()
        code = self._normalize_code(stock_code)
        start_date = (datetime.now() - timedelta(days=days + 30)).strftime("%Y%m%d")

        try:
            df = api.daily(ts_code=code, start_date=start_date)
            if not df.empty:
                df = df.sort_values("trade_date", ascending=True)
                return df[["trade_date", "close", "high", "low"]]
        except Exception:
            pass

        return pd.DataFrame()

    def calculate_price_distribution(self, stock_code: str) -> dict:
        """
        计算 52 周价格分布。

        Returns:
            {high_52w, low_52w, median, q1, q3, position_pct}
            position_pct: 当前位置在 52 周价格区间中的分位数
        """
        df = self.get_historical_data_tushare(stock_code, days=365)
        if df.empty:
            return {}

        closes = df["close"]
        current = closes.iloc[-1]

        return {
            "high_52w": closes.max(),
            "low_52w": closes.min(),
            "median": closes.median(),
            "q1": closes.quantile(0.25),
            "q3": closes.quantile(0.75),
            "position_pct": (closes <= current).sum() / len(closes) * 100,
        }

    def calculate_buy_strategy(
        self, stock_code: str, eps: float = 0, dps: float = 0,
        revenue_growth: float = None, pb: float = 0, industry: str = None
    ) -> dict:
        """
        基于 PE 估值的买入策略。

        经验 PE 区间:
          保守 = 15×, 合理 = 20×, 乐观 = 25×

        Returns:
            {pe_strategy: {保守, 合理, 乐观},
             final_strategy: {strategy, recommendation, reason},
             valuation_note}
        """
        if eps <= 0:
            return {"valuation_note": "EPS数据不可用"}

        pe_levels = {"保守": 15, "合理": 20, "乐观": 25}
        pe_strategy = {level: round(eps * pe, 2) for level, pe in pe_levels.items()}

        return {
            "pe_strategy": pe_strategy,
            "final_strategy": {
                "strategy": {
                    "综合": {
                        "保守": pe_strategy["保守"],
                        "合理": pe_strategy["合理"],
                        "乐观": pe_strategy["乐观"],
                    }
                },
                "recommendation": "在合理价位分批建仓",
                "reason": "基于PE估值法",
            },
            "valuation_note": "估值基于PE法，仅供参考",
        }

    # ──────────────────────────────────────────
    # 内部工具
    # ──────────────────────────────────────────

    def _get_stock_industry(self, stock_code: str) -> str:
        """获取股票所属行业（多数据源尝试）"""
        # 方法1: 东方财富个股信息（最细分）
        for attempt in range(5):
            try:
                info = ak.stock_individual_info_em(symbol=stock_code)
                industry = info[info["item"] == "行业"]["value"].values
                if len(industry) > 0 and str(industry[0]).strip():
                    return str(industry[0])
            except Exception:
                time.sleep(0.5)

        # 方法2: 深交所列表
        if stock_code.startswith("0") or stock_code.startswith("3"):
            try:
                df = ak.stock_info_sz_name_code(symbol="A股列表")
                match = df[df["A股代码"] == stock_code]
                if not match.empty:
                    industry = match.iloc[0].get("所属行业", None)
                    if industry and str(industry).strip():
                        return str(industry)
            except Exception:
                pass

        # 方法3: 上交所列表
        if stock_code.startswith("6"):
            try:
                df = ak.stock_info_sh_name_code(symbol="主板A股")
                match = df[df["证券代码"] == stock_code]
                if not match.empty:
                    industry = match.iloc[0].get("所属行业", None)
                    if industry and str(industry).strip():
                        return str(industry)
            except Exception:
                pass

        return "N/A"

    def _get_ts_api(self):
        """获取 Tushare Pro API 实例"""
        token = self._get_token()
        if token:
            ts.set_token(token)
        return ts.pro_api()

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

    @staticmethod
    def _normalize_code(code: str) -> str:
        """转成 Tushare 格式（带交易所后缀）"""
        code = code.strip()
        if code.startswith("688") or code.startswith("8"):
            return f"{code}.BJ"
        elif code[0] in ("0", "3"):
            return f"{code}.SZ"
        else:
            return f"{code}.SH"
