#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
邮件发送器
支持发送带附件的邮件
"""

import os
import sys
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

# 加载 .env 文件
def load_env():
    """从 .env 文件加载环境变量"""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env()

# 从环境变量获取配置
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.126.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")


def send_email(to_addr: str, subject: str, body: str, attachments: list = None) -> dict:
    """发送邮件"""

    # 检查必要配置
    if not SMTP_USER or not SMTP_PASSWORD:
        return {"success": False, "error": "请设置环境变量 SMTP_USER 和 SMTP_PASSWORD"}
    
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = to_addr
        msg["Subject"] = subject
        
        # 添加正文
        msg.attach(MIMEText(body, "plain", "utf-8"))
        
        # 添加附件
        if attachments:
            for attachment_path in attachments:
                attachment_path = attachment_path.strip()
                if not attachment_path:
                    continue
                    
                if not os.path.exists(attachment_path):
                    print(f"  [!] 附件不存在: {attachment_path}")
                    continue
                
                filename = os.path.basename(attachment_path)
                
                # 读取附件内容
                with open(attachment_path, "rb") as f:
                    attachment_data = f.read()
                
                # 创建附件
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment_data)
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={filename}"
                )
                msg.attach(part)
                print(f"  [V] 已添加附件: {filename}")
        
        # 连接SMTP服务器并发送
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to_addr, msg.as_string())
        server.quit()
        
        return {"success": True, "message": "邮件发送成功"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """主函数"""
    
    if len(sys.argv) < 4:
        print("用法: python main.py <收件人> <主题> <内容> [附件1,附件2,...]")
        print("示例:")
        print("  python main.py test@example.com '测试' '正文内容'")
        print("  python main.py test@example.com '报告' '请查收' ./file.pdf")
        print("  python main.py test@example.com '报告' '请查收' 'file1.pdf,file2.pdf'")
        sys.exit(1)
    
    to_addr = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    
    # 处理附件
    attachments = None
    if len(sys.argv) > 4:
        attachments = sys.argv[4].split(",")
    
    print(f"发送邮件...")
    print(f"  收件人: {to_addr}")
    print(f"  主题: {subject}")
    if attachments:
        print(f"  附件: {attachments}")
    print("-" * 50)
    
    result = send_email(to_addr, subject, body, attachments)
    
    if result["success"]:
        print(f"\n[V] {result['message']}")
    else:
        print(f"\n[X] 发送失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()