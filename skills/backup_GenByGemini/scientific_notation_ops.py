import random

def to_sci_notation(n):
    """將數字轉換為科學記號字串"""
    if n == 0: return "0"
    exponent = 0
    mantissa = float(n)
    while abs(mantissa) >= 10.0:
        mantissa /= 10.0
        exponent += 1
    while abs(mantissa) < 1.0:
        mantissa *= 10.0
        exponent -= 1
    return f"{mantissa:.1f} x 10^{exponent}"

def generate(level=1):
    """
    生成一道「科學記號的四則運算」題目。
    level 1: 乘法或除法。
    level 2: 加法或減法 (需要對齊指數)。
    """
    a = random.randint(1, 9) * 10**random.randint(3, 5)
    b = random.randint(1, 9) * 10**random.randint(2, 4)
    
    a_sci = to_sci_notation(a)
    b_sci = to_sci_notation(b)

    if level == 1:
        op = random.choice(['*', '/'])
        question_text = f"請計算 ({a_sci}) {op} ({b_sci})，並以科學記號表示。"
        ans = a * b if op == '*' else a / b
    else: # level 2
        op = random.choice(['+', '-'])
        question_text = f"請計算 ({a_sci}) {op} ({b_sci})，並以科學記號表示。"
        ans = a + b if op == '+' else a - b

    correct_answer = to_sci_notation(ans)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").lower()
    correct = str(correct_answer).strip().replace(" ", "").lower()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}