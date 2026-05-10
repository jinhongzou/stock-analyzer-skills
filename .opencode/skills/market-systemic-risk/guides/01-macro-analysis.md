# 宏观经济分析指南

**目的**: 监测经济基本面变化，识别可能引发市场崩盘的经济下行信号

**数据采集命令**:
```bash
python .opencode/skills/core/src/skills/market-systemic-risk/collect_macro.py
```

## 核心指标

| 指标 | 数据来源（优先→替补） | 预警阈值 |
|------|----------------------|----------|
| GDP增速 | Tushare `cn_gdp` / akshare `macro_china_gdp` | 连续2季下降>0.5% |
| CPI | Tushare `cn_cpi` / akshare `macro_china_cpi` | CPI>5% |
| PPI | Tushare `cn_ppi` | PPI>10% |
| PMI | akshare `macro_china_pmi`（替补Tushare 65列编码） | <50 (荣枯线) |
| 失业率 | akshare `macro_china_urban_unemployment` | >5.5% |
| 货币供应M2 | akshare `macro_china_money_supply` | — |
| 市场PE | akshare `stock_market_pe_lg`（乐咕数据） | >历史90%分位 |

## 分析流程

```
1. 获取GDP季度数据（Tushare cn_gdp）→ 计算同比增速 → 判断趋势
2. 获取CPI月度数据（Tushare cn_cpi）→ 判断通胀压力
3. 获取PPI月度数据（Tushare cn_ppi）→ 判断工业品价格压力
4. 获取PMI月度数据（akshare macro_china_pmi）→ 判断制造业景气度
5. 获取失业率数据（akshare macro_china_urban_unemployment）→ 判断就业压力
6. 获取M2同比增速（akshare macro_china_money_supply）→ 判断货币宽松程度
7. 获取市场PE历史分位（akshare stock_market_pe_lg）→ 判断估值水平
```

## 预警信号

### 🟢 安全信号
- GDP增速稳定在5%以上
- CPI保持在2-3%区间
- PMI维持在50以上

### 🟡 关注信号
- GDP增速连续下滑
- PMI降至50-55区间

### 🔴 危险信号
- GDP增速连续2季下降>0.5%
- PMI跌破50荣枯线
- CPI>5% 通胀失控
- 企业盈利大面积下滑

## 输出格式

```
## 宏观经济分析结果

### GDP增速
- 当前值: X.X%
- 同比变化: +/-$X.X%
- 趋势: 上升/下降/稳定
- 风险点: [基于 gdp_yoy + gdp_trend(近4期)，评估: ① 近4期gdp_yoy趋势是否连续下滑(连续下滑>2次)? ② 当前gdp_yoy是否<5.0%(政府目标线)? ③ 下滑加速度(相邻两期差值是否扩大)? ④ 与2020年疫情底(3.4%)及2015年股灾前(7%)对比量级?]

### 通胀水平
- CPI: X.X%
- PPI: X.X%
- 评估: 低通胀/温和通胀/通胀失控
- 风险点: [基于 cpi_yoy + ppi_yoy + cpi_mom，评估: ① cpi_yoy是否>3%(通胀红线)或<0%(通缩)? ② cpi_mom环比是否出现加速(环比>0.5%或连续正值)? ③ ppi_yoy是否>10%(成本推动)或负值(工业通缩)? ④ CPI-PPI剪刀差是否扩大(企业利润挤压)?]

### 制造业景气度
- PMI: XX
- 评估: 扩张/收缩
- 风险点: [基于 pmi_manufacturing + pmi_non_manufacturing + pmi_trend(近3期)，评估: ① pmi_manufacturing是否连续<50(进入收缩期)? ② pmi_trend近3期方向(持续下降/波动/回升)? ③ pmi_non_manufacturing是否同步下滑(服务业信心走弱)? ④ PMI与gdp_yoy趋势是否一致(交叉验证)?]

### 就业与货币
- 失业率: X.X%
- M2同比: X.X%
- M1同比: X.X%
- 风险点: [基于 unemployment_value + m2_yoy + m1_yoy，评估: ① unemployment_value是否>5.5%(就业压力线)? ② m2_yoy是否持续下降(流动性收紧)或异常激增(放水过度)? ③ m1_yoy与m2_yoy剪刀差(M1-M2负值扩大=企业活期资金减少=投资意愿弱)?]

### 综合判断
- 信号方向: positive/negative/neutral
- 预警等级: A/B/C/D/E
```
