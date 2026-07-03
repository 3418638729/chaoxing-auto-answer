# 快速入门指南 🚀

## 前置条件

- Python 3.7+
- Chrome 浏览器
- 超星学习通账号（**你自己的！**）

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/chaoxing-auto-answer.git
cd chaoxing-auto-answer
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

这会自动安装：
- `selenium` — 浏览器自动化
- `webdriver-manager` — 自动下载和管理 ChromeDriver

## 配置

### 第一步：填写你的学习通账号

打开 `scripts/chaoxing_click.py`，找到开头的配置区：

```python
# ⚠️ 必须修改为你自己的账号！
USERNAME = "13800000000"          # ← 改成你的手机号
PASSWORD = "your_password_here"   # ← 改成你的密码
```

### 第二步：配置作业 URL

找到 `TASK_URL`，改为你要完成的作业的实际 URL。一般格式为：

```python
TASK_URL = "https://mooc1.chaoxing.com/mooc-ans/mycourse/studentstudy?headless=1&courseId=XXXXX&chapterId=XXXXX"
```

> 💡 **如何获取作业 URL：** 在浏览器中登录学习通 → 进入课程 → 点击作业 → 从地址栏复制完整 URL。

### 第三步：配置答案

修改 `ANSWERS` 字典：

```python
ANSWERS = {
    "题目标题关键字（部分匹配即可）": "A",           # 单选题
    "另一道题的关键字": "ABC",                       # 多选题
    "简答题题干": "这是简答题的答案内容……",          # 简答题
}
```

- **单选题**：答案格式为单个字母 `"A"`
- **多选题**：答案格式为多个字母 `"ABD"`（顺序不重要）
- **简答题**：答案格式为完整文本

> 脚本会根据题干文本**部分匹配**查找答案，所以只需要填写题干中的关键词即可。

## 运行

```bash
cd scripts
python chaoxing_click.py
```

## 运行过程

1. 自动打开 Chrome 浏览器
2. 跳转到学习通登录页并自动填写账号密码
3. 登录成功后跳转到作业页面
4. 逐题填写答案：
   - ✅ 单选题：通过 `addChoice` 点击选中
   - ✅ 多选题：直接操纵 DOM 选中所有正确选项
   - ✅ 简答题：通过 UEditor API 填入内容
5. 点击「暂时保存」
6. 显示验证统计

## 验证

运行结束后，控制台会输出类似这样的统计：

```
📊 验证统计:
  单选题标记: 60
  多选题标记: 96
  隐藏 input: 90
  简答题已填: 10
```

你也可以在浏览器中手动确认答案是否已正确填入。

## 常见问题

### Q: Chrome 浏览器启动后不自动打开页面？
确保 Chrome 已安装。脚本会自动下载匹配的 ChromeDriver。

### Q: 登录失败？
检查你的账号密码是否正确。注意学习通可能有验证码，如果频繁登录失败可尝试手动登录后导出 Cookie 再使用。

### Q: 多选题填不上？
这是常见问题！详见 [技术要点文档](technical-notes.md) 中的"多选题陷阱"章节。

### Q: 简答题没有填上？
简答题使用 UEditor 富文本编辑器，不是普通的 `<textarea>`。脚本已通过 UEditor API 处理，如果仍未填上，检查 `ueditor_` 开头的 iframe 是否存在。

### Q: 答案匹配不上？
`ANSWERS` 使用 `if key in stem` 做**部分匹配**，确保你的关键词在题干的文字中即可。如果不行，手动复制一部分题干文本作为 key。

## 提示

- 运行前**手动在浏览器中打开一次作业**，确认可以正常访问
- 建议先在测试题目上运行，确认答案格式正确
- 答题完成后建议手动检查几题确认无误
