---
name: financial-health
description: 分析 A 股股票财务健康指标（流动比率/速动比率/负债率/ROE/自由现金流/分红送配）
---

# Financial Health Analyzer

**功能**: 分析 A 股股票财务健康指标  
**数据源**: 东方财富 (akshare)

---

## 使用方式

**OpenCode 调用**:
```
skill(name="financial-health")
```

**命令行运行**:
```bash
python .opencode/skills/financial-health/scripts/main.py <股票代码>
```

### 示例

```bash
python .opencode/skills/financial-health/scripts/main.py 600519   # 贵州茅台
python .opencode/skills/financial-health/scripts/main.py 601318   # 中国平安
```

---

## 输出指标

| 指标 | 公式 | 参考标准 |
|------|------|---------|
| 流动比率 | 流动资产 / 流动负债 | >2 良好，>1.5 一般，<1 较差 |
| 速动比率 | (流动资产 - 存货) / 流动负债 | >1 良好，>0.8 一般 |
| 负债权益比 | 净利润 / 股东权益 | 越低越安全 |
| 净资产收益率(ROE) | 净利润 / 股东权益 | >15% 优秀，>10% 良好 |
| 利息覆盖率 | EBIT / 利息费用 | >3 安全，<1.5 危险 |
| 自由现金流 | 经营现金流 - 资本支出 | 正值表示自我造血能力 |
| 股息率 | 年度现金分红 / 股价 | >3% 高股息 |

---

## 依赖安装

```bash
pip install akshare pandas
```
