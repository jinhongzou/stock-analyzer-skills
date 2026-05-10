# 市场结构分析指南

**目的**: 分析市场结构特征，识别估值泡沫和产业资本行为异常

**数据采集命令**:
```bash
python .opencode/skills/core/src/skills/market-systemic-risk/collect_structure.py
```

## 核心指标

| 指标 | 数据来源（优先→替补） | 预警阈值 |
|------|----------------------|----------|
| 产业资本减持 | akshare `stock_shareholder_change_ths` | 月净减持>1000亿 |
| 市场估值(PE) | akshare `stock_market_pe_lg`（乐咕） | >历史90%分位 |
| 市场估值(PB) | akshare `stock_market_pb_lg`（乐咕） | >历史90%分位 |
| 板块集中度 | akshare `stock_sector_spot` | 前3大板块>50% |
| 新股破发率 | Tushare `new_share` | 破发率>30% 或 首日涨幅>200%(过热) |

## 分析流程

```
1. 获取PB历史数据（akshare stock_market_pb_lg）→ 计算分位 → 判断估值泡沫
2. 获取行业板块成交分布（akshare stock_sector_spot）→ 计算板块集中度
3. 获取股东增减持数据（akshare stock_shareholder_change_ths）→ 统计变动
4. 获取新股上市数据（Tushare new_share）→ 计算破发率 + 首日涨幅均值
5. 注：PE历史数据见 01-macro-analysis.md
```

## 预警信号

### 🟢 安全信号
- 产业资本净增持或小幅减持
- PE/PB处于历史30-70%分位
- 板块分布均衡

### 🟡 关注信号
- 月净减持500-1000亿
- PE/PB超过历史80%分位

### 🔴 危险信号
- 月净减持>1000亿
- PE/PB>历史90%分位
- 前3大板块占比>50%
- 新股破发率>30%（市场极度悲观）
- 新股首日平均涨幅>200%（市场过度狂热，也是危险信号）


## 输出格式

```
## 市场结构分析结果

### 产业资本行为
- 近X年变动次数: XX次
- 最近变动: [日期] [股东] [方向] [股数]
- 趋势: 增持/减持/持平
- 风险点: [基于 shareholder_changes(列出近X年股东增减持记录)，评估: ① shareholder_change_count变动频率是否异常(频率突然增加)? ② 大股东(持股>5%)控股股东是否有减持记录(最危险信号)? ③ 增减持方向是否一致(多个股东同时减持=系统性风险)? ④ 近期是否有回购或管理层增持(正面信号)?]

### 估值水平
- PE当前分位(1年/3年/5年): XX% / XX% / XX%
- PB当前分位(1年/3年/5年): XX% / XX% / XX%
- 评估: 低估/合理/高估/严重泡沫
- 风险点: [基于 pe_percentile_1y/3y/5y + pb_current + pb_percentile_1y/3y/5y，评估: ① PE分位是否出现1年>90%且5年>90%(长短周期共振=极端高位)? ② PE与PB分位是否同步(背离时需警惕)? ③ pb_weighted vs pb_median差异是否过大(权重股拉高整体估值)? ④ pb_current vs pb_min/pb_max在区间中的相对位置?]

### 板块分布
- 前3板块占比: XX%
- 前5板块: [名称/成交额/涨跌幅]
- 风险点: [基于 sector_top3_ratio + sector_top5(前5板块明细)，评估: ① sector_top3_ratio是否>50%(资金过度集中在少数板块)? ② 前5板块中涨幅最高的是否已出现放量滞涨(如成交量放大但涨幅<0.5%)? ③ 是否有防御板块(公用事业/医药/消费)进入前5(资金避险信号)? ④ 板块涨跌幅是否分化明显(部分大涨/部分大跌=结构性风险)?]

### 新股情绪
- 统计周期: XXXX-XX-XX ~ XXXX-XX-XX
- 新股总数: XX只
- 破发率: XX%
- 平均首日涨幅: XX%
- 评估: 悲观/正常/过热
- 风险点: [基于 new_share_break_rate + new_share_avg_first_day_pct + new_share_total，评估: ① new_share_break_rate是否>30%(破发率高=市场极度悲观)? ② new_share_avg_first_day_pct是否>200%(首日涨幅过高=投机过热)? ③ 两者同时极低或极高说明市场情绪极端，通常对应顶部或底部? ④ 新股数量new_share_total变化是否异常(IPO骤减/暂停可能是政策干预信号)?]

### 综合判断
- 信号方向: positive/negative/neutral
- 预警等级: A/B/C/D/E
```
