import random

def generate(level=1):
    """
    生成一道「複數定義與四則運算」的題目。
    """
    z1 = complex(random.randint(-5, 5), random.randint(-5, 5))
    z2 = complex(random.randint(1, 5), random.randint(1, 5))
    
    if level == 1:
        op = random.choice(['+', '-'])
        question_text = f"請計算 ({z1}) {op} ({z2}) 的值。(格式: a+bi)"
        ans = z1 + z2 if op == '+' else z1 - z2
    else: # level 2
        op = random.choice(['*', '/'])
        question_text = f"請計算 ({z1}) {op} ({z2}) 的值。(格式: a+bi, 四捨五入至小數點後一位)"
        ans = z1 * z2 if op == '*' else z1 / z2
        
    real_part = round(ans.real, 1)
    imag_part = round(ans.imag, 1)
    correct_answer = f"{real_part}{'+' if imag_part >= 0 else ''}{imag_part}i".replace("+-","-").replace("1.0i","i")
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}