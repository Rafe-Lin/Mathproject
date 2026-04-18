# ==============================================================================
# ID: jh_數學1上_FractionDivision
# Model: qwen3-coder:30b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 111.44s | RAG: 3 examples
# Created At: 2025-12-31 23:50:01
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

def generate_fraction_division_problem():
    # 生成兩個分數，其中至少一個是負數
    num1 = random.randint(1, 10)
    den1 = random.randint(2, 10)
    num2 = random.randint(1, 10)
    den2 = random.randint(2, 10)
    
    # 隨機決定是否為負數
    if random.random() < 0.5:
        num1 = -num1
    if random.random() < 0.5:
        num2 = -num2
    
    frac1 = Fraction(num1, den1)
    frac2 = Fraction(num2, den2)
    
    # 確保除數不為零
    if frac2 == 0:
        frac2 = Fraction(1, 2)
    
    # 計算除法結果
    result = frac1 / frac2
    
    # 格式化問題文字
    question_text = f"計算 $\\frac{{{frac1.numerator}}}{{{frac1.denominator}}} \\div \\frac{{{frac2.numerator}}}{{{frac2.denominator}}}$ 的值為何？"
    
    return {
        'question_text': question_text,
        'answer': str(result),
        'correct_answer': str(result)
    }

def generate_app_problem():
    # 應用題：分數除法在實際情境中的應用
    total_distance = random.randint(10, 50)
    time_taken = random.randint(2, 10)
    
    # 計算平均速度（分數形式）
    avg_speed = Fraction(total_distance, time_taken)
    
    question_text = f"小明騎腳踏車 $ {total_distance} $ 公里，用了 $ {time_taken} $ 小時。請問他平均每小時騎多少公里？"
    
    return {
        'question_text': question_text,
        'answer': str(avg_speed),
        'correct_answer': str(avg_speed)
    }

def generate_calc_problem():
    # 基本分數除法計算
    num1 = random.randint(1, 10)
    den1 = random.randint(2, 10)
    num2 = random.randint(1, 10)
    den2 = random.randint(2, 10)
    
    # 隨機決定是否為負數
    if random.random() < 0.3:
        num1 = -num1
    if random.random() < 0.3:
        num2 = -num2
    
    frac1 = Fraction(num1, den1)
    frac2 = Fraction(num2, den2)
    
    # 確保除數不為零
    if frac2 == 0:
        frac2 = Fraction(1, 2)
    
    # 計算除法結果
    result = frac1 / frac2
    
    # 格式化問題文字
    question_text = f"請計算 $\\frac{{{frac1.numerator}}}{{{frac1.denominator}}} \\div \\frac{{{frac2.numerator}}}{{{frac2.denominator}}}$ 的值為何？"
    
    return {
        'question_text': question_text,
        'answer': str(result),
        'correct_answer': str(result)
    }

def generate(level=1):
    type = random.choice(['calc', 'app'])
    if type == 'calc': 
        return generate_calc_problem()
    else: 
        return generate_app_problem()