import random

def generate(level=1):
    """
    生成一道「由圓的一般式判別圖形」的題目。
    x² + y² + Dx + Ey + F = 0, 判別式 d = D² + E² - 4F
    d > 0: 圓, d = 0: 一點, d < 0: 無圖形
    level 1: D, E 為偶數，F 簡單。
    level 2: D, E, F 為任意整數。
    """
    if level == 1:
        D, E = random.randint(-5, 5) * 2, random.randint(-5, 5) * 2
    else: # level 2
        D, E = random.randint(-9, 9), random.randint(-9, 9)

    # 隨機決定圖形類型
    shape_type = random.choice(['circle', 'point', 'none'])
    d_base = D**2 + E**2

    if shape_type == 'circle': # d > 0 => d_base - 4F > 0 => 4F < d_base
        F = random.randint(-20, d_base // 4 - 1) if d_base // 4 > 0 else random.randint(-20, -1)
        correct_answer = "一個圓"
    elif shape_type == 'point': # d = 0 => 4F = d_base (需為整數)
        if d_base % 4 != 0: return generate(level) # 重來
        F = d_base // 4
        correct_answer = "一個點"
    else: # 'none', d < 0 => 4F > d_base
        F = random.randint(d_base // 4 + 1, d_base // 4 + 20)
        correct_answer = "無圖形"

    question_text = f"請問方程式 x² + y² + {D}x + {E}y + {F} = 0 的圖形為何？"
    question_text = question_text.replace("+-", "-")

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user in correct) # 允許 "圓" 或 "一個圓"
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}