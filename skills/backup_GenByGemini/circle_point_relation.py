import random

def generate(level=1):
    """
    生成一道「判斷點與圓的關係」的題目。
    level 1: 圓心在原點。
    level 2: 圓心不在原點。
    """
    r = random.randint(3, 8)
    if level == 1:
        h, k = 0, 0
        circle_eq = f"x² + y² = {r**2}"
    else: # level 2
        h, k = random.randint(-5, 5), random.randint(-5, 5)
        h_part = f"(x - {h})²" if h > 0 else f"(x + {abs(h)})²"
        k_part = f"(y - {k})²" if k > 0 else f"(y + {abs(k)})²"
        circle_eq = f"{h_part} + {k_part} = {r**2}"

    # 隨機生成一個點
    px, py = random.randint(h-r-2, h+r+2), random.randint(k-r-2, k+r+2)
    
    dist_sq = (px - h)**2 + (py - k)**2
    
    if dist_sq > r**2:
        correct_answer = "圓外"
    elif dist_sq == r**2:
        correct_answer = "圓上"
    else:
        correct_answer = "圓內"

    question_text = f"請問點 P({px}, {py}) 與圓 C: {circle_eq} 的關係為何？ (圓內、圓上、圓外)"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}