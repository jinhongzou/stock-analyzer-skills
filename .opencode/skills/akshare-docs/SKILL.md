---
name: akshare-docs
description: AKshare API文档查询工具。搜索接口名或功能关键词，查询用法、参数说明、返回值格式和代码示例，辅助实现数据获取功能
---

# AKshare Docs

**功能**: 查询 AKshare 接口文档，支持全文搜索和分类浏览
**文档来源**: `.opencode/skills/akshare-docs/akshare_api_reference.md`

---

## 使用方式

**OpenCode 调用**:
```
skill(name="akshare-docs")
```

**命令行运行**:
```bash
python .opencode/skills/core/src/skills/akshare-docs/main.py [搜索关键词]
```

---

## 使用示例

### 1. 搜索特定接口
```bash
python .opencode/skills/core/src/skills/akshare-docs/main.py stock_zh_a_spot
```

### 2. 搜索数据源
```bash
python .opencode/skills/core/src/skills/akshare-docs/main.py 新浪财经
```

### 3. 搜索函数类别
```bash
python .opencode/skills/core/src/skills/akshare-docs/main.py 财务报表
```

---

## 搜索提示

- **接口名搜索**: 如 `stock_zh_a_daily`, `stock_financial_report_sina`
- **数据源搜索**: 如 `东方财富`, `新浪财经`, `雪球`, `乐咕`
- **功能搜索**: 如 `分红`, `股东`, `财务`, `K线`, `新闻`
- **空参数**: 显示文档目录结构

---

## 文档结构

- A股股票数据（市场总貌、实时行情、历史K线、财务报表）
- 指数数据
- 基金数据
- 港股数据
- 美股数据
- 期货数据
- 期权数据
- 债券数据
- 外汇数据
- 加密货币数据
- 宏观数据
- 行业数据