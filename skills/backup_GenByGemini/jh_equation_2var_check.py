# skills/jh_equation_2var_check.py
import random

def generate(level=1):
    """
    生成一道「檢驗二元一次方程式的解」的題目。
    """
    a = random.randint(1, 4)
    b = random.randint(1, 4)
    
    # 隨機決定這組解是否正確
    is_solution = random.choice([True, False])
    
    x_sol = random.randint(-3, 3)
    y_sol = random.randint(-3, 3)
    
    c = a * x_sol + b * y_sol
    
    if is_solution:
        x_check, y_check = x_sol, y_sol
        correct_answer = "是"
    else:
        # 生成一組錯誤的解
        x_check = x_sol + random.choice([-1, 1, 2])
        y_check = y_sol + random.choice([-1, 1, 2])
        while a * x_check + b * y_check == c: # 避免剛好又對了
            x_check = x_sol + random.choice([-1, 1, 2])
        correct_answer = "否"

    equation_str = f"{a}x + {b}y = {c}"
    question_text = f"請問 x={x_check}, y={y_check} 是不是二元一次方程式 {equation_str} 的一組解？ (請回答 '是' 或 '否')"

    context_string = f"將 x={x_check}, y={y_check} 代入方程式 {equation_str}，檢查等號是否成立。"

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