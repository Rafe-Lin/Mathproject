# skills/jh_factor_diff_of_squares.py
import random

def generate(level=1):
    """
    生成一道「平方差公式因式分解」的題目。
    """
    # 構造 a^2 - b^2
    # a 可以是 nx 或 ny
    a_coeff = random.randint(1, 5)
    a_var = random.choice(['x', 'y'])
    a_term_val = f"{a_coeff}{a_var}"
    if a_coeff == 1: a_term_val = a_var
    
    # b 是常數
    b_term_val = random.randint(1, 9)

    # 展開
    expanded_poly = f"{(a_coeff**2)}{a_var}^2 - {b_term_val**2}"
    question_text = f"請對多項式 {expanded_poly} 進行因式分解。"

    correct_answer = f"({a_term_val}+{b_term_val})({a_term_val}-{b_term_val})"

    context_string = "利用平方差公式 a² - b² = (a+b)(a-b) 進行因式分解。"

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