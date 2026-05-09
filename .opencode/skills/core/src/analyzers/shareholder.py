# -*- coding: utf-8 -*-
"""
股东分析器

数据源: 新浪财经 (akshare)
"""
import akshare as ak
import pandas as pd


# 国家队关键词（中央级资金，不含地方国资）
_NATIONAL_TEAM_KEYWORDS = [
    "中央汇金", "中国证券金融", "国家集成电路产业投资基金",
    "国家制造业转型升级基金", "国家绿色发展基金", "国家中小企业发展基金",
    "全国社保基金", "基本养老保险基金", "国新投资", "国调基金",
]

# 机构/基金关键词
_FUND_KEYWORDS = [
    "证券投资基金", "基金管理有限公司", "保险", "信托",
    "资产管理", "理财", "QFII", "合格境外",
]

# 高管关键词
_EXECUTIVE_KEYWORDS = [
    "董事", "监事", "总经理", "副总经理", "财务总监",
    "董事会秘书", "高管", "核心技术人员",
]


class ShareholderAnalyzer:
    """股东结构全维度分析（十大流通股东 / 国家队 / 增减持 / 质押 / 回购）"""

    # ══════════════════════════════════════════
    # 十大流通股东
    # ══════════════════════════════════════════

    def get_top_circulating_holders(self, stock_code: str) -> dict:
        """
        获取十大流通股东（最新一期）。

        Returns:
            {date, holders: [{排名, 股东名称, 持股数量, 占流通股比例, 类型}, ...],
             national_team, institutions, executives, state_owned, hk_connect,
             summary: {国家队持股占比, 机构持股占比, ...}}
        """
        df = ak.stock_circulate_stock_holder(symbol=stock_code)
        if df.empty:
            return {"date": None, "holders": [], "summary": {}}

        latest_date = df["截止日期"].max()
        latest = df[df["截止日期"] == latest_date].copy()

        holders = []
        national_team, institutions, executives, state_owned, hk_connect = [], [], [], [], []

        for _, row in latest.iterrows():
            name = str(row["股东名称"])
            holder_type = self._classify_shareholder(name)
            entry = {
                "排名": int(row["编号"]),
                "股东名称": name,
                "持股数量": int(row["持股数量"]),
                "占流通股比例": float(row["占流通股比例"]),
                "股本性质": str(row["股本性质"]),
                "类型": holder_type,
            }
            holders.append(entry)

            if holder_type == "国家队":
                national_team.append(entry)
            elif holder_type == "机构/基金":
                institutions.append(entry)
            elif holder_type == "高管":
                executives.append(entry)
            elif holder_type == "国有股":
                state_owned.append(entry)
            elif holder_type == "陆股通":
                hk_connect.append(entry)

        return {
            "date": str(latest_date),
            "holders": holders,
            "national_team": national_team,
            "institutions": institutions,
            "executives": executives,
            "state_owned": state_owned,
            "hk_connect": hk_connect,
            "summary": {
                "国家队持股占比": f"{sum(h['占流通股比例'] for h in national_team):.2f}%",
                "机构持股占比": f"{sum(h['占流通股比例'] for h in institutions):.2f}%",
                "国有股占比": f"{sum(h['占流通股比例'] for h in state_owned):.2f}%",
                "陆股通占比": f"{sum(h['占流通股比例'] for h in hk_connect):.2f}%",
            },
        }

    # ══════════════════════════════════════════
    # 股东增减持变动
    # ══════════════════════════════════════════

    def get_holder_changes(self, stock_code: str, periods: int = 5) -> list:
        """
        获取股东持股变动情况（最近 N 期对比）。

        Returns:
            [{股东名称, 类型, 变动记录: [{日期, 持股数量, 占流通股比例, 变动数量, 变动比例, 变动方向}, ...]}, ...]
        """
        df = ak.stock_circulate_stock_holder(symbol=stock_code)
        if df.empty:
            return []

        dates = sorted(sorted(df["截止日期"].unique(), reverse=True)[:periods])

        # 按归一化股东名称聚合
        holder_data = {}
        for date in dates:
            period_df = df[df["截止日期"] == date]
            for _, row in period_df.iterrows():
                raw_name = str(row["股东名称"])
                norm_name = self._normalize_name(raw_name)
                if norm_name not in holder_data:
                    holder_data[norm_name] = {
                        "股东名称": raw_name,
                        "类型": self._classify_shareholder(raw_name),
                        "变动记录": [],
                    }
                holder_data[norm_name]["变动记录"].append({
                    "日期": str(date),
                    "持股数量": int(row["持股数量"]),
                    "占流通股比例": float(row["占流通股比例"]),
                })

        # 计算变动量
        result = []
        for name, data in holder_data.items():
            records = data["变动记录"]
            if len(records) < 2:
                continue

            has_change = False
            for i in range(1, len(records)):
                prev = records[i - 1]["持股数量"]
                curr = records[i]["持股数量"]
                change = curr - prev
                change_pct = (change / prev * 100) if prev != 0 else 0

                records[i]["变动数量"] = change
                records[i]["变动比例"] = f"{change_pct:.2f}%"
                records[i]["变动方向"] = "增持" if change > 0 else ("减持" if change < 0 else "不变")

                if change != 0:
                    has_change = True

            if has_change:
                result.append(data)

        result.sort(key=lambda x: x["变动记录"][-1]["持股数量"], reverse=True)
        return result

    # ══════════════════════════════════════════
    # 抛售风险检测
    # ══════════════════════════════════════════

    def detect_selling_risk(self, stock_code: str, periods: int = 5) -> list:
        """
        检测股东抛售风险（连续减持）。

        Returns:
            [{股东名称, 类型, 连续减持期数, 减持总数量, 减持总比例, 风险等级}, ...]
            按风险等级排序（高→中→低）
        """
        df = ak.stock_circulate_stock_holder(symbol=stock_code)
        if df.empty:
            return []

        dates = sorted(sorted(df["截止日期"].unique(), reverse=True)[:periods])
        alerts = []
        holder_data = {}

        for date in dates:
            period_df = df[df["截止日期"] == date]
            for _, row in period_df.iterrows():
                norm_name = self._normalize_name(str(row["股东名称"]))
                if norm_name not in holder_data:
                    holder_data[norm_name] = {
                        "股东名称": str(row["股东名称"]),
                        "类型": self._classify_shareholder(str(row["股东名称"])),
                        "records": [],
                    }
                holder_data[norm_name]["records"].append({
                    "日期": str(date),
                    "持股数量": int(row["持股数量"]),
                    "占流通股比例": float(row["占流通股比例"]),
                })

        for name, data in holder_data.items():
            records = data["records"]
            if len(records) < 2:
                continue

            consecutive_decrease = 0
            max_consecutive = 0
            total_decrease = 0

            for i in range(1, len(records)):
                change = records[i]["持股数量"] - records[i - 1]["持股数量"]
                if change < 0:
                    consecutive_decrease += 1
                    total_decrease += abs(change)
                    max_consecutive = max(max_consecutive, consecutive_decrease)
                else:
                    consecutive_decrease = 0

            if max_consecutive >= 2:
                first_pct = records[0]["占流通股比例"]
                latest_pct = records[-1]["占流通股比例"]
                pct_change = first_pct - latest_pct

                if max_consecutive >= 4 or pct_change > 5:
                    risk = "高"
                elif max_consecutive >= 3 or pct_change > 2:
                    risk = "中"
                else:
                    risk = "低"

                alerts.append({
                    "股东名称": name,
                    "类型": data["类型"],
                    "连续减持期数": max_consecutive,
                    "减持总数量": total_decrease,
                    "减持总比例": f"{pct_change:.2f}%",
                    "风险等级": risk,
                })

        risk_order = {"高": 0, "中": 1, "低": 2}
        alerts.sort(key=lambda x: (risk_order.get(x["风险等级"], 3), -x["减持总数量"]))
        return alerts

    # ══════════════════════════════════════════
    # 股权质押 & 回购（原 shareholder.py 底部）
    # ══════════════════════════════════════════

    def get_pledge_data(self, stock_code: str) -> dict:
        """
        获取个股股权质押数据。

        Returns:
            {summary: {总质押比例}, details: [{...}, ...]}
        """
        try:
            df = ak.stock_gpzy_individual_pledge_ratio_detail_em(symbol=stock_code)
            if df.empty:
                return {"summary": {}, "details": []}

            total_pct = round(float(df["占总股本比例"].sum()), 2)
            return {
                "summary": {"总质押比例": f"{total_pct}%"},
                "details": df.to_dict("records"),
            }
        except Exception:
            return {"summary": {}, "details": []}

    def get_repurchase_data(self, stock_code: str) -> dict:
        """
        获取个股股份回购数据。

        Returns:
            {summary: {是否正在进行回购, 回购次数}, details: [{...}, ...]}
        """
        try:
            df = ak.stock_repurchase_em()
            if df.empty:
                return {"summary": {"是否正在进行回购": "否", "回购次数": 0}, "details": []}

            stock_df = df[df["股票代码"] == stock_code].copy()
            if stock_df.empty:
                return {"summary": {"是否正在进行回购": "否", "回购次数": 0}, "details": []}

            count = len(stock_df)
            ongoing = any("实施" in str(row.get("实施进度", "")) for _, row in stock_df.iterrows())

            return {
                "summary": {"是否正在进行回购": "是" if ongoing else "否", "回购次数": count},
                "details": stock_df.to_dict("records"),
            }
        except Exception:
            return {"summary": {"是否正在进行回购": "否", "回购次数": 0}, "details": []}

    # ══════════════════════════════════════════
    # 内部工具
    # ══════════════════════════════════════════

    @staticmethod
    def _normalize_ts_code(stock_code: str) -> str:
        """
        将股票代码转为 Tushare 格式（带交易所后缀）。
        沪市 6xxxxx → .SH | 深市 0xxxxx → .SZ | 创业板 3xxxxx → .SZ
        科创板 688xxx → .SH | 北交所 8xxxxx → .BJ
        """
        code = stock_code.strip()
        if code.startswith("6"):
            return f"{code}.SH"
        elif code.startswith("0") or code.startswith("3"):
            return f"{code}.SZ"
        elif code.startswith("8"):
            return f"{code}.BJ"
        return code

    @staticmethod
    def _normalize_name(name: str) -> str:
        """归一化股东名称：统一全角/半角符号，消除多余空格"""
        name = name.replace("－", "-").replace("（", "(").replace("）", ")")
        return name.replace(" ", "")

    @classmethod
    def _classify_shareholder(cls, name: str) -> str:
        """判断股东类型"""
        name = cls._normalize_name(name)
        if any(kw in name for kw in _NATIONAL_TEAM_KEYWORDS):
            return "国家队"
        if any(kw in name for kw in _FUND_KEYWORDS):
            return "机构/基金"
        if any(kw in name for kw in _EXECUTIVE_KEYWORDS):
            return "高管"
        if "国有" in name or "国资" in name:
            return "国有股"
        if "香港中央结算" in name:
            return "陆股通"
        if "个人" in name:
            return "自然人"
        return "其他"


# 向后兼容：允许直接模块级导入
_normalize_ts_code = ShareholderAnalyzer._normalize_ts_code
_normalize_name = ShareholderAnalyzer._normalize_name
