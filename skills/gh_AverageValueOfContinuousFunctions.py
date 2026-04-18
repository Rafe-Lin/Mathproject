# ==============================================================================
# ID: gh_AverageValueOfContinuousFunctions
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 151.08s | RAG: 3 examples
# Created At: 2026-01-29 19:28:42
# Fix Status: [Repaired]
# Fixes: Regex=3, Logic=0
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
    # 隱藏刻度，僅保留 0
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
        # 雙向清理：剝除 LaTeX 符號與空格
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



import re
from datetime import datetime
import fractions # For robust checking and handling fractions

# Helper function to format fractions for display in LaTeX
def _format_fraction(numerator, denominator):
    if denominator == 0:
        raise ValueError("Denominator cannot be zero.")
    if numerator == 0:
        return "0"
    
    # Simplify the fraction
    common_divisor = math.gcd(int(abs(numerator)), int(abs(denominator)))
    num = numerator // common_divisor
    den = denominator // common_divisor

    sign = ""
    if num * den < 0:
        sign = "-"
    
    num = abs(num)
    den = abs(den)

    if den == 1:
        return f"{sign}{num}"
    else:
        # Check for mixed number if num > den
        if num > den:
            integer_part = num // den
            remainder = num % den
            if remainder == 0:
                return f"{sign}{integer_part}"
            else:
                # Use .replace() for LaTeX safety
                return r"{sign}{integer_part}\frac{{{remainder}}}{{{den}}}".replace("{sign}", sign).replace("{integer_part}", str(integer_part)).replace("{remainder}", str(remainder)).replace("{den}", str(den))
        else:
            # Use .replace() for LaTeX safety
            return r"{sign}\frac{{{num}}}{{{den}}}".replace("{sign}", sign).replace("{num}", str(num)).replace("{den}", str(den))

# Helper function to evaluate a polynomial at a point
# coeffs = [c_n, c_{n-1}, ..., c_1, c_0]
def _evaluate_polynomial(coeffs, x):
    result = 0
    for i, coeff in enumerate(reversed(coeffs)): # Start from c_0, c_1*x, ...
        result += coeff * (x ** i)
    return result

# Helper function to integrate a polynomial term by term
# Integral of c * x^n is (c / (n+1)) * x^(n+1)
# Returns a list of (numerator, denominator) for the coefficients of the antiderivative
def _integrate_polynomial(coeffs):
    # coeffs = [c_n, c_{n-1}, ..., c_1, c_0]
    integrated_coeffs = [] # [(numerator, denominator) for the coefficient of x^(power)]
    for i, coeff in enumerate(reversed(coeffs)): # c_0, c_1*x, ..., c_n*x^n
        power = i
        new_coeff_num = coeff
        new_coeff_den = power + 1
        integrated_coeffs.append((new_coeff_num, new_coeff_den))
    
    # Reverse to get [C_{n+1}, C_n, ...] order for evaluation (highest power first)
    integrated_coeffs.reverse()
    return integrated_coeffs

# Helper function to evaluate the definite integral of a polynomial
# Returns (integral_numerator, integral_denominator)
def _evaluate_definite_integral(coeffs, a, b):
    integrated_coeffs_raw = _integrate_polynomial(coeffs)
    
    val_b_num = 0
    val_b_den = 1
    val_a_num = 0
    val_a_den = 1

    # Evaluate at b
    for i, (num_coeff, den_coeff) in enumerate(integrated_coeffs_raw):
        # Power for this term is (len of integrated_coeffs_raw - i)
        # because integrated_coeffs_raw is highest power first
        power = len(integrated_coeffs_raw) - i 
        
        term_num = num_coeff * (b ** power)
        term_den = den_coeff
        
        # Add fractions (A/B + C/D = (AD+BC)/BD)
        new_val_b_num = val_b_num * term_den + term_num * val_b_den
        new_val_b_den = val_b_den * term_den
        
        common = math.gcd(abs(new_val_b_num), abs(new_val_b_den))
        val_b_num = new_val_b_num // common
        val_b_den = new_val_b_den // common

    # Evaluate at a
    for i, (num_coeff, den_coeff) in enumerate(integrated_coeffs_raw):
        power = len(integrated_coeffs_raw) - i
        
        term_num = num_coeff * (a ** power)
        term_den = den_coeff

        new_val_a_num = val_a_num * term_den + term_num * val_a_den
        new_val_a_den = val_a_den * term_den

        common = math.gcd(abs(new_val_a_num), abs(new_val_a_den))
        val_a_num = new_val_a_num // common
        val_a_den = new_val_a_den // common
    
    # Subtract F(b) - F(a)
    integral_num = val_b_num * val_a_den - val_a_num * val_b_den
    integral_den = val_b_den * val_a_den
    
    common = math.gcd(abs(integral_num), abs(integral_den))
    integral_num //= common
    integral_den //= common

    return integral_num, integral_den

def generate(level=1):
    # [CRITICAL RULE: Variant Support]
    # Implements random.choice to toggle between different problem structures.
    problem_type = random.choice(['find_average_value_polynomial', 'find_c_polynomial'])

    question_text = ""
    correct_answer = ""
    solution_text = ""
    image_base64 = None

    if problem_type == 'find_average_value_polynomial':
        # Type 1 (Maps to conceptual Example 1, 3): Find the average value of a polynomial function.
        # [CRITICAL RULE: Grade & Semantic Alignment] - High school calculus concept.
        
        degree = random.randint(1, 3) # Degree 1 to 3 polynomial
        coeffs = [random.randint(-5, 5) for _ in range(degree + 1)] # [c_n, ..., c_0]
        
        # [CRITICAL RULE: 數據禁絕常數] - All numbers are randomized.
        # Ensure at least one non-zero coefficient for highest power or constant
        while all(c == 0 for c in coeffs) or (degree > 0 and coeffs[0] == 0 and len(coeffs) > 1):
             coeffs = [random.randint(-5, 5) for _ in range(degree + 1)]
             if degree > 0 and coeffs[0] == 0: # Ensure leading coefficient is not zero for a polynomial of specific degree
                 coeffs[0] = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])

        a = random.randint(-4, 2)
        b = random.randint(a + 1, 5) # Ensure b > a

        # Construct function string using .replace() for LaTeX safety
        func_terms = []
        for i, coeff in enumerate(coeffs):
            power = degree - i
            if coeff == 0:
                continue
            
            coeff_val_str = ""
            if abs(coeff) != 1 or power == 0:
                coeff_val_str = str(coeff)
            else:
                coeff_val_str = "-" if coeff == -1 else ""

            x_power_str = ""
            if power > 1:
                x_power_str = r"x^{{{power}}}".replace("{power}", str(power))
            elif power == 1:
                x_power_str = "x"
            
            # [CRITICAL RULE: 排版與 LaTeX 安全] - Use .replace() for all LaTeX string construction
            current_term_template = r"{coeff_val}{x_power}"
            current_term = current_term_template.replace("{coeff_val}", coeff_val_str).replace("{x_power}", x_power_str)
            
            if not func_terms: # First term
                func_terms.append(current_term)
            elif current_term.startswith('-'): # Subsequent negative term
                func_terms.append(current_term)
            else: # Subsequent positive term
                func_terms.append(r"+{term}".replace("{term}", current_term))

        func_str_raw = "".join(func_terms)
        if not func_str_raw: # Handle case like f(x) = 0
            func_str_raw = "0"

        # Calculate average value
        integral_num, integral_den = _evaluate_definite_integral(coeffs, a, b)
        
        interval_length_num = b - a
        interval_length_den = 1

        avg_num = integral_num * interval_length_den
        avg_den = integral_den * interval_length_num

        common = math.gcd(abs(avg_num), abs(avg_den))
        avg_num //= common
        avg_den //= common

        # [CRITICAL RULE: Answer Data Purity] - `correct_answer` must be pure data.
        correct_answer_val = f"{avg_num}/{avg_den}" if avg_den != 1 else str(avg_num)

        question_text = r"求函數 $f(x) = {func}$ 在區間 $[{a}, {b}]$ 上的平均值。"
        question_text = question_text.replace("{func}", func_str_raw)
        question_text = question_text.replace("{a}", str(a)).replace("{b}", str(b))

        solution_text = r"函數 $f(x)$ 在區間 $[a, b]$ 上的平均值為 $\frac{1}{b-a} \int_a^b f(x) \, dx$。"
        solution_text += r"\\對於 $f(x) = {func}$，區間為 $[{a}, {b}]$。"
        solution_text = solution_text.replace("{func}", func_str_raw).replace("{a}", str(a)).replace("{b}", str(b))
        
        integral_formula = r"\int_{{{a}}}^{{{b}}} ({func}) \, dx".replace("{a}", str(a)).replace("{b}", str(b)).replace("{func}", func_str_raw)
        
        # Calculate the antiderivative for solution display
        antiderivative_terms = []
        integrated_coeffs_raw = _integrate_polynomial(coeffs)
        
        for i, (num_coeff, den_coeff) in enumerate(integrated_coeffs_raw):
            power = len(integrated_coeffs_raw) - i 
            
            if num_coeff == 0:
                continue
            
            coeff_part_str = _format_fraction(num_coeff, den_coeff) # This already contains LaTeX and sign
            
            power_part_str = ""
            if power > 1:
                power_part_str = r"x^{{{power}}}".replace("{power}", str(power))
            elif power == 1:
                power_part_str = "x"
            
            # [CRITICAL RULE: 排版與 LaTeX 安全] - Use .replace() for all LaTeX string construction
            current_term_template = r"{coeff_part}{power_part}"
            current_term = current_term_template.replace("{coeff_part}", coeff_part_str).replace("{power_part}", power_part_str)
            
            if not antiderivative_terms:
                antiderivative_terms.append(current_term)
            elif current_term.startswith('-'):
                antiderivative_terms.append(current_term)
            else:
                antiderivative_terms.append(r"+{term}".replace("{term}", current_term))

        antiderivative_str_raw = "".join(antiderivative_terms)
        if not antiderivative_str_raw:
            antiderivative_str_raw = "0"
        
        # Recalculate F(b) and F(a) for solution text display
        val_b_num_sol, val_b_den_sol = 0, 1
        val_a_num_sol, val_a_den_sol = 0, 1
        
        for i, (num_coeff, den_coeff) in enumerate(integrated_coeffs_raw):
            power = len(integrated_coeffs_raw) - i
            
            term_val_b_num = num_coeff * (b ** power)
            term_val_b_den = den_coeff
            new_val_b_num = val_b_num_sol * term_val_b_den + term_val_b_num * val_b_den_sol
            new_val_b_den = val_b_den_sol * term_val_b_den
            common_b = math.gcd(abs(new_val_b_num), abs(new_val_b_den))
            val_b_num_sol = new_val_b_num // common_b
            val_b_den_sol = new_val_b_den // common_b

            term_val_a_num = num_coeff * (a ** power)
            term_val_a_den = den_coeff
            new_val_a_num = val_a_num_sol * term_val_a_den + term_val_a_num * val_a_den_sol
            new_val_a_den = val_a_den_sol * term_val_a_den
            common_a = math.gcd(abs(new_val_a_num), abs(new_val_a_den))
            val_a_num_sol = new_val_a_num // common_a
            val_a_den_sol = new_val_a_den // common_a

        Fb_str = _format_fraction(val_b_num_sol, val_b_den_sol)
        Fa_str = _format_fraction(val_a_num_sol, val_a_den_sol)
        integral_val_str = _format_fraction(integral_num, integral_den)
        avg_val_str = _format_fraction(avg_num, avg_den)

        solution_text += r"\\首先計算定積分："
        # [CRITICAL RULE: No Double Dollar Signs] - Use single $ for inline, $ for display.
        solution_text += r"\\${integral_formula} = [{antideriv}]_{{{a}}}^{{{b}}} = ({Fb}) - ({Fa}) = {integral_val}$".replace("{integral_formula}", integral_formula).replace("{antideriv}", antiderivative_str_raw).replace("{a}", str(a)).replace("{b}", str(b)).replace("{Fb}", Fb_str).replace("{Fa}", Fa_str).replace("{integral_val}", integral_val_str)
        solution_text += r"\\區間長度為 $b-a = {b_val} - {a_val} = {length}$。"
        solution_text = solution_text.replace("{b_val}", str(b)).replace("{a_val}", str(a)).replace("{length}", str(b-a))
        solution_text += r"\\平均值為 $\frac{1}{{length}} \times {integral_val} = {avg_val}$。".replace("{length}", str(b-a)).replace("{integral_val}", integral_val_str).replace("{avg_val}", avg_val_str)

    elif problem_type == 'find_c_polynomial':
        # Type 2 (Maps to conceptual Example 2): Find c such that f(c) = average value (Mean Value Theorem for Integrals)

        degree = random.choice([1, 2]) # Keep functions simple for solving f(c)=k
        
        coeffs = [random.randint(-3, 3) for _ in range(degree + 1)] # [c_n, ..., c_0]
        while all(c == 0 for c in coeffs) or (degree > 0 and coeffs[0] == 0 and len(coeffs) > 1):
            coeffs = [random.randint(-3, 3) for _ in range(degree + 1)]
            if degree > 0 and coeffs[0] == 0:
                 coeffs[0] = random.choice([-3, -2, -1, 1, 2, 3])
        
        a = random.randint(-3, 1)
        b = random.randint(a + 2, 4) # Ensure b > a and interval is slightly wider for c to exist

        # Construct function string using .replace() for LaTeX safety
        func_terms = []
        for i, coeff in enumerate(coeffs):
            power = degree - i
            if coeff == 0:
                continue
            
            coeff_val_str = ""
            if abs(coeff) != 1 or power == 0:
                coeff_val_str = str(coeff)
            else:
                coeff_val_str = "-" if coeff == -1 else ""

            x_power_str = ""
            if power > 1:
                x_power_str = r"x^{{{power}}}".replace("{power}", str(power))
            elif power == 1:
                x_power_str = "x"
            
            current_term_template = r"{coeff_val}{x_power}"
            current_term = current_term_template.replace("{coeff_val}", coeff_val_str).replace("{x_power}", x_power_str)
            
            if not func_terms:
                func_terms.append(current_term)
            elif current_term.startswith('-'):
                func_terms.append(current_term)
            else:
                func_terms.append(r"+{term}".replace("{term}", current_term))
        
        func_str_raw = "".join(func_terms)
        if not func_str_raw:
            func_str_raw = "0"
        
        # Calculate average value
        integral_num, integral_den = _evaluate_definite_integral(coeffs, a, b)
        
        interval_length_num = b - a
        interval_length_den = 1
        
        avg_num = integral_num * interval_length_den
        avg_den = integral_den * interval_length_num

        common = math.gcd(abs(avg_num), abs(avg_den))
        avg_num //= common
        avg_den //= common
        
        # Now solve f(c) = avg_num / avg_den
        correct_c_val = None
        
        # Coefficients for f(x) = c_n x^n + ... + c_0
        # coeffs are [c_n, c_{n-1}, ..., c_0]
        if degree == 1:
            c1_coeff = coeffs[0] # Coefficient of x
            c0_coeff = coeffs[1] # Constant term
            
            # Equation: c1_coeff * c + c0_coeff = avg_num / avg_den
            # c1_coeff * c = (avg_num / avg_den) - c0_coeff
            # c = ((avg_num / avg_den) - c0_coeff) / c1_coeff
            
            if c1_coeff == 0: # This means f(x) is a constant, which is allowed but might make 'c' non-unique or non-existent
                # If f(x) = constant and constant = average value, then any c works.
                # If f(x) = constant and constant != average value, then no c works.
                # To simplify, we enforce c1_coeff != 0 for degree 1 to avoid this.
                return generate(level) # Regenerate if leading coeff is 0 for specific degree
            
            avg_frac = fractions.Fraction(avg_num, avg_den)
            c0_frac = fractions.Fraction(c0_coeff)
            
            c_rhs_frac = avg_frac - c0_frac
            c_val_frac = c_rhs_frac / fractions.Fraction(c1_coeff)
            
            c_float = float(c_val_frac)
            if not (a <= c_float <= b):
                return generate(level) # c must be within the interval
            
            correct_c_val = c_val_frac

        elif degree == 2:
            c2_coeff = coeffs[0]
            c1_coeff = coeffs[1]
            c0_coeff = coeffs[2]

            avg_frac = fractions.Fraction(avg_num, avg_den)
            
            # Equation: c2_coeff * c^2 + c1_coeff * c + c0_coeff = avg_frac
            # c2_coeff * c^2 + c1_coeff * c + (c0_coeff - avg_frac) = 0
            
            a_quad = c2_coeff
            b_quad = c1_coeff
            c_quad_frac = fractions.Fraction(c0_coeff) - avg_frac
            
            # Convert to float for quadratic formula, then try to convert back to fraction
            # to keep answers exact if possible.
            # Avoid direct float arithmetic where possible, but for quadratic formula it's often necessary.
            
            # To maintain precision, convert all to common denominator for delta calculation if possible,
            # or use fractions library's float conversion carefully.
            
            # Current coeffs are integers, only c_quad_frac might be a fraction.
            # So, equation is A*c^2 + B*c + C = 0 where C is a fraction.
            # Multiply by C.denominator to clear fraction:
            # (A*C.denominator)*c^2 + (B*C.denominator)*c + C.numerator = 0
            
            a_quad_scaled = a_quad * c_quad_frac.denominator
            b_quad_scaled = b_quad * c_quad_frac.denominator
            c_quad_scaled = c_quad_frac.numerator
            
            delta = b_quad_scaled**2 - 4 * a_quad_scaled * c_quad_scaled
            
            if delta < 0: # No real solutions
                return generate(level)
            
            sqrt_delta = math.sqrt(delta)
            
            # Check if sqrt_delta is an integer (perfect square)
            # This allows exact fraction solutions.
            if abs(sqrt_delta - round(sqrt_delta)) < 1e-9:
                sqrt_delta_int = round(sqrt_delta)
                sol1_num = -b_quad_scaled + sqrt_delta_int
                sol1_den = 2 * a_quad_scaled
                
                sol2_num = -b_quad_scaled - sqrt_delta_int
                sol2_den = 2 * a_quad_scaled
                
                sol1_frac = fractions.Fraction(sol1_num, sol1_den)
                sol2_frac = fractions.Fraction(sol2_num, sol2_den)

                valid_solutions_frac = []
                if a <= float(sol1_frac) <= b:
                    valid_solutions_frac.append(sol1_frac)
                if a <= float(sol2_frac) <= b and sol2_frac != sol1_frac: # Avoid duplicates if delta=0
                    valid_solutions_frac.append(sol2_frac)
            else: # Irrational solutions, fallback to float comparison
                # This path is less preferred for exact answers but sometimes unavoidable.
                # However, the problem asks for the value of c, implying an exact value.
                # For this problem, we'll try to generate such that sqrt_delta is integer.
                # For now, if delta is not a perfect square, regenerate.
                return generate(level)

            if not valid_solutions_frac:
                return generate(level) # No valid c in interval
            
            correct_c_val = random.choice(valid_solutions_frac)

        if correct_c_val is None:
            return generate(level)

        correct_answer_val = f"{correct_c_val.numerator}/{correct_c_val.denominator}" if correct_c_val.denominator != 1 else str(correct_c_val.numerator)

        question_text = r"已知函數 $f(x) = {func}$ 在區間 $[{a}, {b}]$ 上的平均值為 $k$。"
        question_text += r"求在區間中滿足 $f(c) = k$ 的 $c$ 值。"
        question_text = question_text.replace("{func}", func_str_raw)
        question_text = question_text.replace("{a}", str(a)).replace("{b}", str(b))

        avg_val_str = _format_fraction(avg_num, avg_den)
        
        solution_text = r"函數 $f(x)$ 在區間 $[a, b]$ 上的平均值為 $k = \frac{1}{b-a} \int_a^b f(x) \, dx$。"
        solution_text += r"\\對於 $f(x) = {func}$，區間為 $[{a}, {b}]$。"
        solution_text = solution_text.replace("{func}", func_str_raw).replace("{a}", str(a)).replace("{b}", str(b))

        integral_formula = r"\int_{{{a}}}^{{{b}}} ({func}) \, dx".replace("{a}", str(a)).replace("{b}", str(b)).replace("{func}", func_str_raw)
        
        integral_num_sol, integral_den_sol = _evaluate_definite_integral(coeffs, a, b)
        integral_val_str_sol = _format_fraction(integral_num_sol, integral_den_sol)
        
        avg_val_str_sol = _format_fraction(avg_num, avg_den)

        solution_text += r"\\首先計算定積分："
        # Calculate the antiderivative for solution display
        antiderivative_terms = []
        integrated_coeffs_raw = _integrate_polynomial(coeffs)
        
        for i, (num_coeff, den_coeff) in enumerate(integrated_coeffs_raw):
            power = len(integrated_coeffs_raw) - i 
            
            if num_coeff == 0:
                continue
            
            coeff_part_str = _format_fraction(num_coeff, den_coeff) # This already contains LaTeX and sign
            
            power_part_str = ""
            if power > 1:
                power_part_str = r"x^{{{power}}}".replace("{power}", str(power))
            elif power == 1:
                power_part_str = "x"
            
            current_term_template = r"{coeff_part}{power_part}"
            current_term = current_term_template.replace("{coeff_part}", coeff_part_str).replace("{power_part}", power_part_str)
            
            if not antiderivative_terms:
                antiderivative_terms.append(current_term)
            elif current_term.startswith('-'):
                antiderivative_terms.append(current_term)
            else:
                antiderivative_terms.append(r"+{term}".replace("{term}", current_term))

        antiderivative_str_raw = "".join(antiderivative_terms)
        if not antiderivative_str_raw:
            antiderivative_str_raw = "0"

        # Recalculate F(b) and F(a) for solution text display
        val_b_num_sol, val_b_den_sol = 0, 1
        val_a_num_sol, val_a_den_sol = 0, 1
        
        for i, (num_coeff, den_coeff) in enumerate(integrated_coeffs_raw):
            power = len(integrated_coeffs_raw) - i
            
            term_val_b_num = num_coeff * (b ** power)
            term_val_b_den = den_coeff
            new_val_b_num = val_b_num_sol * term_val_b_den + term_val_b_num * val_b_den_sol
            new_val_b_den = val_b_den_sol * term_val_b_den
            common_b = math.gcd(abs(new_val_b_num), abs(new_val_b_den))
            val_b_num_sol = new_val_b_num // common_b
            val_b_den_sol = new_val_b_den // common_b

            term_val_a_num = num_coeff * (a ** power)
            term_val_a_den = den_coeff
            new_val_a_num = val_a_num_sol * term_val_a_den + term_val_a_num * val_a_den_sol
            new_val_a_den = val_a_den_sol * term_val_a_den
            common_a = math.gcd(abs(new_val_a_num), abs(new_val_a_den))
            val_a_num_sol = new_val_a_num // common_a
            val_a_den_sol = new_val_a_den // common_a

        Fb_str = _format_fraction(val_b_num_sol, val_b_den_sol)
        Fa_str = _format_fraction(val_a_num_sol, val_a_den_sol)

        solution_text += r"\\${integral_formula} = [{antideriv}]_{{{a}}}^{{{b}}} = ({Fb}) - ({Fa}) = {integral_val}$".replace("{integral_formula}", integral_formula).replace("{antideriv}", antiderivative_str_raw).replace("{a}", str(a)).replace("{b}", str(b)).replace("{Fb}", Fb_str).replace("{Fa}", Fa_str).replace("{integral_val}", integral_val_str_sol)
        solution_text += r"\\區間長度為 $b-a = {b_val} - {a_val} = {length}$。"
        solution_text = solution_text.replace("{b_val}", str(b)).replace("{a_val}", str(a)).replace("{length}", str(b-a))
        solution_text += r"\\平均值 $k = \frac{1}{{length}} \times {integral_val} = {avg_val}$。".replace("{length}", str(b-a)).replace("{integral_val}", integral_val_str_sol).replace("{avg_val}", avg_val_str_sol)
        
        solution_text += r"\\接著，我們需要找到 $c$ 值使得 $f(c) = k$。"
        func_c_str_raw = func_str_raw.replace('x', 'c')
        solution_text += r"\\即 ${func_c} = {avg_val}$。"
        solution_text = solution_text.replace("{func_c}", func_c_str_raw).replace("{avg_val}", avg_val_str_sol)
        
        if degree == 1:
            solution_text += r"\\解此線性方程式可得 $c = {c_ans}$。"
            solution_text = solution_text.replace("{c_ans}", _format_fraction(correct_c_val.numerator, correct_c_val.denominator))

        elif degree == 2:
            solution_text += r"\\解此二次方程式可得 $c = {c_ans}$。"
            solution_text = solution_text.replace("{c_ans}", _format_fraction(correct_c_val.numerator, correct_c_val.denominator))
        
        solution_text += r"\\由於 $c = {c_ans}$ 位於區間 $[{a}, {b}]$ 內，所以這是符合條件的答案。"
        solution_text = solution_text.replace("{a}", str(a)).replace("{b}", str(b)).replace("{c_ans}", _format_fraction(correct_c_val.numerator, correct_c_val.denominator))
        
    return {
        "question_text": question_text,
        "correct_answer": correct_answer_val, # Pure data string
        "answer": solution_text, # Detailed explanation
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    import re, math
    import fractions
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        # Remove LaTeX math delimiters, non-numeric characters except for '/', '-', '.'
        # Keep '/' for fractions, '-' for negative numbers, '.' for decimals
        return re.sub(r'[\$\s\(\)\{\}\[\]\\a-zA-Z=,;:\u4e00-\u9fff]', '', s) 

    # [V18.13 Update] 支援中英文是非題互通 - Not applicable for numerical answers here, but kept for template adherence.
    u_str = str(user_answer).strip()
    c_str = str(correct_answer).strip()
    
    yes_group = ["是", "yes", "true", "1", "o", "right"]
    no_group = ["否", "no", "false", "0", "x", "wrong"]
    
    # Check for boolean/yes-no type answers first
    if c_str.lower() in yes_group:
        return {"correct": u_str.lower() in yes_group, "result": "正確！" if u_str.lower() in yes_group else "答案錯誤"}
    if c_str.lower() in no_group:
        return {"correct": u_str.lower() in no_group, "result": "正確！" if u_str.lower() in no_group else "答案錯誤"}

    # 3. 數值與字串比對
    try:
        # 解析分數與浮點數
        def parse_numeric(v):
            # Attempt to parse as a fraction first
            try:
                return fractions.Fraction(v)
            except ValueError:
                # If it's not a simple fraction, try float
                return float(v)
        
        u_val_raw = clean(u_str)
        c_val_raw = clean(c_str)

        u_parsed = parse_numeric(u_val_raw)
        c_parsed = parse_numeric(c_val_raw)

        # Compare fractions directly if both are fractions
        if isinstance(u_parsed, fractions.Fraction) and isinstance(c_parsed, fractions.Fraction):
            if u_parsed == c_parsed:
                return {"correct": True, "result": "正確！"}
        
        # Fallback to float comparison for mixed types or if fraction comparison isn't exact enough (e.g., repeating decimals)
        # Use float() on fractions for comparison if they are not directly equal
        u_float = float(u_parsed)
        c_float = float(c_parsed)
        
        if math.isclose(u_float, c_float, rel_tol=1e-5, abs_tol=1e-9):
            return {"correct": True, "result": "正確！"}
    except (ValueError, ZeroDivisionError):
        pass # Fall through to string comparison if numeric parsing fails
        
    # Final fallback: strict string comparison after cleaning
    if clean(u_str) == clean(c_str): 
        return {"correct": True, "result": "正確！"}
    
    return {"correct": False, "result": f"答案錯誤。"}


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
                # 僅針對「文字反斜線+n」進行物理換行替換，不進行全局編碼轉換
                import re
                # 解決 r-string 導致的 \n 問題
                res['question_text'] = re.sub(r'\n', '\n', res['question_text'])
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則：若答案包含複雜運算符號，強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            # [V13.1 修復] 移除 '(' 與 ','，允許座標與數列使用純文字輸入
            triggers = ['^', '/', '|', '[', '{', '\\']
            
            # [V11.1 Refined] 僅在題目尚未包含提示時注入，避免重複堆疊
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
                # 若 answer 不存在或為空字串，強制同步 correct_answer
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
