import random
from fractions import Fraction
import math

def _format_equation(a, b, c):
    """
    Formats coefficients into a human-readable linear equation string in LaTeX.
    Example: (2, -1, 5) -> '$2x - y = 5$'
    """
    g = math.gcd(math.gcd(a, b), c)
    if g > 1:
        a //= g
        b //= g
        c //= g
        
    # Term X
    if a == 1:
        term1 = "x"
    elif a == -1:
        term1 = "-x"
    elif a == 0:
        term1 = ""
    else:
        term1 = f"{a}x"

    # Term Y
    if b == 1:
        term2 = " + y"
    elif b == -1:
        term2 = " - y"
    elif b > 0:
        term2 = f" + {b}y"
    elif b < 0:
        term2 = f" - {abs(b)}y"
    else:  # b == 0
        term2 = ""

    # Combine
    if not term1:
        left_side = term2.lstrip(" +")
    else:
        left_side = term1 + term2
    
    if not left_side:
        left_side = "0"

    return f"${left_side} = {c}$"

def _format_fraction(f):
    """
    Formats a Fraction object into a LaTeX string.
    """
    if f.denominator == 1:
        return str(f.numerator)
    
    sign = ""
    num = f.numerator
    if num < 0:
        sign = "-"
        num = abs(num)
        
    num_str = f"{num}"
    den_str = f"{f.denominator}"
    
    return f"{sign}\\frac{{{num_str}}}{{{den_str}}}"

def generate(level=1):
    """
    生成「二元一次聯立方程式的幾何意義」相關題目。
    包含：
    1. 求兩直線交點座標
    2. 求兩直線與座標軸所圍成的面積
    """
    problem_type = random.choice(['intersection', 'area'])
    
    if problem_type == 'intersection':
        return generate_intersection_problem()
    else:
        return generate_area_problem()

def generate_intersection_problem():
    """
    生成求兩直線交點的題目。
    可能產生整數解或分數解。
    """
    # Generate coefficients ensuring a unique solution (determinant != 0)
    while True:
        a1 = random.randint(-5, 5)
        b1 = random.randint(-5, 5)
        a2 = random.randint(-5, 5)
        b2 = random.randint(-5, 5)

        # Avoid trivial equations like 0=c
        if (a1 == 0 and b1 == 0) or (a2 == 0 and b2 == 0):
            continue
        
        # Ensure lines are not parallel/coincident
        determinant = a1 * b2 - a2 * b1
        if determinant != 0:
            break

    # Generate solution point and then constants c1, c2
    # This allows for both integer and fractional solutions based on coefficients
    if random.random() < 0.6: # Higher chance for integer solutions
        x_sol = random.randint(-5, 5)
        y_sol = random.randint(-5, 5)
        c1 = a1 * x_sol + b1 * y_sol
        c2 = a2 * x_sol + b2 * y_sol
        x_ans = str(x_sol)
        y_ans = str(y_sol)
    else: # Fractional solutions
        c1 = random.randint(-10, 10)
        c2 = random.randint(-10, 10)
        dx = c1 * b2 - c2 * b1
        dy = a1 * c2 - a2 * c1
        
        x_sol_frac = Fraction(dx, determinant)
        y_sol_frac = Fraction(dy, determinant)
        x_ans = _format_fraction(x_sol_frac)
        y_ans = _format_fraction(y_sol_frac)

    eq1_str = _format_equation(a1, b1, c1)
    eq2_str = _format_equation(a2, b2, c2)
    
    question_text = f"在坐標平面上，兩直線的方程式分別為：<br>{eq1_str}<br>{eq2_str}<br>請問這兩條直線的交點坐標為何？"
    
    correct_answer = f"({x_ans}, {y_ans})"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_area_problem():
    """
    生成求兩直線與座標軸所圍面積的題目。
    """
    axis = random.choice(['x', 'y'])
    
    # Generate intersection point (non-zero coordinates)
    x_i = random.choice([i for i in range(-5, 6) if i != 0])
    y_i = random.choice([i for i in range(-5, 6) if i != 0])

    # Generate intercepts on the chosen axis
    if axis == 'x':
        # Force area to be an integer
        if y_i % 2 != 0:
            diff = random.randint(1, 5) * 2
        else:
            diff = random.randint(1, 10)
        
        p1 = random.randint(-8, 8)
        p2 = p1 + diff
        if p1 == x_i or p2 == x_i:
            p1 += 1
            p2 += 1

        # Derive line equations from points (x_i, y_i), (p1, 0), (p2, 0)
        a1, b1, c1 = y_i, p1 - x_i, y_i * p1
        a2, b2, c2 = y_i, p2 - x_i, y_i * p2
        
        base = abs(p1 - p2)
        height = abs(y_i)

    else: # axis == 'y'
        # Force area to be an integer
        if x_i % 2 != 0:
            diff = random.randint(1, 5) * 2
        else:
            diff = random.randint(1, 10)

        q1 = random.randint(-8, 8)
        q2 = q1 + diff
        if q1 == y_i or q2 == y_i:
            q1 += 1
            q2 += 1
            
        # Derive line equations from points (x_i, y_i), (0, q1), (0, q2)
        a1, b1, c1 = q1 - y_i, x_i, x_i * q1
        a2, b2, c2 = q2 - y_i, x_i, x_i * q2

        base = abs(q1 - q2)
        height = abs(x_i)
        
    area = Fraction(base * height, 2)
    correct_answer = _format_fraction(area)

    eq1_str = _format_equation(a1, b1, c1)
    eq2_str = _format_equation(a2, b2, c2)

    question_text = f"求二元一次方程式 {eq1_str}、{eq2_str} 的圖形與 ${axis}$ 軸所圍成的區域面積。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確，可處理單一數值與座標。
    """
    # Normalize by removing spaces and parentheses
    norm_user = user_answer.replace(' ', '').replace('(', '').replace(')', '')
    norm_correct = correct_answer.replace(' ', '').replace('(', '').replace(')', '')
    
    is_correct = (norm_user.lower() == norm_correct.lower())
    
    if not is_correct:
        try:
            # Case 1: single number (area or single coordinate)
            if ',' not in norm_correct:
                user_val = float(eval(str(norm_user)))
                correct_val = float(eval(str(norm_correct)))
                if abs(user_val - correct_val) < 1e-9:
                    is_correct = True
            # Case 2: coordinates (x,y)
            else:
                user_parts = norm_user.split(',')
                correct_parts = norm_correct.split(',')
                if len(user_parts) == 2 and len(correct_parts) == 2:
                    user_x = float(eval(str(user_parts[0])))
                    user_y = float(eval(str(user_parts[1])))
                    corr_x = float(eval(str(correct_parts[0])))
                    corr_y = float(eval(str(correct_parts[1])))
                    if abs(user_x - corr_x) < 1e-9 and abs(user_y - corr_y) < 1e-9:
                        is_correct = True
        except Exception:
            # Could not parse/compare numerically
            pass

    # Use the original correct_answer for display to preserve formatting
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
