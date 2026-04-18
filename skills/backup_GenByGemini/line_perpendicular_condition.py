import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「垂直線條件」的題目。
    level 1: 兩直線垂直，斜率相乘為 -1。
    level 2: 給定 ax+by+c=0，求過某點的垂直線。
    """
    if level == 1:
        m1 = Fraction(random.randint(-5, 5), random.randint(1, 3))
        while m1 == 0: m1 = Fraction(random.randint(-5, 5), random.randint(1, 3))
        m2 = -1/m1
        
        m1_str = str(m1.numerator) if m1.denominator == 1 else f"{m1.numerator}/{m1.denominator}"
        m2_str = str(m2.numerator) if m2.denominator == 1 else f"{m2.numerator}/{m2.denominator}"
        
        question_text = f"若直線 L1: y = {m1_str}x + 3 與直線 L2: y = (k)x - 2 垂直，請問 k 的值是多少？"
        correct_answer = m2_str
    else: # level 2
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
        while a == 0 or b == 0: a,b = random.randint(-5, 5), random.randint(-5, 5)
        c = random.randint(-10, 10)
        line_eq = f"{a}x + {b}y + {c} = 0".replace("+-", "-")
        
        px, py = random.randint(-5, 5), random.randint(-5, 5)
        
        question_text = f"請求出通過點 ({px}, {py}) 且與直線 {line_eq} 垂直的直線方程式 (一般式 ax+by+c=0)。"
        # 垂直線 bx-ay+k=0, 代入點求 k
        k = -b*px + a*py
        correct_answer = f"{b}x - {a}y + {k} = 0".replace("+-", "-").replace("+ -", "- ").replace("--", "+")

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").lower()
    correct = str(correct_answer).strip().replace(" ", "").lower()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}