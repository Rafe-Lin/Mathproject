# skills/jh_equation_quad_solve_complete_square.py
import random

def generate(level=1):
    """
    生成一道「配方法解一元二次方程式」的題目。
    """
    # 構造 (x+p)^2 = q 的形式，確保 q 是正數
    p = random.randint(-5, 5)
    q_sqrt = random.randint(1, 6)
    q = q_sqrt**2

    # 展開 x^2 + 2px + p^2 = q  => x^2 + 2px + (p^2-q) = 0
    a = 1
    b = 2 * p
    c = p**2 - q

    equation_str = f"x² {'+' if b > 0 else '-'} {abs(b)}x {'+' if c >= 0 else '-'} {abs(c)} = 0"

    question_text = f"請用「配方法」解一元二次方程式：\n{equation_str}\n若有兩解，請用逗號分隔 (例如: 3,-5)"
    
    # 解為 x = -p ± sqrt(q)
    sol1 = -p + q_sqrt
    sol2 = -p - q_sqrt
    correct_answer = f"{sol1},{sol2}"

    context_string = "利用配方法將方程式整理成 (x+p)² = q 的形式再求解。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    try:
        user_sols = sorted(map(int, user_answer.strip().replace(" ", "").split(',')))
        correct_sols = sorted(map(int, correct_answer.strip().split(',')))
        is_correct = user_sols == correct_sols
        result_text = f"完全正確！解為 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    except ValueError:
        is_correct = False
        result_text = f"請用逗號分隔兩個解，例如 3,-5。正確答案是：{correct_answer}"

    return {"correct": is_correct, "result": result_text, "next_question": is_correct}