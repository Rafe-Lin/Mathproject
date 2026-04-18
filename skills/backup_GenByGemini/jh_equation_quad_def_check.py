# skills/jh_equation_quad_def_check.py
import random

def generate(level=1):
    """
    生成一道「檢驗二次方程式的解」的題目。
    """
    # 構造一組整數解
    r1 = random.randint(-4, 4)
    r2 = random.randint(-3, 3)
    while r1 == r2:
        r2 = random.randint(-3, 3)

    # (x - r1)(x - r2) = 0 => x^2 - (r1+r2)x + r1*r2 = 0
    a = 1
    b = -(r1 + r2)
    c = r1 * r2

    # 隨機決定要檢查的值是否為解
    is_solution = random.choice([True, False])
    if is_solution:
        check_val = r1
        correct_answer = "是"
    else:
        check_val = r1 + random.choice([-1, 1])
        correct_answer = "否"

    equation_str = f"x² {'+' if b > 0 else '-'} {abs(b)}x {'+' if c > 0 else '-'} {abs(c)} = 0"
    if b == 0: equation_str = f"x² {'+' if c > 0 else '-'} {abs(c)} = 0"

    question_text = f"請問 x = {check_val} 是不是一元二次方程式 {equation_str} 的一個解？ (請回答 '是' 或 '否')"

    context_string = f"將 x = {check_val} 代入方程式，檢查等號是否成立。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = str(correct_answer).strip()
    if user in ["是", "Y", "y"] and correct == "是": is_correct = True
    elif user in ["否", "N", "n"] and correct == "否": is_correct = True
    else: is_correct = False
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}