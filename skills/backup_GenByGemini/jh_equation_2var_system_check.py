# skills/jh_equation_2var_system_check.py
import random

def generate(level=1):
    """
    生成一道「檢驗二元一次聯立方程式的解」的題目。
    """
    # 生成一組真實解
    x_sol = random.randint(-5, 5)
    y_sol = random.randint(-5, 5)

    # 構造方程式
    a1, b1 = random.randint(1, 3), random.randint(1, 3)
    c1 = a1 * x_sol + b1 * y_sol
    a2, b2 = random.randint(1, 3), random.randint(1, 3)
    while a1 * b2 == a2 * b1: # 避免無限多解或無解
        a2, b2 = random.randint(1, 3), random.randint(1, 3)
    c2 = a2 * x_sol + b2 * y_sol

    # 隨機決定要檢驗的解是否正確
    is_solution = random.choice([True, False])
    if is_solution:
        x_check, y_check = x_sol, y_sol
        correct_answer = "是"
    else:
        # 生成一組錯誤的解
        x_check = x_sol + random.choice([-1, 1])
        y_check = y_sol + random.choice([-1, 1])
        correct_answer = "否"

    eq1_str = f"{a1}x + {b1}y = {c1}"
    eq2_str = f"{a2}x + {b2}y = {c2}"
    question_text = f"請問 x={x_check}, y={y_check} 是不是聯立方程式 \n(1) {eq1_str}\n(2) {eq2_str}\n 的一組解？ (請回答 '是' 或 '否')"

    context_string = f"將 x={x_check}, y={y_check} 同時代入兩個方程式，檢查等號是否都成立。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip()
    correct = str(correct_answer).strip()
    if user in ["是", "Y", "y"] and correct == "是": is_correct = True
    elif user in ["否", "N", "n"] and correct == "否": is_correct = True
    else: is_correct = False
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}