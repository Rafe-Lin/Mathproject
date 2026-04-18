import random
from math import gcd

def generate_linear_equation_question():
    # Generate two points (x1, y1) and (x2, y2)
    x1, y1 = random.randint(-5, 5), random.randint(-5, 5)
    x2, y2 = random.randint(-5, 5), random.randint(-5, 5)
    while x1 == x2: # Ensure distinct x-coordinates for a non-vertical line
        x2 = random.randint(-5, 5)

    # Calculate slope (m) and y-intercept (b)
    m_num = y2 - y1
    m_den = x2 - x1

    # Simplify the slope if possible
    common_divisor = gcd(m_num, m_den)
    m_num //= common_divisor
    m_den //= common_divisor

    # Equation: y - y1 = m(x - x1)
    # y = (m_num/m_den) * x - (m_num/m_den) * x1 + y1
    # To avoid fractions in the answer, we'll ask for the slope and y-intercept
    
    question_text = f"已知兩點 ({x1}, {y1}) 和 ({x2}, {y2})，求通過這兩點的直線斜率。"
    
    # Answer is the simplified slope
    if m_den == 1:
        answer = str(m_num)
    else:
        answer = f"{m_num}/{m_den}"

    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
