# skills/jh_poly_division_relation.py
import random

def generate(level=1):
    """
    生成一道「多項式除法關係式」的題目。
    """
    # 構造 A = BQ + R
    # B: x+b
    b = random.randint(-5, 5)
    B_str = f"(x {'+' if b > 0 else '-'} {abs(b)})"
    # Q: x+q
    q = random.randint(-5, 5)
    Q_str = f"(x {'+' if q > 0 else '-'} {abs(q)})"
    # R: r
    r = random.randint(-9, 9)

    # A = (x+b)(x+q) + r = x^2 + (b+q)x + bq + r
    A_c2 = 1
    A_c1 = b + q
    A_c0 = b * q + r
    A_str = f"x² {'+' if A_c1 > 0 else '-'} {abs(A_c1)}x {'+' if A_c0 > 0 else '-'} {abs(A_c0)}"

    q_type = random.choice(['find_A', 'find_R'])
    if q_type == 'find_A':
        question_text = f"已知多項式 A 除以 {B_str}，得到商式為 {Q_str}，餘式為 {r}。請問多項式 A 是什麼？"
        correct_answer = A_str.replace(" ", "").replace("²", "^2")
    else: # find_R
        question_text = f"已知多項式 {A_str} 除以 {B_str}，得到商式為 {Q_str}。請問餘式是多少？"
        correct_answer = str(r)

    context_string = "利用多項式除法關係式：被除式 = 除式 × 商式 + 餘式。"

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
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。參考答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}