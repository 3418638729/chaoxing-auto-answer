# 技术要点与踩坑记录 🧠

> 本文档记录了在开发超星学习通自动答题脚本过程中遇到的关键技术问题和解决方案。
>
> **页面结构基于 2025–2026 年版本，如有变动请按需调整。**

---

## 一、DOM 结构概览

```
DIV#question{questionId}.padBom50.questionLi.fontLabel.singleQuesId
  ├── H3.mark_name.colorDeep          ← 题干
  ├── DIV.clear                       ← 分隔
  ├── INPUT                           ← 隐藏参数
  ├── INPUT                           ← 隐藏参数
  ├── DIV.stem_answer                 ← 选项容器
  │   ├── DIV.clearfix.answerBg.workTextWrap[qid="{qid}"][role="radio"]  ← 选项A
  │   │   ├── SPAN.choice{qid}.num_option.fl  (data="A")  → 选项字母
  │   │   └── DIV.answer_p  → 选项文字
  │   ├── DIV.clearfix.answerBg.workTextWrap[qid="{qid}"][role="radio"]  ← 选项B
  │   │   └── ...
  │   └── ...
  └── INPUT#answer{questionId}        ← 隐藏 input（存放最终答案）
```

---

## 二、单选题 vs 多选题的关键差异 🎯

### 类名不同（最重要！）

| 类型 | span 类名 | role 属性 | 说明 |
|------|-----------|-----------|------|
| **单选题** | `num_option` | `radio` | 只能选一个 |
| **多选题** | `num_option_dx` | `checkbox` | 可以选多个 |

⚠️ **`num_option_dx` 中的 `_dx` 是重点！**
直接用 `$('.num_option')` 查不到多选题的选项，只能找到单选题的。

### 处理方式不同

- **单选题**：可以使用页面内置的 `addChoice()` 函数
- **多选题**：**不能使用 `addChoice()`**，必须直接操纵 DOM

---

## 三、`addChoice` 函数分析

页面内置了 `addChoice` 函数用于处理选项点击：

```javascript
function addChoice(obj) {
    var qid = $(obj).attr("qid");
    var qt = $(obj).attr("qtype");
    if ($(obj).find(".num_option").hasClass("check_answer")) {
        // 取消选中
        $(obj).find(".num_option").removeClass("check_answer");
        $(obj).attr("aria-checked","false");
    } else {
        $(".choice" + qid).removeClass("check_answer");  // ← 清除同组其他选中
        $(obj).find(".num_option").addClass("check_answer");
        $(obj).attr("aria-checked","true");
    }
    // 收集选中值写入隐藏 input
    var choiceContent = "";
    $(".choice" + qid).each(function() {
        if ($(this).hasClass("check_answer"))
            choiceContent += $(this).attr("data");
    });
    $("#answer" + qid).val(choiceContent);
    answerContentChange();
    if (qt == 14) ... else ...
}
```

### 为什么 `addChoice` 不能用与多选题？

关键在这一行：

```javascript
$(".choice" + qid).removeClass("check_answer");  // 清除同组所有选中
```

每次调用 `addChoice` 时，它会**先清除同组所有选项的选中状态**，然后再选中当前点击的选项。这对单选题是正确的，但对多选题意味着每次点击都会取消之前选中的选项，导致最终只能选中一个。

---

## 四、正确答案的填写方式

### 4.1 单选题 — 使用 `addChoice`

```javascript
const div = document.querySelector(
  `div.answerBg.workTextWrap[qid="${qid}"] span.num_option[data="${letter}"]`
);
if (div) addChoice(div.closest('div.answerBg.workTextWrap'));
```

### 4.2 多选题 — 直接操纵 DOM

```javascript
// 第一步：先清除同组所有选中
$('.choice' + qid).removeClass('check_answer');

// 第二步：逐个选中正确选项
for (const letter of ans) {
  const span = $(`.choice${qid}[data="${letter}"]`);
  if (span.length > 0) {
    span.addClass('check_answer');
    span.closest('div.answerBg').attr('aria-checked', 'true');
  }
}

// 第三步：收集选中值写入隐藏 input
let content = '';
$('.choice' + qid + '.check_answer').each(function() {
  content += $(this).attr('data');
});
$('#answer' + qid).val(content);
```

### 4.3 简答题 — 使用 UEditor API

简答题用的是 **百度 UEditor 富文本编辑器**，不是普通的 `<textarea>`！

```html
<!-- 普通 textarea 被隐藏（visible=false） -->
<textarea name="answer{questionId}" id="answer{questionId}" style="display:none"></textarea>

<!-- 实际可编辑区域是 UEditor 生成的 iframe -->
<iframe id="ueditor_0" ...></iframe>
```

**正确答案填写方式：**

```javascript
// 方法1：UEditor API（最可靠）✅
const editor = UE.getEditor('ueditor_' + idx);
editor.setContent(answer);

// 方法2：直接写 iframe body（备选）
const iframe = document.getElementById('ueditor_' + idx);
iframe.contentDocument.body.innerHTML = answer;
```

每个 iframe 的 id 从 `ueditor_0` 到 `ueditor_9`，对应第 1~10 题。

---

## 五、验证答案的方法

### 5.1 在浏览器控制台验证

```javascript
// 单选题标记数
document.querySelectorAll('span.num_option.check_answer').length

// 多选题标记数
document.querySelectorAll('span.num_option_dx.check_answer').length

// 隐藏 input 数（所有题目）
document.querySelectorAll('input[id^="answer"]').length

// UEditor 简答验证
for (let i = 0; i < 10; i++) {
  const ifr = document.getElementById('ueditor_' + i);
  if (ifr && ifr.contentDocument && ifr.contentDocument.body) {
    console.log(`简答${i}:`, ifr.contentDocument.body.textContent.trim().length > 10 ? '✅' : '❌');
  }
}
```

### 5.2 建议的检查点

1. 单选题：`selected` 类是否加上了 → 检查 `$('span.num_option.check_answer')`
2. 多选题：多个选项是否都有 `check_answer` → 检查 `$('span.num_option_dx.check_answer')`
3. 隐藏 input：`$('#answer{questionId}').val()` 是否包含正确的字母组合
4. 简答题：UEditor iframe body 内是否有内容

---

## 六、完整页面结构示例

```
DIV#question405987650.padBom50.questionLi.fontLabel.singleQuesId
  H3.mark_name.colorDeep          ← 题干
  DIV.clear                       ← 分隔
  INPUT                           ← 隐藏参数
  INPUT                           ← 隐藏参数
  DIV.stem_answer                 ← 选项容器
    DIV.clearfix.answerBg.workTextWrap[qid="405987650"][role="radio"]  ← 选项A
      SPAN.choice405987650.num_option.fl  (data="A")  → A
      DIV.answer_p  → 选项文字
    DIV.clearfix.answerBg.workTextWrap[qid="405987650"][role="radio"]  ← 选项B
      ...
  选项后会有一个隐藏 input: input#answer405987650

多选时 role="checkbox"，span 类名是 num_option_dx
简答题多一个 <textarea name="answer405987740" id="answer405987740"> + UEditor iframe
```

---

## 七、踩坑总结

| 坑 | 表现 | 原因 | 解决 |
|----|------|------|------|
| 多选题填不上 | 只能选中一个选项 | `addChoice` 会清除同组所有选中 | 直接操纵 DOM |
| 多选题查不到 | `$('.num_option')` 找不到 | 多选的 class 是 `num_option_dx` | 用 `num_option_dx` |
| 简答题填不上 | textarea 写了没反应 | 用的是 UEditor 富文本 | 用 UEditor API |
| addChoice 点击无效 | 点击了但没选中 | 传入的是 span 而不是 div | 传入 `div.answerBg` |
| 验证时发现不对 | `div.selected` 查不到 | `addChoice` 不加 selected class | 查 `check_answer` class |

---

## 八、版本记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-06-17 | v1.0 | 完成 "24级本科习思想期末复习作业" 完整调试 |
| | | 发现多选类名差异 `num_option` vs `num_option_dx` |
| | | 发现简答题 UEditor 富文本编辑器 |
| | | 验证统计：单选 60 + 多选约 96 + 简答 10 |
