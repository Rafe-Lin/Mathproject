# ==============================================================================
# ID: jh_數學1上_PrimeNumbersAndPrimeFactorization
# Model: qwen3-coder:30b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 132.86s | RAG: 8 examples
# Created At: 2025-12-31 23:56:49
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

def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(n**0.5)+1, 2):
        if n % i == 0: return False
    return True

def prime_factorization(n):
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

def generate_calc_problem():
    # 生成一個質數判斷題
    val = random.choice([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47])
    if random.random() < 0.5:
        return {
            'question_text': f'判斷下列數字中，哪一個是質數？',
            'answer': str(val),
            'correct_answer': str(val)
        }
    else:
        # 生成一個質因數分解題
        num = random.choice([12, 18, 20, 24, 30, 36, 40, 42, 48, 50])
        factors = prime_factorization(num)
        latex_factors = " \\times ".join([str(f) for f in factors])
        return {
            'question_text': f'將數字 {num} 以標準分解式表示，並寫出所有的質因數。', 
            'answer': f"標準分解式為 ${latex_factors}$，質因數為 {', '.join(set(str(f) for f in factors))}。",
            'correct_answer': f"標準分解式為 ${latex_factors}$，質因數為 {', '.join(set(str(f) for f in factors))}。"
        }

def generate_app_problem():
    # 應用題：根據對話判斷生日
    n = 2030
    # 找出四個不同的正整數，使其乘積為 2030
    divisors = []
    for i in range(1, int(n**0.5)+1):
        if n % i == 0:
            divisors.append(i)
            if i != n // i:
                divisors.append(n // i)
    divisors.sort()
    
    # 選擇四個不同數字
    selected = random.sample(divisors, 4)
    while selected[0] * selected[1] * selected[2] * selected[3] != n:
        selected = random.sample(divisors, 4)
    
    # 分成兩組，計算每組和
    group1 = selected[:2]
    group2 = selected[2:]
    sum1 = sum(group1)
    sum2 = sum(group2)
    
    # 確保結果合理（月份與日期）
    month = min(sum1, sum2)
    day = max(sum1, sum2)
    
    return {
        'question_text': f'根據以下小翊與小妍的對話過程，判斷小妍的生日應為幾月幾日？\n'
                         f'小翊：小妍，你的生日是幾月幾日？\n'
                         f'小妍：給你一個提示！將 {n} 拆成 4 個相異正整數的乘積，再將這 4 個正整數分成 2 組，每組 2 個的和，就是我的生日囉！',
        'answer': f'{month} 月 {day} 日',
        'correct_answer': f'{month} 月 {day} 日'
    }

def generate(level=1):
    type = random.choice(['calc', 'app'])
    if type == 'calc': 
        return generate_calc_problem()
    else: 
        return generate_app_problem()