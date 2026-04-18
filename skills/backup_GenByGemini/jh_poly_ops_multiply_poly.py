# skills/jh_poly_ops_multiply_poly.py
import random

def generate(level=1):
    """
    生成一道「多項式乘以多項式」的題目。
    """
    # (ax+b)(cx+d)
    a = random.randint(1, 3)
    b = random.randint(-5, 5)
    c = random.randint(1, 3)
    d = random.randint(-5, 5)

    poly1_str = f"({a}x {'+' if b > 0 else '-'} {abs(b)})"
    poly2_str = f"({c}x {'+' if d > 0 else '-'} {abs(d)})"

    question_text = f"請計算 {poly1_str} × {poly2_str}"

    # 計算答案: acx^2 + (ad+bc)x + bd
    res_a = a * c
    res_b = a * d + b * c
    res_c = b * d

    parts = []
    if res_a != 0: parts.append(f"{res_a}x²")
    if res_b != 0: parts.append(f"{'+' if res_b > 0 else ''}{res_b}x")
    if res_c != 0: parts.append(f"{'+' if res_c > 0 else ''}{res_c}")
    correct_answer = "".join(parts).lstrip('+')

    context_string = "使用分配律，將第一個多項式的每一項，分別乘以第二個多項式的每一項，再合併同類項。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "").replace("²", "^2")
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}