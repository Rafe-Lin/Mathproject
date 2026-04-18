# ==============================================================================
# ID: jh_數學1上_FourArithmeticOperationsOfNumbers
# Model: qwen3-coder:30b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 82.70s | RAG: 4 examples
# Created At: 2025-12-31 23:44:58
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
    # [TEMPLATE] Example: Addition with parentheses
    val_a = random.randint(-10, -1)
    val_b = random.randint(-10, 10)
    # Example VARIATION: Mix absolute value (IF RELEVANT to skill)
    if random.random() < 0.3: 
         return {'question_text': f'請計算 $|{val_a}| + {fmt_num(val_b)}$ 的值為何？', 'answer': str(abs(val_a)+val_b), 'correct_answer': str(abs(val_a)+val_b)}
    
    # Standard calculation
    ans = val_a + val_b 
    # Note usage of fmt_num for correct negative formatting
    return {'question_text': f'請計算 ${fmt_num(val_a)} + {fmt_num(val_b)}$ 的值為何？', 'answer': str(ans), 'correct_answer': str(ans)}

def generate_app_problem():
    # Word problem involving subtraction and ratio
    total_weight = random.randint(30, 50)
    time_used = random.randint(10, 30)
    remaining_weight = random.randint(10, 25)
    
    # Calculate rate of consumption
    consumed_weight = total_weight - remaining_weight
    rate_per_minute = consumed_weight / time_used
    
    # Find empty drone weight
    empty_weight = total_weight - (rate_per_minute * time_used)
    
    # Generate question
    question_text = f"一臺農用無人機裝滿農藥的重量為 {total_weight} 公斤，若每分鐘噴灑的農藥重量皆相等，噴灑飛行 {time_used} 分鐘後，可將農藥噴完沒有剩下。某次此無人機裝滿農藥噴灑飛行 {time_used} 分鐘後，無人機與剩餘農藥重量為 {remaining_weight} 公斤，則此無人機未裝農藥時的重量為多少公斤？"
    
    return {
        'question_text': question_text,
        'answer': str(empty_weight),
        'correct_answer': str(empty_weight)
    }

def generate(level=1):
    type = random.choice(['calc', 'app'])
    if type == 'calc': return generate_calc_problem()
    else: return generate_app_problem()