# skills/jh_function_linear_find_eq.py
import random

def generate(level=1):
    """
    生成一道「求一次函數」的題目。
    """
    # 構造 y = mx + b
    m = random.randint(-3, 3)
    while m == 0: m = random.randint(-3, 3)
    b = random.randint(-5, 5)

    # 找線上兩個點
    x1 = random.randint(-2, 2)
    y1 = m * x1 + b
    
    x2 = x1 + random.randint(1, 3)
    y2 = m * x2 + b

    question_text = f"已知一個一次函數的圖形通過點 ({x1}, {y1}) 和 ({x2}, {y2})，請求出此函數。\n(請以 y=ax+b 的格式作答)"
    
    correct_answer = f"y={m}x{'+' if b > 0 else ''}{b}"
    if b == 0: correct_answer = f"y={m}x"
    if m == 1: correct_answer = correct_answer.replace('1x', 'x')
    if m == -1: correct_answer = correct_answer.replace('-1x', '-x')

    context_string = "將兩點代入 y=ax+b，解出 a 和 b，即可得到函數。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。參考答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}