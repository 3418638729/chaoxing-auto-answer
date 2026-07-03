# 超星学习通自动答题工具 🚀

> **⚠️ 重要声明：** 本项目仅供学习和技术研究使用！请使用**你自己的学习通账号密码**，不要使用他人的账号。使用本工具可能违反平台规定，请自行评估风险。

## 功能概述

自动完成超星学习通（chaoxing.com）作业的 Python 脚本。支持：

- ✅ **单选题** — 自动选择正确答案
- ✅ **多选题** — 自动选择多个正确答案
- ✅ **简答题** — 通过 UEditor API 填入富文本答案
- ✅ **自动登录** — 使用 Selenium 模拟浏览器登录
- ✅ **自动保存** — 答题完成后点击"暂时保存"

## 快速开始

```bash
git clone https://github.com/YOUR_USERNAME/chaoxing-auto-answer.git
cd chaoxing-auto-answer
pip install -r requirements.txt
```

修改脚本中的账号密码为**你自己的学习通账号**：

```python
# scripts/chaoxing_click.py — 搜索以下行并替换
USERNAME = "13800000000"   # ← 改成你的手机号
PASSWORD = "yourpassword"  # ← 改成你的密码
```

运行：

```bash
python scripts/chaoxing_click.py
```

> 📖 详细用法见 [快速入门指南](docs/quick-start.md)

## 项目结构

```
chaoxing-auto-answer/
├── README.md                  # 本文件
├── requirements.txt           # Python 依赖
├── .gitignore                 # Git 忽略规则
├── config.example.json        # 示例配置文件（填入你自己的账号）
├── scripts/
│   ├── chaoxing_click.py      # ✅ 主脚本（推荐使用）
│   └── chaoxing_final.py      # 备用版本
└── docs/
    ├── quick-start.md         # 快速入门指南
    └── technical-notes.md     # 技术要点与踩坑记录
```

## 脚本说明

| 脚本 | 状态 | 说明 |
|------|------|------|
| `chaoxing_click.py` | ✅ 推荐 | 登录 + 点击选项版，最新稳定版 |
| `chaoxing_final.py` | 🔧 备用 | 登录 + 点击选项的早期版本 |

## 技术要点

答题过程中遇到的一些关键发现（详细见 [技术要点文档](docs/technical-notes.md)）：

1. **单选题 vs 多选题的 DOM 类名不同** — 多选用 `num_option_dx`，不是 `num_option`
2. **多选题不能用 `addChoice()` 函数** — 该函数会清除同组其他选中状态
3. **简答题是 UEditor 富文本编辑器** — 不是普通 textarea，必须用 UEditor API
4. **验证答案方法** — 通过检查 `span.num_option.check_answer` 或隐藏 input

## 免责声明

- 本项目仅用于**学习和研究目的**
- 使用前请替换为**你自己的学习通账号密码**
- 请勿用于侵犯他人权益或违反平台规定的行为
- 使用本工具产生的任何后果由使用者自行承担

---

**Happy auto-answering!** 🎉
