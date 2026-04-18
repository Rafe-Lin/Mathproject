# skills/jh_poly_def_terms_degree.py
import random

def generate(level=1):
    """
    生成一道「多項式項、係數、次數」的題目。
    """
    c3 = random.randint(-5, 5)
    c2 = random.randint(-5, 5)
    c1 = random.randint(-5, 5)
    c0 = random.randint(-5, 5)
    
    # 確保最高次項存在
    while c3 == 0: c3 = random.randint(-5, 5)

    poly_str = f"{c3}x³"
    if c2 != 0: poly_str += f" {'+' if c2 > 0 else '-'} {abs(c2)}x²"
    if c1 != 0: poly_str += f" {'+' if c1 > 0 else '-'} {abs(c1)}x"
    if c0 != 0: poly_str += f" {'+' if c0 > 0 else '-'} {abs(c0)}"

    q_type = random.choice(['degree', 'term_coeff', 'const_term'])

    if q_type == 'degree':
        question_text = f"請問多項式 {poly_str} 的次數是多少？"
        correct_answer = "3"
    elif q_type == 'term_coeff':
        q_deg = random.randint(1, 3)
        question_text = f"請問多項式 {poly_str} 的 {q_deg} 次項係數是多少？"
        coeffs = {3: c3, 2: c2, 1: c1}
        correct_answer = str(coeffs[q_deg])
    else: # const_term
        question_text = f"請問多項式 {poly_str} 的常數項是多少？"
        correct_answer = str(c0)

    context_string = "學習辨識多項式的次數、各項係數與常數項。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = correct_answer.strip().replace("²", "^2").replace("³", "^3")
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}