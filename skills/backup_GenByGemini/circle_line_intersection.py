import random

def generate(level=1):
    """
    生成一道「求圓與直線交點」的題目。
    level 1: 圓心在原點，直線為 y=c 或 x=c，交點為整數。
    level 2: 圓心在原點，直線為 y=x+c，交點為整數。
    """
    if level == 1:
        # x^2+y^2=r^2, y=c.  x^2 = r^2-c^2
        c = random.randint(3, 5)
        x = random.randint(1, c-1)
        r_sq = c**2 + x**2
        question_text = f"請求出圓 x² + y² = {r_sq} 與直線 y = {c} 的所有交點座標。\n(若有兩點，請用分號 ; 分隔，例如 (x1,y1);(x2,y2))"
        correct_answer = f"({x},{c});(-{x},{c})"
    else: # level 2
        # x^2+y^2=r^2, y=x+c
        # x^2+(x+c)^2=r^2 => 2x^2+2cx+c^2-r^2=0
        # 為了讓解是整數，反向構造
        x1 = random.randint(-4, 4)
        x2 = random.randint(-4, 4)
        while x1 == x2: x2 = random.randint(-4, 4)
        # 2(x-x1)(x-x2) = 2(x^2 - (x1+x2)x + x1x2) = 2x^2 - 2(x1+x2)x + 2x1x2
        # 2c = -2(x1+x2) => c = -(x1+x2)
        c = -(x1+x2)
        # c^2-r^2 = 2x1x2 => r^2 = c^2 - 2x1x2
        r_sq = c**2 - 2*x1*x2
        if r_sq <= 0: return generate(level) # 確保是圓
        
        y1 = x1 + c
        y2 = x2 + c
        question_text = f"請求出圓 x² + y² = {r_sq} 與直線 y = x + {c} 的所有交點座標。\n(若有兩點，請用分號 ; 分隔)"
        correct_answer = f"({x1},{y1});({x2},{y2})"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_parts = sorted(user_answer.strip().replace(" ", "").split(';'))
    correct_parts = sorted(correct_answer.strip().split(';'))
    is_correct = (user_parts == correct_parts)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}