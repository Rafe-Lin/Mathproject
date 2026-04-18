# ==============================================================================
# ID: jh_數學1上_PowerOfNumbers
# Model: qwen3-coder:30b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 113.93s | RAG: 8 examples
# Created At: 2025-12-31 23:54:36
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
    # 乘方運算：正數、負數、分數
    if random.random() < 0.5:
        # 產生負數的乘方
        base = random.choice([-2, -3, -4, -5])
        exp = random.choice([2, 3, 4])
        ans = base ** exp
        return {
            'question_text': f'請計算 $({fmt_num(base)})^{exp}$ 的值為何？',
            'answer': str(ans),
            'correct_answer': str(ans)
        }
    else:
        # 產生分數的乘方
        num = random.randint(1, 5)
        den = random.randint(2, 6)
        exp = random.choice([2, 3])
        base = Fraction(num, den)
        ans = base ** exp
        return {
            'question_text': f'請計算 $\\left(\\frac{{{num}}}{{{den}}}\\right)^{exp}$ 的值為何？',
            'answer': to_latex(ans),
            'correct_answer': to_latex(ans)
        }

def generate_app_problem():
    # 應用題：比較大小
    if random.random() < 0.5:
        # 比較相同底數不同指數
        base = random.choice([Fraction(2, 3), Fraction(3, 4), Fraction(4, 5)])
        exp1 = random.randint(2, 5)
        exp2 = random.randint(2, 5)
        while exp1 == exp2:
            exp2 = random.randint(2, 5)
        val1 = base ** exp1
        val2 = base ** exp2
        if val1 > val2:
            comp = ">"
        elif val1 < val2:
            comp = "<"
        else:
            comp = "="
        return {
            'question_text': f'比較下列各組數的大小：$\\left({to_latex(base)}\\right)^{exp1}$ 與 $\\left({to_latex(base)}\\right)^{exp2}$',
            'answer': comp,
            'correct_answer': comp
        }
    else:
        # 計算複合運算
        base1 = random.choice([-2, -3])
        exp1 = random.choice([2, 3])
        base2 = random.choice([2, 3])
        exp2 = random.choice([2, 3])
        val1 = base1 ** exp1
        val2 = base2 ** exp2
        ans = val1 * val2
        return {
            'question_text': f'請計算 $({fmt_num(base1)})^{exp1} \\times ({fmt_num(base2)})^{exp2}$ 的值為何？',
            'answer': str(ans),
            'correct_answer': str(ans)
        }

def generate(level=1):
    type = random.choice(['calc', 'app'])
    if type == 'calc': 
        return generate_calc_problem()
    else: 
        return generate_app_problem()