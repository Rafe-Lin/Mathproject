# skills/jh_equation_2var_word_problem_setup.py
import random

def generate(level=1):
    """
    生成一道「二元一次應用問題列式」的題目。
    """
    scenarios = [
        ("雞兔同籠，頭共 35 個，腳共 94 隻。假設雞有 x 隻，兔子有 y 隻，請依題意列出二元一次聯立方程式。", "x+y=35;2x+4y=94"),
        ("5 個蘋果和 3 個橘子共 150 元，3 個蘋果和 5 個橘子共 130 元。假設蘋果一個 x 元，橘子一個 y 元，請列出聯立方程式。", "5x+3y=150;3x+5y=130"),
        ("全票一張 100 元，半票一張 50 元。小明共買了 10 張票，花了 800 元。假設全票買了 x 張，半票買了 y 張，請列出聯立方程式。", "x+y=10;100x+50y=800"),
    ]

    question, answer = random.choice(scenarios)

    question_text = f"請依據以下情境列出二元一次聯立方程式（不需計算，兩式用分號 ; 隔開）：\n\n{question}"
    correct_answer = answer

    context_string = "學習將應用問題的兩個條件，分別轉化為兩個二元一次方程式。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")

    # 為了處理順序問題，將方程式拆開並排序
    user_parts = sorted(user.split(';'))
    correct_parts = sorted(correct.split(';'))

    if user_parts == correct_parts:
        is_correct = True
        result_text = f"完全正確！列式為 {correct_answer.replace(';', ' 和 ')}。"
    else:
        is_correct = False
        result_text = f"列式不正確。參考答案為：{correct_answer.replace(';', ' 和 ')}"

    return {
        "correct": is_correct,
        "result": result_text,
        "next_question": True
    }