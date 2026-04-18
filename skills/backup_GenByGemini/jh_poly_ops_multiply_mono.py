# skills/jh_poly_ops_multiply_mono.py
import random

def generate(level=1):
    """
    生成一道「多項式乘以單項式」的題目。
    """
    # Monomial: ax^p
    a = random.randint(-5, 5)
    while a == 0: a = random.randint(-5, 5)
    p = random.randint(1, 2)
    mono_str = f"{a}x²" if p > 1 else f"{a}x"

    # Polynomial: bx+c
    b = random.randint(-5, 5)
    while b == 0: b = random.randint(-5, 5)
    c = random.randint(-5, 5)
    while c == 0: c = random.randint(-5, 5)
    poly_str = f"({b}x {'+' if c > 0 else '-'} {abs(c)})"

    question_text = f"請計算 {mono_str} × {poly_str}"

    # 計算答案: (ax^p)(bx+c) = abx^(p+1) + acx^p
    res_coeff1 = a * b
    res_exp1 = p + 1
    res_coeff2 = a * c
    res_exp2 = p
    
    term1 = f"{res_coeff1}x³" if res_exp1 == 3 else f"{res_coeff1}x²"
    term2 = f"{res_coeff2}x²" if res_exp2 == 2 else f"{res_coeff2}x"
    
    correct_answer = f"{term1}{'+' if res_coeff2 > 0 else ''}{term2}"


    context_string = "利用分配律，將單項式分別乘以多項式的每一項。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "").replace("²", "^2").replace("³", "^3")
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}