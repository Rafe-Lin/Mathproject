# skills/jh_exponent_law_power_of_product.py
import random

def generate(level=1):
    """
    生成一道「指數律：積的次方」的題目。
    (ab)^n = a^n * b^n
    """
    base1 = random.randint(2, 5)
    base2 = random.randint(base1 + 1, 7) # 確保底數不同
    exp = random.randint(2, 4)

    question_text = f"請求出 $({base1} \\times {base2})^{{{exp}}}$ 的值。（請以 a^n * b^n 的形式作答）"

    correct_answer = f"{base1}^{exp}*{base2}^{exp}"

    context_string = f"使用指數律 (ab)^n = a^n * b^n 計算"

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
    user = user_answer.strip().replace(" ", "").replace("x", "*")
    correct = str(correct_answer).strip().replace(" ", "")

    # 考慮順序交換
    parts_user = sorted(user.split('*'))
    parts_correct = sorted(correct.split('*'))

    if parts_user == parts_correct:
        is_correct = True
        result_text = f"完全正確！答案是 {correct_answer}。"
    else:
        is_correct = False
        result_text = f"答案不正確。正確答案是：{correct_answer}"

    return {
        "correct": is_correct,
        "result": result_text,
        "next_question": True
    }