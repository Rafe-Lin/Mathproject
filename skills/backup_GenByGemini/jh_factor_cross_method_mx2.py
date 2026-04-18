# skills/jh_factor_cross_method_mx2.py
import random

def generate(level=1):
    """
    生成一道「十字交乘法 (首項係數不為1)」的題目。
    """
    # 構造 (ax+b)(cx+d)
    a = random.randint(2, 3)
    c = random.randint(1, 2)
    b = random.randint(-5, 5)
    while b == 0: b = random.randint(-5, 5)
    d = random.randint(-5, 5)
    while d == 0: d = random.randint(-5, 5)

    # 展開: acx^2 + (ad+bc)x + bd
    A = a * c
    B = a * d + b * c
    C = b * d

    poly_str = f"{A}x² {'+' if B > 0 else '-'} {abs(B)}x {'+' if C > 0 else '-'} {abs(C)}"
    question_text = f"請使用十字交乘法因式分解：{poly_str}"

    # 答案可以交換順序
    ans1 = f"({a}x{'+' if b>0 else ''}{b})({c}x{'+' if d>0 else ''}{d})"
    ans2 = f"({c}x{'+' if d>0 else ''}{d})({a}x{'+' if b>0 else ''}{b})"
    correct_answer = ans1 # 以其中一個為標準答案

    context_string = "利用十字交乘法將二次三項式分解為兩個一次式的乘積。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("*", "")
    # 簡化檢查，未來可引入符號運算庫
    is_correct = user == correct_answer.replace(" ", "").replace("*", "") or user == f"({correct_answer.split(')(')[1]})({correct_answer.split(')(')[0]})".replace(" ", "").replace("*", "")
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。參考答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}