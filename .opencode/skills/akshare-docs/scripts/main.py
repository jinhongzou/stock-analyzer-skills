# -*- coding: utf-8 -*-
"""
AKshare Docs - 文档搜索工具
用法: python main.py [搜索关键词]
"""

import sys
import os
import re

# 文档路径
DOC_PATH = os.path.join(os.path.dirname(__file__), "..", "akshare_api_reference.md")

def load_doc():
    """加载文档"""
    if not os.path.exists(DOC_PATH):
        print(f"错误: 文档文件不存在: {DOC_PATH}")
        return ""
    with open(DOC_PATH, "r", encoding="utf-8") as f:
        return f.read()

def search_doc(doc, keyword):
    """搜索文档"""
    if not keyword:
        # 显示目录结构
        return show_toc(doc)

    keyword = keyword.lower()
    lines = doc.split("\n")
    results = []
    current_section = ""
    in_result = False
    match_count = 0

    for i, line in enumerate(lines):
        # 跟踪当前章节
        if line.startswith("#### ") or line.startswith("### ") or line.startswith("## "):
            current_section = line.strip()

        # 搜索匹配
        if keyword in line.lower():
            match_count += 1
            in_result = True
            # 收集上下文（前后各20行）
            start = max(0, i - 5)
            end = min(len(lines), i + 30)

            context = "\n".join(lines[start:end])
            results.append({
                "section": current_section,
                "line_num": i + 1,
                "match": line.strip(),
                "context": context
            })
            if len(results) >= 10:  # 限制结果数量
                break

    return results, match_count

def show_toc(doc):
    """显示目录结构"""
    lines = doc.split("\n")
    toc = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## ") or stripped.startswith("### ") or stripped.startswith("#### "):
            level = len(line) - len(line.lstrip("#"))
            toc.append(("  " * (level - 2)) + stripped)

    return toc

def format_results(results, total):
    """格式化输出"""
    output = []
    output.append("=" * 70)
    output.append(f"找到 {total} 处匹配结果（显示前 {len(results)} 处）")
    output.append("=" * 70)

    for i, r in enumerate(results, 1):
        output.append(f"\n【{i}】{r['section']}")
        output.append(f"行号: {r['line_num']}")
        output.append(f"匹配: {r['match'][:100]}...")
        output.append("-" * 50)
        output.append(r["context"][:500])
        output.append("-" * 50)

    return "\n".join(output)

def format_toc(toc):
    """格式化目录"""
    output = []
    output.append("=" * 70)
    output.append("AKshare 接口文档目录")
    output.append("=" * 70)
    output.append("")
    for item in toc[:100]:  # 限制显示
        output.append(item)
    if len(toc) > 100:
        output.append(f"\n... 还有 {len(toc) - 100} 个子章节")
    return "\n".join(output)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    keyword = sys.argv[1] if len(sys.argv) > 1 else ""

    print(f"加载文档: {DOC_PATH}")
    doc = load_doc()
    if not doc:
        print("文档加载失败")
        sys.exit(1)

    print(f"文档大小: {len(doc)} 字符")

    if not keyword:
        result = show_toc(doc)
        print(format_toc(result))
    else:
        results, total = search_doc(doc, keyword)
        print(format_results(results, total))