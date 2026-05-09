---
name: risk-analysis
description: 综合风控分析。整合新闻风险评估 + 历史分位数分析，评估新闻风险等级（高/中/低），输出估值分位信号和操作建议
---

# Risk Analysis - 风险分析技能手册
**功能**: 新闻风险评估 + 历史分位数分析
**数据源**: Tushare Pro + akshare
**合并**: news-risk-analyzer + percentile-analyzer

---

## 使用方式

**命令行运行**（数据获取使用 `news-risk-analyzer` + `valuation-anchor`）：
```bash
python .opencode/skills/core/src/skills/news-risk-analyzer/main.py <股票代码>
python .opencode/skills/core/src/skills/valuation-anchor/main.py <股票代码>
```

### 示例

```bash
python .opencode/skills/core/src/skills/news-risk-analyzer/main.py 000651   # 格力电器新闻风险
python .opencode/skills/core/src/skills/valuation-anchor/main.py 000651    # 格力电器估值分位数
```

---

## 输出维度

### Step 1: 新闻风险评估
- 高/中/低风险新闻统计
- 诚信风险关键词检测
### Step 2: 历史分位数
- 近1年/3年/5年分位数
- 社保基金买入分位数（可选）

---

## 推理过程（必须展示）

1. **数据获取** → 调用Tushare/AKShare接口
2. **计算推理** → 计算风险等级/分位数
3. **判断** → 与阈值对比
4. **结论** → 汇总表：维度/评估结果/信号

---

## AI评估要求（必须在报告中体现）

当使用本技能生成分析报告时，AI必须自己对返回的数据进行以下评估：
### 1. 新闻风险评估
- **输入数据**: 高/中/低风险新闻数量
- **评估标准**:
  - 高风险 > 0: 高风险 → 利空
  - 中风险 > 0: 中风险 → 中性
  - 全部低风险/无风险 → 利好
- **输出**: 对应信号 + 诚信风险检测
### 2. 价格分位数评估
- **输入数据**: 当前价格的历史分位数
- **评估标准**:
  - < 30%: 严重低估 → 利好（强烈买入）
  - 30-50%: 偏低估 → 利好（买入）
  - 50-70%: 合理 → 中性（观望）
  - 70-90%: 偏高估 → 利空（减仓）
  - > 90%: 严重高估 → 利空（卖出）
- **输出**: 对应信号 + 操作建议

### 3. 综合评分
- 计算2个维度的平均分
- 生成A-E评级
- 给出投资建议

---

## 返回数据格式

```json
{
  "news": {"total": 10, "high": 0, "medium": 0, "low": 10, "integrity": 0},
  "percentile": {"current": 39.89, "percentile": 94.4, "signal": "negative", "advice": "减仓/止损"},
  "summary": [
    {"dimension": "新闻风险", "result": "高/中/低:0", "signal": "利好"},
    {"dimension": "分位数", "result": "94.4%", "signal": "利空"}
  ]
}
```

**注意**: 本技能只返回原始数据，不包含AI评估。AI在生成报告时必须自己对数据进行分析评估。
