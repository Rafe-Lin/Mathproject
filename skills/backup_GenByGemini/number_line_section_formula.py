import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「數線分點公式」的題目。
    level 1: 內分點
    level 2: 外分點
    """
    A = random.randint(-10, 0)
    B = random.randint(1, 10)
    m = random.randint(1, 5)
    n = random.randint(1, 5)
    
    if level == 1:
        question_text = f"數線上兩點 A({A})、B({B})，若 P 點在 A、B 之間且 AP:PB = {m}:{n}，求 P 點坐標。"
        P = Fraction(m*B + n*A, m + n)
    else: # level 2
        question_text = f"數線上兩點 A({A})、B({B})，若 P 點在直線 AB 上（A-B-P）且 AP:PB = {m+n}:{n}，求 P 點坐標。"
        P = Fraction((m+n)*B - n*A, m)

    correct_answer = f"{P.numerator}/{P.denominator}" if P.denominator != 1 else str(P.numerator)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}