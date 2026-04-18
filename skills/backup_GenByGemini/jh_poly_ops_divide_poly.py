# skills/jh_poly_ops_divide_poly.py
import random

def generate(level=1):
    """
    生成一道「多項式除法」的題目。
    """
    # 構造 A = BQ + R，確保可以整除，R=0
    # B: x+b
    b = random.randint(-5, 5)
    while b == 0: b = random.randint(-5, 5)
    B_str = f"(x {'+' if b > 0 else '-'} {abs(b)})"
    # Q: x+q
    q = random.randint(-5, 5)
    while q == 0: q = random.randint(-5, 5)
    Q_str = f"(x {'+' if q > 0 else '-'} {abs(q)})"
    
    # A = (x+b)(x+q) = x^2 + (b+q)x + bq
    A_c1 = b + q
    A_c0 = b * q
    A_str = f"x² {'+' if A_c1 > 0 else '-'} {abs(A_c1)}x {'+' if A_c0 > 0 else '-'} {abs(A_c0)}"

    # 隨機問商式或餘式
    q_type = random.choice(['quotient', 'remainder'])
    if q_type == 'quotient':
        question_text = f"請問 ({A_str}) ÷ ({B_str}) 的商式是多少？"
        correct_answer = Q_str.replace("(", "").replace(")", "")
    else: # remainder
        # 加上餘式
        r = random.randint(-9, 9)
        A_c0_new = A_c0 + r
        A_str_new = f"x² {'+' if A_c1 > 0 else '-'} {abs(A_c1)}x {'+' if A_c0_new > 0 else '-'} {abs(A_c0_new)}"
        question_text = f"請問 ({A_str_new}) ÷ ({B_str}) 的餘式是多少？"
        correct_answer = str(r)

    context_string = "使用長除法或綜合除法來計算多項式除法。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。參考答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}