# ==============================================================================
# ID: jh_數學1上_IntegerAdditionOperation
# Model: freehuntx/qwen3-coder:14b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 301.25s | RAG: 4 examples
# Created At: 2025-12-31 12:47:39
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

def generate_calc_problem():
    # 生成整數加法問題
    val_a = random.randint(-10, -1)
    val_b = random.randint(-10, -1)
    ans = val_a + val_b
    return {'question_text': f'請計算 ${fmt_num(val_a)} + {fmt_num(val_b)}$ 的值為何？', 'answer': str(ans), 'correct_answer': str(ans)}

def generate_app_problem():
    # 生成應用問題
    val_a = random.randint(-10, -1)
    val_b = random.randint(-10, -1)
    ans = val_a + val_b
    return {'question_text': f'小明在遊戲中先輸了 {abs(val_a)} 分，再輸了 {abs(val_b)} 分，總共輸了多少分？', 'answer': str(ans), 'correct_answer': str(ans)}

def generate(level=1):
    type = random.choice(['calc', 'app'])
    if type == 'calc': return generate_calc_problem()
    else: return generate_app_problem()