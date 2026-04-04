---
name: shareholder-analyzer
description: 分析 A 股个股十大流通股东、国家队持股、机构持股、高管持股、股东增减持变动及抛售风险
---

# Shareholder Analyzer

**功能**: 分析个股股东结构及变动情况  
**数据源**: 新浪财经 (akshare)

---

## 使用方式

**OpenCode 调用**:
```
skill(name="shareholder-analyzer")
```

**命令行运行**:
```bash
python .opencode/skills/shareholder-analyzer/scripts/main.py <股票代码>
```

### 示例

```bash
python .opencode/skills/shareholder-analyzer/scripts/main.py 600519   # 贵州茅台
python .opencode/skills/shareholder-analyzer/scripts/main.py 002714   # 牧原股份
```

---

## 输出内容

| 模块 | 内容 |
|------|------|
| 最新十大流通股东 | 排名/股东名称/持股数量/占流通股比/股本性质/类型 |
| 股东类型分布 | 国家队/机构/国有/陆股通/自然人 |
| 国家队持股明细 | 社保基金/汇金/证金/国家基金等 |
| 机构持股明细 | 基金/保险/信托/QFII 等 |
| 股东增减持变动 | 近 5 期持股变化（增持/减持/不变） |
| 抛售风险预警 | 连续减持检测 + 风险等级评估 |

---

## 股东类型识别

| 类型 | 识别关键词 |
|------|-----------|
| 国家队 | 中央汇金、中国证券金融、全国社保基金、基本养老保险基金、国家大基金等 |
| 机构/基金 | 证券投资基金、基金管理、保险、信托、QFII 等 |
| 高管 | 董事、监事、总经理、财务总监等 |
| 国有股 | 国有资本、国资等 |
| 陆股通 | 香港中央结算 |

---

## 依赖安装

```bash
pip install akshare pandas
```
