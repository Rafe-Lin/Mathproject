import random

def generate(level=1):
    """
    生成一道「合成函數」的題目。
    """
    a, b = random.randint(1, 5), random.randint(1, 5)
    c, d = random.randint(1, 5), random.randint(1, 5)
    x_val = random.randint(1, 5)
    
    f_str = f"{a}x + {b}"
    g_str = f"x²" if level == 1 else f"{c}x - {d}"
    
    question_text = f"已知 f(x) = {f_str}，g(x) = {g_str}，請求出 g(f({x_val})) 的值。"
    
    f_val = a * x_val + b
    if level == 1:
        g_f_val = f_val ** 2
    else:
        g_f_val = c * f_val - d
    correct_answer = str(g_f_val)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}