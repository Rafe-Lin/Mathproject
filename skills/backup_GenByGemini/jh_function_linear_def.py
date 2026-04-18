# skills/jh_function_linear_def.py
import random

def generate(level=1):
    """
    生成一道「一次函數定義」的題目。
    """
    # 隨機生成一個一次函數或非一次函數
    is_linear = random.choice([True, False])
    
    if is_linear:
        m = random.randint(-5, 5)
        while m == 0: m = random.randint(-5, 5)
        b = random.randint(-10, 10)
        equation = f"y = {m}x {'+' if b >= 0 else '-'} {abs(b)}"
        correct_answer = "是"
    else:
        # 構造非一次函數
        eq_type = random.choice(['quadratic', 'constant', 'inverse'])
        if eq_type == 'quadratic':
            a = random.randint(2, 5)
            equation = f"y = {a}x²"
        elif eq_type == 'constant':
            c = random.randint(1, 10)
            equation = f"y = {c}" # 常數函數
        else: # inverse
            k = random.randint(1, 10)
            equation = f"xy = {k}" # 反比關係
        correct_answer = "否"

    question_text = f"請問下列關係式是不是一個一次函數？\n\n{equation}\n\n(請回答 '是' 或 '否')"

    context_string = "一次函數是指可以寫成 y = ax + b (其中 a≠0) 形式的函數。"

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