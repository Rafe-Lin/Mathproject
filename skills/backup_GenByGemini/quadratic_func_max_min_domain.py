import random

def generate(level=1):
    """
    生成一道「二次函數在限定範圍內的最大最小值」的題目。
    level 1: 頂點在範圍內。
    level 2: 頂點在範圍外。
    """
    a = random.choice([-2, -1, 1, 2])
    h = random.randint(-3, 3) # 頂點 x 座標
    k = random.randint(-5, 5) # 頂點 y 座標

    if level == 1: # 頂點在範圍內
        d1 = random.randint(1, 3)
        d2 = random.randint(1, 3)
        x_min, x_max = h - d1, h + d2
    else: # 頂點在範圍外
        if random.random() < 0.5: # 範圍在頂點右側
            x_min = h + random.randint(1, 3)
            x_max = x_min + random.randint(2, 4)
        else: # 範圍在頂點左側
            x_max = h - random.randint(1, 3)
            x_min = x_max - random.randint(2, 4)

    func_str = f"y = {a}(x-{h})² + {k}".replace("+-", "-")
    q_type = random.choice(['max', 'min'])
    question_text = f"在 {x_min} ≤ x ≤ {x_max} 的範圍內，求二次函數 {func_str} 的{'最大值' if q_type == 'max' else '最小值'}。"

    # 計算 f(x_min), f(x_max), k
    f_xmin = a * (x_min - h)**2 + k
    f_xmax = a * (x_max - h)**2 + k
    
    possible_values = [f_xmin, f_xmax]
    if x_min <= h <= x_max: possible_values.append(k)

    correct_answer = str(int(max(possible_values) if q_type == 'max' else min(possible_values)))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}