import random

def generate(level=1):
    """
    生成一道「圓的標準式」的題目。
    level 1: 圓心在原點。
    level 2: 圓心不在原點。
    """
    r = random.randint(2, 10)
    r_sq = r**2

    if level == 1:
        h, k = 0, 0
        question_text = f"一個以原點 (0, 0) 為圓心，半徑為 {r} 的圓，其方程式為何？"
        correct_answer = f"x² + y² = {r_sq}"
    else: # level 2
        h = random.randint(-9, 9)
        k = random.randint(-9, 9)
        while h == 0 and k == 0: h, k = random.randint(-9, 9), random.randint(-9, 9)
        
        question_text = f"一個以 ({h}, {k}) 為圓心，半徑為 {r} 的圓，其方程式為何？"
        h_part = f"(x - {h})²" if h > 0 else f"(x + {abs(h)})²" if h < 0 else "x²"
        k_part = f"(y - {k})²" if k > 0 else f"(y + {abs(k)})²" if k < 0 else "y²"
        correct_answer = f"{h_part} + {k_part} = {r_sq}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("^2", "²")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}