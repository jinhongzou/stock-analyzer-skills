# -*- coding: utf-8 -*-
"""
报告导出模块 — 将分析数据转换为 Markdown 格式
"""

from datetime import datetime
import pandas as pd


def generate_report_md(
    stock_code: str,
    profile: dict,
    sector: dict = None,
    market_overview: dict = None,
    market_trend: dict = None,
    roce_data: list = None,
    health: dict = None,
    tech: dict = None,
    news: dict = None,
    dividend=None,
    score_result: dict = None,
    shareholder_data: dict = None,
    holder_changes: list = None,
    selling_alerts: list = None,
    dividend_metrics: dict = None,
) -> str:
    """
    生成 Markdown 格式的综合分析报告

    参数:
        stock_code: 股票代码
        profile: 个股基本信息
        market_overview: 市场概览
        market_trend: 市场趋势
        roce_data: ROCE 历史数据
        health: 财务健康数据
        tech: 技术分析数据
        news: 新闻风险数据
        dividend: 分红历史 DataFrame
        score_result: 综合评分结果

    返回:
        Markdown 字符串
    """
    import pandas as pd

    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    name = profile.get("名称", stock_code) if profile else stock_code

    # ========== 标题 ==========
    lines.append(f"# {name}（{stock_code}）— 综合分析报告")
    lines.append(f"\n> 分析时间：{now}")
    lines.append(f"> 数据来源：雪球 / 新浪财经 / 东方财富 / 乐咕")
    lines.append("")

    # ========== 一、基本信息 ==========
    lines.append("## 一、基本信息")
    lines.append("")
    if profile:
        lines.append("| 项目 | 值 |")
        lines.append("|------|-----|")
        lines.append(f"| 股票名称 | {profile.get('名称', 'N/A')} |")
        lines.append(f"| 现价 | {profile.get('现价', 'N/A')} 元 |")
        lines.append(f"| 涨跌幅 | {profile.get('涨幅', 'N/A')}% |")
        lines.append(f"| 总市值 | {profile.get('资产净值/总市值', 'N/A')} |")
        lines.append(f"| 所属行业 | {profile.get('行业', 'N/A')} |")

    # 行业分析
    if sector and sector.get("行业"):
        lines.append("")
        lines.append("### 行业分析")
        lines.append("")
        lines.append(f"- **行业**: {sector.get('行业', 'N/A')}")
        if sector.get("趋势") and sector.get("趋势") != "N/A":
            lines.append(f"- **行业趋势**: {sector.get('趋势')}")
        if sector.get("表现") and sector.get("表现") != "N/A":
            lines.append(f"- **行业近期表现**: {sector.get('表现'):.2f}%")
        if sector.get("波动性") and sector.get("波动性") != "N/A":
            lines.append(f"- **行业波动性**: {sector.get('波动性'):.2f}%")
    lines.append("")

    # ========== 二、市场环境 ==========
    lines.append("## 二、市场环境")
    lines.append("")
    lines.append("| 项目 | 值 |")
    lines.append("|------|-----|")
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

    # ========== 三、估值指标 ==========
    if profile:
        lines.append("## 三、估值指标")
        lines.append("")
        lines.append("| 指标 | 值 |")
        lines.append("|------|-----|")
        lines.append(f"| 市盈率(动) | {profile.get('市盈率(动)', 'N/A')} |")
        lines.append(f"| 市盈率(TTM) | {profile.get('市盈率(TTM)', 'N/A')} |")
        lines.append(f"| 市净率 | {profile.get('市净率', 'N/A')} |")
        lines.append(f"| 股息率(TTM) | {profile.get('股息率(TTM)', 'N/A')}% |")
        lines.append(f"| 每股收益 | {profile.get('每股收益', 'N/A')} |")
        lines.append(f"| 每股净资产 | {profile.get('每股净资产', 'N/A')} |")
        lines.append("")

    # ========== 四、ROCE ==========
    if roce_data:
        lines.append("## 四、ROCE（资本回报率）")
        lines.append("")
        lines.append("| 年份 | ROCE | 净利润 | EBIT | 投入资本 |")
        lines.append("|------|------|--------|------|---------|")
        for r in roce_data:
            lines.append(
                f"| {r['year']} | {r['roce']:.2%} | "
                f"{r['net_profit'] / 1e8:.1f}亿 | "
                f"{r['ebit'] / 1e8:.1f}亿 | "
                f"{r['capital'] / 1e8:.1f}亿 |"
            )
        lines.append("")

    # ========== 五、财务健康 ==========
    if health.get("ratios"):
        lines.append("## 五、财务健康")
        lines.append("")
        lines.append("| 日期 | 流动比率 | 速动比率 | 资产负债率 | ROE |")
        lines.append("|------|---------|---------|-----------|-----|")
        for r in health["ratios"]:
            lines.append(
                f"| {r['date']} | {r['current_ratio']:.2f} | "
                f"{r['quick_ratio']:.2f} | {r['debt_ratio']:.2%} | "
                f"{r['roe']:.2%} |"
            )
        lines.append("")

        if health.get("cash_flow"):
            lines.append("### 自由现金流")
            lines.append("")
            lines.append("| 日期 | 经营现金流 | 自由现金流 |")
            lines.append("|------|-----------|-----------|")
            for c in health["cash_flow"]:
                lines.append(
                    f"| {c['date']} | {c['ocf'] / 1e8:.1f}亿 | {c['fcf'] / 1e8:.1f}亿 |"
                )
            lines.append("")

    # ========== 六、技术分析 ==========
    lines.append("## 六、技术分析")
    lines.append("")
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

    # Beta 指标
    beta = tech.get("beta", {})
    if beta and beta.get("beta") is not None:
        lines.append(
            f"- **Beta（相对沪深300）**：{beta['beta']:.4f}（{beta['interpretation']}）"
        )
        lines.append(f"  - 交易日：{beta['trading_days']}，区间：{beta['date_range']}")

    # 52周价格分布
    pd = tech.get("price_distribution", {})
    if pd and pd.get("high_52w"):
        lines.append(f"- **52周价格分布**：")
        lines.append(f"  - 52周高点：{pd.get('high_52w')}元")
        lines.append(f"  - 52周低点：{pd.get('low_52w')}元")
        lines.append(f"  - 中位数：{pd.get('median')}元")
        lines.append(f"  - Q1(25%)：{pd.get('q1')}元")
        lines.append(f"  - 当前位置：{pd.get('position_pct')}%分位")

    # 买入点策略
    bs = tech.get("buy_strategy", {})
    if bs and bs.get("final_strategy"):
        final = bs["final_strategy"]

        # 特殊情况标识
        special = bs.get("special_case")
        if special:
            lines.append(f"- **特殊情况**：{special}")

        # 估值方法提示（行业与PE/PB的关系）
        valuation_note = bs.get("valuation_note")
        if valuation_note:
            lines.append(f"- **{valuation_note}**")

        # PE/PEG/PB 估值详情
        if bs.get("peg_strategy"):
            pg = bs["peg_strategy"]
            lines.append(f"- **PEG估值**：PEG={pg.get('peg')}（成长股）")
            lines.append(
                f"  - 激进/稳健/理想: {pg.get('激进')}元 / {pg.get('稳健')}元 / {pg.get('理想')}元"
            )
        elif bs.get("pb_strategy"):
            pb = bs["pb_strategy"]
            lines.append(f"- **PB估值**：PB={pb.get('pb')}（周期股）")
            lines.append(
                f"  - 激进/稳健/理想: {pb.get('激进')}元 / {pb.get('稳健')}元 / {pb.get('理想')}元"
            )
        elif bs.get("pe_strategy"):
            pe = bs["pe_strategy"]
            lines.append(
                f"- **PE估值**：激进/稳健/理想: {pe.get('激进')}元 / {pe.get('稳健')}元 / {pe.get('理想')}元"
            )

        # 股息率锚定
        if bs.get("dividend_strategy"):
            div = bs["dividend_strategy"]
            lines.append(
                f"- **股息率锚定**：激进/稳健/理想: {div.get('激进')}元 / {div.get('稳健')}元 / {div.get('理想')}元"
            )

        lines.append(f"- **买入点策略**：")
        lines.append(f"  - 推荐：{final.get('recommendation')}")
        lines.append(f"  - 原因：{final.get('reason')}")

        strat = final.get("strategy", {})
        if strat and strat.get("综合"):
            lines.append(f"  - 综合价格（多维交叉）：")
            for k, v in strat["综合"].items():
                lines.append(f"    - {k}：{v}元")

        # 透明化推理说明
        notes = bs.get("reasoning_notes", [])
        if notes:
            lines.append("  - 透明化推理：")
            for note in notes:
                lines.append(f"    • {note}")

    lines.append(
        f"- **数据范围**：{tech.get('date_range', '')}（{tech.get('trade_days', 0)} 个交易日）"
    )
    lines.append("")

    # ========== 七、新闻风险 ==========
    lines.append("## 七、新闻风险")
    lines.append("")
    lines.append(f"- **分析新闻**：{news['total']} 条")
    lines.append(f"- 🔴 高风险：{news['high']} 条")
    lines.append(f"- 🟡 中风险：{news['medium']} 条")
    lines.append(f"- 🟢 低风险：{news['low']} 条")
    if news["integrity"] > 0:
        lines.append(f"- ⚠️ **诚信风险**：{news['integrity']} 条")

    # 网络舆情（Tavily）
    if news.get("total_web", 0) > 0:
        web_high = sum(1 for r in news.get("web_results", []) if r["level"] == "高")
        web_med = sum(1 for r in news.get("web_results", []) if r["level"] == "中")
        lines.append(f"- **网络舆情（Tavily）**：{news['total_web']} 条")
        lines.append(f"  - 🔴 高风险：{web_high} 条")
        lines.append(f"  - 🟡 中风险：{web_med} 条")

    lines.append("")

    if news.get("alerts"):
        lines.append("### 本地新闻风险明细")
        lines.append("")
        lines.append("| 等级 | 类型 | 标题 | 日期 | 关键词 |")
        lines.append("|------|------|------|------|--------|")
        for a in news["alerts"][:10]:
            lines.append(
                f"| {a['level']} | {a['type']} | {a['title']} | "
                f"{a['date']} | {', '.join(a['keywords'])} |"
            )
        lines.append("")

    # 网络舆情明细
    if news.get("web_results"):
        lines.append("### 网络舆情风险明细")
        lines.append("")
        lines.append("| 等级 | 类型 | 标题 | 关键词 | 来源 |")
        lines.append("|------|------|------|------|--------|------|")
        for a in news["web_results"][:10]:
            title = (
                a.get("title", "")[:30] + "..."
                if len(a.get("title", "")) > 30
                else a.get("title", "")
            )
            source = (
                a.get("source", "")[:25] + "..."
                if len(a.get("source", "")) > 25
                else a.get("source", "")
            )
            lines.append(
                f"| {a['level']} | {a['type']} | {title} | {', '.join(a.get('keywords', []))} | {source} |"
            )
        lines.append("")

    # ========== 八、分红历史 ==========
    try:
        dividend_df = dividend if isinstance(dividend, pd.DataFrame) else None
        if dividend_df is not None and not dividend_df.empty:
            lines.append("## 八、分红历史")
            lines.append("")
            lines.append(
                "| 年份 | 每股分红 | 股息率 | 送转比例 | 每股收益 | 每股净资产 |"
            )
            lines.append("|------|---------|--------|---------|---------|-----------|")
            for _, row in dividend_df.iterrows():
                lines.append(
                    f"| {int(row['年份'])} | {row['每股分红']:.2f} | "
                    f"{row['股息率']:.4f} | "
                    f"{row['送转比例'] if pd.notna(row['送转比例']) else '-'} | "
                    f"{row['每股收益']:.2f} | {row['每股净资产']:.2f} |"
                )
            lines.append("")

            # 分红质量指标
            if dividend_metrics:
                lines.append("### 分红质量指标")
                lines.append("")

                dy = dividend_metrics.get("股息率")
                if dy is not None:
                    lines.append(f"- **股息率**: {dy:.2f}%")
                    lines.append(
                        f"  - 解读: {dividend_metrics.get('股息率解读', 'N/A')}"
                    )
                else:
                    lines.append(f"- **股息率**: N/A")
                    lines.append(
                        f"  - 解读: {dividend_metrics.get('股息率解读', '暂无数据')}"
                    )

                pr = dividend_metrics.get("股利支付率")
                if pr is not None:
                    lines.append(f"- **股利支付率**: {pr:.1f}%")
                    lines.append(
                        f"  - 解读: {dividend_metrics.get('股利支付率解读', 'N/A')}"
                    )
                else:
                    lines.append(f"- **股利支付率**: N/A")
                    lines.append(
                        f"  - 解读: {dividend_metrics.get('股利支付率解读', '暂无数据')}"
                    )

                fr = dividend_metrics.get("派现融资比")
                if fr is not None:
                    lines.append(f"- **派现融资比**: {fr:.1f}%")
                    lines.append(
                        f"  - 解读: {dividend_metrics.get('派现融资比解读', 'N/A')}"
                    )
                else:
                    lines.append(f"- **派现融资比**: N/A")
                    lines.append(
                        f"  - 解读: {dividend_metrics.get('派现融资比解读', '暂无数据')}"
                    )

                lines.append("")
    except Exception as e:
        pass  # 忽略分红数据错误

    # ========== 九、股东结构分析 ==========
    if shareholder_data and shareholder_data.get("holders"):
        lines.append("## 九、股东结构分析")
        lines.append("")
        lines.append(f"**截止日期**: {shareholder_data.get('date', 'N/A')}")
        lines.append("")

        # 十大流通股东
        lines.append("### 最新十大流通股东")
        lines.append("")
        lines.append("| 排名 | 股东名称 | 持股数量 | 占比% | 类型 |")
        lines.append("|------|----------|---------|-------|------|")
        for h in shareholder_data["holders"][:10]:
            name = (
                h["股东名称"][:42] + ".." if len(h["股东名称"]) > 45 else h["股东名称"]
            )
            lines.append(
                f"| {h['排名']} | {name} | {h['持股数量']:,} | "
                f"{h['占流通股比例']:.2f} | {h.get('类型', 'N/A')} |"
            )
        lines.append("")

        # 股东类型汇总
        summary = shareholder_data.get("summary", {})
        if summary:
            lines.append("### 股东类型分布")
            lines.append("")
            for key, val in summary.items():
                lines.append(f"- **{key}**: {val}")
            lines.append("")

        # 国家队
        if shareholder_data.get("national_team"):
            lines.append("### 国家队持股")
            lines.append("")
            lines.append("| 股东名称 | 持股数量 | 占比% |")
            lines.append("|----------|---------|-------|")
            for h in shareholder_data["national_team"]:
                lines.append(
                    f"| {h['股东名称'][:40]} | {h['持股数量']:,} | {h['占流通股比例']:.2f}% |"
                )
            lines.append("")

        # 机构/基金
        if shareholder_data.get("institutions"):
            lines.append("### 机构/基金持股")
            lines.append("")
            lines.append(
                f"共 {len(shareholder_data['institutions'])} 家机构持股，主要包括："
            )
            lines.append("")
            for h in shareholder_data["institutions"][:10]:
                lines.append(
                    f"- {h['股东名称'][:45]}: {h['持股数量']:,} 股 ({h['占流通股比例']:.2f}%)"
                )
            if len(shareholder_data["institutions"]) > 10:
                lines.append(
                    f"- ... 及其他 {len(shareholder_data['institutions']) - 10} 家"
                )
            lines.append("")

        # 股东增减持变动
        if holder_changes:
            lines.append("### 股东增减持变动（近5期）")
            lines.append("")
            lines.append("| 类型 | 股东名称 | 最新持股 | 占比% | 变动情况 |")
            lines.append("|------|----------|---------|-------|----------|")
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
                    lines.append(
                        f"| {item.get('类型', 'N/A')} | {name} | {latest.get('持股数量', 0):,} | "
                        f"{latest.get('占流通股比例', 0):.2f} | {change_info} |"
                    )
            lines.append("")

        # 抛售风险预警
        if selling_alerts:
            lines.append("### ⚠️ 抛售风险预警")
            lines.append("")
            lines.append("| 股东名称 | 类型 | 连续减持期数 | 减持比例 | 风险等级 |")
            lines.append("|----------|------|-------------|---------|---------|")
            for a in selling_alerts:
                name = a.get("股东名称", "N/A")[:30]
                risk = a.get("风险等级", "N/A")
                risk_icon = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(risk, "⚪")
                pct = a.get("减持总比例", "0")
                lines.append(
                    f"| {name} | {a.get('类型', 'N/A')} | {a.get('连续减持期数', 0)} | "
                    f"{pct} | {risk_icon} {risk} |"
                )
            lines.append("")
        else:
            lines.append("### ✅ 抛售风险")
            lines.append("")
            lines.append("未检测到连续减持行为，股东结构稳定。")
            lines.append("")

    # ========== 十、综合评分 ==========
    lines.append("## 十、综合评分")
    lines.append("")
    lines.append("| 维度 | 得分 | 满分 |")
    lines.append("|------|------|------|")
    for dim, sc in score_result["scores"].items():
        lines.append(f"| {dim} | {sc} | 20 |")
    lines.append(f"| **总分** | **{score_result['total']}** | **100** |")
    lines.append("")
    lines.append(f"**综合评级：{score_result['grade']}**")
    lines.append("")

    grade_table = {
        "A": "优秀 — 积极关注，可考虑买入",
        "B": "良好 — 基本面良好，逢低布局",
        "C": "一般 — 观望为主，等待更好时机",
        "D": "较差 — 风险较高，谨慎对待",
        "E": "危险 — 回避，风险过大",
    }
    grade_letter = score_result["grade"][0] if score_result["grade"] else "?"
    if grade_letter in grade_table:
        lines.append(f"> {grade_table[grade_letter]}")
        lines.append("")

    # ========== 十一、投资建议 ==========
    lines.append("## 十一、投资建议")
    lines.append("")
    if score_result["total"] >= 80:
        lines.append("📈 **建议：积极关注，可考虑买入**")
    elif score_result["total"] >= 65:
        lines.append("📊 **建议：基本面良好，逢低布局**")
    elif score_result["total"] >= 50:
        lines.append("⏳ **建议：观望为主，等待更好时机**")
    elif score_result["total"] >= 35:
        lines.append("⚠️ **建议：风险较高，谨慎对待**")
    else:
        lines.append("🚫 **建议：回避，风险过大**")
    lines.append("")

    risks = []
    if roce_data and roce_data[0]["roce"] < 0.05:
        risks.append(f"ROCE 仅 {roce_data[0]['roce']:.2%}，盈利能力极弱")
    if health.get("ratios") and health["ratios"][0]["current_ratio"] < 1:
        risks.append(
            f"流动比率 {health['ratios'][0]['current_ratio']:.2f}，短期偿债压力大"
        )
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
        lines.append("### 风险提示")
        lines.append("")
        for r in risks:
            lines.append(f"- ⚠️ {r}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("> **声明**：本分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。")
    lines.append("")
    lines.append("> **透明化说明**：")
    lines.append("> - 买入价格区间基于多维度交叉验证，具体计算已在上文展示")
    lines.append("> - PE/PEG/PB估值采用的行业参数为经验值，不同分析师可能有不同判断")
    lines.append("> - 建议结合自身风险承受能力和投资期限做出决策")

    return "\n".join(lines)
