# skills/jh_poly_ops_add_sub_simple.py
import random

def generate(level=1):
    """
    生成一道「多項式加減」的題目。
    """
    # Poly 1: a1*x^2 + b1*x + c1
    a1, b1, c1 = [random.randint(-5, 5) for _ in range(3)]
    # Poly 2: a2*x^2 + b2*x + c2
    a2, b2, c2 = [random.randint(-5, 5) for _ in range(3)]

    op = random.choice(['+', '-'])

    poly1_str = f"({a1}x² {'+' if b1 > 0 else '-'} {abs(b1)}x {'+' if c1 > 0 else '-'} {abs(c1)})"
    poly2_str = f"({a2}x² {'+' if b2 > 0 else '-'} {abs(b2)}x {'+' if c2 > 0 else '-'} {abs(c2)})"

    question_text = f"請計算 {poly1_str} {op} {poly2_str}"

    if op == '+':
        res_a, res_b, res_c = a1 + a2, b1 + b2, c1 + c2
    else:
        res_a, res_b, res_c = a1 - a2, b1 - b2, c1 - c2

    # 格式化答案
    parts = []
    if res_a != 0: parts.append(f"{res_a}x²")
    if res_b != 0: parts.append(f"{'+' if res_b > 0 else ''}{res_b}x")
    if res_c != 0: parts.append(f"{'+' if res_c > 0 else ''}{res_c}")
    correct_answer = "".join(parts).lstrip('+')
    if not correct_answer: correct_answer = "0"

    context_string = "對多項式進行加減運算時，將同類項的係數相加減。"

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