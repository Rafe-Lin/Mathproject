# ==============================================================================
# ID: jh_數學1上_CommonMultipleAndLeastCommonMultiple
# Model: qwen3-coder:30b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 108.26s | RAG: 8 examples
# Created At: 2025-12-31 23:41:31
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
    # 生成兩個正整數，用於求最小公倍數
    a = random.randint(2, 15)
    b = random.randint(2, 15)
    
    # 確保 a 和 b 不相同，避免過於簡單
    if a == b:
        b = random.randint(2, 15)
    
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

    # 生成最小公倍數的標準分解式
    lcm_factors = {}
    all_primes = set(fa.keys()) | set(fb.keys())
    for p in all_primes:
        lcm_factors[p] = max(fa.get(p, 0), fb.get(p, 0))

    # 生成問題文字
    lcm_expr = " \\times ".join([f"{p}^{{{lcm_factors[p]}}}" if lcm_factors[p] > 1 else str(p) for p in sorted(lcm_factors.keys())])
    
    # 生成問題
    question_text = f"已知 $a = {a}$、$b = {b}$，求 $[a, b]$ 的標準分解式為何？"
    
    # 答案
    answer = f"$ {lcm_expr} $"
    correct_answer = answer
    
    return {
        'question_text': question_text,
        'answer': answer,
        'correct_answer': correct_answer
    }

def generate_app_problem():
    # 應用題：公倍數與最小公倍數的實際應用
    a = random.randint(2, 10)
    b = random.randint(2, 10)
    if a == b:
        b = random.randint(2, 10)
    
    # 假設 a 和 b 是兩個活動週期（例如：每 a 天和每 b 天）
    # 問題：他們同時進行的最小週期是多少天？
    question_text = f"某兩個活動分別每 {a} 天和每 {b} 天進行一次，請問這兩個活動同時進行的最小週期為多少天？"
    
    # 計算最小公倍數
    def gcd(x, y):
        while y:
            x, y = y, x % y
        return x

    def lcm(x, y):
        return abs(x * y) // gcd(x, y)

    ans = lcm(a, b)
    
    return {
        'question_text': question_text,
        'answer': str(ans),
        'correct_answer': str(ans)
    }

def generate(level=1):
    type = random.choice(['calc', 'app'])
    if type == 'calc': 
        return generate_calc_problem()
    else: 
        return generate_app_problem()