---
name: email-sender
description: 邮件发送。通过SMTP协议发送邮件到指定邮箱，支持文本内容和附件
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
python .opencode/skills/core/src/skills/email-sender/main.py <收件人> <主题> <内容> [附件路径]
```

### 示例

```bash
# 发送简单邮件
python .opencode/skills/core/src/skills/email-sender/main.py "test@example.com" "测试主题" "测试内容"

# 带附件
python .opencode/skills/core/src/skills/email-sender/main.py "test@example.com" "报告" "请查收" "./report.pdf"

# 多个附件
python .opencode/skills/core/src/skills/email-sender/main.py "test@example.com" "报告" "请查收" "file1.pdf,file2.pdf"
```

---

## 配置

### 默认发件人（已配置）

- **邮箱**: jinhongzou@126.com
- **SMTP服务器**: smtp.126.com
- **SMTP端口**: 465 (SSL)
> 没有提供目标邮箱地址，则发送给 `jinhongzou@126.com`
