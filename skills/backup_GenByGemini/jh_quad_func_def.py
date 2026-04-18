# skills/jh_quad_func_def.py
import random

def generate(level=1):
    """
    生成一道「二次函數定義」的題目。
    """
    is_quadratic = random.choice([True, False])
    
    if is_quadratic:
        a = random.randint(-5, 5)
        while a == 0: a = random.randint(-5, 5)
        b = random.randint(-5, 5)
        c = random.randint(-10, 10)
        equation = f"y = {a}x² {'+' if b >= 0 else '-'} {abs(b)}x {'+' if c >= 0 else '-'} {abs(c)}"
        correct_answer = "是"
    else:
        # 構造非二次函數
        eq_type = random.choice(['linear', 'cubic', 'constant'])
        if eq_type == 'linear':
            m = random.randint(1, 5)
            c = random.randint(1, 5)
            equation = f"y = {m}x + {c}"
        elif eq_type == 'cubic':
            a = random.randint(1, 3)
            equation = f"y = {a}x³"
        else: # constant
            c = random.randint(1, 10)
            equation = f"y = {c}"
        correct_answer = "否"

    question_text = f"請問下列關係式中，y 是不是 x 的二次函數？\n\n{equation}\n\n(請回答 '是' 或 '否')"
    context_string = "二次函數是指可以寫成 y = ax² + bx + c (其中 a≠0) 形式的函數。"

    return { "question_text": question_text, "answer": correct_answer, "correct_answer": "text", "context_string": context_string }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = str(correct_answer).strip()
    if user in ["是", "Y", "y"] and correct == "是": is_correct = True
    elif user in ["否", "N", "n"] and correct == "否": is_correct = True
    else: is_correct = False
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}