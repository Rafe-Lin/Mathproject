# ==============================================================================
# ID: jh_數學1上_OppositesAndAbsoluteValue
# Model: qwen3-coder:30b | Strategy: General Math Pedagogy v7.3 (Chinese)
# Duration: 101.96s | RAG: 4 examples
# Created At: 2025-12-30 23:06:07
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
    # CSS: overflow-x: auto (Scrollable), background for contrast
    return (f"<div style='width: 100%; overflow-x: auto; background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;'>"
            f"<pre style='font-family: Consolas, monospace; line-height: 1.1; display: inline-block; margin: 0;'>{content}</pre></div>")

def generate_concept_problem():
    # Type: Concept (Explicit Options)
    target = -5
    others = [3, 0, 8]
    options = [target] + others
    random.shuffle(options)
    opt_str = ', '.join([str(x) for x in options])
    return {'question_text': f'在 {opt_str} 中，何者為負數？', 'answer': str(target), 'correct_answer': str(target)}

def generate_calc_problem():
    val = random.randint(-10, -1)
    return {'question_text': f'請計算 $|{val}|$ 的值為何？', 'answer': str(abs(val)), 'correct_answer': str(abs(val))}

def generate_reverse_problem():
    # Type: Reverse (Find the number given its opposite)
    num = random.randint(1, 10)
    opposite = -num
    return {'question_text': f'若一個數的相反數為 {opposite}，則這個數為何？', 'answer': str(num), 'correct_answer': str(num)}

def generate_application_problem():
    # Type: Application (Compare absolute values)
    a = random.randint(-10, -1)
    b = random.randint(-10, -1)
    abs_a = abs(a)
    abs_b = abs(b)
    if abs_a < abs_b:
        smaller = a
        larger = b
    else:
        smaller = b
        larger = a
    return {
        'question_text': f'分別寫出 {a} 和 {b} 的絕對值，並比較這兩個數絕對值的大小。又請判斷哪一個數比較大？',
        'answer': f'｜{a}｜= {abs_a}, ｜{b}｜= {abs_b}, ｜{a}｜＜｜{b}｜；{larger} 比較大',
        'correct_answer': f'｜{a}｜= {abs_a}, ｜{b}｜= {abs_b}, ｜{a}｜＜｜{b}｜；{larger} 比較大'
    }

def generate(level=1):
    type = random.choice(['concept', 'calc', 'reverse', 'application'])
    if type == 'concept': return generate_concept_problem()
    elif type == 'calc': return generate_calc_problem()
    elif type == 'reverse': return generate_reverse_problem()
    else: return generate_application_problem()