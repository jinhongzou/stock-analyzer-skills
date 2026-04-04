---
name: report-exporter
description: 将股票分析数据导出为 Markdown 格式报告文件
---

# Report Exporter

**功能**: 将综合分析数据导出为格式化的 Markdown 报告文件  
**整合模块**: 调用 comprehensive-analyzer 的所有数据源，生成可保存、可分享的 MD 文档

---

## 使用方式

**OpenCode 调用**:
```
skill(name="report-exporter")
```

**命令行运行**:
```bash
python .opencode/skills/report-exporter/scripts/main.py <股票代码> [输出路径]
```

### 示例

```bash
# 默认输出到当前目录：002714_牧原股份_分析报告.md
python .opencode/skills/report-exporter/scripts/main.py 002714

# 指定输出路径
python .opencode/skills/report-exporter/scripts/main.py 600519 ./reports/
```

---

## 输出内容

生成的 Markdown 报告包含 10 个章节：

| 章节 | 内容 |
|------|------|
| 一、基本信息 | 股票名称/现价/涨跌幅/总市值/行业 |
| 二、市场环境 | 全市场平均PE/上证指数MA20/MA50/牛熊判断 |
| 三、估值指标 | PE(动/静/TTM)/PB/股息率/每股收益 |
| 四、ROCE | 近10年资本回报率趋势 |
| 五、财务健康 | 流动比率/速动比率/资产负债率/ROE/自由现金流 |
| 六、技术分析 | MA50/MA200 金叉死叉 + RSI(14) |
| 七、新闻风险 | 诚信风险/经营风险关键词检测 |
| 八、分红历史 | 近10年每股分红/股息率/送转比例 |
| 九、综合评分 | 5维度评分（各20分）+ 综合评级（A-E） |
| 十、投资建议 | 基于评分的买卖建议 + 风险提示 |

---

## 文件命名规则

```
{股票代码}_{股票名称}_分析报告_{日期}.md
```

示例：`002714_牧原股份_分析报告_20260402.md`

---

## 依赖安装

```bash
pip install akshare pandas
```
