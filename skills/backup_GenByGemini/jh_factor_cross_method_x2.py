# skills/jh_factor_cross_method_x2.py
import random

def generate(level=1):
    """
    生成一道「十字交乘法 (首項係數為1)」的題目。
    """
    # 構造 (x+a)(x+b)
    a = random.randint(-7, 7)
    while a == 0: a = random.randint(-7, 7)
    b = random.randint(-7, 7)
    while b == 0 or a == b: b = random.randint(-7, 7)

    # 展開: x^2 + (a+b)x + ab
    B = a + b
    C = a * b

    poly_str = f"x² {'+' if B > 0 else '-'} {abs(B)}x {'+' if C > 0 else '-'} {abs(C)}"
    question_text = f"請使用十字交乘法因式分解：{poly_str}"

    # 答案可以交換順序
    ans1 = f"(x{'+' if a>0 else ''}{a})(x{'+' if b>0 else ''}{b})"
    ans2 = f"(x{'+' if b>0 else ''}{b})(x{'+' if a>0 else ''}{a})"
    correct_answer = ans1 # 以其中一個為標準答案

    context_string = "找出兩個數，其和為一次項係數，其積為常數項。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("*", "")
    is_correct = user == correct_answer.replace(" ", "").replace("*", "") or user == f"({correct_answer.split(')(')[1]})({correct_answer.split(')(')[0]})".replace(" ", "").replace("*", "")
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。參考答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}