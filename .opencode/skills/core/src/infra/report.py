# -*- coding: utf-8 -*-
"""
报告生成器

合并自原 scorer.py + report.py
功能: 综合评分计算 + Markdown 报告生成
"""
from datetime import datetime


class ReportGenerator:
    """
    综合评分 + Markdown 报告生成。

    评分维度（各 20 分，满分 100）：
      盈利能力 / 财务安全 / 估值合理性 / 技术面 / 新闻风险
    """

    # ══════════════════════════════════════════
    # 综合评分（原 scorer.py）
    # ══════════════════════════════════════════

    def calculate_score(self, profile: dict, roce_data: list, health: dict, tech: dict, news: dict) -> dict:
        """
        综合评分系统（严格模式：考虑趋势恶化）。

        Args:
            profile: 个股基本信息（含市盈率等）
            roce_data: ROCE 历史列表 [{roce, ...}, ...]
            health: 财务健康数据 {ratios: [{current_ratio, debt_ratio, ...}]}
            tech: 技术分析数据 {ma: {signal}, rsi: {signal}}
            news: 新闻风险数据 {total, high, medium, ...}

        Returns:
            {scores: {盈利能力, 财务安全, 估值, 技术面, 新闻风险}, total: int, grade: str}
        """
        scores = {}

        # 1. 盈利能力 (0-20) — ROCE 绝对值 + 趋势
        if roce_data:
            latest_roce = roce_data[0]["roce"] if roce_data else 0
            trend_decline = False
            if len(roce_data) >= 3:
                trend_decline = roce_data[0]["roce"] < roce_data[2]["roce"] * 0.5

            if latest_roce > 0.20 and not trend_decline:
                scores["盈利能力"] = 20
            elif latest_roce > 0.15:
                scores["盈利能力"] = 15
            elif latest_roce > 0.10:
                scores["盈利能力"] = 10
            elif latest_roce > 0.05:
                scores["盈利能力"] = 5
            else:
                scores["盈利能力"] = 2

            if trend_decline:
                scores["盈利能力"] = max(2, scores["盈利能力"] - 5)
        else:
            scores["盈利能力"] = 10

        # 2. 财务安全 (0-20) — 流动比率权重更高
        if health.get("ratios"):
            latest = health["ratios"][0]
            cr = latest["current_ratio"]
            dr = latest["debt_ratio"]
            score = 10
            if cr > 2:
                score += 6
            elif cr > 1.5:
                score += 4
            elif cr > 1:
                score += 2
            elif cr < 0.5:
                score -= 6
            elif cr < 0.8:
                score -= 4
            if dr < 0.3:
                score += 4
            elif dr < 0.5:
                score += 2
            elif dr > 0.7:
                score -= 4
            scores["财务安全"] = max(0, min(20, score))
        else:
            scores["财务安全"] = 10

        # 3. 估值合理性 (0-20)
        try:
            pe = float(profile.get("市盈率(动)", 0))
            if 0 < pe < 15:
                scores["估值"] = 20
            elif 15 <= pe < 25:
                scores["估值"] = 15
            elif 25 <= pe < 40:
                scores["估值"] = 10
            elif pe >= 40:
                scores["估值"] = 5
            else:
                scores["估值"] = 10
        except (ValueError, TypeError):
            scores["估值"] = 10

        # 4. 技术面 (0-20)
        if "ma" in tech:
            ma_signal = tech["ma"].get("signal", "")
            rsi_signal = tech.get("rsi", {}).get("signal", "")
            score = 10
            if ma_signal == "Bullish":
                score += 5
            else:
                score -= 3
            if rsi_signal == "超卖":
                score += 3
            elif rsi_signal == "超买":
                score -= 3
            scores["技术面"] = max(0, min(20, score))
        else:
            scores["技术面"] = 10

        # 5. 新闻风险 (0-20)
        if news.get("total", 0) > 0:
            if news["high"] > 0:
                scores["新闻风险"] = 5
            elif news["medium"] > 0:
                scores["新闻风险"] = 12
            else:
                scores["新闻风险"] = 20
        else:
            scores["新闻风险"] = 15

        # 总分与评级
        total = sum(scores.values())
        if total >= 80:
            grade = "A (优秀)"
        elif total >= 65:
            grade = "B (良好)"
        elif total >= 50:
            grade = "C (一般)"
        elif total >= 35:
            grade = "D (较差)"
        else:
            grade = "E (危险)"

        return {"scores": scores, "total": total, "grade": grade}

    # ══════════════════════════════════════════
    # Markdown 报告生成（原 report.py）
    # ══════════════════════════════════════════

    def generate_report_md(
        self,
        stock_code: str,
        profile: dict,
        market_overview: dict,
        market_trend: dict,
        roce_data: list,
        health: dict,
        tech: dict,
        news: dict,
        dividend,
        score_result: dict,
        shareholder_data: dict = None,
        holder_changes: list = None,
        selling_alerts: list = None,
        dividend_metrics: dict = None,
    ) -> str:
        """
        生成 Markdown 格式的综合分析报告（11 章节）。

        参数说明: 与 calculate_score() 相同，加上股东/分红等补充数据。

        Returns:
            Markdown 字符串
        """
        import pandas as pd

        lines = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        name = profile.get("名称", stock_code) if profile else stock_code

        # ── 标题 ──
        lines.append(f"# {name}（{stock_code}）— 综合分析报告")
        lines.append(f"\n> 分析时间：{now}")
        lines.append("> 数据来源：雪球 / 新浪财经 / 东方财富 / 乐咕")
        lines.append("")

        # ── 一、基本信息 ──
        lines.append("## 一、基本信息\n")
        if profile:
            lines.append("| 项目 | 值 |\n|------|-----|")
            lines.append(f"| 股票名称 | {profile.get('名称', 'N/A')} |")
            lines.append(f"| 现价 | {profile.get('现价', 'N/A')} 元 |")
            lines.append(f"| 涨跌幅 | {profile.get('涨幅', 'N/A')}% |")
            lines.append(f"| 总市值 | {profile.get('资产净值/总市值', 'N/A')} |")
            lines.append(f"| 所属行业 | {profile.get('行业', 'N/A')} |")
            lines.append("")

        # ── 二、市场环境 ──
        lines.append("## 二、市场环境\n")
        lines.append("| 项目 | 值 |\n|------|-----|")
        if market_overview:
            lines.append(f"| 全市场平均 PE | {market_overview['average_pe']:.2f} |")
            lines.append(f"| 指数值 | {market_overview['index_value']:.2f} |")
            lines.append(f"| 数据日期 | {market_overview['date']} |")
        if market_trend:
            lines.append(f"| 上证指数 | {market_trend['latest_close']:.2f} |")
            lines.append(f"| MA20 | {market_trend['ma20']:.2f} |")
            lines.append(f"| MA50 | {market_trend['ma50']:.2f} |")
            lines.append(f"| 市场状态 | {market_trend['trend']} |")
            lines.append(f"| 信号 | {market_trend['signal']} |")
        lines.append("")

        # ── 三、估值指标 ──
        if profile:
            lines.append("## 三、估值指标\n")
            lines.append("| 指标 | 值 |\n|------|-----|")
            lines.append(f"| 市盈率(动) | {profile.get('市盈率(动)', 'N/A')} |")
            lines.append(f"| 市盈率(TTM) | {profile.get('市盈率(TTM)', 'N/A')} |")
            lines.append(f"| 市净率 | {profile.get('市净率', 'N/A')} |")
            lines.append(f"| 股息率(TTM) | {profile.get('股息率(TTM)', 'N/A')}% |")
            lines.append(f"| 每股收益 | {profile.get('每股收益', 'N/A')} |")
            lines.append(f"| 每股净资产 | {profile.get('每股净资产', 'N/A')} |")
            lines.append("")

        # ── 四、ROCE ──
        if roce_data:
            lines.append("## 四、ROCE（资本回报率）\n")
            lines.append("| 年份 | ROCE | 净利润 | EBIT | 投入资本 |\n|------|------|--------|------|---------|")
            for r in roce_data:
                lines.append(f"| {r['year']} | {r['roce']:.2%} | {r['net_profit']/1e8:.1f}亿 | {r['ebit']/1e8:.1f}亿 | {r['capital']/1e8:.1f}亿 |")
            lines.append("")

        # ── 五、财务健康 ──
        if health.get("ratios"):
            lines.append("## 五、财务健康\n")
            lines.append("| 日期 | 流动比率 | 速动比率 | 资产负债率 | ROE |\n|------|---------|---------|-----------|-----|")
            for r in health["ratios"]:
                lines.append(f"| {r['date']} | {r['current_ratio']:.2f} | {r['quick_ratio']:.2f} | {r['debt_ratio']:.2%} | {r['roe']:.2%} |")
            lines.append("")

            if health.get("cash_flow"):
                lines.append("### 自由现金流\n")
                lines.append("| 日期 | 经营现金流 | 自由现金流 |\n|------|-----------|-----------|")
                for c in health["cash_flow"]:
                    lines.append(f"| {c['date']} | {c['ocf']/1e8:.1f}亿 | {c['fcf']/1e8:.1f}亿 |")
                lines.append("")

        # ── 六、技术分析 ──
        lines.append("## 六、技术分析\n")
        ma = tech.get("ma", {})
        if "ma50" in ma:
            lines.append(f"- **MA50**：{ma['ma50']:.2f}")
            lines.append(f"- **MA200**：{ma['ma200']:.2f}")
        else:
            lines.append(f"- **MA短期**：{ma.get('ma_short', 0):.2f}")
            lines.append(f"- **MA长期**：{ma.get('ma_long', 0):.2f}")
        lines.append(f"- **均线信号**：{ma.get('signal', 'N/A')}")
        if ma.get("note"):
            lines.append(f"- **备注**：{ma['note']}")
        rsi = tech.get("rsi", {})
        if rsi.get("rsi") is not None:
            lines.append(f"- **RSI(14)**：{rsi['rsi']:.2f}（{rsi['signal']}）")
        lines.append(f"- **数据范围**：{tech.get('date_range', '')}（{tech.get('trade_days', 0)} 个交易日）")
        lines.append("")

        # ── 七、新闻风险 ──
        lines.append("## 七、新闻风险\n")
        lines.append(f"- **分析新闻**：{news['total']} 条")
        lines.append(f"- 🔴 高风险：{news['high']} 条")
        lines.append(f"- 🟡 中风险：{news['medium']} 条")
        lines.append(f"- 🟢 低风险：{news['low']} 条")
        if news["integrity"] > 0:
            lines.append(f"- ⚠️ **诚信风险**：{news['integrity']} 条")
        lines.append("")
        if news.get("alerts"):
            lines.append("### 风险新闻明细\n")
            lines.append("| 等级 | 类型 | 标题 | 日期 | 关键词 |\n|------|------|------|------|--------|")
            for a in news["alerts"][:10]:
                lines.append(f"| {a['level']} | {a['type']} | {a['title']} | {a['date']} | {', '.join(a['keywords'])} |")
            lines.append("")

        # ── 八、分红历史 ──
        if isinstance(dividend, pd.DataFrame) and not dividend.empty:
            lines.append("## 八、分红历史\n")
            lines.append("| 年份 | 每股分红 | 股息率 | 送转比例 | 每股收益 | 每股净资产 |\n|------|---------|--------|---------|---------|-----------|")
            for _, row in dividend.iterrows():
                lines.append(f"| {int(row['年份'])} | {row['每股分红']:.2f} | {row['股息率']:.4f} | {row['送转比例'] if pd.notna(row['送转比例']) else '-'} | {row['每股收益']:.2f} | {row['每股净资产']:.2f} |")
            lines.append("")

            if dividend_metrics:
                lines.append("### 分红质量指标\n")
                dy = dividend_metrics.get("股息率")
                lines.append(f"- **股息率**: {dy:.2f}% — {dividend_metrics.get('股息率解读', 'N/A')}" if dy else "- **股息率**: N/A")
                pr = dividend_metrics.get("股利支付率")
                lines.append(f"- **股利支付率**: {pr:.1f}% — {dividend_metrics.get('股利支付率解读', 'N/A')}" if pr else "- **股利支付率**: N/A")
                fr = dividend_metrics.get("派现融资比")
                lines.append(f"- **派现融资比**: {fr:.1f}% — {dividend_metrics.get('派现融资比解读', 'N/A')}" if fr else "- **派现融资比**: N/A")
                lines.append("")

        # ── 九、股东结构分析 ──
        if shareholder_data and shareholder_data.get("holders"):
            lines.append("## 九、股东结构分析\n")
            lines.append(f"**截止日期**: {shareholder_data.get('date', 'N/A')}\n")
            lines.append("### 最新十大流通股东\n")
            lines.append("| 排名 | 股东名称 | 持股数量 | 占比% | 类型 |\n|------|----------|---------|-------|------|")
            for h in shareholder_data["holders"][:10]:
                name = h["股东名称"][:42] + ".." if len(h["股东名称"]) > 45 else h["股东名称"]
                lines.append(f"| {h['排名']} | {name} | {h['持股数量']:,} | {h['占流通股比例']:.2f} | {h.get('类型', 'N/A')} |")
            lines.append("")

            summary = shareholder_data.get("summary", {})
            if summary:
                lines.append("### 股东类型分布\n")
                for key, val in summary.items():
                    lines.append(f"- **{key}**: {val}")
                lines.append("")

            if shareholder_data.get("national_team"):
                lines.append("### 国家队持股\n")
                lines.append("| 股东名称 | 持股数量 | 占比% |\n|----------|---------|-------|")
                for h in shareholder_data["national_team"]:
                    lines.append(f"| {h['股东名称'][:40]} | {h['持股数量']:,} | {h['占流通股比例']:.2f}% |")
                lines.append("")

            if holder_changes:
                lines.append("### 股东增减持变动（近5期）\n")
                lines.append("| 类型 | 股东名称 | 最新持股 | 占比% | 变动情况 |\n|------|----------|---------|-------|----------|")
                for item in holder_changes[:15]:
                    records = item.get("变动记录", [])
                    if records:
                        latest = records[-1]
                        change_info = ""
                        for r in reversed(records):
                            if "变动方向" in r:
                                change_info = f"{r['变动方向']}({r.get('变动数量', 0):+,})"
                                break
                        name = item.get("股东名称", "N/A")[:25]
                        lines.append(f"| {item.get('类型', 'N/A')} | {name} | {latest.get('持股数量', 0):,} | {latest.get('占流通股比例', 0):.2f} | {change_info} |")
                lines.append("")

            if selling_alerts:
                lines.append("### ⚠️ 抛售风险预警\n")
                lines.append("| 股东名称 | 类型 | 连续减持期数 | 减持比例 | 风险等级 |\n|----------|------|-------------|---------|---------|")
                for a in selling_alerts:
                    risk_icon = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(a.get("风险等级", ""), "⚪")
                    lines.append(f"| {a.get('股东名称', 'N/A')[:30]} | {a.get('类型', 'N/A')} | {a.get('连续减持期数', 0)} | {a.get('减持总比例', '0')} | {risk_icon} {a.get('风险等级', 'N/A')} |")
                lines.append("")
            else:
                lines.append("### ✅ 抛售风险\n\n未检测到连续减持行为，股东结构稳定。\n")

        # ── 十、综合评分 ──
        lines.append("## 十、综合评分\n")
        lines.append("| 维度 | 得分 | 满分 |\n|------|------|------|")
        for dim, sc in score_result["scores"].items():
            lines.append(f"| {dim} | {sc} | 20 |")
        lines.append(f"| **总分** | **{score_result['total']}** | **100** |\n")
        lines.append(f"**综合评级：{score_result['grade']}**\n")

        grade_table = {
            "A": "优秀 — 积极关注，可考虑买入",
            "B": "良好 — 基本面良好，逢低布局",
            "C": "一般 — 观望为主，等待更好时机",
            "D": "较差 — 风险较高，谨慎对待",
            "E": "危险 — 回避，风险过大",
        }
        grade_letter = score_result["grade"][0] if score_result["grade"] else "?"
        if grade_letter in grade_table:
            lines.append(f"> {grade_table[grade_letter]}\n")

        # ── 十一、投资建议 ──
        lines.append("## 十一、投资建议\n")
        if score_result["total"] >= 80:
            lines.append("📈 **建议：积极关注，可考虑买入**\n")
        elif score_result["total"] >= 65:
            lines.append("📊 **建议：基本面良好，逢低布局**\n")
        elif score_result["total"] >= 50:
            lines.append("⏳ **建议：观望为主，等待更好时机**\n")
        elif score_result["total"] >= 35:
            lines.append("⚠️ **建议：风险较高，谨慎对待**\n")
        else:
            lines.append("🚫 **建议：回避，风险过大**\n")

        risks = []
        if roce_data and roce_data[0]["roce"] < 0.05:
            risks.append(f"ROCE 仅 {roce_data[0]['roce']:.2%}，盈利能力极弱")
        if health.get("ratios") and health["ratios"][0]["current_ratio"] < 1:
            risks.append(f"流动比率 {health['ratios'][0]['current_ratio']:.2f}，短期偿债压力大")
        if news["integrity"] > 0:
            risks.append(f"存在 {news['integrity']} 条诚信风险新闻")
        try:
            pe = float(profile.get("市盈率(动)", 0))
            if pe > 50:
                risks.append(f"PE {pe:.1f}x，估值偏高")
        except (ValueError, TypeError):
            pass
        if market_trend and market_trend.get("trend") == "熊市":
            risks.append("市场处于熊市，注意系统性风险")

        if risks:
            lines.append("### 风险提示\n")
            for r in risks:
                lines.append(f"- ⚠️ {r}")
            lines.append("")

        lines.append("---\n")
        lines.append("> **声明**：本分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。")

        return "\n".join(lines)
