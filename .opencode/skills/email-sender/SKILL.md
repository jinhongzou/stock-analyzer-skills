---
name: email-sender
description: 发送邮件到指定邮箱，支持SMTP协议
---

# Email Sender

**功能**: 发送邮件到指定邮箱，支持附件  
**数据源**: SMTP协议

---

## 使用方式

**OpenCode 调用**:
```
skill(name="email-sender")
```

**命令行运行**:
```bash
python .opencode/skills/email-sender/scripts/main.py <收件人> <主题> <内容> [附件路径]
```

### 示例

```bash
# 发送简单邮件
python .opencode/skills/email-sender/scripts/main.py "test@example.com" "测试主题" "测试内容"

# 带附件
python .opencode/skills/email-sender/scripts/main.py "test@example.com" "报告" "请查收" "./report.pdf"

# 多个附件
python .opencode/skills/email-sender/scripts/main.py "test@example.com" "报告" "请查收" "file1.pdf,file2.pdf"
```

---

## 配置

### 默认发件人（已配置）

- **邮箱**: jinhongzou@126.com
- **SMTP服务器**: smtp.126.com
- **SMTP端口**: 465 (SSL)

### 自定义发件人

如需使用其他邮箱，修改 `.env` 文件：

```
SMTP_HOST=smtp.126.com
SMTP_PORT=465
SMTP_USER=your_email@126.com
SMTP_PASSWORD=your_password
```

---

## 依赖安装

```bash
pip install python-dotenv
```