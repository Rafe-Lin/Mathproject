# ==============================================================================
# ID: jh_數學1上_FractionMultiplication
# Model: qwen3-coder:30b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 80.36s | RAG: 4 examples
# Created At: 2025-12-31 23:51:22
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

def generate_fraction_multiplication_problem():
    # 生成兩個分數乘法題目，包含負數與混合數
    def generate_fraction():
        num = random.randint(1, 10)
        den = random.randint(2, 10)
        return Fraction(num, den)
    
    def generate_mixed_number():
        whole = random.randint(1, 5)
        num = random.randint(1, 9)
        den = random.randint(2, 10)
        return Fraction(whole * den + num, den)
    
    # 隨機選擇是否使用混合數
    use_mixed = random.choice([True, False])
    
    if use_mixed:
        frac1 = generate_mixed_number()
        frac2 = generate_fraction()
        # 確保至少有一個是負數
        if random.random() < 0.5:
            frac1 = -frac1
        else:
            frac2 = -frac2
    else:
        frac1 = generate_fraction()
        frac2 = generate_fraction()
        # 確保至少有一個是負數
        if random.random() < 0.5:
            frac1 = -frac1
        else:
            frac2 = -frac2
    
    # 計算結果
    result = frac1 * frac2
    
    # 格式化題目
    frac1_latex = to_latex(frac1)
    frac2_latex = to_latex(frac2)
    
    question_text = f'計算下列各式的值。\\n⑴ $ {frac1_latex} \\times {frac2_latex} $'
    
    return {
        'question_text': question_text,
        'answer': str(result),
        'correct_answer': str(result)
    }

def generate(level=1):
    return generate_fraction_multiplication_problem()