# skills/jh_inequality_def_symbols.py
import random

def generate(level=1):
    """
    生成一道「不等式與符號定義」的題目。
    """
    scenarios = [
        ("x 大於 5", "x > 5"),
        ("y 小於 -3", "y < -3"),
        ("a 不小於 10 (大於或等於)", "a >= 10"),
        ("b 不大於 0 (小於或等於)", "b <= 0"),
        ("c 超過 100", "c > 100"),
        ("d 未滿 18", "d < 18"),
        ("身高 h 至少 150 公分", "h >= 150"),
        ("體重 w 至多 60 公斤", "w <= 60"),
    ]

    description, inequality = random.choice(scenarios)

    question_text = f"請將下列描述改寫成數學上的不等式：\n\n「{description}」"
    correct_answer = inequality

    context_string = "學習將文字描述轉換為數學不等式符號（>、<、>=、<=）。"

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

    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}