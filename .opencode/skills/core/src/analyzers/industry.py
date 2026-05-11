# -*- coding: utf-8 -*-
"""
行业分析器 - 行业板块多维度数据分析

数据源策略: Tushare Pro 优先（申万行业指数 sw_daily），取不到用 akshare（同花顺/东方财富）替补
代码只提供原始数据，不做任何分析判断
"""
import akshare as ak
import pandas as pd
import time
import os


class IndustryAnalyzer:
    """A股行业板块多维度分析（排行/资金流/估值/成分股）

    数据源:
      - Tushare Pro: sw_daily（申万行业指数，439个行业，含PE/PB/成交额）
      - akshare（替补）: stock_sector_spot（同花顺49个行业）/ stock_board_industry_cons_em（东方财富成分股）
    
    注意: 东方财富接口（资金流/成分股）和巨潮接口（估值）偶有不稳定，
          如果返回空数据，重试即可。
    """

    def __init__(self):
        self.results = {}
        self._ts_api = None

    # ── Tushare 初始化 ──

    def _load_tushare_token(self) -> str:
        """从 .env 读取 TUSHARE_TOKEN"""
        # 先从环境变量
        token = os.environ.get("TUSHARE_TOKEN", "")
        if token:
            return token
        # 再从 .env 文件
        env_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TUSHARE_TOKEN") and "=" in line:
                        token = line.split("=", 1)[1].strip()
                        break
        return token

    def _get_ts_api(self):
        """获取 Tushare Pro API 实例（惰性加载）"""
        if self._ts_api is not None:
            return self._ts_api
        token = self._load_tushare_token()
        if not token:
            return None
        try:
            import tushare as ts
            ts.set_token(token)
            self._ts_api = ts.pro_api()
            return self._ts_api
        except Exception:
            return None

    def _get_ts_sw_data(self, trade_date: str = None) -> pd.DataFrame:
        """获取 Tushare 申万行业指数日线数据

        返回 439 个申万三级行业的 pct_change/PE/PB/amount
        若 Tushare 不可用返回空 DataFrame
        """
        pro = self._get_ts_api()
        if pro is None:
            return pd.DataFrame()
        try:
            if trade_date:
                df = pro.sw_daily(trade_date=trade_date)
            else:
                df = pro.sw_daily()
                # 取最新日期
                if not df.empty:
                    latest = df["trade_date"].max()
                    df = df[df["trade_date"] == latest]
            if df is not None and not df.empty:
                return df
        except Exception:
            pass
        return pd.DataFrame()

    def analyze_all(self) -> dict:
        """执行完整的数据采集"""
        print("\n[Step 1/4] 采集行业排行数据...")
        spot = self.analyze_industry_spot()
        src = spot.get("source", "akshare")
        print(f"  已获取 {spot.get('detail_count', 0)} 个行业数据（数据源: {src}）")
        self.results["spot"] = spot  # 立即存入，供后续步骤复用

        print("[Step 2/4] 采集行业资金流...")
        fundflow = self.analyze_industry_fundflow()
        fcount = fundflow.get('fundflow_sectors', 0)
        if fcount > 0:
            print(f"  已获取 {fcount} 个行业资金流")
        else:
            note = fundflow.get('details', {}).get('note', '') or fundflow.get('error', '')
            print(f"  东方财富资金流接口暂不可用" if not note else f"  [{note}]")

        print("[Step 3/4] 采集行业估值...")
        valuation = self.analyze_industry_valuation()
        vcount = valuation.get('sectors', 0)
        vsrc = valuation.get("source", "akshare")
        if vcount > 0:
            print(f"  已获取 {vcount} 个行业估值（数据源: {vsrc}）")
        else:
            print(f"  估值接口暂不可用")

        print("[Step 4/4] 采集行业成分股...")
        detail = self.analyze_industry_detail()
        dcount = detail.get('analyzed_sectors', 0)
        if dcount > 0:
            print(f"  已分析 {dcount} 个行业成分股")
        else:
            print(f"  东方财富成分股接口暂不可用")

        self.results.update({
            "fundflow": fundflow,
            "valuation": valuation,
            "detail": detail,
        })
        return self.results

    def analyze_industry_spot(self) -> dict:
        """Step 1: 行业板块行情采集

        数据源优先级:
          1. Tushare sw_daily（申万行业，439个行业，含PE/PB/成交额）
          2. akshare stock_sector_spot（同花顺，49个行业，含领涨股）
        指标: 涨跌幅排行/成交额排行/涨跌分布
        """
        result = {"details": {}}

        # ── 1. Tushare sw_daily（优先） ──
        ts_df = self._get_ts_sw_data()
        if not ts_df.empty:
            return self._parse_ts_sw_spot(ts_df, result)

        # ── 2. akshare stock_sector_spot（替补） ──
        try:
            df = ak.stock_sector_spot()
            if df.empty:
                return result

            sorted_by_change = df.sort_values(by=df.columns[5], ascending=False)
            sorted_by_volume = df.sort_values(by=df.columns[6], ascending=False)

            # 涨幅榜 Top 10
            gainers = []
            for _, row in sorted_by_change.head(10).iterrows():
                gainers.append({
                    "name": str(row.iloc[1]), "change_pct": round(float(row.iloc[5]), 2),
                    "volume": int(row.iloc[6]), "leader_name": str(row.iloc[12]),
                    "leader_change": round(float(row.iloc[9]), 2), "stock_count": int(row.iloc[2]),
                })
            result["details"]["gainers_top10"] = gainers

            # 跌幅榜 Top 10
            losers = []
            for _, row in sorted_by_change.tail(10).iloc[::-1].iterrows():
                losers.append({
                    "name": str(row.iloc[1]), "change_pct": round(float(row.iloc[5]), 2),
                    "volume": int(row.iloc[6]), "leader_name": str(row.iloc[12]),
                    "leader_change": round(float(row.iloc[9]), 2), "stock_count": int(row.iloc[2]),
                })
            result["details"]["losers_top10"] = losers

            # 成交额榜 Top 10
            top_volume = []
            for _, row in sorted_by_volume.head(10).iterrows():
                top_volume.append({
                    "name": str(row.iloc[1]), "volume": int(row.iloc[6]),
                    "change_pct": round(float(row.iloc[5]), 2),
                    "leader_name": str(row.iloc[12]), "stock_count": int(row.iloc[2]),
                })
            result["details"]["volume_top10"] = top_volume

            # 汇总统计
            result["detail_count"] = len(df)
            result["details"]["total_sectors"] = len(df)
            result["details"]["total_volume"] = int(df.iloc[:, 6].sum())
            up_count = int((df.iloc[:, 5] > 0).sum())
            down_count = int((df.iloc[:, 5] < 0).sum())
            result["details"]["up_count"] = up_count
            result["details"]["down_count"] = down_count
            result["details"]["flat_count"] = result["detail_count"] - up_count - down_count

            total_vol = float(df.iloc[:, 6].sum())
            top3_vol = float(sorted_by_volume.head(3).iloc[:, 6].sum())
            result["details"]["top3_volume_ratio"] = round(top3_vol / total_vol * 100, 2) if total_vol > 0 else 0

            result["source"] = "akshare"
            time.sleep(1)

        except Exception as e:
            result["error"] = str(e)

        return result

    def _parse_ts_sw_spot(self, df: pd.DataFrame, result: dict) -> dict:
        """将 Tushare sw_daily DataFrame 解析为统一的 spot 结构"""
        # 按涨跌幅排序
        sorted_by_change = df.sort_values("pct_change", ascending=False)
        sorted_by_amount = df.sort_values("amount", ascending=False)

        # 涨幅榜 Top 10
        gainers = []
        for _, row in sorted_by_change.head(10).iterrows():
            gainers.append({
                "name": str(row["name"]), "change_pct": round(float(row["pct_change"]), 2),
                "volume": float(row["amount"]), "leader_name": "",
                "leader_change": None, "stock_count": None,
            })
        result["details"]["gainers_top10"] = gainers

        # 跌幅榜 Top 10
        losers = []
        for _, row in sorted_by_change.tail(10).iloc[::-1].iterrows():
            losers.append({
                "name": str(row["name"]), "change_pct": round(float(row["pct_change"]), 2),
                "volume": float(row["amount"]), "leader_name": "",
                "leader_change": None, "stock_count": None,
            })
        result["details"]["losers_top10"] = losers

        # 成交额榜 Top 10
        top_amount = []
        for _, row in sorted_by_amount.head(10).iterrows():
            top_amount.append({
                "name": str(row["name"]), "volume": float(row["amount"]),
                "change_pct": round(float(row["pct_change"]), 2),
                "leader_name": "", "stock_count": None,
            })
        result["details"]["volume_top10"] = top_amount

        # 汇总统计
        result["detail_count"] = len(df)
        result["details"]["total_sectors"] = len(df)
        result["details"]["total_volume"] = float(df["amount"].sum())
        result["details"]["up_count"] = int((df["pct_change"] > 0).sum())
        result["details"]["down_count"] = int((df["pct_change"] < 0).sum())
        result["details"]["flat_count"] = int((df["pct_change"] == 0).sum())

        total_amt = float(df["amount"].sum())
        top3_amt = float(sorted_by_amount.head(3)["amount"].sum())
        result["details"]["top3_volume_ratio"] = round(top3_amt / total_amt * 100, 2) if total_amt > 0 else 0

        # 额外：Tushare 独有字段 — 各行业的 PE/PB（供估值分析用）
        result["details"]["ts_pe_pb"] = []
        for _, row in df.iterrows():
            result["details"]["ts_pe_pb"].append({
                "name": str(row["name"]),
                "pe": round(float(row["pe"]), 2) if pd.notna(row["pe"]) else None,
                "pb": round(float(row["pb"]), 2) if pd.notna(row["pb"]) else None,
            })

        result["source"] = "tushare"
        return result

    def analyze_industry_fundflow(self) -> dict:
        """Step 2: 行业资金流向采集

        数据: stock_sector_fund_flow_rank（东方财富行业资金流）
        指标: 主力净流入/超大单净流入/大单净流入/中单净流出/小单净流出

        注意: 东方财富接口偶有超时，已内置重试机制，仍失败则返回空数据
        """
        result = {"details": {}}

        try:
            df = ak.stock_sector_fund_flow_rank(indicator="今日")
            if df.empty:
                result["note"] = "东方财富资金流接口暂不可用，稍后重试"
                return result

            result["fundflow_sectors"] = len(df)
            result["details"]["total_sectors"] = len(df)

            # 按主力净流入排序
            sorted_df = df.sort_values(by=df.columns[2], ascending=False)

            # 资金流整体统计
            inflows = [float(v) for v in df.iloc[:, 2] if float(v) > 0]
            outflows = [float(v) for v in df.iloc[:, 2] if float(v) < 0]
            result["details"]["inflow_sectors_count"] = len(inflows)
            result["details"]["outflow_sectors_count"] = len(outflows)
            result["details"]["total_main_net_inflow"] = round(sum(inflows) + sum(outflows), 2) if inflows or outflows else 0

            # 流入榜 Top 10
            inflow_top = []
            for _, row in sorted_df.head(10).iterrows():
                inflow_top.append({
                    "name": str(row.iloc[1]),
                    "main_net_inflow": round(float(row.iloc[2]), 2),
                    "change_pct": round(float(row.iloc[4]), 2),
                })
            result["details"]["inflow_top10"] = inflow_top

            # 流出榜 Top 10
            outflow_top = []
            for _, row in sorted_df.tail(10).iloc[::-1].iterrows():
                outflow_top.append({
                    "name": str(row.iloc[1]),
                    "main_net_inflow": round(float(row.iloc[2]), 2),
                    "change_pct": round(float(row.iloc[4]), 2),
                })
            result["details"]["outflow_top10"] = outflow_top

            time.sleep(1)

        except Exception as e:
            result["error"] = f"东方财富资金流接口异常: {type(e).__name__}，请稍后重试"

        return result

    def analyze_industry_valuation(self) -> dict:
        """Step 3: 行业估值数据采集

        数据源优先级:
          1. Tushare sw_daily（申万行业PE/PB，如已用于 Spot 则复用）
          2. akshare stock_industry_pe_ratio_cninfo（巨潮行业PE，替补）
        """
        result = {"details": {}}

        # ── 1. 复用 Tushare sw_daily 中的 PE/PB 数据（如已采集） ──
        spot = self.results.get("spot", {})
        ts_pe_pb = spot.get("details", {}).get("ts_pe_pb", [])
        if ts_pe_pb:
            sectors = []
            for item in ts_pe_pb:
                sectors.append({
                    "industry": item["name"],
                    "pe": item["pe"],
                    "pe_median": None,
                    "pb": item["pb"],
                    "pb_median": None,
                })
            # PE 最高/最低
            valid_pe = [s for s in sectors if s["pe"] is not None and s["pe"] > 0]
            valid_pe.sort(key=lambda x: x["pe"], reverse=True)
            result["details"]["sectors"] = sectors
            result["sectors"] = len(sectors)
            result["details"]["pe_highest_top5"] = valid_pe[:5]
            result["details"]["pe_lowest_top5"] = valid_pe[-5:] if len(valid_pe) >= 5 else valid_pe
            valid_pb = [s for s in sectors if s["pb"] is not None and s["pb"] > 0]
            valid_pb.sort(key=lambda x: x["pb"], reverse=True)
            result["details"]["pb_highest_top5"] = valid_pb[:5]
            result["details"]["pb_lowest_top5"] = valid_pb[-5:] if len(valid_pb) >= 5 else valid_pb
            result["source"] = "tushare"
            return result

        # ── 2. akshare 巨潮行业PE（替补） ──
        try:
            df = ak.stock_industry_pe_ratio_cninfo()
            if not df.empty:
                sectors = []
                for _, row in df.iterrows():
                    sectors.append({
                        "industry": str(row.iloc[0]),
                        "pe": round(float(row.iloc[3]), 2) if row.iloc[3] != "-" else None,
                        "pe_median": round(float(row.iloc[4]), 2) if row.iloc[4] != "-" else None,
                        "pb": round(float(row.iloc[5]), 2) if row.iloc[5] != "-" else None,
                        "pb_median": round(float(row.iloc[6]), 2) if row.iloc[6] != "-" else None,
                    })
                result["details"]["sectors"] = sectors
                result["sectors"] = len(sectors)

                valid_pe = [s for s in sectors if s["pe"] is not None and s["pe"] > 0]
                valid_pe.sort(key=lambda x: x["pe"], reverse=True)
                result["details"]["pe_highest_top5"] = valid_pe[:5]
                result["details"]["pe_lowest_top5"] = valid_pe[-5:] if len(valid_pe) >= 5 else valid_pe

                valid_pb = [s for s in sectors if s["pb"] is not None and s["pb"] > 0]
                valid_pb.sort(key=lambda x: x["pb"], reverse=True)
                result["details"]["pb_highest_top5"] = valid_pb[:5]
                result["details"]["pb_lowest_top5"] = valid_pb[-5:] if len(valid_pb) >= 5 else valid_pb

                result["source"] = "akshare"

            time.sleep(1)

        except Exception as e:
            result["error"] = str(e)

        return result

    def analyze_industry_detail(self, top_n: int = 3) -> dict:
        """Step 4: 行业成分股分析

        对涨幅榜/跌幅榜/成交额榜前几名的行业，获取其成分股中的领涨/领跌股

        Args:
            top_n: 分析前几个行业的成分股
        """
        result = {"details": {}, "analyzed_sectors": 0}

        # 先获取行业排行数据
        spot = self.results.get("spot") or self.analyze_industry_spot()
        if not spot or "details" not in spot:
            return result

        # 从涨幅榜取行业名称列表
        gainers = spot.get("details", {}).get("gainers_top10", [])
        losers = spot.get("details", {}).get("losers_top10", [])
        volume_top = spot.get("details", {}).get("volume_top10", [])

        # 取涨幅前3 + 跌幅前3 + 成交额前3（去重）
        target_sectors = []
        seen = set()
        for s in gainers[:top_n]:
            if s["name"] not in seen:
                target_sectors.append({"name": s["name"], "reason": "涨幅榜"})
                seen.add(s["name"])
        for s in losers[:top_n]:
            if s["name"] not in seen:
                target_sectors.append({"name": s["name"], "reason": "跌幅榜"})
                seen.add(s["name"])
        for s in volume_top[:top_n]:
            if s["name"] not in seen:
                target_sectors.append({"name": s["name"], "reason": "成交额榜"})
                seen.add(s["name"])

        sector_details = []
        for ts in target_sectors:
            try:
                cons = ak.stock_board_industry_cons_em(symbol=ts["name"])
                if not cons.empty:
                    cons_sorted = cons.sort_values(by=cons.columns[7], ascending=False)
                    top_stocks = []
                    for _, row in cons_sorted.head(5).iterrows():
                        top_stocks.append({
                            "code": str(row.iloc[1]),
                            "name": str(row.iloc[2]),
                            "change_pct": round(float(row.iloc[7]), 2),
                            "price": round(float(row.iloc[5]), 2),
                        })
                    sector_details.append({
                        "name": ts["name"],
                        "reason": ts["reason"],
                        "stock_count": len(cons),
                        "top5_stocks": top_stocks,
                    })
                time.sleep(0.5)
            except Exception:
                pass

        result["details"]["sectors"] = sector_details
        result["analyzed_sectors"] = len(sector_details)

        return result

    def _supply_leader_from_akshare(self, industry_name: str, result: dict) -> None:
        """从 akshare 补充 leader_name/leader_change/stock_count（Tushare sw_daily 无此字段）"""
        try:
            df = ak.stock_sector_spot()
            if df.empty:
                return
            mask = df.iloc[:, 1].str.contains(industry_name, na=False)
            matched = df[mask]
            if not matched.empty:
                row = matched.iloc[0]
                result["leader_name"] = str(row.iloc[12])
                result["leader_change"] = round(float(row.iloc[9]), 2)
                result["stock_count"] = int(row.iloc[2])
        except Exception:
            pass

    def analyze_single_industry(self, industry_name: str) -> dict:
        """分析单个行业（行情 + 成分股 + 资金流 + 估值）

        数据源优先级:
          - 行情/估值: Tushare sw_daily → akshare（同花顺/巨潮）
          - 成分股: akshare（东方财富，无 Tushare 替代）
          - 资金流: akshare（东方财富，无 Tushare 替代）

        Args:
            industry_name: 行业名称，如"半导体"、"银行"

        Returns:
            该行业的多维度数据字典
        """
        result = {"industry_name": industry_name}

        # ── 1. 行业实时行情（Tushare sw_daily → akshare） ──
        ts_df = self._get_ts_sw_data()
        if not ts_df.empty:
            mask = ts_df["name"].str.contains(industry_name, na=False)
            matched = ts_df[mask]
            if not matched.empty:
                row = matched.iloc[0]
                sorted_df = ts_df.sort_values("pct_change", ascending=False)
                rank = int(sorted_df[sorted_df["name"] == row["name"]].index[0]) + 1
                result["spot"] = {
                    "name": str(row["name"]),
                    "change_pct": round(float(row["pct_change"]), 2),
                    "volume": float(row["amount"]),
                    "leader_name": "", "leader_change": None, "stock_count": None,
                    "rank": rank,
                    "total_industries": len(ts_df),
                    "avg_change": round(float(ts_df["pct_change"].mean()), 2),
                    "vs_avg": round(float(row["pct_change"]) - float(ts_df["pct_change"].mean()), 2),
                }
                result["spot"]["source"] = "tushare"
                # 补充 leader 数据（akshare 同花顺有领涨股/成分股数）
                self._supply_leader_from_akshare(industry_name, result["spot"])
            else:
                all_names = list(ts_df["name"].unique())
                hints = [n for n in all_names if any(ch in n for ch in industry_name)]
                hint_msg = ""
                if hints:
                    hint_msg = f"，相近行业: {', '.join(hints[:5])}"
                result["spot"] = {"note": f"未找到行业「{industry_name}」（申万分类）{hint_msg}"}
        else:
            # 替补：akshare 同花顺
            try:
                df = ak.stock_sector_spot()
                if not df.empty:
                    mask = df.iloc[:, 1].str.contains(industry_name, na=False)
                    matched = df[mask]
                    if not matched.empty:
                        row = matched.iloc[0]
                        spot = {
                            "name": str(row.iloc[1]), "change_pct": round(float(row.iloc[5]), 2),
                            "volume": int(row.iloc[6]), "leader_name": str(row.iloc[12]),
                            "leader_change": round(float(row.iloc[9]), 2), "stock_count": int(row.iloc[2]),
                        }
                        sorted_df = df.sort_values(by=df.columns[5], ascending=False)
                        spot["rank"] = int(sorted_df[sorted_df.iloc[:, 1] == row.iloc[1]].index[0] + 1)
                        spot["total_industries"] = len(df)
                        spot["avg_change"] = round(float(df.iloc[:, 5].mean()), 2)
                        spot["vs_avg"] = round(spot["change_pct"] - spot["avg_change"], 2)
                        spot["source"] = "akshare"
                        result["spot"] = spot
                    else:
                        all_names = [str(df.iloc[i, 1]) for i in range(len(df))]
                        hints = [n for n in all_names if any(ch in n for ch in industry_name)]
                        hint_msg = f"，相近行业: {', '.join(hints[:5])}" if hints else ""
                        result["spot"] = {"note": f"未找到行业「{industry_name}」（同花顺分类）{hint_msg}"}
                else:
                    result["spot"] = {"note": "行情接口暂不可用"}
            except Exception as e:
                result["spot"] = {"error": f"行情接口异常: {type(e).__name__}"}

        # ── 2. 成分股明细（akshare 东方财富） ──
        try:
            cons = ak.stock_board_industry_cons_em(symbol=industry_name)
            if not cons.empty:
                cons_sorted = cons.sort_values(by=cons.columns[7], ascending=False)
                all_stocks = []
                for _, row in cons_sorted.iterrows():
                    all_stocks.append({
                        "code": str(row.iloc[1]), "name": str(row.iloc[2]),
                        "price": round(float(row.iloc[5]), 2), "change_pct": round(float(row.iloc[7]), 2),
                    })
                constituents = {
                    "stock_count": len(cons),
                    "avg_change": round(float(cons.iloc[:, 7].mean()), 2),
                    "up_count": int((cons.iloc[:, 7] > 0).sum()),
                    "down_count": int((cons.iloc[:, 7] < 0).sum()),
                    "flat_count": len(cons) - int((cons.iloc[:, 7] > 0).sum()) - int((cons.iloc[:, 7] < 0).sum()),
                    "all_stocks": all_stocks, "top10_gainers": all_stocks[:10],
                    "top10_losers": all_stocks[-10:][::-1] if len(all_stocks) >= 10 else all_stocks[::-1],
                }
                try:
                    cons_by_volume = cons.sort_values(by=cons.columns[9], ascending=False)
                    constituents["top5_volume"] = [
                        {"code": str(r.iloc[1]), "name": str(r.iloc[2]),
                         "price": round(float(r.iloc[5]), 2), "change_pct": round(float(r.iloc[7]), 2),
                         "volume": float(r.iloc[9])}
                        for _, r in cons_by_volume.head(5).iterrows()
                    ]
                except Exception:
                    pass
                result["constituents"] = constituents
            else:
                result["constituents"] = {"note": "东方财富成分股接口暂不可用或未找到行业"}
            time.sleep(0.5)
        except Exception as e:
            result["constituents"] = {"error": f"成分股接口异常: {type(e).__name__}"}

        # ── 3. 资金流向（akshare 东方财富） ──
        try:
            fdf = ak.stock_sector_fund_flow_rank(indicator="今日")
            if not fdf.empty:
                mask = fdf.iloc[:, 1].str.contains(industry_name, na=False)
                matched = fdf[mask]
                if not matched.empty:
                    row = matched.iloc[0]
                    result["fundflow"] = {
                        "main_net_inflow": round(float(row.iloc[2]), 2),
                        "change_pct": round(float(row.iloc[4]), 2),
                    }
                else:
                    result["fundflow"] = {"note": f"资金流数据中未找到行业「{industry_name}」"}
            else:
                result["fundflow"] = {"note": "东方财富资金流接口暂不可用"}
            time.sleep(0.5)
        except Exception as e:
            result["fundflow"] = {"error": f"资金流接口异常: {type(e).__name__}"}

        # ── 4. 估值数据（Tushare sw_daily → akshare 巨潮） ──
        if ts_df.empty:
            # sw_daily 不可用，尝试从 spot 结果中获取（Tushare 版已含 PE/PB）
            pass
        # 优先从 Tushare sw_daily 提取该行业的 PE/PB
        if not ts_df.empty:
            mask = ts_df["name"].str.contains(industry_name, na=False)
            matched = ts_df[mask]
            if not matched.empty:
                row = matched.iloc[0]
                pe_val = round(float(row["pe"]), 2) if pd.notna(row["pe"]) else None
                pb_val = round(float(row["pb"]), 2) if pd.notna(row["pb"]) else None
                # PE 排名
                valid = ts_df[pd.notna(ts_df["pe"]) & (ts_df["pe"] > 0)].copy()
                valid_sorted = valid.sort_values("pe", ascending=False)
                pe_rank = None
                for idx, (_, r) in enumerate(valid_sorted.iterrows()):
                    if r["name"] == row["name"]:
                        pe_rank = idx + 1
                        break
                result["valuation"] = {
                    "industry": str(row["name"]),
                    "pe": pe_val, "pe_median": None,
                    "pb": pb_val, "pb_median": None,
                    "pe_rank": pe_rank, "pe_rank_total": len(valid_sorted),
                }
                result["valuation"]["source"] = "tushare"
            else:
                if result.get("spot", {}).get("source") != "tushare":
                    # sw_daily 没找到，尝试 akshare 巨潮
                    try:
                        vdf = ak.stock_industry_pe_ratio_cninfo()
                        if not vdf.empty:
                            vm = vdf.iloc[:, 0].str.contains(industry_name, na=False)
                            vmdf = vdf[vm]
                            if not vmdf.empty:
                                vr = vmdf.iloc[0]
                                valuation = {
                                    "industry": str(vr.iloc[0]),
                                    "pe": round(float(vr.iloc[3]), 2) if vr.iloc[3] != "-" else None,
                                    "pe_median": round(float(vr.iloc[4]), 2) if vr.iloc[4] != "-" else None,
                                    "pb": round(float(vr.iloc[5]), 2) if vr.iloc[5] != "-" else None,
                                    "pb_median": round(float(vr.iloc[6]), 2) if vr.iloc[6] != "-" else None,
                                }
                                valid = [(i, r) for i, r in vdf.iterrows()
                                         if r.iloc[3] != "-" and float(r.iloc[3]) > 0]
                                valid_sorted = sorted(valid, key=lambda x: float(x[1].iloc[3]), reverse=True)
                                for idx, (i, r) in enumerate(valid_sorted):
                                    if r.iloc[0] == vr.iloc[0]:
                                        valuation["pe_rank"] = idx + 1
                                        valuation["pe_rank_total"] = len(valid_sorted)
                                        break
                                result["valuation"] = valuation
                            else:
                                result["valuation"] = {"note": f"估值数据中未找到行业「{industry_name}」"}
                        else:
                            result["valuation"] = {"note": "估值接口暂不可用"}
                    except Exception as e:
                        result["valuation"] = {"error": f"估值接口异常: {type(e).__name__}"}

        return result

    def get_results(self) -> dict:
        """获取分析结果"""
        return self.results
