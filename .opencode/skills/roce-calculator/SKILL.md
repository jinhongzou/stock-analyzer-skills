---
name: roce-calculator
description: 计算 A 股股票的 ROCE（资本回报率）近10年趋势
---

# ROCE Calculator

**功能**: 计算 A 股股票的 ROCE（资本回报率）  
**数据源**: 新浪财经 (akshare)

---

## 核心公式

```
ROCE = EBIT / 投入资本
投入资本 = 总资产 - 流动负债
EBIT = 净利润 + 利息费用 + 所得税
```

---

## 使用方式

**OpenCode 调用**:
```
skill(name="roce-calculator")
```

**命令行运行**:
```bash
python .opencode/skills/roce-calculator/scripts/main.py <股票代码>
```

### 示例

```bash
python .opencode/skills/roce-calculator/scripts/main.py 600519   # 贵州茅台
python .opencode/skills/roce-calculator/scripts/main.py 600338   # 西藏珠峰
python .opencode/skills/roce-calculator/scripts/main.py 002594   # 比亚迪
```

---

## 输出字段

| 字段 | 说明 |
|------|------|
| ROCE | 资本回报率 |
| 净利润 | 归属母公司净利润 |
| EBIT | 息税前利润 |
| 投入资本 | 总资产 - 流动负债 |

---

## 依赖安装

```bash
pip install akshare pandas
```

---

## ROCE 参考标准

| 范围 | 评价 |
|------|------|
| > 20% | 优秀 |
| 15% - 20% | 良好 |
| 10% - 15% | 一般 |
| < 10% | 较差 |

---

## 常见股票代码

| 股票 | 代码 | 交易所 |
|------|------|--------|
| 贵州茅台 | 600519 | 上交所 |
| 西藏珠峰 | 600338 | 上交所 |
| 中国平安 | 601318 | 上交所 |
| 比亚迪 | 002594 | 深交所 |
| 宁德时代 | 300750 | 深交所 |
