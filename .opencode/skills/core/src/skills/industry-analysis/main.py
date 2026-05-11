# -*- coding: utf-8 -*-
"""
行业分析 - 行业板块数据采集与分析入口

用法:
    python main.py                  # 全市场行业分析（多维度排行）
    python main.py <行业名>         # 单个行业深度分析
    示例:
    python main.py 半导体
    python main.py 白酒
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from core import IndustryAnalyzer


def _fmt(n) -> str:
    if n is None:
        return "N/A"
    if isinstance(n, (int, float)):
        if abs(n) >= 1e8:
            return f"{n/1e8:.2f}亿"
        if abs(n) >= 1e4:
            return f"{n/1e4:.2f}万"
    return str(n)


def _dim_status(data: dict) -> tuple:
    """返回 (status_str, key_finding) 用于汇总表"""
    if data.get("error"):
        return "[异常]", data["error"]
    if data.get("note"):
        return "[不可用]", data["note"]
    return "[已获取]", ""


def output_single_industry(results: dict, industry_name: str):
    """输出单个行业深度分析报告（参照市场系统性风险报告格式）"""
    from datetime import date

    spot = results.get("spot", {})
    cons = results.get("constituents", {})
    fundflow = results.get("fundflow", {})
    valuation = results.get("valuation", {})

    # 汇总表关键发现
    spot_finding = ""
    if not spot.get("error") and not spot.get("note"):
        spot_finding = f"{spot.get('change_pct', '')}% 排名{spot.get('rank', '')}/{spot.get('total_industries', '')}"

    cons_finding = ""
    if not cons.get("error") and not cons.get("note"):
        cons_finding = f"{cons.get('stock_count', '')}只成分股 均价{cons.get('avg_change', '')}%"

    fundflow_finding = ""
    if not fundflow.get("error") and not fundflow.get("note"):
        fundflow_finding = f"主力净流入{fundflow.get('main_net_inflow', '')}亿元"

    val_finding = ""
    if not valuation.get("error") and not valuation.get("note"):
        val_finding = f"PE={valuation.get('pe', '')} PB={valuation.get('pb', '')}"

    display_name = spot.get("name", industry_name)

    # ══════════════════════════════════════════════════════════════════
    #  报告标题
    # ══════════════════════════════════════════════════════════════════
    print("=" * 66)
    print(f"             行业深度分析报告 —— {display_name}")
    print("=" * 66)
    print()
    print(f"  【分析日期】: {date.today()}")
    print(f"  【数据来源】: collect_single_industry.py / IndustryAnalyzer")
    print()

    # ══════════════════════════════════════════════════════════════════
    #  一、各维度数据汇总
    # ══════════════════════════════════════════════════════════════════
    print("-" * 66)
    print("  一、各维度数据汇总")
    print("-" * 66)
    print(f"  {'维度':<16} {'状态':<14} {'关键发现'}")
    print("  " + "-" * 60)
    s1, f1 = _dim_status(spot)
    s2, f2 = _dim_status(cons)
    s3, f3 = _dim_status(fundflow)
    s4, f4 = _dim_status(valuation)
    print(f"  {'实时行情':<16} {s1:<14} {f1 or spot_finding}")
    print(f"  {'成分股明细':<16} {s2:<14} {f2 or cons_finding}")
    print(f"  {'资金流向':<16} {s3:<14} {f3 or fundflow_finding}")
    print(f"  {'估值数据':<16} {s4:<14} {f4 or val_finding}")
    print()

    # ══════════════════════════════════════════════════════════════════
    #  二、逐维度分析
    # ══════════════════════════════════════════════════════════════════
    print("-" * 66)
    print("  二、逐维度分析")
    print("-" * 66)
    print()

    # ── 1. 实时行情 ──
    print("  ### 1. 实时行情分析")
    print()
    if spot.get("error") or spot.get("note"):
        status_msg = spot.get("error") or spot.get("note")
        print(f"  【数据状态】[!] {status_msg}")
        print()
    else:
        print("  【数据展示】")
        print(f"    行业名称:   {spot.get('name', industry_name)}")
        print(f"    涨跌幅:     {spot.get('change_pct', 'N/A')}%")
        print(f"    成交额:     {_fmt(spot.get('volume'))}")
        leader_name = spot.get('leader_name', '')
        leader_change = spot.get('leader_change')
        if leader_name:
            lc_str = f"({leader_change}%)" if leader_change is not None else ""
            print(f"    领涨股:     {leader_name} {lc_str}")
        else:
            print(f"    领涨股:     （Tushare 无此字段）")
        stock_count = spot.get('stock_count')
        print(f"    成分股数:   {stock_count if stock_count is not None else '（Tushare 无此字段）'} 只")
        print(f"    涨幅排名:   {spot.get('rank', 'N/A')}/{spot.get('total_industries', 'N/A')}")
        vs_avg = spot.get('vs_avg')
        if vs_avg is not None:
            direction = "跑赢" if vs_avg > 0 else "跑输"
            print(f"    相对表现:   {direction}全行业均值 {abs(vs_avg)}%")
        print()
        # 简评要点
        print("  【评估要点】")
        rank = spot.get('rank', 0)
        total = spot.get('total_industries', 1)
        pct = rank / total if total else 1
        if pct <= 0.2:
            print(f"    ① 排名前20%（{rank}/{total}），处于市场领先位置")
        elif pct <= 0.5:
            print(f"    ① 排名中上（{rank}/{total}），表现高于平均水平")
        else:
            print(f"    ① 排名靠后（{rank}/{total}），表现弱于大多数行业")
        leader_change = spot.get('leader_change')
        if leader_change is not None and abs(leader_change) >= 9.5:
            print(f"    ② 领涨股涨停/接近涨停（{leader_change}%），板块情绪极强")
        elif leader_change is not None and leader_change >= 5:
            print(f"    ② 领涨股大涨（{leader_change}%），龙头带动效应明显")
        print()

    # ── 2. 成分股明细 ──
    print("  ### 2. 成分股明细分析")
    print()
    if cons.get("error") or cons.get("note"):
        status_msg = cons.get("error") or cons.get("note")
        print(f"  【数据状态】[!] {status_msg}")
        print()
    else:
        print("  【数据展示】")
        print(f"    成分股总数: {cons.get('stock_count', 'N/A')} 只")
        print(f"    平均涨幅:   {cons.get('avg_change', 'N/A')}%")
        print(f"    上涨/下跌:  {cons.get('up_count', 0)} / {cons.get('down_count', 0)}")
        print()
        print(f"  【涨幅前十】")
        for i, s in enumerate(cons.get('top10_gainers', []), 1):
            print(f"    {i:>2}. {s['name']}({s['code']}): {s['change_pct']:>6.2f}%  现价={s['price']}")
        print()
        losers = cons.get('top10_losers', [])
        if losers:
            print(f"  【跌幅前十】")
            for i, s in enumerate(losers, 1):
                print(f"    {i:>2}. {s['name']}({s['code']}): {s['change_pct']:>6.2f}%  现价={s['price']}")
            print()
        top5_vol = cons.get('top5_volume', [])
        if top5_vol:
            print(f"  【成交额前五】")
            for i, s in enumerate(top5_vol, 1):
                print(f"    {i:>2}. {s['name']}({s['code']}): {_fmt(s['volume']):>8}  {s['change_pct']:>6.2f}%")
            print()
        # 简评
        print("  【评估要点】")
        up = cons.get('up_count', 0)
        total_c = cons.get('stock_count', 1)
        up_ratio = up / total_c if total_c else 0
        if up_ratio >= 0.7:
            print(f"    ① 板块内普涨（{up}/{total_c}），市场情绪一致看多")
        elif up_ratio >= 0.5:
            print(f"    ① 涨多跌少（{up}/{total_c}），板块整体偏强")
        elif up_ratio >= 0.3:
            print(f"    ① 涨跌互现（{up}/{total_c}），板块内部分化明显")
        else:
            print(f"    ① 跌多涨少（{up}/{total_c}），板块整体承压")
        avg_c = cons.get('avg_change')
        if avg_c is not None:
            leader_c = cons.get('top10_gainers', [{}])[0].get('change_pct', 0) if cons.get('top10_gainers') else 0
            if leader_c - avg_c > 8:
                print(f"    ② 龙头溢价显著（领涨{leader_c}% vs 均值{avg_c}%），行情由少数个股驱动")
        print()

    # ── 3. 资金流向 ──
    print("  ### 3. 资金流向分析")
    print()
    if fundflow.get("error") or fundflow.get("note"):
        status_msg = fundflow.get("error") or fundflow.get("note")
        print(f"  【数据状态】[!] {status_msg}")
        print()
    else:
        print("  【数据展示】")
        print(f"    主力净流入: {fundflow.get('main_net_inflow', 'N/A')} 亿元")
        print(f"    同期涨跌幅: {fundflow.get('change_pct', 'N/A')}%")
        print()
        print("  【评估要点】")
        net = fundflow.get('main_net_inflow')
        if net is not None:
            if net > 0:
                print(f"    ① 主力资金净流入 {net} 亿元，资金面支持上涨")
            else:
                print(f"    ① 主力资金净流出 {abs(net)} 亿元，资金面承压")
        print()

    # ── 4. 估值数据 ──
    print("  ### 4. 估值数据分析")
    print()
    if valuation.get("error") or valuation.get("note"):
        status_msg = valuation.get("error") or valuation.get("note")
        print(f"  【数据状态】[!] {status_msg}")
        print()
    else:
        print("  【数据展示】")
        print(f"    PE:         {valuation.get('pe', 'N/A')}")
        print(f"    PE 中位数:  {valuation.get('pe_median', 'N/A')}")
        print(f"    PB:         {valuation.get('pb', 'N/A')}")
        print(f"    PB 中位数:  {valuation.get('pb_median', 'N/A')}")
        pe_rank = valuation.get('pe_rank')
        pe_total = valuation.get('pe_rank_total')
        if pe_rank is not None and pe_total:
            print(f"    PE 排名:    {pe_rank}/{pe_total}（从高到低）")
        print()
        print("  【评估要点】")
        pe = valuation.get('pe')
        pe_med = valuation.get('pe_median')
        if pe is not None and pe_med is not None:
            if pe > pe_med * 1.5:
                print(f"    ① PE（{pe}）远高于中位数（{pe_med}），龙头股拉高板块估值")
            elif pe > pe_med:
                print(f"    ① PE（{pe}）高于中位数（{pe_med}），估值分布偏右")
            else:
                print(f"    ① PE（{pe}）低于中位数（{pe_med}），估值分布偏左")
        if pe_rank is not None and pe_total:
            pe_pct = pe_rank / pe_total
            if pe_pct <= 0.2:
                print(f"    ② PE 排名前20%（{pe_rank}/{pe_total}），属于高估值行业")
            elif pe_pct >= 0.8:
                print(f"    ② PE 排名后20%（{pe_rank}/{pe_total}），属于低估值行业")
            else:
                print(f"    ② PE 排名居中（{pe_rank}/{pe_total}），估值处于市场中游")
        print()

    # ══════════════════════════════════════════════════════════════════
    #  三、综合评估
    # ══════════════════════════════════════════════════════════════════
    print("-" * 66)
    print("  三、综合评估")
    print("-" * 66)
    print()

    # 统计可用维度
    dims = []
    if not spot.get("error") and not spot.get("note"):
        score_p = "价格上涨" if spot.get("change_pct", 0) > 0 else "价格下跌"
        dims.append(f"实时行情({score_p})")
    if not cons.get("error") and not cons.get("note"):
        dims.append("成分股明细")
    if not fundflow.get("error") and not fundflow.get("note"):
        dir_f = "资金流入" if fundflow.get("main_net_inflow", 0) > 0 else "资金流出"
        dims.append(f"资金流向({dir_f})")
    if not valuation.get("error") and not valuation.get("note"):
        dims.append("估值数据")

    unavailable = 4 - len(dims)

    print(f"  【可用维度】{len(dims)}/4 个维度可用（{unavailable} 个暂不可用）")
    if dims:
        print(f"  {', '.join('[OK]' + d for d in dims)}")
    print()
    print(f"  【数据交叉验证】")
    if not spot.get("error") and not spot.get("note") and not fundflow.get("error") and not fundflow.get("note"):
        chg = spot.get("change_pct", 0)
        net = fundflow.get("main_net_inflow", 0)
        if chg > 0 and net > 0:
            print(f"    [OK] 价格↑ + 资金流入 → 健康上涨，趋势可持续")
        elif chg > 0 and net < 0:
            print(f"    [!] 价格↑ + 资金流出 → 资金背离，警惕诱多")
        elif chg < 0 and net < 0:
            print(f"    [!] 价格↓ + 资金流出 → 资金流出确认下跌")
        elif chg < 0 and net > 0:
            print(f"    [?] 价格↓ + 资金流入 → 资金逆势布局，关注反转信号")
    else:
        print(f"    [!] 资金流数据暂不可用，无法进行量价交叉验证")
    print()

    print(f"  【参考指南】guides/05-single-industry-deep-dive.md")
    print()
    print("=" * 66)
    print("                  免责声明")
    print("=" * 66)
    print("  本分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。")
    print()


def output_market_overview(results: dict):
    """输出全市场行业多维度概览"""
    print("=" * 60)
    print("行业分析 - 多维度数据采集")
    print("=" * 60)

    spot = results.get("spot", {}).get("details", {})
    print(f"\n[行业排行]")
    print(f"  行业总数: {spot.get('total_sectors', 'N/A')}")
    print(f"  总成交额: {spot.get('total_volume', 'N/A')}")
    print(f"  上涨/下跌: {spot.get('up_count', 0)}/{spot.get('down_count', 0)}")
    print(f"  前3大板块成交占比: {spot.get('top3_volume_ratio', 'N/A')}%")

    for s in spot.get('gainers_top10', [])[:3]:
        leader_name = s.get('leader_name', '')
        leader_change = s.get('leader_change')
        if leader_name:
            lc_str = f"({leader_change}%)" if leader_change is not None else ""
            print(f"    {s['name']}: {s['change_pct']}% 领涨={leader_name}{lc_str}")
        else:
            print(f"    {s['name']}: {s['change_pct']}%")

    losers = spot.get('losers_top10', [])
    if losers:
        print(f"  跌幅前3:")
        for s in losers[:3]:
            print(f"    {s['name']}: {s['change_pct']}%")

    # ── 行业资金流 ──
    fundflow = results.get("fundflow", {})
    fundflow_note = fundflow.get("note") or fundflow.get("details", {}).get("note", "")
    print(f"\n[行业资金流]")
    if fundflow_note:
        print(f"  [{fundflow_note}]")
    else:
        fd = fundflow.get("details", {})
        print(f"  主力净流入/流出行业数: {fd.get('inflow_sectors_count', 0)}/{fd.get('outflow_sectors_count', 0)}")
        print(f"  全市场主力净流入合计: {fd.get('total_main_net_inflow', 'N/A')}亿元")
        inflow = fd.get('inflow_top10', [])
        if inflow:
            print(f"  资金流入前3:")
            for s in inflow[:3]:
                print(f"    {s['name']}: {s['main_net_inflow']}亿元 {s['change_pct']}%")
        outflow = fd.get('outflow_top10', [])
        if outflow:
            print(f"  资金流出前3:")
            for s in outflow[:3]:
                print(f"    {s['name']}: {s['main_net_inflow']}亿元 {s['change_pct']}%")

    # ── 行业估值 ──
    valuation = results.get("valuation", {})
    print(f"\n[行业估值]")
    if valuation.get("note"):
        print(f"  [{valuation['note']}]")
    elif valuation.get("error"):
        print(f"  [{valuation['error']}]")
    else:
        print(f"  有估值数据行业数: {valuation.get('sectors', 0)}")
        vd = valuation.get("details", {})
        pe_high = vd.get('pe_highest_top5', [])
        if pe_high:
            print(f"  PE最高 Top 3:")
            for s in pe_high[:3]:
                print(f"    {s['industry']}: PE={s['pe']} PB={s['pb']}")
        pe_low = vd.get('pe_lowest_top5', [])
        if pe_low:
            print(f"  PE最低 Top 3:")
            for s in pe_low[:3]:
                print(f"    {s['industry']}: PE={s['pe']} PB={s['pb']}")

    # ── 行业成分股 ──
    detail = results.get("detail", {}).get("details", {})
    print(f"\n[热门行业成分股]")
    if detail.get('sectors'):
        for s in detail['sectors']:
            print(f"  {s['name']}（{s['reason']}）:")
            for stk in s.get('top5_stocks', [])[:3]:
                print(f"    {stk['name']}({stk['code']}): {stk['change_pct']}%")
    else:
        print(f"  东方财富成分股接口暂不可用，稍后重试即可")

    print(f"\n{'=' * 60}")
    print("数据采集完成，请基于以上数据进行分析判断")
    print("=" * 60)


def main():
    analyzer = IndustryAnalyzer()

    # 带行业名参数 → 单个行业深度分析
    if len(sys.argv) >= 2:
        industry_name = sys.argv[1]
        results = analyzer.analyze_single_industry(industry_name)
        output_single_industry(results, industry_name)
        return

    # 无参数 → 全市场行业多维度分析
    results = analyzer.analyze_all()
    output_market_overview(results)


if __name__ == "__main__":
    main()
