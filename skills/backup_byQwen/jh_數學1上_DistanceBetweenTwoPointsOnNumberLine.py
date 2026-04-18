# ==============================================================================
# ID: jh_數學1上_DistanceBetweenTwoPointsOnNumberLine
# Model: freehuntx/qwen3-coder:14b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 203.73s | RAG: 6 examples
# Created At: 2025-12-31 22:58:34
# Fix Status: [Clean Pass]
# ==============================================================================

import random
from fractions import Fraction

def to_latex(num):
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            rem = abs(num) - (abs(num).numerator // abs(num).denominator)
            return f"{sign}{abs(num).numerator // abs(num).denominator} \\frac{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num):
    """Formats negative numbers with parentheses for equations."""
    if num < 0: return f"({num})"
    return str(num)

def draw_number_line(points_map):
    """Generates aligned ASCII number line with HTML CSS (Scrollable)."""
    values = [int(v) if isinstance(v, (int, float)) else int(v.numerator/v.denominator) for v in points_map.values()]
    if not values: values = [0]
    r_min, r_max = min(min(values)-1, -5), max(max(values)+1, 5)
    if r_max - r_min > 12: c=sum(values)//len(values); r_min, r_max = c-6, c+6
    
    u_w = 5
    l_n, l_a, l_l = "", "", ""
    for i in range(r_min, r_max+1):
        l_n += f"{str(i):^{u_w}}"
        l_a += ("+" + " "*(u_w-1)) if i == r_max else ("+" + "-"*(u_w-1))
        lbls = [k for k,v in points_map.items() if (v==i if isinstance(v, int) else int(v)==i)]
        l_l += f"{lbls[0]:^{u_w}}" if lbls else " "*u_w
    
    content = f"{l_n}\n{l_a}\n{l_l}"
    return (f"<div style='width: 100%; overflow-x: auto; background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;'>"
            f"<pre style='font-family: Consolas, monospace; line-height: 1.1; display: inline-block; margin: 0;'>{content}</pre></div>")

def generate_distance_problem():
    # Generate two random points on the number line
    point_a = random.randint(-20, 20)
    point_b = random.randint(-20, 20)
    
    # Ensure the two points are different
    while point_a == point_b:
        point_b = random.randint(-20, 20)
    
    # Calculate the distance between the two points
    distance = abs(point_a - point_b)
    
    # Format the question
    question_text = f"數線上有 A ({fmt_num(point_a)})、B ({fmt_num(point_b)}) 兩點，則 A、B 兩點的距離 AB 為多少？"
    
    return {'question_text': question_text, 'answer': str(distance), 'correct_answer': str(distance)}

def generate_distance_with_variable_problem():
    # Generate one random point and a distance
    point_a = random.randint(-20, 20)
    distance = random.randint(1, 10)
    
    # Calculate the possible values for the second point
    point_b1 = point_a + distance
    point_b2 = point_a - distance
    
    # Format the question
    question_text = f"數線上有 A ({fmt_num(point_a)})、B (b) 兩點，如果 AB={distance}，則 b 可能是多少？"
    
    return {'question_text': question_text, 'answer': f"{point_b1} 或 {point_b2}", 'correct_answer': f"{point_b1} 或 {point_b2}"}

def generate_midpoint_problem():
    # Generate two random points on the number line
    point_a = random.randint(-20, 20)
    point_b = random.randint(-20, 20)
    
    # Ensure the two points are different
    while point_a == point_b:
        point_b = random.randint(-20, 20)
    
    # Calculate the midpoint
    midpoint = (point_a + point_b) / 2
    
    # Format the question
    question_text = f"數線上有 A ({fmt_num(point_a)})、B ({fmt_num(point_b)})、C (c) 三點，若 C 為 A、B 的中點，則 c 是多少？"
    
    return {'question_text': question_text, 'answer': str(midpoint), 'correct_answer': str(midpoint)}

def generate(level=1):
    type = random.choice(['distance', 'distance_with_variable', 'midpoint'])
    if type == 'distance': return generate_distance_problem()
    elif type == 'distance_with_variable': return generate_distance_with_variable_problem()
    else: return generate_midpoint_problem()