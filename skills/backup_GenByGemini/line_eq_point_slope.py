import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「點斜式」求直線方程式的題目。
    level 1: 斜率為整數。
    level 2: 斜率為分數。
    """
    x1, y1 = random.randint(-5, 5), random.randint(-5, 5)
    if level == 1:
        m = random.randint(-4, 4)
        m_str = str(m)
    else: # level 2
        m = Fraction(random.randint(-5, 5), random.randint(2, 4))
        m_str = f"{m.numerator}/{m.denominator}"

    question_text = f"已知直線 L 通過點 ({x1}, {y1}) 且斜率為 {m_str}，請求出直線 L 的一般式 (ax+by+c=0)。"

    # y - y1 = m(x - x1) => m*x - y - m*x1 + y1 = 0
    # (m_num/m_den)*x - y - (m_num/m_den)*x1 + y1 = 0
    # m_num*x - m_den*y - m_num*x1 + m_den*y1 = 0
    a = m.numerator
    b = -m.denominator
    c = -m.numerator * x1 + m.denominator * y1

    # 標準化：讓 x 係數為正
    if a < 0:
        a, b, c = -a, -b, -c
    
    correct_answer = f"{a}x{'+' if b>0 else ''}{b}y{'+' if c>0 else ''}{c}=0".replace("1x","x").replace("1y","y").replace("+-","-")

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").lower()
    correct = str(correct_answer).strip().replace(" ", "").lower()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}