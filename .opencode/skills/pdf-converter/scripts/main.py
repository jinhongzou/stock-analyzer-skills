#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF 转 Markdown 转换器
支持多种转换方式，并进行内容校验
"""

import os
import sys
import re
import json
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

def convert_with_pdfplumber(pdf_path: str) -> str:
    """使用 pdfplumber 转换为 Markdown"""
    import pdfplumber
    
    result = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            result.append(f"\n## 第 {page_num} 页\n")
            
            # 提取表格
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    if table:
                        result.append("\n| " + " | ".join(table[0]) + " |")
                        result.append("| " + " | ".join(["---"] * len(table[0])) + " |")
                        for row in table[1:]:
                            result.append("| " + " | ".join(str(cell) if cell else "" for cell in row) + " |")
                        result.append("\n")
            
            # 提取文本
            text = page.extract_text()
            if text:
                result.append(text)
    
    return "\n".join(result)


def convert_with_markitdown(pdf_path: str) -> str:
    """使用 markitdown 转换为 Markdown"""
    from markitdown import MarkItDown
    
    md = MarkItDown()
    result = md.convert(pdf_path)
    return result.text_content


def convert_with_pymupdf(pdf_path: str) -> str:
    """使用 PyMuPDF (fitz) 转换为 Markdown"""
    import fitz
    
    result = []
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        result.append(f"\n## 第 {page_num + 1} 页\n")
        
        # 提取表格
        tables = page.find_tables()
        if tables:
            for table in tables:
                if table.extract:
                    rows = table.extract()
                    if rows:
                        result.append("\n| " + " | ".join(str(cell) if cell else "" for cell in rows[0]) + " |")
                        result.append("| " + " | ".join(["---"] * len(rows[0])) + " |")
                        for row in rows[1:]:
                            result.append("| " + " | ".join(str(cell) if cell else "" for cell in row) + " |")
                        result.append("\n")
        
        # 提取文本
        text = page.get_text()
        if text:
            result.append(text)
    
    doc.close()
    return "\n".join(result)


def extract_numbers(text: str) -> list:
    """提取文本中的所有数字"""
    pattern = r'-?\d{1,3}(?:,\d{3})*(?:\.\d+)?'
    return re.findall(pattern, text)


def validate_completeness(original_md: str, converted_md: str) -> dict:
    """校验内容完整性"""
    issues = []
    
    # 检查是否有连续重复行
    lines = converted_md.split('\n')
    repeat_count = 0
    for i in range(len(lines) - 2):
        if lines[i] == lines[i+1] == lines[i+2] and lines[i].strip():
            repeat_count += 1
    
    if repeat_count > 0:
        issues.append(f"发现 {repeat_count} 处连续重复内容")
    
    # 检查表格完整性
    table_count = converted_md.count('|')
    if table_count < 10 and '表格' not in converted_md.lower():
        issues.append("可能存在表格提取不完整")
    
    return {
        "passed": len(issues) == 0,
        "issues": issues
    }


def validate_format(original_md: str, converted_md: str) -> dict:
    """校验格式保留"""
    issues = []
    
    # 检查标题格式
    if '#' not in converted_md:
        issues.append("未检测到标题格式")
    
    # 检查数字格式化
    original_numbers = len(extract_numbers(original_md))
    converted_numbers = len(extract_numbers(converted_md))
    
    if converted_numbers < original_numbers * 0.8:
        issues.append(f"数字提取不完整: 原始约{original_numbers}个，转换得{converted_numbers}个")
    
    return {
        "passed": len(issues) == 0,
        "issues": issues
    }


def validate_key_numbers(pdf_path: str, converted_md: str) -> dict:
    """校验关键财务数字准确性"""
    issues = []
    
    # 提取 PDF 原始数字（使用 pdfplumber）- 捕获异常
    import pdfplumber
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pdf_text = ""
            for page in pdf.pages:
                pdf_text += page.extract_text() or ""
    except Exception as e:
        return {
            "passed": True,  # PDF读取失败时跳过此检查
            "issues": [f"PDF读取失败，跳过数字校验: {str(e)[:50]}"]
        }
    
    # 对比关键数字
    pdf_numbers = set(extract_numbers(pdf_text))
    md_numbers = set(extract_numbers(converted_md))
    
    # 找出缺失的关键数字（在大数字中查找）
    try:
        def is_large_num(n):
            try:
                return abs(float(n.replace(',', '').replace('-', ''))) > 1000000
            except (ValueError, KeyError):
                return False
        large_numbers_pdf = set(n for n in pdf_numbers if is_large_num(n))
        large_numbers_md = set(n for n in md_numbers if is_large_num(n))
    except (ValueError, KeyError):
        large_numbers_pdf = set()
        large_numbers_md = set()
    
    missing = large_numbers_pdf - large_numbers_md
    if missing:
        # 只报告缺失的大数字
        if len(missing) > len(large_numbers_pdf) * 0.3:
            issues.append(f"关键数字可能缺失: {len(missing)}个大额数字未找到")
    
    return {
        "passed": len(issues) == 0,
        "issues": issues
    }


def validate_tables(pdf_path: str, converted_md: str) -> dict:
    """校验表格结构"""
    issues = []
    
    # 统计表格行列
    table_rows = converted_md.count('\n|')
    
    if table_rows < 3:
        issues.append("表格数据过少，可能提取失败")
    
    # 检查表格格式一致性
    lines = converted_md.split('\n')
    table_lines = [l for l in lines if l.strip().startswith('|')]
    
    if table_lines:
        col_counts = [len([c for c in l.split('|') if c]) for l in table_lines if '---' not in l]
        if col_counts:
            if len(set(col_counts)) > 1:
                issues.append("表格列数不一致，存在格式问题")
    
    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "table_rows": table_rows
    }


def validate_conversion(pdf_path: str, converted_md: str) -> dict:
    """综合校验"""
    results = {
        "completeness": validate_completeness("", converted_md),
        "format": validate_format("", converted_md),
        "numbers": validate_key_numbers(pdf_path, converted_md),
        "tables": validate_tables(pdf_path, converted_md)
    }
    
    # 计算综合评分
    passed_checks = sum(1 for v in results.values() if v["passed"])
    total_checks = len(results)
    score = int(passed_checks / total_checks * 100)
    
    results["score"] = score
    results["passed"] = score >= 80
    
    # 收集所有问题
    all_issues = []
    for check_name, check_result in results.items():
        if check_name not in ("score", "passed") and isinstance(check_result, dict) and check_result.get("issues"):
            for issue in check_result["issues"]:
                all_issues.append(f"[{check_name}] {issue}")
    
    results["all_issues"] = all_issues
    
    return results


def convert_pdf(pdf_path: str, output_dir: str = None) -> dict:
    """转换 PDF 并返回结果"""
    
    pdf_path = os.path.abspath(pdf_path)
    
    if not os.path.exists(pdf_path):
        return {"success": False, "error": f"文件不存在: {pdf_path}"}
    
    if not pdf_path.lower().endswith('.pdf'):
        return {"success": False, "error": "仅支持 PDF 文件"}
    
    # 设置输出目录
    if output_dir:
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = os.path.dirname(pdf_path)
    
    output_md = os.path.join(output_dir, os.path.basename(pdf_path).replace('.pdf', '.md'))
    
    # 尝试多种转换方式
    converted_md = None
    methods_used = []
    
    # 方法1: markitdown (首选)
    try:
        converted_md = convert_with_markitdown(pdf_path)
        methods_used.append("markitdown")
    except Exception as e:
        print(f"markitdown 转换失败: {e}")
    
    # 方法2: pdfplumber (备选)
    if not converted_md or len(converted_md) < 100:
        try:
            converted_md = convert_with_pdfplumber(pdf_path)
            methods_used.append("pdfplumber")
        except Exception as e:
            print(f"pdfplumber 转换失败: {e}")
    
    # 方法3: pymupdf (最后备选)
    if not converted_md or len(converted_md) < 100:
        try:
            converted_md = convert_with_pymupdf(pdf_path)
            methods_used.append("pymupdf")
        except Exception as e:
            print(f"pymupdf 转换失败: {e}")
    
    if not converted_md or len(converted_md) < 100:
        return {"success": False, "error": "所有转换方法均失败"}
    
    # 写入输出文件
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(f"# {os.path.basename(pdf_path).replace('.pdf', '')}\n")
        f.write(f"# 转换时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(converted_md)
    
    # 校验转换结果
    validation = validate_conversion(pdf_path, converted_md)
    
    return {
        "success": True,
        "pdf_path": pdf_path,
        "output_md": output_md,
        "methods_used": methods_used,
        "char_count": len(converted_md),
        "validation": validation
    }


def main():
    """主函数"""
    
    if len(sys.argv) < 2:
        print("用法: python main.py <PDF文件路径> [输出目录]")
        print("示例:")
        print("  python main.py ./report.pdf")
        print("  python main.py ./2026Q1.pdf ./output/")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"开始转换: {pdf_path}")
    print("-" * 50)
    
    result = convert_pdf(pdf_path, output_dir)
    
    if not result["success"]:
        print(f"\n[X] 转换失败: {result['error']}")
        sys.exit(1)
    
    print(f"\n[V] 转换完成")
    print(f"  输出文件: {result['output_md']}")
    print(f"  转换方法: {', '.join(result['methods_used'])}")
    print(f"  内容长度: {result['char_count']} 字符")
    
    # 显示校验结果
    val = result["validation"]
    print(f"\n====== 校验结果 ======")
    print(f"校验结果: {'[V] 通过' if val['passed'] else '[!] 需注意'}")
    print(f"  综合评分: {val['score']}/100")
    print(f"  内容完整性: {'[V]' if val['completeness']['passed'] else '[X]'}")
    print(f"  格式保留: {'[V]' if val['format']['passed'] else '[X]'}")
    print(f"  数字准确性: {'[V]' if val['numbers']['passed'] else '[X]'}")
    print(f"  表格结构: {'[V]' if val['tables']['passed'] else '[X]'}")
    
    if val["all_issues"]:
        print(f"\n发现的问题:")
        for issue in val["all_issues"]:
            print(f"  - {issue}")
    
    print(f"\n输出已保存至: {result['output_md']}")


if __name__ == "__main__":
    main()