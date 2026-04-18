import random
from fractions import Fraction
import math

def _get_lcm(a, b):
    """Calculates the least common multiple for non-zero integers."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // math.gcd(a, b)

def _format_answer_string(a, b):
    """Formats the function y=ax+b into a canonical string for checking."""
    def format_val(val):
        if isinstance(val, Fraction):
            if val.denominator == 1:
                return str(val.numerator)
            # No mixed fractions, just simple a/b
            return f"{val.numerator}/{val.denominator}"
        return str(val)

    a_str_part = ""
    if a != 0:
        if a == 1:
            a_str_part = "x"
        elif a == -1:
            a_str_part = "-x"
        else:
            a_str_part = f"{format_val(a)}x"

    b_str_part = ""
    if b != 0:
        b_val_str = format_val(abs(b))
        if b > 0:
            if a != 0:
                b_str_part = f"+{b_val_str}"
            else:
                b_str_part = b_val_str
        else: # b < 0
             b_str_part = f"-{b_val_str}"
    
    if a == 0:
        return f"y={b_str_part}"
    elif b == 0:
        return f"y={a_str_part}"
    else:
        return f"y={a_str_part}{b_str_part}"

def generate(level=1):
    """
    生成「函數圖形」相關題目。
    包含：
    1. 從兩點求函數
    2. 常數函數
    3. 應用問題（求x截距）
    4. 應用問題（求交點）
    """
    problem_type = random.choice(['from_points', 'constant', 'application', 'intersection'])
    
    if problem_type == 'from_points':
        return generate_find_function_from_points()
    elif problem_type == 'constant':
        return generate_find_constant_function()
    elif problem_type == 'application':
        return generate_application_problem()
    else: # 'intersection'
        return generate_find_intersection()

def generate_find_function_from_points():
    """題型：已知線型函數圖形通過兩點，求此函數。"""
    x1 = random.randint(-8, 8)
    y1 = random.randint(-15, 15)
    
    dx = random.randint(1, 8) * random.choice([-1, 1])
    dy = random.randint(-15, 15)
    # Ensure dy is not 0 if dx is not 0, to make it interesting and avoid constant functions here
    if dy == 0:
        dy = random.randint(1, 15) * random.choice([-1, 1])
        
    x2 = x1 + dx
    y2 = y1 + dy
    
    a = Fraction(dy, dx)
    b = y1 - a * x1
    
    question_text = (f"已知線型函數 $y=ax+b$ 的圖形為通過 $({x1}, {y1})$、$({x2}, {y2})$ 兩點的直線，"
                     f"則此函數為何？(請以 $y=ax+b$ 或 $y=b$ 的格式作答，分數請以 a/b 表示)")
    correct_answer = _format_answer_string(a, b)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_constant_function():
    """題型：已知圖形為水平線且通過一點，求此常數函數。"""
    x1 = random.randint(-10, 10)
    y1 = random.randint(-10, 10)
    if y1 == 0:
        y1 = random.randint(1, 10) * random.choice([-1, 1])
        
    axis_name = random.choice(["$x$ 軸", "水平"])
    
    question_text = f"已知一線型函數的圖形是平行 {axis_name} 的直線，且圖形通過點 $({x1}, {y1})$，則此函數為何？"
    correct_answer = f"y={y1}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_application_problem():
    """題型：應用問題，從兩點數據反推起始值(x截距)。"""
    den = random.choice([1, 2, 4, 5])
    num = random.randint(5, 25)
    a = Fraction(num, den)

    x_int = random.randint(2, 10) * den
    b = -a * x_int
    b = b.numerator

    # Generate two points (x1, y1), (x2, y2) with x > x_int
    mult1 = random.randint(int(x_int / den) + 1, int(x_int / den) + 5)
    x1 = mult1 * den
    y1 = int(a * x1 + b)
    
    mult2 = mult1 + random.randint(2, 6)
    x2 = mult2 * den
    y2 = int(a * x2 + b)

    question_text = (f"某高速公路收費方式為：每日行駛優惠里程數以內不收費，超過部分，"
                     f"費用(元)與行駛距離(公里)成線型函數關係。若行駛 ${x1}$ 公里需收費 ${y1}$ 元，"
                     f"行駛 ${x2}$ 公里需收費 ${y2}$ 元，請問每日的優惠里程數為多少公里？")
    correct_answer = str(x_int)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_intersection():
    """題型：應用問題，求兩線型函數的交點。"""
    a1 = random.randint(1, 4)
    a2 = a1 + random.randint(1, 3)

    common_mult = _get_lcm(a1, a2)
    k = random.randint(2, 6)
    y_intersect = k * common_mult
    
    min_x = max(y_intersect // a1, y_intersect // a2) + random.randint(5, 15)
    max_x = min_x + 20
    x_intersect = random.randint(min_x, max_x)
    
    b1 = y_intersect - a1 * x_intersect
    b2 = y_intersect - a2 * x_intersect

    # 甲機 (func 1)
    setup_time1 = int(-b1 / a1)
    op_time1 = setup_time1 + random.randint(5, 15)
    pages1 = a1 * op_time1 + b1
    
    # 乙機 (func 2)
    setup_time2 = int(-b2 / a2)
    op_time2 = setup_time2 + random.randint(5, 15)
    pages2 = a2 * op_time2 + b2

    question_text = (f"甲、乙兩臺影印機的複印張數與時間(秒)成線型函數關係。"
                     f"甲機製版 ${setup_time1}$ 秒後開始複印，在第 ${op_time1}$ 秒時總共印了 ${pages1}$ 張。"
                     f"乙機製版 ${setup_time2}$ 秒後開始複印，在第 ${op_time2}$ 秒時總共印了 ${pages2}$ 張。"
                     f"若兩機同時按下開始鍵，請問需經過多少秒，兩機複印的張數會相同？")
    correct_answer = str(x_intersect)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Normalize function string answers
    user_norm = user_answer.lower().replace(" ", "").replace("*", "")
    correct_norm = correct_answer.lower().replace(" ", "").replace("*", "")
    
    # Handle cases like y=1x+2 vs y=x+2
    user_norm = user_norm.replace('y=', '').replace('1x', 'x')
    correct_norm = correct_norm.replace('y=', '').replace('1x', 'x')

    is_correct = (user_norm == correct_norm)
    
    # Fallback for numerical answers
    if not is_correct:
        try:
            # Allow for some tolerance if floats are involved
            if abs(float(user_answer) - float(correct_answer)) < 1e-9:
                is_correct = True
        except (ValueError, TypeError):
            pass
            
    if is_correct:
        # Use LaTeX for numeric answers, plain text for function answers in feedback
        is_numeric = correct_answer.strip().replace('-', '', 1).replace('.', '', 1).isdigit()
        if is_numeric:
             result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
             result_text = f"完全正確！答案是 {correct_answer}。"
    else:
        is_numeric = correct_answer.strip().replace('-', '', 1).replace('.', '', 1).isdigit()
        if is_numeric:
             result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        else:
             result_text = f"答案不正確。正確答案應為：{correct_answer}"

    return {"correct": is_correct, "result": result_text, "next_question": True}