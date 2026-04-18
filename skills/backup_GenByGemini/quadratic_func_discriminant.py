import random

def generate(level=1):
    """
    生成一道「二次函數判別式」的題目。
    判斷 y = ax²+bx+c 的圖形與 x 軸的交點個數。
    level 1: 給一般式。
    level 2: 給頂點式 (需轉換)。
    """
    a = random.randint(1, 3) * random.choice([1, -1])
    h = random.randint(-5, 5)
    
    # 隨機決定交點個數
    num_intersections = random.choice([0, 1, 2])
    
    if num_intersections == 2: # D > 0, a*k < 0
        k = random.randint(1, 5) * (-1 if a > 0 else 1)
        correct_answer = "2"
    elif num_intersections == 1: # D = 0, k = 0
        k = 0
        correct_answer = "1"
    else: # D < 0, a*k > 0
        k = random.randint(1, 5) * (1 if a > 0 else -1)
        correct_answer = "0"

    b = -2 * a * h
    c = a * h**2 + k

    a_str = "" if a == 1 else "- " if a == -1 else f"{a}"
    b_str = "" if b == 0 else f" + {b}x" if b > 0 else f" - {abs(b)}x"
    c_str = "" if c == 0 else f" + {c}" if c > 0 else f" - {abs(c)}"
    func_str = f"y = {a_str}x²{b_str}{c_str}"

    question_text = f"請問二次函數 {func_str} 的圖形與 x 軸有幾個交點？"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}