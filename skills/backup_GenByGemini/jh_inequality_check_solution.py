# skills/jh_inequality_check_solution.py
import random

def generate(level=1):
    """
    生成一道「檢驗一元一次不等式的解」的題目。
    """
    a = random.randint(1, 5)
    b = random.randint(-10, 10)
    op = random.choice(['>', '<', '>=', '<='])
    
    # 構造一個邊界值
    boundary = random.randint(-5, 5)
    c = a * boundary + b
    
    # 選擇一個要檢查的值
    check_val = boundary + random.choice([-2, -1, 1, 2])
    
    inequality_str = f"{a}x + {b} {op} {c}"
    
    # 判斷 check_val 是否為解
    is_solution = False
    expr_val = a * check_val + b
    if op == '>' and expr_val > c: is_solution = True
    elif op == '<' and expr_val < c: is_solution = True
    elif op == '>=' and expr_val >= c: is_solution = True
    elif op == '<=' and expr_val <= c: is_solution = True
        
    correct_answer = "是" if is_solution else "否"

    question_text = f"請問 x = {check_val} 是不是不等式 {inequality_str} 的一個解？ (請回答 '是' 或 '否')"

    context_string = f"將 x = {check_val} 代入不等式 {inequality_str}，檢查不等式是否成立。"

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