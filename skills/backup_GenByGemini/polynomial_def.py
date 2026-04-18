# skills/polynomial_def.py
import random
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「多項式的基本概念」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 生成一個 2 到 4 次的多項式
    degree = random.randint(2, 4)
    coeffs = [random.randint(-7, 7) for _ in range(degree + 1)]
    while coeffs[0] == 0: coeffs[0] = random.randint(1, 7) # 確保最高次項係數不為0

    poly_str = poly_to_string(coeffs)
    
    q_type = random.choice(['degree', 'coeff', 'const'])

    if q_type == 'degree':
        question_text = f"請問多項式 f(x) = {poly_str} 的次數是多少？"
        correct_answer = str(degree)
    elif q_type == 'coeff':
        # 隨機選一個存在的項來問係數
        target_power = random.randint(1, degree)
        while coeffs[degree - target_power] == 0:
            target_power = random.randint(1, degree)
        
        power_str = "x" if target_power == 1 else f"x{ {2:'²', 3:'³', 4:'⁴'}.get(target_power, f'^{target_power}') }"
        question_text = f"請問多項式 f(x) = {poly_str} 中，{power_str} 項的係數是多少？"
        correct_answer = str(coeffs[degree - target_power])
    else: # 'const'
        question_text = f"請問多項式 f(x) = {poly_str} 的常數項是多少？"
        correct_answer = str(coeffs[-1])

    context_string = f"關於多項式 f(x) = {poly_str} 的基本概念"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """檢查使用者輸入的答案是否正確"""
    user = user_answer.strip()
    correct = correct_answer.strip()
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}