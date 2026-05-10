# 资金流动分析指南

**目的**: 追踪市场资金流向，识别主力资金异常行为

**数据采集命令**:
```bash
python .opencode/skills/core/src/skills/market-systemic-risk/collect_capital_flow.py
```

## 核心指标

| 指标 | 数据来源 | 预警阈值 |
|------|----------|----------|
| 北向资金 | akshare `stock_hsgt_hist_em`（东方财富） | 连续5日流出>100亿（⚠️ 数据自2024-03起未更新） |
| 融资融券(上交所) | akshare `stock_margin_sse` | 融资余额一周下降>10% |
| 融资融券(深交所) | akshare `stock_margin_szse` | 融资余额大幅下降 |
| 主力资金 | akshare `stock_market_fund_flow` | 连续10日净流出 |

## 分析流程

```
1. 获取北向资金每日流向（akshare stock_hsgt_hist_em）→ 统计连续流出天数和金额
2. 获取融资融券余额变化（akshare stock_margin_sse/szse）→ 判断杠杆资金情绪
3. 获取主力资金流向（akshare stock_market_fund_flow）→ 追踪大单行为（超大单/大单/中单/小单）
4. 注：北向资金数据自2024年3月起东方财富接口未更新，分析时需说明
```

## 预警信号

### 🟢 安全信号
- 北向资金持续净流入
- 融资余额稳定增长
- 主力资金净流入
- 超大单与主力方向一致（机构看多）

### 🟡 关注信号
- 北向资金单日流出
- 融资余额持平或微降
- 主力资金偶有流出但未持续

### 🔴 危险信号
- 北向资金连续5日流出>100亿
- 融资余额一周下降>10%
- 主力资金连续10日净流出
- 近20日主力净流出天数>15/20
- 超大单净流入但大单净流出（机构分歧/出货）

## 输出格式

```
## 资金流动分析结果

### 北向资金
- 数据状态: 正常/滞后/不可用
- 最新数据日期: XXXX-XX-XX
- 近5日净流入: XX亿元
- 趋势: 流入/流出/持平
- 风险点: [基于 hsgt_date + hsgt_north_trade + hsgt_5d + hsgt_data_note，评估: ① hsgt_north_trade是否为None(数据不可用则注明hsgt_data_note)? ② hsgt_5d中最新连续方向(连流/连入天数)? ③ 数据若滞后>3个月则不纳入分析，注明数据可用性局限]

### 杠杆资金
- 上交所融资余额: XX亿元
- 深交所融资余额: XX亿元
- 沪深合计: XX亿元
- 较上周变化: +/-X.X%
- 趋势: 增长/下降/稳定
- 风险点: [基于 margin_sse_balance + margin_sse_weekly_change + margin_sse_trend(近10日)，评估: ① margin_sse_weekly_change是否<-5%(融资余额骤降=杠杆资金恐慌)? ② margin_sse_trend近10日方向(持续下降/稳定/上升)? ③ margin_sse_balance绝对值与历史区间对比(当前在历史什么水平)? ④ 沪深合计融资余额是否出现同步下降?]

### 主力资金
- 最新日期: XXXX-XX-XX
- 今日净流入: XX亿元
- 近5日累计净流入: XX亿元
- 近20日净流出天数: XX/20
- 超大单: XX亿 / 大单: XX亿 / 中单: XX亿 / 小单: XX亿
- 趋势: 流入/流出
- 风险点: [基于 fund_main_net + fund_out_days_20d + fund_10d_trend + fund_super_large + fund_large + fund_small，评估: ① fund_out_days_20d是否>15/20(>75%天数净流出=系统性出货)? ② fund_10d_trend近5日方向(持续流出/出现转折)? ③ fund_super_large与fund_large方向是否一致(一致=机构共识，背离=分歧)? ④ fund_small与fund_main_net反向(小单买入+主力卖出=散户接盘)? ⑤ fund_main_net绝对值趋势(流出加速或减速)?]

### 综合判断
- 信号方向: positive/negative/neutral
- 预警等级: A/B/C/D/E
```
