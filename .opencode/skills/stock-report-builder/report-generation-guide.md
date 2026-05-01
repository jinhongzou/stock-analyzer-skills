# 股票投资分析报告生成步骤

## 执行流程

### 步骤1：确定分析目标
- 股票代码：`{{股票代码}}`
- 股票名称：`{{股票名称}}`
- 分析日期：`{{日期}}`
- **Skill**: 无

---

### 步骤2：获取基础数据（并行执行）

| 数据项 | 来源 | Skill |
|--------|------|-------|
| 基本信息/行情/估值 | 雪球 | `stock-analyzer` |
| 财务指标 | 新浪财经 | `financial-health` |
| 技术指标 | 新浪财经 | `technical-analyzer` |
| 新闻风险 | 东方财富 | `news-risk-analyzer` |
| 股东持股 | 东方财富 | `shareholder-analyzer` |
| ROCE趋势 | 新浪财经 | `roce-calculator` |
| 分红历史 | 东方财富 | `a-dividend-analyzer` |
| 市场环境 | 乐咕/新浪 | `market-analyzer` |
| **历史分位数** | 新浪财经 | `**percentile-analyzer**` |

**Skill**: stock-analyzer, financial-health, technical-analyzer, news-risk-analyzer, shareholder-analyzer, roce-calculator, a-dividend-analyzer, market-analyzer, **percentile-analyzer**

---

### 步骤3：核心分析

#### 3.1 行情分析
- 今日走势：跌停/涨停/大涨
- 原因分析：板块效应/个股消息/市场情绪
- 验证：同板块其他个股表现
- **Skill**: stock-analyzer（查板块行情）

#### 3.2 业务分析
- 核心业务：产能/收入/利润贡献
- 战略业务：项目进展/规划产能
- 增长驱动：量价/降本/扩产
- **Skill**: stock-analyzer, financial-health, a-dividend-analyzer（查项目公告）

#### 3.3 大股东深度分析
1. 获取前十大股东数据 → `shareholder-analyzer`
2. 锁定控股股东
3. 股权穿透：工商信息查询
4. 查历史变动：减持时间线/数量
5. 查风险事件：债务违约/司法拍卖/信披违规
- **Skill**: shareholder-analyzer, 网络搜索（工商/公告）

#### 3.4 股东增持/减持分析
1. 对比Q1/Q2/Q3股东持股变化 → `shareholder-analyzer`
2. 识别陆股通（外资）增持趋势
3. 识别牛散新进
4. 识别ETF配置
5. 识别实控人关联方减持
- **Skill**: shareholder-analyzer

**Skill**: shareholder-analyzer, 网络搜索

---

### 步骤4：数据验证

- PDF财报数据提取 → `pdf-converter`
- 关键财务数字校验
- 股东数据与公告交叉验证
- 网络信息交叉验证（工商/诉讼/担保）

**Skill**: pdf-converter

---

### 步骤5：市场环境分析（可选）

- 大盘走势：上证指数MA20/MA50 → `market-analyzer`
- 行业走势：板块涨跌/轮动 → `stock-analyzer`（行业对比）
- 牛熊判断：牛市/熊市

**Skill**: market-analyzer, stock-analyzer

---

### 步骤5.1：历史分位数分析（新增）

- 计算近3月/1年/3年/5年价格分位数
- 生成各周期分位数对比表
- 输出操作建议

**分位数数据获取**：

```python
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

# 获取数据
df = ak.stock_zh_a_daily(symbol='sh600338', adjust='qfq')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').set_index('date')

# 计算分位数
def calc_percentile(data, current_value):
    return (data <= current_value).sum() / len(data) * 100

# 分析各周期
periods = {'3月': 90, '1年': 365, '3年': 1095, '5年': 1825}
for name, days in periods.items():
    start_date = datetime.now() - timedelta(days=days)
    period_df = df[df.index >= start_date]
    current = period_df['close'].iloc[-1]
    pct = calc_percentile(period_df['close'], current)
    print(f"{name}: {current:.2f}元, 分位: {pct:.1f}%")
```

**Skill**: percentile-analyzer, akshare-docs

---

### 步骤6："门外来客"调查（可选）

- 查询是否被外部公司举牌 → 交易所公告查询
- 查询增持股份是否达到5%红线
- 查询股权变更公告

**Skill**: 网络搜索（公告查询）

---

### 步骤7：综合评分

| 维度 | 得分 | 依据 |
|------|------|------|
| 盈利能力 | 15 | ROCE改善，金属价格支撑 |
| 财务安全 | 8 | 流动比率仅0.34 |
| 估值合理性 | 10 | PE偏高 |
| 技术面 | 12 | MA金叉但RSI偏弱 |
| 业务前景 | 12 | 资源丰富但进展存疑 |
| 公司治理 | 8 | 债务违约/信披违规记录 |
| **总分** | **65** | **C+（谨慎乐观）** |

**Skill**: 综合计算（基于步骤2-6数据）

---

### 步骤8：导出报告

- 格式：Markdown
- 文件名格式：`{{股票名称}}_{{股票代码}}_综合投资分析报告_{{日期}}.md`
- 包含10章节标准结构

**Skill**: 无（手动整理）

---

### 步骤9：发送报告（可选）

- 附件发送至指定邮箱

**Skill**: email-sender

---

## Skill使用汇总

| 步骤 | Skill | 用途 |
|:---:|-------|------|
| 2 | stock-analyzer | ��本信息/估值/行情/行业 |
| 2 | financial-health | 财务指标 |
| 2 | technical-analyzer | MA/RSI |
| 2 | news-risk-analyzer | 风险新闻 |
| 2 | shareholder-analyzer | 股东结构 |
| 2 | roce-calculator | ROCE趋势 |
| 2 | a-dividend-analyzer | 分红配送 |
| 2 | market-analyzer | 大盘/牛熊 |
| 3.1 | stock-analyzer | 板块行情 |
| 3.3 | shareholder-analyzer | 大股东穿透 |
| 4 | pdf-converter | PDF转换 |
| 9 | email-sender | 邮件发送 |

---

## 关键数据源

| 数据类型 | 数据源 | 用途 |
|----------|--------|----------|
| 实时行情 | 雪球 | 价格/涨跌幅/PE |
| 财务数据 | 新浪财经 | 三大表/季报/年报 |
| K线数据 | 新浪财经 | MA/RSI |
| 新闻 | 东方财富 | 风险事件 |
| 股东持股 | 东方财富 | 十大股东/变动 |
| 分红配送 | 东方财富 | 送转/现金 |
| 公司公告 | 交易所 | 股权变动/资产重组 |
| 市场PE | 乐咕 | 平均PE |
| 上证指数 | 新浪 | MA20/MA50 |

---

## 外部信息验证（可选）

| 平台 | 内容 |
|------|------|
| 国家企业信用信息公示系统 | 工商登记/注册资本/经营异常 |
| 中国执行信息公开网 | 实控人/关联公司被执行信息 |
| 裁判文书网 | 诉讼/仲裁记录 |
| 专利局 | 专利申请/授权 |