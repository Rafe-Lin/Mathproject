import random

def generate(level=1):
    """
    生成一道「平面點法式」的題目。
    """
    normal = [random.randint(-5, 5) for _ in range(3)]
    # 確保法向量不是零向量
    while all(c == 0 for c in normal):
        normal = [random.randint(-5, 5) for _ in range(3)]
    point = [random.randint(-5, 5) for _ in range(3)]
    
    if level == 1:
        question_text = f"已知平面 E 的法向量為 {tuple(normal)}，且通過點 {tuple(point)}，請求出平面 E 的方程式。(一般式 ax+by+cz+d=0)"
        # a(x-x0) + b(y-y0) + c(z-z0) = 0 => ax+by+cz - (ax0+by0+cz0) = 0
        d = -sum(normal[i] * point[i] for i in range(3))
        correct_answer = f"{normal[0]}x+{normal[1]}y+{normal[2]}z+{d}=0".replace("+-", "-").replace("1x","x")
    else: # level 2
        d = random.randint(-10, 10)
        question_text = f"請問平面 E: {normal[0]}x + {normal[1]}y + {normal[2]}z + {d} = 0 的一個法向量為何？"
        correct_answer = f"({normal[0]},{normal[1]},{normal[2]})"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").lower()
    correct = str(correct_answer).strip().replace(" ", "").lower()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}