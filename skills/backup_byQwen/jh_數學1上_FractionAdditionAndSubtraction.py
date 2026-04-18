# ==============================================================================
# ID: jh_數學1上_FractionAdditionAndSubtraction
# Model: qwen3-coder:30b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 192.13s | RAG: 8 examples
# Created At: 2025-12-31 23:48:10
# Fix Status: [Repaired]
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
            return f"{sign}{abs(num).numerator // abs(num).denominator} \\frac{{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{{num.numerator}}}{{{num.denominator}}}"
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

def generate_fraction_add_sub_problem():
    # 產生兩個分數加減的題目
    # 確保分母為 2~12 之間的數字
    den1 = random.randint(2, 12)
    den2 = random.randint(2, 12)
    
    # 為了避免太複雜，限制分子為 1~10
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    
    # 隨機決定是否為負數
    sign1 = random.choice([-1, 1])
    sign2 = random.choice([-1, 1])
    
    frac1 = Fraction(sign1 * num1, den1)
    frac2 = Fraction(sign2 * num2, den2)
    
    # 隨機選擇加法或減法
    operation = random.choice(['+', '-'])
    
    if operation == '+':
        result = frac1 + frac2
        question_text = f'請計算 $ {to_latex(frac1)} + {to_latex(frac2)} $ 的值為何？'
    else:
        result = frac1 - frac2
        question_text = f'請計算 $ {to_latex(frac1)} - {to_latex(frac2)} $ 的值為何？'
    
    return {
        'question_text': question_text,
        'answer': str(result),
        'correct_answer': str(result)
    }

def generate_mixed_fraction_problem():
    # 產生帶分數的加減題目
    # 帶分數的整數部分為 1~5，分數部分為 1/2 到 11/12
    int1 = random.randint(1, 5)
    int2 = random.randint(1, 5)
    
    den1 = random.randint(2, 12)
    den2 = random.randint(2, 12)
    
    num1 = random.randint(1, den1 - 1)
    num2 = random.randint(1, den2 - 1)
    
    sign1 = random.choice([-1, 1])
    sign2 = random.choice([-1, 1])
    
    frac1 = Fraction(sign1 * (int1 * den1 + num1), den1)
    frac2 = Fraction(sign2 * (int2 * den2 + num2), den2)
    
    # 隨機選擇加法或減法
    operation = random.choice(['+', '-'])
    
    if operation == '+':
        result = frac1 + frac2
        question_text = f'請計算 $ {to_latex(frac1)} + {to_latex(frac2)} $ 的值為何？'
    else:
        result = frac1 - frac2
        question_text = f'請計算 $ {to_latex(frac1)} - {to_latex(frac2)} $ 的值為何？'
    
    return {
        'question_text': question_text,
        'answer': str(result),
        'correct_answer': str(result)
    }

def generate_complex_fraction_problem():
    # 產生較複雜的分數加減題目（含括號）
    den1 = random.randint(2, 12)
    den2 = random.randint(2, 12)
    den3 = random.randint(2, 12)
    den4 = random.randint(2, 12)
    
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    num3 = random.randint(1, 10)
    num4 = random.randint(1, 10)
    
    sign1 = random.choice([-1, 1])
    sign2 = random.choice([-1, 1])
    sign3 = random.choice([-1, 1])
    sign4 = random.choice([-1, 1])
    
    frac1 = Fraction(sign1 * num1, den1)
    frac2 = Fraction(sign2 * num2, den2)
    frac3 = Fraction(sign3 * num3, den3)
    frac4 = Fraction(sign4 * num4, den4)
    
    # 產生如：(frac1 + frac2) - (frac3 + frac4) 這樣的題目
    if random.random() < 0.5:
        result = (frac1 + frac2) - (frac3 + frac4)
        question_text = f'請計算 $ ({to_latex(frac1)} + {to_latex(frac2)}) - ({to_latex(frac3)} + {to_latex(frac4)}) $ 的值為何？'
    else:
        result = (frac1 - frac2) + (frac3 - frac4)
        question_text = f'請計算 $ ({to_latex(frac1)} - {to_latex(frac2)}) + ({to_latex(frac3)} - {to_latex(frac4)}) $ 的值為何？'
    
    return {
        'question_text': question_text,
        'answer': str(result),
        'correct_answer': str(result)
    }

def generate_app_problem():
    # 產生應用題
    # 例如：小明有 3/4 公斤的糖，他吃了 1/3 公斤，還剩下多少？
    den1 = random.randint(2, 12)
    den2 = random.randint(2, 12)
    
    num1 = random.randint(1, den1 - 1)
    num2 = random.randint(1, den2 - 1)
    
    frac1 = Fraction(num1, den1)
    frac2 = Fraction(num2, den2)
    
    # 隨機選擇加法或減法
    operation = random.choice(['+', '-'])
    
    if operation == '+':
        result = frac1 + frac2
        question_text = f'小明有 {to_latex(frac1)} 公斤的糖，他又買了 {to_latex(frac2)} 公斤，總共有多少公斤？'
    else:
        result = frac1 - frac2
        question_text = f'小明有 {to_latex(frac1)} 公斤的糖，他吃了 {to_latex(frac2)} 公斤，還剩下多少公斤？'
    
    return {
        'question_text': question_text,
        'answer': str(result),
        'correct_answer': str(result)
    }

def generate(level=1):
    # 根據難度選擇不同類型的題目
    if level == 1:
        return generate_fraction_add_sub_problem()
    elif level == 2:
        return generate_mixed_fraction_problem()
    elif level == 3:
        return generate_complex_fraction_problem()
    else:
        # 隨機選擇一種題型
        prob_type = random.choice([generate_fraction_add_sub_problem, generate_mixed_fraction_problem, generate_complex_fraction_problem])
        return prob_type()

# 產生一個分數加減題目
if __name__ == "__main__":