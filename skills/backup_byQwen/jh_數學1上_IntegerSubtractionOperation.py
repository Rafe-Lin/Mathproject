# ==============================================================================
# ID: jh_數學1上_IntegerSubtractionOperation
# Model: freehuntx/qwen3-coder:14b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 194.12s | RAG: 2 examples
# Created At: 2025-12-31 22:41:14
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

def generate_subtraction_problem():
    # Generate two random integers for the problem
    val_a = random.randint(-100, 100)
    val_b = random.randint(-100, 100)
    
    # Ensure that the problem is not trivial (e.g., 0 - 0)
    while val_a == val_b:
        val_b = random.randint(-100, 100)
    
    # Calculate the answer
    ans = val_a - val_b
    
    # Format the question
    question_text = f"請計算 ${fmt_num(val_a)} - {fmt_num(val_b)}$ 的值為何？"
    
    return {'question_text': question_text, 'answer': str(ans), 'correct_answer': str(ans)}

def generate_app_problem():
    # Word problem for integer subtraction
    val_a = random.randint(-100, 100)
    val_b = random.randint(-100, 100)
    
    # Ensure that the problem is not trivial (e.g., 0 - 0)
    while val_a == val_b:
        val_b = random.randint(-100, 100)
    
    # Calculate the answer
    ans = val_a - val_b
    
    # Create a word problem
    if val_a >= 0 and val_b >= 0:
        question_text = f"小明有 {val_a} 元，他花了 {val_b} 元，請問他還剩下多少元？"
    elif val_a < 0 and val_b < 0:
        question_text = f"小明欠了 {abs(val_a)} 元，他又欠了 {abs(val_b)} 元，請問他總共欠了多少元？"
    elif val_a < 0 and val_b >= 0:
        question_text = f"小明欠了 {abs(val_a)} 元，他還了 {val_b} 元，請問他還欠多少元？"
    else:
        question_text = f"小明有 {val_a} 元，他花了 {abs(val_b)} 元，請問他還剩下多少元？"
    
    return {'question_text': question_text, 'answer': str(ans), 'correct_answer': str(ans)}

def generate(level=1):
    type = random.choice(['calc', 'app'])
    if type == 'calc': return generate_subtraction_problem()
    else: return generate_app_problem()