# ==============================================================================
# ID: gh_DefiniteIntegral
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 110.84s | RAG: 2 examples
# Created At: 2026-01-29 19:17:03
# Fix Status: [Repaired]
# Fixes: Regex=4, Logic=0
#==============================================================================


# [V12.3 Elite Standard Math Tools]
import random
import math
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fractions import Fraction
from functools import reduce
import ast
import base64
import io
import re

# [V11.6 Elite Font & Style] - Hardcoded
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

def to_latex(num):
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num == 0: return "0"
        if num.denominator == 1: return str(num.numerator)
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return r"{s}{w}".replace("{s}", sign).replace("{w}", str(whole))
            return r"{s}{w} \frac{{n}}{{d}}".replace("{s}", sign).replace("{w}", str(whole)).replace("{n}", str(rem_num)).replace("{d}", str(abs_num.denominator))
        return r"\frac{{n}}{{d}}".replace("{n}", str(num.numerator)).replace("{d}", str(num.denominator))
    return str(num)

def fmt_num(num, signed=False, op=False):
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    is_neg = (num < 0)
    abs_str = to_latex(abs(num))
    if op:
        if is_neg: return r" - {v}".replace("{v}", abs_str)
        return r" + {v}".replace("{v}", abs_str)
    if signed:
        if is_neg: return r"-{v}".replace("{v}", abs_str)
        return r"+{v}".replace("{v}", abs_str)
    if is_neg: return r"({v})".replace("{v}", latex_val)
    return latex_val

# --- 2. Number Theory Helpers ---
def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def get_positive_factors(n):
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def get_prime_factorization(n):
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def gcd(a, b): return math.gcd(int(a), int(b))
def lcm(a, b): return abs(int(a) * int(b)) // math.gcd(int(a), int(b))

def op_latex(num):
    return fmt_num(num, op=True)

def clean_latex_output(s):
    return str(s).strip()

# --- 3. Fraction Generator & Helpers ---
def simplify_fraction(n, d):
    common = math.gcd(n, d)
    return n // common, d // common

def _calculate_distance_1d(a, b):
    return abs(a - b)

def get_random_fraction(min_val=-10, max_val=10, denominator_limit=10, simple=True):
    for _ in range(100):
        den = random.randint(2, denominator_limit)
        num = random.randint(min_val * den, max_val * den)
        if den == 0: continue
        val = Fraction(num, den)
        if simple and val.denominator == 1: continue 
        if val == 0: continue
        return val
    return Fraction(1, 2)

# --- 7 下 強化組件 A: 數線區間渲染器 (針對不等式) ---
def draw_number_line(points_map, x_min=None, x_max=None, intervals=None, **kwargs):
    """
    intervals: list of dict, e.g., [{'start': 3, 'direction': 'right', 'include': False}]
    """
    values = [float(v) for v in points_map.values()] if points_map else [0]
    if intervals:
        for inter in intervals: values.append(float(inter['start']))
    
    if x_min is None: x_min = math.floor(min(values)) - 2
    if x_max is None: x_max = math.ceil(max(values)) + 2
    
    fig = Figure(figsize=(8, 2))
    ax = fig.add_subplot(111)
    ax.plot([x_min, x_max], [0, 0], 'k-', linewidth=1.5)
    ax.plot(x_max, 0, 'k>', markersize=8, clip_on=False)
    ax.plot(x_min, 0, 'k<', markersize=8, clip_on=False)
    
    # 數線刻度規範
    ax.set_xticks([0])
    ax.set_xticklabels(['0'], fontsize=18, fontweight='bold')
    
    # 繪製不等式區間 (7 下 關鍵)
    if intervals:
        for inter in intervals:
            s = float(inter['start'])
            direct = inter.get('direction', 'right')
            inc = inter.get('include', False)
            color = 'red'
            # 畫圓點 (空心/實心)
            ax.plot(s, 0.2, marker='o', mfc='white' if not inc else color, mec=color, ms=10, zorder=5)
            # 畫折線射線
            target_x = x_max if direct == 'right' else x_min
            ax.plot([s, s, target_x], [0.2, 0.5, 0.5], color=color, lw=2)

    for label, val in points_map.items():
        v = float(val)
        ax.plot(v, 0, 'ro', ms=7)
        ax.text(v, 0.08, label, ha='center', va='bottom', fontsize=16, fontweight='bold', color='red')

    ax.set_yticks([]); ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 7 下 強化組件 B: 直角坐標系渲染器 (針對方程式圖形) ---
def draw_coordinate_system(lines=None, points=None, x_range=(-5, 5), y_range=(-5, 5)):
    """
    繪製標準坐標軸與直線方程式
    """
    fig = Figure(figsize=(5, 5))
    ax = fig.add_subplot(111)
    ax.set_aspect('equal') # 鎖死比例
    
    # 繪製網格與軸線
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.axhline(0, color='black', lw=1.5)
    ax.axvline(0, color='black', lw=1.5)
    
    # 繪製直線 (y = mx + k)
    if lines:
        import numpy as np
        for line in lines:
            m, k = line.get('m', 0), line.get('k', 0)
            x = np.linspace(x_range[0], x_range[1], 100)
            y = m * x + k
            ax.plot(x, y, lw=2, label=line.get('label', ''))

    # 繪製點 (x, y)
    if points:
        for p in points:
            ax.plot(p[0], p[1], 'ro')
            ax.text(p[0]+0.2, p[1]+0.2, p.get('label', ''), fontsize=14, fontweight='bold')

    ax.set_xlim(x_range); ax.set_ylim(y_range)
    # 隱藏刻度,僅保留 0
    ax.set_xticks([0]); ax.set_yticks([0])
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def draw_geometry_composite(polygons, labels, x_limit=(0,10), y_limit=(0,10)):
    """[V11.6 Ultra Visual] 物理級幾何渲染器 (Physical Geometry Renderer)"""
    fig = Figure(figsize=(5, 4))
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    ax.set_aspect('equal', adjustable='datalim')
    all_x, all_y = [], []
    for poly_pts in polygons:
        polygon = patches.Polygon(poly_pts, closed=True, fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(polygon)
        for p in poly_pts:
            all_x.append(p[0])
            all_y.append(p[1])
    for text, pos in labels.items():
        all_x.append(pos[0])
        all_y.append(pos[1])
        ax.text(pos[0], pos[1], text, fontsize=20, fontweight='bold', ha='center', va='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1))
    if all_x and all_y:
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        rx = (max_x - min_x) * 0.3 if (max_x - min_x) > 0 else 1.0
        ry = (max_y - min_y) * 0.3 if (max_y - min_y) > 0 else 1.0
        ax.set_xlim(min_x - rx, max_x + rx)
        ax.set_ylim(min_y - ry, max_y + ry)
    else:
        ax.set_xlim(x_limit)
        ax.set_ylim(y_limit)
    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    del fig
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 4. Answer Checker (V11.6 Smart Formatting Standard) ---
def check(user_answer, correct_answer):
    import math, random, re
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    
    # 將字典或複雜格式轉為乾淨字串
    def _format_ans(a):
        if isinstance(a, dict):
            if "quotient" in a: 
                return r"{q}, {r}".replace("{q}", str(a.get("quotient",""))).replace("{r}", str(a.get("remainder","")))
            return ", ".join([r"{k}={v}".replace("{k}", str(k)).replace("{v}", str(v)) for k, v in a.items()])
        return str(a)

    def _clean(s):
        # 雙向清理:剝除 LaTeX 符號與空格
        return str(s).strip().replace(" ", "").replace("，", ",").replace("$", "").replace("\\", "").lower()
    
    u = _clean(user_answer)
    c_raw = _format_ans(correct_answer)
    c = _clean(c_raw)
    
    if u == c: return {"correct": True, "result": "正確！"}
    
    try:
        import math
        if math.isclose(float(u), float(c), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
    except: pass
    
    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", c_raw)}


import datetime

import re


    """
    Checks the user's answer against the correct answer.
    This function adheres to the Universal Check Template (系統底層鐵律).
    """
    import re, math
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        # Regex to remove LaTeX symbols, whitespace, parentheses, braces, brackets, backslashes,
        # alphabetic characters (a-zA-Z), equals sign, comma, semicolon, colon, and CJK characters.
        # This is designed to isolate the numerical part of the answer.
        return re.sub(r'[\$\s\(\)\{\}\[\]\\a-zA-Z=,;:\u4e00-\u9fff]', '', s) 

    u_str = str(user_answer).strip()
    c_str = str(correct_answer).strip()
    
    yes_group = ["是", "Yes", "TRUE", "True", "1", "O", "right"]
    no_group = ["否", "No", "FALSE", "False", "0", "X", "wrong"]
    
    if c_str in yes_group:
        return {"correct": u_str in yes_group, "result": "正確！" if u_str in yes_group else "答案錯誤"}
    if c_str in no_group:
        return {"correct": u_str in no_group, "result": "正確！" if u_str in no_group else "答案錯誤"}

    try:
        def parse(v):
           if "/" in v: 
               parts = v.split("/")
               if len(parts) == 2 and parts[1] != '0':
                   return float(parts[0]) / float(parts[1])
               return float('nan') # Indicate invalid fraction (e.g., division by zero)
           return float(v)
        
        u_val = parse(clean(u_str))
        c_val = parse(clean(c_str))
        if math.isclose(u_val, c_val, rel_tol=1e-5):
            return {"correct": True, "result": "正確！"}
    except (ValueError, ZeroDivisionError):
        # Catch errors if cleaning results in a non-numeric string or division by zero
        pass
        
    if u_str == c_str: return {"correct": True, "result": "正確！"}
    return {"correct": False, "result": f"答案錯誤。"}

def _format_antiderivative_term(coeff_num, coeff_den, exponent):
    """
    Formats a single term of an antiderivative into a LaTeX string,
    handling integer and fractional coefficients, and variable exponents.
    e.g., (3, 2, 3) -> \frac{3}{2}x^3, (1, 1, 2) -> x^2, (-1, 1, 1) -> -x
    """
    if coeff_num == 0:
        return ""
    
    # Simplify the fraction
    gcd_val = math.gcd(abs(coeff_num), abs(coeff_den))
    num_s = coeff_num // gcd_val
    den_s = coeff_den // gcd_val

    coeff_part = ""
    # Handle the coefficient part
    if den_s == 1:
        if num_s == 1:
            coeff_part = ""
        elif num_s == -1:
            coeff_part = "-"
        else:
            coeff_part = str(num_s)
    else:
        coeff_part = r"\frac{" + str(num_s) + r"}{" + str(den_s) + r"}"
    
    # Handle the variable part
    variable_part = ""
    if exponent == 1:
        variable_part = "x"
    elif exponent > 1:
        variable_part = f"x^{{exponent}}"

    return f"{coeff_part}{variable_part}"

def _format_integrand_term(coeff, exponent, is_first_term=False):
    """
    Formats a single term of the integrand (ax^n) into a LaTeX-friendly string.
    Handles coefficients 1, -1, and constants.
    e.g., (3, 2) -> 3x^2, (-1, 1) -> -x, (1, 3) -> x^3, (5, 0) -> 5
    """
    if coeff == 0:
        return ""

    sign = "+" if coeff > 0 and not is_first_term else ""
    if coeff < 0:
        sign = "-"

    abs_coeff = abs(coeff)
    coeff_str = ""
    if abs_coeff != 1 or exponent == 0: # For x^0, always show the coefficient.
        coeff_str = str(abs_coeff)

    if exponent == 0:
        return f"{sign}{coeff_str}"
    elif exponent == 1:
        return f"{sign}{coeff_str}x"
    else:
        return f"{sign}{coeff_str}x^{{exponent}}"

def _format_integrand_expression(terms_list):
    """
    Combines a list of (coeff, exponent) tuples into a formatted polynomial string for the integrand.
    Sorts terms by exponent in descending order for standard representation.
    """
    terms_list.sort(key=lambda x: x[1], reverse=True)

    formatted_parts = []
    for i, (coeff, exponent) in enumerate(terms_list):
        if coeff == 0:
            continue
        part = _format_integrand_term(coeff, exponent, is_first_term=(len(formatted_parts) == 0))
        formatted_parts.append(part)
    
    if not formatted_parts:
        return "0" 
    
    result = "".join(formatted_parts)
    # Remove leading '+' if it's the first term (e.g., "+3x^2" becomes "3x^2")
    if result.startswith("+"):
        result = result[1:]
    
    return result

def _format_antiderivative_expression(antiderivative_terms_info):
    """
    Combines a list of (numerical_coeff_value, exponent, latex_string_for_term) tuples
    into a formatted polynomial string for the antiderivative.
    Sorts terms by exponent in descending order and correctly places '+' signs.
    """
    antiderivative_terms_info.sort(key=lambda x: x[1], reverse=True) # Sort by exponent
    
    formatted_parts = []
    for i, (numerical_coeff_value, exponent, latex_str) in enumerate(antiderivative_terms_info):
        if not latex_str: # Skip empty terms (e.g., if coefficient was 0)
            continue
        
        # Add '+' sign if it's not the first term and the term itself doesn't start with a '-'
        if i > 0 and not latex_str.startswith('-'):
            formatted_parts.append("+")
        
        formatted_parts.append(latex_str)
    
    return "".join(formatted_parts)

def generate():
    """
    Generates a definite integral problem based on one of three types.
    """
    problem_type = random.choice([1, 2, 3])
    
    question_text = ""
    correct_answer = ""
    answer = ""
    
    if problem_type == 1:
        # Type 1: Basic Power Rule Integral: int_a^b cx^n dx
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
        while a >= b: # Ensure a < b
            a = random.randint(-5, 5)
            b = random.randint(-5, 5)
        
        c = random.randint(-5, 5)
        while c == 0: # Ensure c != 0
            c = random.randint(-5, 5)
        
        n = random.randint(1, 3) # Exponent 1, 2, or 3

        integrand_str = _format_integrand_expression([(c, n)])

        question_text = r"計算定積分：$\int_{{a}}^{{b}} {integrand} dx$"
        question_text = question_text.replace("{a}", str(a))
        question_text = question_text.replace("{b}", str(b))
        question_text = question_text.replace("{integrand}", integrand_str)

        # Calculate correct answer
        antiderivative_b = c * (b**(n + 1)) / (n + 1)
        antiderivative_a = c * (a**(n + 1)) / (n + 1)
        result = antiderivative_b - antiderivative_a
        correct_answer = f"{result:.2f}"

        # Generate answer explanation
        indefinite_integral_latex = _format_antiderivative_term(c, n + 1, n + 1)
        
        F_b_val = antiderivative_b
        F_a_val = antiderivative_a

        answer_template = r"解：\n根據積分公式，$\int x^k dx = \frac{x^{{{k+1}}}}{k+1} + C$\n因此，$\\int {integrand_str} dx = {indefinite_integral_latex} + C$\n將上下限代入：\n$[{indefinite_integral_latex}]_{{{a}}}^{{{b}}} = ({F_b_val_str}) - ({F_a_val_str})$\n"
        
        # Adjust the subtraction line based on the sign of F_a_val for clarity
        if F_a_val < 0:
            answer_template += r"$= {F_b_val_str} + {abs_F_a_val_str} = {result_val_str}$\n所以，定積分的值為 ${result_val_str}$。"
        else:
            answer_template += r"$= {F_b_val_str} - {F_a_val_str} = {result_val_str}$\n所以，定積分的值為 ${result_val_str}$。"
        
        answer = answer_template.replace("{integrand_str}", integrand_str) \
                                .replace("{indefinite_integral_latex}", indefinite_integral_latex) \
                                .replace("{a}", str(a)) \
                                .replace("{b}", str(b)) \
                                .replace("{F_b_val_str}", f"{F_b_val:.2f}") \
                                .replace("{F_a_val_str}", f"{F_a_val:.2f}") \
                                .replace("{abs_F_a_val_str}", f"{abs(F_a_val):.2f}") \
                                .replace("{result_val_str}", f"{result:.2f}")

    elif problem_type == 2:
        # Type 2: Sum/Difference of Polynomial Terms: int_a^b (ax^m + bx^n) dx
        a_bound = random.randint(-4, 4)
        b_bound = random.randint(-4, 4)
        while a_bound >= b_bound:
            a_bound = random.randint(-4, 4)
            b_bound = random.randint(-4, 4)
        
        a_coeff = random.randint(-4, 4)
        while a_coeff == 0:
            a_coeff = random.randint(-4, 4)
        
        b_coeff = random.randint(-4, 4)
        while b_coeff == 0:
            b_coeff = random.randint(-4, 4)
        
        m = random.randint(1, 3)
        n = random.randint(1, 3)
        while m == n: # Ensure m != n
            n = random.randint(1, 3)

        integrand_str = _format_integrand_expression([(a_coeff, m), (b_coeff, n)])

        question_text = r"計算定積分：$\int_{{a}}^{{b}} ({integrand}) dx$"
        question_text = question_text.replace("{a}", str(a_bound))
        question_text = question_text.replace("{b}", str(b_bound))
        question_text = question_text.replace("{integrand}", integrand_str)

        # Calculate correct answer
        term1_b = a_coeff * (b_bound**(m + 1)) / (m + 1)
        term1_a = a_coeff * (a_bound**(m + 1)) / (m + 1)
        
        term2_b = b_coeff * (b_bound**(n + 1)) / (n + 1)
        term2_a = b_coeff * (a_bound**(n + 1)) / (n + 1)
        
        result = (term1_b + term2_b) - (term1_a + term2_a)
        correct_answer = f"{result:.2f}"

        # Generate answer explanation
        antiderivative_terms_info = []
        antiderivative_terms_info.append((a_coeff / (m+1), m+1, _format_antiderivative_term(a_coeff, m + 1, m + 1)))
        antiderivative_terms_info.append((b_coeff / (n+1), n+1, _format_antiderivative_term(b_coeff, n + 1, n + 1)))
        
        final_antiderivative_latex_expression = _format_antiderivative_expression(antiderivative_terms_info)
        
        F_b_val = term1_b + term2_b
        F_a_val = term1_a + term2_a

        answer_template = r"解：\n根據積分公式，$\int (f(x) + g(x)) dx = \int f(x) dx + \int g(x) dx$\n因此，$\\int ({integrand_str}) dx = {final_antiderivative_latex_expression} + C$\n將上下限代入：\n$[{final_antiderivative_latex_expression}]_{{{a_bound}}}^{{{b_bound}}} = ({F_b_val_str}) - ({F_a_val_str})$\n"
        
        if F_a_val < 0:
            answer_template += r"$= {F_b_val_str} + {abs_F_a_val_str} = {result_val_str}$\n所以，定積分的值為 ${result_val_str}$。"
        else:
            answer_template += r"$= {F_b_val_str} - {F_a_val_str} = {result_val_str}$\n所以，定積分的值為 ${result_val_str}$。"
        
        answer = answer_template.replace("{integrand_str}", integrand_str) \
                                .replace("{final_antiderivative_latex_expression}", final_antiderivative_latex_expression) \
                                .replace("{a_bound}", str(a_bound)) \
                                .replace("{b_bound}", str(b_bound)) \
                                .replace("{F_b_val_str}", f"{F_b_val:.2f}") \
                                .replace("{F_a_val_str}", f"{F_a_val:.2f}") \
                                .replace("{abs_F_a_val_str}", f"{abs(F_a_val):.2f}") \
                                .replace("{result_val_str}", f"{result:.2f}")

    elif problem_type == 3:
        # Type 3: Polynomial with Constant Term: int_a^b (ax^n + c) dx
        a_bound = random.randint(-4, 4)
        b_bound = random.randint(-4, 4)
        while a_bound >= b_bound:
            a_bound = random.randint(-4, 4)
            b_bound = random.randint(-4, 4)
        
        a_coeff = random.randint(-4, 4)
        while a_coeff == 0:
            a_coeff = random.randint(-4, 4)
        
        n = random.randint(1, 3)
        
        c_const = random.randint(-5, 5)
        while c_const == 0:
            c_const = random.randint(-5, 5)

        integrand_str = _format_integrand_expression([(a_coeff, n), (c_const, 0)])

        question_text = r"計算定積分：$\int_{{a}}^{{b}} ({integrand}) dx$"
        question_text = question_text.replace("{a}", str(a_bound))
        question_text = question_text.replace("{b}", str(b_bound))
        question_text = question_text.replace("{integrand}", integrand_str)

        # Calculate correct answer
        term_x_b = a_coeff * (b_bound**(n + 1)) / (n + 1)
        term_x_a = a_coeff * (a_bound**(n + 1)) / (n + 1)
        
        term_const_b = c_const * b_bound
        term_const_a = c_const * a_bound
        
        result = (term_x_b + term_const_b) - (term_x_a + term_const_a)
        correct_answer = f"{result:.2f}"

        # Generate answer explanation
        antiderivative_terms_info = []
        antiderivative_terms_info.append((a_coeff / (n+1), n+1, _format_antiderivative_term(a_coeff, n + 1, n + 1)))
        antiderivative_terms_info.append((float(c_const), 1, _format_antiderivative_term(c_const, 1, 1))) # Constant C integrates to Cx^1
        
        final_antiderivative_latex_expression = _format_antiderivative_expression(antiderivative_terms_info)
        
        F_b_val = term_x_b + term_const_b
        F_a_val = term_x_a + term_const_a

        answer_template = r"解：\n根據積分公式，$\int (f(x) + g(x)) dx = \int f(x) dx + \int g(x) dx$\n因此，$\\int ({integrand_str}) dx = {final_antiderivative_latex_expression} + C$\n將上下限代入：\n$[{final_antiderivative_latex_expression}]_{{{a_bound}}}^{{{b_bound}}} = ({F_b_val_str}) - ({F_a_val_str})$\n"
        
        if F_a_val < 0:
            answer_template += r"$= {F_b_val_str} + {abs_F_a_val_str} = {result_val_str}$\n所以，定積分的值為 ${result_val_str}$。"
        else:
            answer_template += r"$= {F_b_val_str} - {F_a_val_str} = {result_val_str}$\n所以，定積分的值為 ${result_val_str}$。"
        
        answer = answer_template.replace("{integrand_str}", integrand_str) \
                                .replace("{final_antiderivative_latex_expression}", final_antiderivative_latex_expression) \
                                .replace("{a_bound}", str(a_bound)) \
                                .replace("{b_bound}", str(b_bound)) \
                                .replace("{F_b_val_str}", f"{F_b_val:.2f}") \
                                .replace("{F_a_val_str}", f"{F_a_val:.2f}") \
                                .replace("{abs_F_a_val_str}", f"{abs(F_a_val):.2f}") \
                                .replace("{result_val_str}", f"{result:.2f}")

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer,
        "image_base64": None,
        "created_at": datetime.datetime.now(),
        "version": 1
    }

# [Auto-Injected Patch v11.0] Universal Return, Linebreak & Handwriting Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        
        # 1. 針對 check 函式的布林值回傳進行容錯封裝
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤'}
        
        if isinstance(res, dict):
            # [V11.3 Standard Patch] - 解決換行與編碼問題
            if 'question_text' in res and isinstance(res['question_text'], str):
                # 僅針對「文字反斜線+n」進行物理換行替換,不進行全局編碼轉換
                import re
                # 解決 r-string 導致的 \n 問題
                res['question_text'] = re.sub(r'\n', '\n', res['question_text'])
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則:若答案包含複雜運算符號,強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            # [V13.1 修復] 移除 '(' 與 ','，允許座標與數列使用純文字輸入
            triggers = ['^', '/', '|', '[', '{', '\\']
            
            # [V11.1 Refined] 僅在題目尚未包含提示時注入,避免重複堆疊
            has_prompt = "手寫" in res.get('question_text', '')
            should_inject = (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers)
            
            if should_inject and not has_prompt:
                res['input_mode'] = 'handwriting'
                # [V11.3] 確保手寫提示語在最後一行
                res['question_text'] = res['question_text'].rstrip() + "\n(請在手寫區作答!)"

            # 3. 確保反饋訊息中文
            if func.__name__ == 'check' and 'result' in res:
                if res['result'].lower() in ['correct!', 'correct', 'right']:
                    res['result'] = '正確！'
                elif res['result'].lower() in ['incorrect', 'wrong', 'error']:
                    res['result'] = '答案錯誤'
            
            # 4. 確保欄位完整性 & 答案同步
            if 'correct_answer' in res:
                # 若 answer 不存在或為空字串,強制同步 correct_answer
                if 'answer' not in res or not res['answer']:
                     res['answer'] = res['correct_answer']
            
            if 'answer' in res:
                res['answer'] = str(res['answer'])
            if 'image_base64' not in res:
                res['image_base64'] = ""
        return res
    return wrapper

import sys
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith('generate') or _name == 'check'):
        globals()[_name] = _patch_all_returns(_func)
