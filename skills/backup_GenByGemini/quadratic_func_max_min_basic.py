import random

def generate(level=1):
    """
    生成一道「二次函數最大最小值(無範圍限制)」的題目。
    level 1: 給頂點式。
    level 2: 給一般式。
    """
    a = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    h = random.randint(-5, 5)
    k = random.randint(-10, 10)
    
    extreme_type = "最大值" if a < 0 else "最小值"

    if level == 1:
        h_part = f"(x - {h})²" if h > 0 else f"(x + {abs(h)})²" if h < 0 else "x²"
        k_part = f" + {k}" if k > 0 else f" - {abs(k)}" if k < 0 else ""
        a_part = str(a) if a != 1 else ""
        func_str = f"y = {a_part}{h_part}{k_part}"
    else: # level 2
        b = -2 * a * h
        c = a * h**2 + k
        a_str = "" if a == 1 else "- " if a == -1 else f"{a}"
        b_str = "" if b == 0 else f" + {b}x" if b > 0 else f" - {abs(b)}x"
        c_str = "" if c == 0 else f" + {c}" if c > 0 else f" - {abs(c)}"
        func_str = f"y = {a_str}x²{b_str}{c_str}"

    question_text = f"請求出二次函數 {func_str} 的{extreme_type}。"
    correct_answer = str(k)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}