import random

def generate(level=1):
    """
    生成一道「從直徑兩端點求圓方程式」的題目。
    level 1: 端點座標為偶數，使圓心為整數。
    level 2: 端點座標為任意整數，圓心可能為分數。
    """
    if level == 1:
        x1, y1 = random.randint(-5, 5) * 2, random.randint(-5, 5) * 2
        x2, y2 = random.randint(-5, 5) * 2, random.randint(-5, 5) * 2
        while x1 == x2 and y1 == y2: x2, y2 = random.randint(-5, 5) * 2, random.randint(-5, 5) * 2
    else: # level 2
        x1, y1 = random.randint(-9, 9), random.randint(-9, 9)
        x2, y2 = random.randint(-9, 9), random.randint(-9, 9)
        while x1 == x2 and y1 == y2: x2, y2 = random.randint(-9, 9), random.randint(-9, 9)

    question_text = f"已知一圓的直徑兩端點為 A({x1}, {y1}) 與 B({x2}, {y2})，請求出此圓的標準式。"

    # 圓心為中點
    h = (x1 + x2) / 2
    k = (y1 + y2) / 2
    # 半徑平方 r^2 = (x1-h)^2 + (y1-k)^2
    r_sq = (x1 - h)**2 + (y1 - k)**2

    h_part = f"(x - {int(h)})²" if h > 0 else f"(x + {abs(int(h))})²" if h < 0 else "x²"
    k_part = f"(y - {int(k)})²" if k > 0 else f"(y + {abs(int(k))})²" if k < 0 else "y²"
    correct_answer = f"{h_part} + {k_part} = {int(r_sq)}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("^2", "²")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}