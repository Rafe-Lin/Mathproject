# ==============================================================================
# ID: jh_數學1上_ApplicationProblems
# Model: qwen3-coder:30b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 125.44s | RAG: 8 examples
# Created At: 2025-12-31 23:33:52
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

def generate_app_problem():
    # 問題類型：最大公因數與最小公倍數應用
    # 問題情境：水果分裝、學生分組、跑步周期、收成時間、拼磚問題、種樹問題、路燈問題
    # 本題選擇「學生分組」類型
    
    # 隨機產生 A 校與 B 校學生人數
    a_school = random.randint(10, 30)
    b_school = random.randint(10, 30)
    
    # 計算最大公因數
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    
    g = gcd(a_school, b_school)
    
    # 問題描述
    question_text = (
        f"臺灣的 A 校為了招待來自新加坡的姐妹學校 B 校，安排 {a_school} 位學生來接待 B 校 {b_school} 位學生，"
        f"現將其分成若干組進行參觀活動，每組都要包含 A 校及 B 校學生，而且每組 A 校學生人數一樣多、"
        f"B 校學生人數也一樣多，請問：\n"
        f"⑴ 最多可分成幾組？\n"
        f"⑵ 承⑴，此時每組共有多少位學生？"
    )
    
    answer = f"⑴ {g} 組\n⑵ {a_school // g + b_school // g} 位學生"
    correct_answer = f"⑴ {g} 組\n⑵ {a_school // g + b_school // g} 位學生"
    
    return {
        'question_text': question_text,
        'answer': answer,
        'correct_answer': correct_answer
    }

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

def generate(level=1):
    type = random.choice(['calc', 'app'])
    if type == 'calc': return generate_calc_problem()
    else: return generate_app_problem()