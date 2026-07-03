"""
超星学习通自动答题脚本（备用版）
=================================
⚠️ 请使用你自己的学习通账号密码！

这个版本是早期版本，功能与 chaoxing_click.py 类似但结构略有不同。
推荐使用 chaoxing_click.py（主脚本）。
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ============================================================
# ⚠️ 请使用你自己的学习通账号密码！
# ============================================================
USERNAME = "13800000000"
PASSWORD = "your_password_here"
TASK_URL = "https://mooc1.chaoxing.com/mooc-ans/mycourse/studentstudy?headless=1"

# ============================================================
# 题库答案（格式同上）
# ============================================================
ANSWERS = {
    "示例题目一": "A",
    "示例题目二": "BCD",
    "示例简答题": "这是示例答案内容，请替换为你自己的答案。",
}


def setup_driver():
    """初始化 Chrome 浏览器"""
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def login(driver):
    """登录"""
    driver.get("https://passport2.chaoxing.com/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "phone")))
    driver.find_element(By.ID, "phone").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.CLASS_NAME, "login-btn").click()
    time.sleep(3)
    print("登录完成")


def do_work(driver):
    """答题主逻辑（使用页面 JS 直接操纵 DOM）"""
    time.sleep(3)

    # 按题目类型分组处理
    # 单选题
    for qid, answer in ANSWERS.items():
        print(f"处理题目: {qid}")

        # 单选题: 用 addChoice
        if len(answer) == 1:
            js = f"""
            var span = document.querySelector(
                'span.num_option[data="{answer}"]'
            );
            if (span) {{
                addChoice(span.closest('div.answerBg.workTextWrap'));
            }}
            """
        # 多选题: 直接操纵 DOM
        else:
            js = f"""
            var letters = "{answer}".split("");
            // 先清除同组
            for (var el of document.querySelectorAll('span.num_option_dx')) {{
                el.classList.remove('check_answer');
            }}
            for (var l of letters) {{
                var span = document.querySelector('span.num_option_dx[data="' + l + '"]');
                if (span) {{
                    span.classList.add('check_answer');
                    span.closest('div.answerBg').setAttribute('aria-checked', 'true');
                }}
            }}
            var content = "";
            document.querySelectorAll('span.num_option_dx.check_answer').forEach(function(el) {{
                content += el.getAttribute('data');
            }});
            """

        driver.execute_script(js)
        time.sleep(0.5)

    print("答题完成")

    # 点击保存
    try:
        driver.execute_script(
            "document.querySelector('input[value=\"暂时保存\"]').click()"
        )
        print("已保存")
    except Exception:
        print("保存按钮未找到")


def main():
    driver = setup_driver()
    try:
        login(driver)
        driver.get(TASK_URL)
        do_work(driver)
        time.sleep(10)
    except Exception as e:
        print(f"错误: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
