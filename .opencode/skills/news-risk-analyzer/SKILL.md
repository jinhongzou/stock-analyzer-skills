---
name: news-risk-analyzer
description: 个股新闻风险评估。获取A股个股新闻，AI逐条评估风险等级（高/中/低），检测诚信风险关键词（财务造假/监管处罚等50+关键词）
---

# News Risk Analyzer

**功能**: 获取 A 股个股新闻，AI 逐条进行风险评估  
**数据源**: 东方财富 (akshare)

---

## 使用方式

**OpenCode 调用**:
```
skill(name="news-risk-analyzer")
```

**命令行运行**:
```bash
python .opencode/skills/core/src/skills/news-risk-analyzer/main.py <股票代码> [新闻数量]
```

### 示例

```bash
python .opencode/skills/core/src/skills/news-risk-analyzer/main.py 600519        # 贵州茅台，默认20条
python .opencode/skills/core/src/skills/news-risk-analyzer/main.py 600338 10     # 西藏珠峰，10条
python .opencode/skills/core/src/skills/news-risk-analyzer/main.py 002594 30     # 比亚迪，30条
```

---

## 风险评级

| 等级 | 说明 |
|------|------|
| 🔴 高风险 | 可能严重影响股价（如财务造假、重大诉讼、监管处罚、核心高管变动） |
| 🟡 中风险 | 可能影响股价（如业绩下滑、行业政策变化、股东减持、竞争加剧） |
| 🟢 低风险 | 影响较小（如日常经营、常规公告、正面新闻） |

---

## 依赖安装

```bash
pip install akshare pandas
```

---

## 输出示例

```
===========================================================================
股票: 600338 (西藏珠峰)
获取时间: 2026-03-31 17:30:00
新闻数量: 20条
===========================================================================

[1/20] 标题: 西藏珠峰2024年净利润下滑82%
     日期: 2025-03-15
     来源: 东方财富
     风险等级: 🔴 高风险
     风险摘要: 净利润大幅下滑，反映主营业务盈利能力急剧恶化

[2/20] 标题: 西藏珠峰完成矿山安全生产检查
     日期: 2025-03-10
     来源: 新浪财经
     风险等级: 🟢 低风险
     风险摘要: 常规安全检查，属正常经营行为
```
