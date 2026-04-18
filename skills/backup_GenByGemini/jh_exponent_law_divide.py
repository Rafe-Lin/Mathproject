# skills/jh_exponent_law_divide.py
import random

def generate(level=1):
    """
    生成一道「指數律：同底數冪相除」的題目。
    a^m / a^n = a^(m-n)
    """
    base = random.randint(2, 5)
    exp1 = random.randint(5, 10)
    exp2 = random.randint(2, exp1 - 1)

    final_exp = exp1 - exp2
    
    # 題目以分數形式呈現
    question_text = f"請求出 $\\frac{{{base}^{{{exp1}}}}}{{{base}^{{{exp2}}}}}$ 的值。（請以指數形式作答，例如 a^b）"

    correct_answer = f"{base}^{final_exp}"

    context_string = f"使用指數律 a^m / a^n = a^(m-n) 計算"

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

    # 允許多種寫法
    if user.replace("**", "^") == correct.replace("**", "^"):
        is_correct = True
        result_text = f"完全正確！答案是 {correct}。"
    else:
        is_correct = False
        result_text = f"答案不正確。正確答案是：{correct}"

    return {
        "correct": is_correct,
        "result": result_text,
        "next_question": True
    }