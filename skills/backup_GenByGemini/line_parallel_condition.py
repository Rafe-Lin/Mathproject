import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「平行線條件」的題目。
    level 1: 兩直線平行，斜率相等。
    level 2: 給定 ax+by+c=0，求過某點的平行線。
    """
    if level == 1:
        m = Fraction(random.randint(-5, 5), random.randint(1, 3))
        c1 = random.randint(-5, 5)
        c2 = random.randint(-5, 5)
        while c1 == c2: c2 = random.randint(-5, 5)
        
        m_str = str(m.numerator) if m.denominator == 1 else f"{m.numerator}/{m.denominator}"
        
        question_text = f"若直線 L1: y = {m_str}x + {c1} 與直線 L2: y = (k)x + {c2} 平行，請問 k 的值是多少？"
        correct_answer = m_str
    else: # level 2
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
        while a == 0 or b == 0: a,b = random.randint(-5, 5), random.randint(-5, 5)
        c = random.randint(-10, 10)
        line_eq = f"{a}x + {b}y + {c} = 0".replace("+-", "-")
        
        px, py = random.randint(-5, 5), random.randint(-5, 5)
        # 確保點不在線上
        while a*px + b*py + c == 0: px, py = random.randint(-5, 5), random.randint(-5, 5)
        
        question_text = f"請求出通過點 ({px}, {py}) 且與直線 {line_eq} 平行的直線方程式 (一般式 ax+by+c=0)。"
        # 平行線 ax+by+k=0, 代入點求 k
        k = -a*px - b*py
        correct_answer = f"{a}x + {b}y + {k} = 0".replace("+-", "-").replace("+ -", "- ")

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").lower()
    correct = str(correct_answer).strip().replace(" ", "").lower()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}