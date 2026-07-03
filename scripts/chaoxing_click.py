"""
超星学习通自动答题脚本（推荐版）
=================================
⚠️ 请使用你自己的学习通账号密码！
本脚本仅供学习和研究使用。

功能：登录超星学习通 → 打开作业页面 → 自动完成所有题目 → 暂时保存

使用方法：
  1. 修改下方的 USERNAME 和 PASSWORD 为你自己的账号密码
  2. 修改 TASK_URL 为目标作业 URL
  3. 确保已安装依赖：pip install selenium webdriver-manager
  4. 运行：python chaoxing_click.py
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ============================================================
# ⚠️ 请使用你自己的学习通账号密码！
# ============================================================
USERNAME = "13800000000"        # ← 改成你的学习通手机号
PASSWORD = "your_password_here"  # ← 改成你的学习通密码
TASK_URL = (
    "https://mooc1.chaoxing.com/mooc-ans/mycourse/studentstudy?"
    "headless=1&courseId=你的课程ID&chapterId=你的章节ID"
)

# ============================================================
# 题库答案（key = 题目标题，value = 正确答案）
# 单选题：单个字母如 "A"
# 多选题：字母字符串如 "ABC"
# 简答题：文本字符串
# ============================================================
ANSWERS = {
    # ===== 示例题目（请替换为你自己的答案数据） =====
    # 单选题示例
    "中国特色社会主义最本质的特征是": "A",
    "科学发展观的核心立场是": "B",
    # 多选题示例
    "下列属于社会主义核心价值观内容的有": "ABD",
    "中国特色社会主义理论体系包括": "ABC",
    # 简答题示例
    "简述新时代中国特色社会主义思想的历史地位": (
        "新时代中国特色社会主义思想是马克思主义中国化的最新成果，"
        "是党和人民实践经验和集体智慧的结晶，"
        "是中国特色社会主义理论体系的重要组成部分。"
    ),
}

# ============================================================
# DOM 选择器与技术要点（详见 docs/technical-notes.md）
# ============================================================
# 单选题 span:    span.choice{questionId}.num_option.fl
# 多选题 span:    span.choice{questionId}.num_option_dx.fl
# 多选用 addChoice 会清除同组选中，必须直接操纵 DOM！
# 简答用 UEditor：UE.getEditor('ueditor_' + idx).setContent(answer)
# ============================================================


def setup_driver():
    """初始化 Chrome 浏览器"""
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # 取消注释以启用无头模式
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # 防止被检测
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def login(driver):
    """登录超星学习通"""
    print("正在登录...")
    driver.get("https://passport2.chaoxing.com/login")

    # 等待登录页面加载
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "phone"))
    )

    # 填入账号密码
    phone_input = driver.find_element(By.ID, "phone")
    phone_input.send_keys(USERNAME)

    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(PASSWORD)

    # 点击登录按钮
    login_btn = driver.find_element(By.CLASS_NAME, "login-btn")
    login_btn.click()

    # 等待登录完成
    time.sleep(3)
    print("登录完成！")


def answer_single_choice(driver, qid, answer):
    """
    填写单选题
    使用页面内置的 addChoice 函数
    """
    answer = answer.strip().upper()
    js = f"""
    const div = document.querySelector(
        `div.answerBg.workTextWrap[qid="{qid}"] span.num_option[data="{answer}"]`
    );
    if (div) {{
        addChoice(div.closest('div.answerBg.workTextWrap'));
        return true;
    }}
    return false;
    """
    return driver.execute_script(js)


def answer_multiple_choice(driver, qid, answer):
    """
    填写多选题
    ⚠️ 不能使用 addChoice！它会清除同组其他选中状态。
    必须直接操纵 DOM。
    """
    letters = list(answer.strip().upper())
    js_template = """
    // 先清除同组所有选中
    $('.choice' + qid).removeClass('check_answer');
    var selected = @letters@;
    var count = 0;
    for (var i = 0; i < selected.length; i++) {
        var span = document.querySelector(
            'span.choice' + qid + '[data="' + selected[i] + '"]'
        );
        if (span) {
            span.classList.add('check_answer');
            span.closest('div.answerBg').setAttribute('aria-checked', 'true');
            count++;
        }
    }
    // 收集选中值写入隐藏 input
    var content = '';
    document.querySelectorAll('.choice' + qid + '.check_answer').forEach(function(el) {
        content += el.getAttribute('data');
    });
    var hid = document.getElementById('answer' + qid);
    if (hid) hid.value = content;
    return count;
    """
    js = js_template.replace("@letters@", str(letters).replace("'", '"'))
    return driver.execute_script(js)


def answer_essay(driver, qid, idx, answer):
    """
    填写简答题
    使用 UEditor API（百度富文本编辑器）
    """
    js = f"""
    var editor = UE.getEditor('ueditor_{idx}');
    if (editor) {{
        editor.setContent(`{answer}`);
        return true;
    }}
    // 备选方案：直接写 iframe body
    var iframe = document.getElementById('ueditor_{idx}');
    if (iframe && iframe.contentDocument) {{
        iframe.contentDocument.body.innerHTML = `{answer}`;
        return true;
    }}
    return false;
    """
    return driver.execute_script(js)


def process_questions(driver):
    """遍历并回答所有题目"""
    wait = WebDriverWait(driver, 10)
    time.sleep(2)

    # 获取所有题目容器
    questions = driver.find_elements(By.CSS_SELECTOR, "div.questionLi")
    print(f"找到 {len(questions)} 道题")

    answered_count = 0
    essay_idx = 0

    for q in questions:
        try:
            # 获取题目 ID
            qid = q.get_attribute("id")
            if qid:
                qid = qid.replace("question", "")

            # 获取题干文本（用于匹配答案）
            stem = q.find_element(By.CSS_SELECTOR, "h3.mark_name").text.strip()

            # 获取题目类型
            role = q.get_attribute("role")  # radio = 单选, checkbox = 多选
            qtype = q.get_attribute("qtype")

            # 查找匹配的答案
            answer = None
            for key, val in ANSWERS.items():
                if key in stem:
                    answer = val
                    break

            if answer is None:
                print(f"  ⏭️  跳过未知题目: {stem[:30]}...")
                continue

            if qtype == "14" or role == "radio":
                # 单选题
                result = answer_single_choice(driver, qid, answer)
                status = "✅" if result else "❌"
                print(f"  {status} 单选 [{qid}]: {stem[:30]}... → {answer}")

            elif qtype == "15" or role == "checkbox":
                # 多选题
                result = answer_multiple_choice(driver, qid, answer)
                status = "✅" if result and result > 0 else "❌"
                print(f"  {status} 多选 [{qid}]: {stem[:30]}... → {answer}")

            elif qtype == "16":
                # 简答题
                result = answer_essay(driver, qid, essay_idx, answer)
                status = "✅" if result else "❌"
                print(f"  {status} 简答 [{qid}]: {stem[:30]}... (已填)")
                essay_idx += 1

            else:
                print(f"  ⏭️  未知类型 [qtype={qtype}]: {stem[:30]}...")
                continue

            answered_count += 1

        except Exception as e:
            print(f"  ⚠️  处理题目时出错: {e}")
            continue

    print(f"\n共计回答 {answered_count} 题")


def save_and_verify(driver):
    """点击暂时保存并验证"""
    try:
        # 点击暂时保存
        save_btn = driver.find_element(By.CSS_SELECTOR, "input[value='暂时保存']")
        save_btn.click()
        time.sleep(1)
        print("✅ 已点击「暂时保存」")
    except Exception as e:
        print(f"  ⚠️  保存按钮未找到: {e}")

    # 验证答案
    verify_js = """
    var result = {
        single: document.querySelectorAll('span.num_option.check_answer').length,
        multi: document.querySelectorAll('span.num_option_dx.check_answer').length,
        hidden: document.querySelectorAll('input[id^="answer"]').length
    };
    // UEditor 验证
    var essayFilled = 0;
    for (var i = 0; i < 10; i++) {
        var ifr = document.getElementById('ueditor_' + i);
        if (ifr && ifr.contentDocument && ifr.contentDocument.body) {
            if (ifr.contentDocument.body.textContent.trim().length > 10)
                essayFilled++;
        }
    }
    result.essayFilled = essayFilled;
    return result;
    """
    stats = driver.execute_script(verify_js)
    print("\n📊 验证统计:")
    print(f"  单选题标记: {stats['single']}")
    print(f"  多选题标记: {stats['multi']}")
    print(f"  隐藏 input: {stats['hidden']}")
    print(f"  简答题已填: {stats['essayFilled']}")


def main():
    print("=" * 50)
    print("超星学习通自动答题工具")
    print("=" * 50)
    print()

    driver = setup_driver()
    try:
        # 登录
        login(driver)

        # 打开作业页面
        print("正在打开作业页面...")
        driver.get(TASK_URL)
        time.sleep(3)

        # 处理所有题目
        process_questions(driver)

        # 保存并验证
        save_and_verify(driver)

        print("\n🎉 全部完成！按 Ctrl+C 退出浏览器，或稍后自动关闭。")
        time.sleep(60)

    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
    finally:
        driver.quit()
        print("浏览器已关闭")


if __name__ == "__main__":
    main()
