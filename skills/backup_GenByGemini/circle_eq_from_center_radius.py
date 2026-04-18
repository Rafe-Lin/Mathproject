import random

def generate(level=1):
    """
    生成一道「從圓心和半徑求圓方程式」的題目。
    level 1: 圓心、半徑為整數。
    level 2: 圓心、半徑為整數，但數字較大。
    """
    if level == 1:
        h, k = random.randint(-5, 5), random.randint(-5, 5)
        r = random.randint(2, 6)
    else: # level 2
        h, k = random.randint(-15, 15), random.randint(-15, 15)
        r = random.randint(7, 15)

    r_sq = r**2
    question_text = f"已知一圓的圓心為 ({h}, {k})，半徑為 {r}，請求出此圓的標準式。"
    
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