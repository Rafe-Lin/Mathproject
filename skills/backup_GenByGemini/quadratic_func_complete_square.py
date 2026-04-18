import random

def generate(level=1):
    """
    生成一道「二次函數配方法」的題目。
    level 1: x² 項係數為 1。
    level 2: x² 項係數不為 1。
    """
    if level == 1:
        a = 1
    else: # level 2
        a = random.choice([-3, -2, 2, 3, 4])

    # 從頂點式 y = a(x-h)² + k 反推
    h = random.randint(-5, 5)
    k = random.randint(-10, 10)
    
    # y = a(x² - 2hx + h²) + k = ax² - 2ahx + ah² + k
    b = -2 * a * h
    c = a * h**2 + k
    
    a_str = "" if a == 1 else "- " if a == -1 else f"{a}"
    b_str = "" if b == 0 else f" + {b}x" if b > 0 else f" - {abs(b)}x"
    c_str = "" if c == 0 else f" + {c}" if c > 0 else f" - {abs(c)}"
    
    question_text = f"請利用配方法，將二次函數 y = {a_str}x²{b_str}{c_str} 化為頂點式 y = a(x-h)² + k。"
    
    h_part = f"(x - {h})²" if h > 0 else f"(x + {abs(h)})²" if h < 0 else "x²"
    k_part = f" + {k}" if k > 0 else f" - {abs(k)}" if k < 0 else ""
    a_part = str(a) if a != 1 else ""
    correct_answer = f"y = {a_part}{h_part}{k_part}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("^2","²")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}