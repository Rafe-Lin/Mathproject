# ==============================================================================
# ID: jh_數學1上_SimplestFraction
# Model: qwen3-coder:30b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 108.81s | RAG: 6 examples
# Created At: 2025-12-31 23:58:37
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

def generate_fraction_problem():
    # 生成兩個隨機整數，作為分數的分子與分母
    num = random.randint(-50, 50)
    den = random.randint(1, 50)
    
    # 確保分母不為零
    if den == 0:
        den = 1
    
    # 簡化分數
    frac = Fraction(num, den)
    
    # 生成問題
    question_text = f"將分數 $\\frac{{{num}}}{{{den}}}$ 化為最簡分數。"
    
    # 答案
    answer = f"$\\frac{{{frac.numerator}}}{{{frac.denominator}}}$"
    correct_answer = f"$\\frac{{{frac.numerator}}}{{{frac.denominator}}}$"
    
    return {
        'question_text': question_text,
        'answer': answer,
        'correct_answer': correct_answer
    }

def generate_comparison_problem():
    # 生成兩個分數進行比較
    num1 = random.randint(-20, 20)
    den1 = random.randint(1, 20)
    num2 = random.randint(-20, 20)
    den2 = random.randint(1, 20)
    
    frac1 = Fraction(num1, den1)
    frac2 = Fraction(num2, den2)
    
    # 生成問題
    question_text = f"比較 $\\frac{{{num1}}}{{{den1}}}$ 與 $\\frac{{{num2}}}{{{den2}}}$ 的大小，並用「>」或「<」表示。"
    
    # 判斷大小
    if frac1 > frac2:
        symbol = ">"
    elif frac1 < frac2:
        symbol = "<"
    else:
        symbol = "="
    
    answer = f"$\\frac{{{num1}}}{{{den1}}} {symbol} \\frac{{{num2}}}{{{den2}}}$"
    correct_answer = f"$\\frac{{{num1}}}{{{den1}}} {symbol} \\frac{{{num2}}}{{{den2}}}$"
    
    return {
        'question_text': question_text,
        'answer': answer,
        'correct_answer': correct_answer
    }

def generate_is_simplest_problem():
    # 生成一個分數
    num = random.randint(-50, 50)
    den = random.randint(1, 50)
    
    # 簡化分數
    frac = Fraction(num, den)
    
    # 判斷是否為最簡分數
    is_simplest = (frac.numerator == num and frac.denominator == den)
    
    # 生成問題
    question_text = f"分數 $\\frac{{{num}}}{{{den}}}$ 是否為最簡分數？請說明理由。"
    
    answer = "是" if is_simplest else "不是"
    correct_answer = "是" if is_simplest else "不是"
    
    return {
        'question_text': question_text,
        'answer': answer,
        'correct_answer': correct_answer
    }

def generate(level=1):
    # 根據難度選擇問題類型
    problem_types = [
        generate_fraction_problem,
        generate_comparison_problem,
        generate_is_simplest_problem
    ]
    
    return random.choice(problem_types)()