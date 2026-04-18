# skills/jh_factor_square_of_sum_diff.py
import random

def generate(level=1):
    """
    生成一道「和/差的平方公式因式分解」的題目。
    """
    # 構造 (ax ± b)^2 = a^2x^2 ± 2abx + b^2
    a = random.randint(1, 4)
    b = random.randint(1, 6)
    op = random.choice(['+', '-'])

    A = a**2
    B = 2 * a * b
    C = b**2

    a_term = f"{a}x" if a > 1 else "x"

    if op == '+':
        poly_str = f"{A}x² + {B}x + {C}"
        correct_answer = f"({a_term}+{b})²"
    else:
        poly_str = f"{A}x² - {B}x + {C}"
        correct_answer = f"({a_term}-{b})²"

    question_text = f"請對多項式 {poly_str} 進行因式分解。"

    context_string = "利用和的平方 a²+2ab+b²=(a+b)² 或差的平方 a²-2ab+b²=(a-b)² 公式進行因式分解。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("*", "")
    correct = correct_answer.strip().replace(" ", "").replace("*", "").replace("²", "^2")
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。參考答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}