# skills/jh_algebra_distributive_law_simplify.py
import random

def generate(level=1):
    """
    生成一道「使用分配律化簡代數式」的題目。
    例如：a(bx + c)
    """
    a = random.randint(-5, 5)
    while a == 0 or a == 1:
        a = random.randint(-5, 5)

    b = random.randint(-5, 5)
    while b == 0:
        b = random.randint(-5, 5)

    c = random.randint(-5, 5)
    while c == 0:
        c = random.randint(-5, 5)

    expr = f"{a}({b}x {'+' if c > 0 else '-'} {abs(c)})"
    question_text = f"請使用分配律化簡下列式子：{expr}"

    # 計算答案
    final_coeff = a * b
    final_const = a * c

    correct_answer = f"{final_coeff}x{'+' if final_const > 0 else ''}{final_const}"
    if final_const == 0:
        correct_answer = f"{final_coeff}x"

    context_string = f"化簡 {expr}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}