# ==============================================================================
# ID: jh_數學1上_CommonDivisorAndGreatestCommonDivisor
# Model: qwen3-coder:30b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 129.37s | RAG: 7 examples
# Created At: 2025-12-31 23:39:42
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
    # 生成兩個數字，用於求最大公因數
    a = random.randint(10, 50)
    b = random.randint(10, 50)
    
    # 確保 a 和 b 不相同，避免太簡單
    if a == b:
        b += 1
    
    # 生成標準分解式
    def prime_factors(n):
        factors = {}
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors[d] = factors.get(d, 0) + 1
                n //= d
            d += 1
        if n > 1:
            factors[n] = factors.get(n, 0) + 1
        return factors

    fa = prime_factors(a)
    fb = prime_factors(b)

    # 求最大公因數的標準分解式
    gcd_factors = {}
    for p in fa:
        if p in fb:
            gcd_factors[p] = min(fa[p], fb[p])

    # 生成問題
    if random.random() < 0.5:
        # 問題：請列出 a 和 b 的因數，並找出最大公因數
        return {
            'question_text': f'請列出 $ {a} $ 和 $ {b} $ 的所有因數，並找出它們的最大公因數。', 
            'answer': f'因數：{a} 為 {sorted([i for i in range(1, a+1) if a % i == 0])}；{b} 為 {sorted([i for i in range(1, b+1) if b % i == 0])}；最大公因數為 {gcd(a, b)}',
            'correct_answer': f'{gcd(a, b)}'
        }
    else:
        # 問題：用標準分解式求最大公因數
        gcd_latex = " \\times ".join([f"{p}^{{{gcd_factors[p]}}}" for p in sorted(gcd_factors.keys())]) if gcd_factors else "1"
        return {
            'question_text': f'已知 $ {a} = {to_latex(Fraction(a))} $ 的標準分解式為 $ {to_latex(Fraction(a))} $，$ {b} = {to_latex(Fraction(b))} $ 的標準分解式為 $ {to_latex(Fraction(b))} $，請用標準分解式求出 $ ({a}, {b}) $ 的最大公因數。', 
            'answer': f'$ ({a}, {b}) = {gcd_latex} $',
            'correct_answer': f'{gcd(a, b)}'
        }

def gcd(x, y):
    while y:
        x, y = y, x % y
    return x

def generate_app_problem():
    # 應用題：找出最大公因數
    a = random.randint(10, 50)
    b = random.randint(10, 50)
    if a == b:
        b += 1
    
    # 假設 a 和 b 是長度（單位：公分），要剪成相同長度的小段，求最大可能長度
    return {
        'question_text': f'有一根長度為 $ {a} $ 公分的繩子和一根長度為 $ {b} $ 公分的繩子，若要將它們都剪成相同長度的小段，且每段長度為整數公分，則每段最多可以剪成多少公分？', 
        'answer': f'每段最多可以剪成 {gcd(a, b)} 公分',
        'correct_answer': f'{gcd(a, b)}'
    }

def generate(level=1):
    type = random.choice(['calc', 'app'])
    if type == 'calc': 
        return generate_calc_problem()
    else: 
        return generate_app_problem()