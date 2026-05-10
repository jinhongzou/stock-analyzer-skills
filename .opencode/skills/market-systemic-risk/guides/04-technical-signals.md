# 技术面信号分析指南

**目的**: 通过技术分析识别市场阶段性顶部的经典信号

**数据采集命令**:
```bash
python .opencode/skills/core/src/skills/market-systemic-risk/collect_technical.py
```

## 核心指标

| 指标 | 数据来源 | 预警阈值 |
|------|----------|----------|
| RSI(14) | akshare `stock_zh_index_daily` → 自算 | >70 超买（>80 极度超买） |
| RSI(6) | akshare `stock_zh_index_daily` → 自算 | >90 极值超买 |
| 均线系统 | akshare `stock_zh_index_daily` → 自算MA | MA50<MA200 死叉 |
| 成交量 | akshare `stock_zh_index_daily` | 量比>2 或 天量滞涨 |
| 量价关系 | akshare `stock_zh_index_daily` | 价创新高量萎缩 |
| K线形态 | akshare `stock_zh_index_daily` | 连续3阴/覆盖线/缺口 |

## 分析流程

```
1. 获取上证指数日线（akshare stock_zh_index_daily）→ 计算涨跌幅/量比
2. 计算MA5/MA10/MA20/MA50/MA100/MA200 → 判断均线排列和交叉信号
3. 计算RSI(6)和RSI(14) → 判断超买超卖
4. 分析近期K线（阳阴比/连续阴线/区间位置）→ 识别反转风险
5. 成交量分析（历史天量对比/量比/量价关系）→ 判断天量滞涨/放量下跌
```

## 预警信号

### 🟢 安全信号
- 上涨时放量、下跌时缩量
- MA50>MA200 金叉，多头排列
- RSI(14)在30-70区间
- 阳线明显多于阴线

### 🟡 关注信号
- RSI(14)>70 超买
- 量价轻微背离（指数新高量未跟进）
- 价格在20日区间>90%位置

### 🔴 危险信号
- RSI(6)>90 极度超买
- RSI(14)>80 严重超买
- 高位天量滞涨（量创历史新高但价不涨）
- 放量下跌趋势确认
- MA50下穿MA200 死叉
- 连续3根以上大阴线
- 跌破重要支撑缺口
- 20日区间顶部放量滞涨

## 输出格式

```
## 技术信号分析结果

### 均线系统
- MA20: XX / MA50: XX / MA200: XX
- 排列: 多头排列/空头排列
- MA50/MA200: 金叉/死叉
- 风险点: [基于 ma20/ma50/ma200 + ma20_ma50_cross + ma50_ma200_cross + ma_cross_signal，评估: ① ma50_ma200是金叉还是死叉(死叉=技术面转熊最强烈信号)? ② ma_cross_signal是否为"刚形成死叉"(趋势刚刚逆转最危险)? ③ 排列是否多头(MA5>MA10>MA20>MA50>MA200)? ④ 短期均线(MA5)与长期(MA200)乖离是否过大(乖离>15%=超买回调风险)? ⑤ MA20/MA50趋势方向(走平=趋势减弱)?]

### RSI指标
- RSI(6): XX（超卖/中性/超买/极值）
- RSI(14): XX（超卖/中性/超买）
- 风险点: [基于 rsi_6 + rsi_14，评估: ① rsi_6是否>90(极度超买=短期回调概率极高)? ② rsi_14是否>80(严重超买=中期顶部信号)? ③ rsi_6/14趋势(从高位回落=顶背离雏形，继续上升=超买加剧)? ④ 历史相似rsi水平后的市场走势参考?]

### 成交量信号
- 当前量能: XX亿元
- 量比(60日): X.X
- 历史天量: XX亿元 (日期: XXXX-XX-XX)
- 评估: 正常/天量滞涨/放量下跌
- 风险点: [基于 volume_current + volume_ratio + volume_hist_max + volume_current_vs_max_pct + change_1d/5d，评估: ① volume_ratio是否>2(异常放量)或<0.5(异常缩量)? ② volume_current_vs_max_pct是否接近100%同时change_1d<0(天量滞涨=最危险信号)? ③ 下跌日成交额是否大于上涨日成交额(down_volume_20d vs up_volume_20d)? ④ 近期量能趋势(持续放大/缩小)?]

### K线形态
- 近20日阳线/阴线: XX/XX
- 最大连续阴线: X天
- 当前在20日区间位置: XX%
- 近期形态: XXX
- 风险点: [基于 up_days_20d + down_days_20d + max_consecutive_down_20d + position_20d_pct + recent_30d，评估: ① position_20d_pct是否>95%(在区间顶部=短期回调压力)? ② max_consecutive_down_20d是否>3(连续阴线=空头主导)? ③ up_days_20d/down_days_20d比例是否恶化(近期阴线增多)? ④ recent_30d最新几日是否出现长上影/十字星(顶部反转信号)? ⑤ 是否出现跳空缺口(突破/衰竭)?]

### 综合判断
- 信号方向: positive/negative/neutral
- 预警等级: A/B/C/D/E
```
