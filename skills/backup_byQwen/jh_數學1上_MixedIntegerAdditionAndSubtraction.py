# ==============================================================================
# ID: jh_數學1上_MixedIntegerAdditionAndSubtraction
# Model: freehuntx/qwen3-coder:14b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 291.61s | RAG: 8 examples
# Created At: 2025-12-31 22:51:28
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
    # 生成整數加減運算問題
    val_a = random.randint(-100, 100)
    val_b = random.randint(-100, 100)
    val_c = random.randint(-100, 100)
    
    # 隨機選擇問題類型
    problem_type = random.choice(['simple', 'with_absolute', 'with_parentheses', 'comparison'])
    
    if problem_type == 'simple':
        # 簡單的加減運算
        ans = val_a + val_b - val_c
        question_text = f"請計算 ${fmt_num(val_a)} + {fmt_num(val_b)} - {fmt_num(val_c)}$ 的值為何？"
        return {'question_text': question_text, 'answer': str(ans), 'correct_answer': str(ans)}
    
    elif problem_type == 'with_absolute':
        # 加入絕對值
        abs_val = random.choice([abs(val_a), abs(val_b), abs(val_c)])
        ans = abs_val + val_b - val_c
        question_text = f"請計算 $|{fmt_num(val_a)}| + {fmt_num(val_b)} - {fmt_num(val_c)}$ 的值為何？"
        return {'question_text': question_text, 'answer': str(ans), 'correct_answer': str(ans)}
    
    elif problem_type == 'with_parentheses':
        # 加入括號
        ans = val_a + (val_b - val_c)
        question_text = f"請計算 ${fmt_num(val_a)} + ({fmt_num(val_b)} - {fmt_num(val_c)})$ 的值為何？"
        return {'question_text': question_text, 'answer': str(ans), 'correct_answer': str(ans)}
    
    elif problem_type == 'comparison':
        # 比較運算結果是否相同
        expr1 = f"({fmt_num(val_a)} + {fmt_num(val_b)}) - {fmt_num(val_c)}"
        expr2 = f"{fmt_num(val_a)} + ({fmt_num(val_b)} - {fmt_num(val_c)})"
        ans1 = val_a + val_b - val_c
        ans2 = val_a + (val_b - val_c)
        if ans1 == ans2:
            result = "相同"
        else:
            result = "不同"
        question_text = f"比較下列兩式的運算結果是否相同：\n⑴ ${expr1}$ 和 ⑵ ${expr2}$"
        return {'question_text': question_text, 'answer': result, 'correct_answer': result}

def generate_app_problem():
    # 生成應用問題
    problem_type = random.choice(['temperature', 'elevation', 'money'])
    
    if problem_type == 'temperature':
        temp1 = random.randint(-20, 30)
        temp2 = random.randint(-20, 30)
        ans = temp1 + temp2
        question_text = f"某地早上氣溫為 ${fmt_num(temp1)}°C$，中午氣溫上升了 ${fmt_num(temp2)}°C$，請問中午的氣溫為多少度？"
        return {'question_text': question_text, 'answer': str(ans), 'correct_answer': str(ans)}
    
    elif problem_type == 'elevation':
        elev1 = random.randint(-100, 100)
        elev2 = random.randint(-100, 100)
        ans = elev1 - elev2
        question_text = f"某地海拔為 ${fmt_num(elev1)}$ 公尺，另一地比它低 ${fmt_num(elev2)}$ 公尺，請問另一地的海拔為多少公尺？"
        return {'question_text': question_text, 'answer': str(ans), 'correct_answer': str(ans)}
    
    elif problem_type == 'money':
        money1 = random.randint(100, 1000)
        money2 = random.randint(100, 1000)
        money3 = random.randint(100, 1000)
        ans = money1 - money2 + money3
        question_text = f"小明有 ${money1}$ 元，買書花了 ${money2}$ 元，又收到 ${money3}$ 元的紅包，請問小明現在有幾元？"
        return {'question_text': question_text, 'answer': str(ans), 'correct_answer': str(ans)}

def generate(level=1):
    type = random.choice(['calc', 'app'])
    if type == 'calc': return generate_calc_problem()
    else: return generate_app_problem()