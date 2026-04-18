# ==============================================================================
# ID: jh_數學2上_PolynomialDivision
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 101.28s | RAG: 5 examples
# Created At: 2026-01-18 14:47:56
# Fix Status: [Repaired]
# Fixes: Regex=1, Logic=0
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
from fractions import Fraction



def poly_to_str(coeffs, var='x'):
    """
    Converts a list of polynomial coefficients to a string representation.
    Coefficients are ordered from highest degree to lowest degree.
    Uses standard arithmetic operators with proper spacing for LaTeX.
    e.g., [1, 2, 3] -> "x^2 + 2x + 3"
          [-1, 0, 5] -> "-x^2 + 5"
    """
    parts = []
    degree = len(coeffs) - 1
    
    if not coeffs or all(c == 0 for c in coeffs):
        return "0"

    for i, c in enumerate(coeffs):
        if c == 0:
            continue
        
        current_degree = degree - i
        
        term_str = ""
        
        # Determine sign and spacing
        if c > 0:
            if parts: # Not the first term and positive, prepend ' + '
                term_str += " + "
        else: # c < 0
            if parts: # Not the first term and negative, prepend ' - '
                term_str += " - "
            else: # First term negative, prepend '-'
                term_str += "-"
        
        abs_c = abs(c)
        
        # Coefficient part: omit '1' for non-constant terms, keep for constant terms
        if abs_c != 1 or current_degree == 0:
            term_str += str(abs_c)
        
        # Variable part
        if current_degree > 0:
            term_str += var
            if current_degree > 1:
                term_str += f"^{current_degree}"
        
        parts.append(term_str)
    
    return "".join(parts)

# Function to perform polynomial long division
def poly_div(dividend_coeffs, divisor_coeffs):
    """
    Performs polynomial long division and returns quotient and remainder coefficients.
    Coefficients are ordered from highest degree to lowest degree.
    """
    n = len(dividend_coeffs) - 1 # Degree of dividend
    m = len(divisor_coeffs) - 1 # Degree of divisor
    
    if m > n:
        return [0], dividend_coeffs # Quotient is 0, remainder is dividend
    
    if m == 0: # Divisor is a constant, e.g., [k]
        if divisor_coeffs[0] == 0:
            raise ValueError("Division by zero polynomial")
        quotient_coeffs = [c / divisor_coeffs[0] for c in dividend_coeffs]
        return [int(round(c)) for c in quotient_coeffs], [0]

    quotient_coeffs = [0.0] * (n - m + 1)
    remainder_coeffs = list(dividend_coeffs) # Copy to modify, use floats for intermediate calcs
    remainder_coeffs = [float(c) for c in remainder_coeffs]

    divisor_leading_coeff = float(divisor_coeffs[0])
    
    for i in range(n - m, -1, -1):
        current_dividend_leading_coeff = remainder_coeffs[i + m]
        
        if abs(current_dividend_leading_coeff) < 1e-9: # If leading term is effectively zero
            quotient_coeffs[i] = 0.0
            continue 
        
        quotient_term_coeff = current_dividend_leading_coeff / divisor_leading_coeff
        quotient_coeffs[i] = quotient_term_coeff
        
        # Subtract (quotient_term_coeff * x^i) * divisor from remainder
        for j in range(m + 1):
            remainder_coeffs[i + j] -= quotient_term_coeff * divisor_coeffs[j]
            
    # The remainder's degree must be less than the divisor's degree (m)
    final_remainder_coeffs = remainder_coeffs[:m] 
    
    # Remove leading zeros from quotient and remainder and convert to int if possible
    def clean_coeffs(coeffs_list):
        idx = 0
        # Find first non-zero coefficient
        while idx < len(coeffs_list) - 1 and abs(coeffs_list[idx]) < 1e-9:
            idx += 1
        
        if len(coeffs_list[idx:]) == 1 and abs(coeffs_list[idx]) < 1e-9: # If only a single 0 is left
            return [0]
        
        return [int(round(c)) if abs(round(c) - c) < 1e-9 else c for c in coeffs_list[idx:]]

    return clean_coeffs(quotient_coeffs), clean_coeffs(final_remainder_coeffs)


def generate(level=1, problem_type=None):
    """
    Generates a polynomial division problem based on the specified problem_type.
    Mirrors the mathematical models from RAG Examples 1-5.
    """
    # Level-based logic
    if problem_type is None:
        if level == 1:
            # Level 1: Monomial divisor or simple polynomial division
            problem_type = random.choice(["Type 1", "Type 2", "Type 3"])
        elif level == 2:
            # Level 2: Polynomial divisor (Long division)
            problem_type = random.choice(["Type 4", "Type 5"])
        else:
            # Level 3+: Same as level 2 but can be expanded for higher complexity later
            problem_type = random.choice(["Type 4", "Type 5"])

    problem_text = ""
    correct_answer = ""
    solution = "" # New solution field
    
    if problem_type == "Type 1": # Ex 1: 單項式除以單項式 (A*x^p) / (B*x^q)
        # Generate coefficients and exponents
        B = random.choice([1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7])
        A = B * random.choice([1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7, 8, -8, 9, -9, 10, -10])
        while A == 0: # Ensure A is not zero
             A = B * random.choice([1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7, 8, -8, 9, -9, 10, -10])

        p = random.randint(1, 3) # Max x^3
        q = random.randint(1, p) # q must be less than or equal to p
        
        # Helper to format monomial strings for problem display
        def format_monomial_input(coeff, power, var='x'):
            s = ""
            if coeff == 1:
                if power == 0: return "1" 
            elif coeff == -1:
                if power == 0: return "-1"
                else: s += "-"
            else:
                s += str(coeff)
            
            if power > 0:
                s += var
                if power > 1:
                    s += f"^{power}"
            if not s: s = "1"
            return s
        
        dividend_str = format_monomial_input(A, p)
        divisor_str = format_monomial_input(B, q)

        # Calculate result using Fractions for precise representation
        coeff_result = Fraction(A, B)
        exp_result = p - q
        
        result_str = ""
        coeff_str_part = ""
        if coeff_result.denominator == 1:
            coeff_str_part = str(coeff_result.numerator)
        else:
            coeff_str_part = f"{coeff_result.numerator}/{coeff_result.denominator}"

        if exp_result == 0: # Constant result
            result_str = coeff_str_part
        elif exp_result == 1: # x term
            if coeff_result == 1: result_str = "x"
            elif coeff_result == -1: result_str = "-x"
            else: result_str = f"{coeff_str_part}x"
        else: # x^N term (N > 1)
            if coeff_result == 1: result_str = f"x^{exp_result}"
            elif coeff_result == -1: result_str = f"-x^{exp_result}"
            else: result_str = f"{coeff_str_part}x^{exp_result}"

        # FIX: Inline math and parentheses
        problem_text = f"計算下列各式。 $({dividend_str}) \div ({divisor_str})$"
        correct_answer = result_str
        solution = f"$({dividend_str}) \div ({divisor_str}) = {result_str}$"
        
    elif problem_type in ["Type 2", "Type 3"]: # Ex 2 & 3: 多項式除以單項式 (ax^2 + bx + c) / (dx)
        # Generate divisor (dx)
        d = random.choice([1, -1, 2, -2, 3, -3, 4, -4, 5, -5])
        
        # Generate dividend (ax^2 + bx + c) ensuring 'a' and 'b' are multiples of 'd'
        # for simpler quotient terms (as seen in examples)
        a = d * random.choice([1, -1, 2, -2, 3, -3, 4, -4, 5, -5])
        b = d * random.choice([1, -1, 2, -2, 3, -3, 4, -4, 5, -5])
        c = random.choice([0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5]) # Remainder
        
        # For Type 3.1, there's often a remainder of 0. Introduce this randomness.
        if problem_type == "Type 3" and random.random() < 0.5: # 50% chance for remainder 0
             c = 0
        
        # Ensure dividend is at least linear (has an x or x^2 term)
        while a == 0 and b == 0:
            a = d * random.choice([1, -1, 2, -2, 3, -3, 4, -4, 5, -5])
            b = d * random.choice([1, -1, 2, -2, 3, -3, 4, -4, 5, -5])
        
        dividend_coeffs = [a, b, c] # ax^2 + bx + c
        divisor_coeffs = [d, 0]     # dx + 0
        
        dividend_str = poly_to_str(dividend_coeffs)
        divisor_str = poly_to_str(divisor_coeffs)

        quotient_coeffs, remainder_coeffs = poly_div(dividend_coeffs, divisor_coeffs)
        
        quotient_str = poly_to_str(quotient_coeffs)
        remainder_str = poly_to_str(remainder_coeffs)

        problem_text = f"求 $({dividend_str}) \div ({divisor_str})$ 的商式與餘式。"
        correct_answer = f"商式為 {quotient_str}，餘式為 {remainder_str}"
        solution = f"商式=${quotient_str}$，餘式=${remainder_str}$"

    elif problem_type in ["Type 4", "Type 5"]: # Ex 4 & 5: 多項式除以二項式 (ax^2 + bx + c) / (dx + e)
        # Generate divisor (dx + e)
        d_options = [1, -1] if problem_type == "Type 4" else [1, -1, 2, -2, 3, -3] # d=1 or -1 for Type 4
        d = random.choice(d_options)
        e = random.choice([1, -1, 2, -2, 3, -3, 4, -4])
        
        # Generate quotient (qx + r)
        q = random.choice([1, -1, 2, -2, 3, -3])
        r = random.choice([0, 1, -1, 2, -2, 3, -3, 4, -4]) # Constant term in quotient
        
        # Generate remainder (rem)
        rem = random.choice([0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7, 8, -8, 9, -9, 10, -10])
        if random.random() < 0.3: # 30% chance for remainder 0
            rem = 0

        # Calculate dividend coefficients from (dx+e)(qx+r) + rem
        # (d*q)x^2 + (d*r + e*q)x + (e*r + rem)
        a = d * q
        b = d * r + e * q
        c = e * r + rem
        
        dividend_coeffs = [a, b, c]
        divisor_coeffs = [d, e]

        dividend_str = poly_to_str(dividend_coeffs)
        divisor_str = poly_to_str(divisor_coeffs)

        quotient_coeffs, remainder_coeffs = poly_div(dividend_coeffs, divisor_coeffs)
        
        quotient_str = poly_to_str(quotient_coeffs)
        remainder_str = poly_to_str(remainder_coeffs)

        problem_text = f"求下列各多項式除法的商式與餘式。 $({dividend_str}) \div ({divisor_str})$"
        correct_answer = f"商式為 {quotient_str}，餘式為 {remainder_str}"
        solution = f"商式=${quotient_str}$，餘式=${remainder_str}$"
    
    else:
        # Fallback if problem_type is somehow not set (should be handled by level logic)
        return generate(level=level, problem_type="Type 1")

    return {
        "problem_text": problem_text, 
        "question_text": problem_text, # Standardize output key
        "correct_answer": correct_answer,
        "answer": solution,
        "image_base64": None, # No images required for these problems
    }

# Helper function to parse a polynomial string into a dictionary of coefficients
def _parse_poly_to_coeffs_dict(poly_str):
    """
    Parses a polynomial string (e.g., "x^2+2x-3") into a dictionary of {power: coefficient}.
    Handles 'x', 'x^1', '1x', '-x', '0', and constant terms.
    Returns None if parsing fails for non-polynomial, non-number string.
    """
    s = poly_str.replace(" ", "").replace("＋", "+").replace("－", "-")
    s = s.replace("x^1", "x").lower() # Normalize x^1 to x, and ensure variable is lowercase
    if not s: return {0: 0} # Empty string means 0

    # Ensure leading sign if missing for proper regex matching
    if s[0] not in ['+', '-'] and s != '0':
        s = '+' + s
    
    # Regex to find terms: [+-]? (coefficient) x ( ^power)? or [+-]? (constant)
    # This regex is robust for various forms of polynomial terms.
    terms = re.findall(r'([+-]?\d*x(?:\^\d+)?|[+-]?\d+)', s)
    coeffs_dict = {} # {power: coefficient}

    if not terms and s != '0': # If no terms found, it might be a single number like "5" or "-2"
        try:
            coeffs_dict[0] = int(s)
        except ValueError:
            return None # Parsing failed for non-polynomial, non-number string
    elif s == '0':
        coeffs_dict[0] = 0
    
    for term in terms:
        coeff_val = 1
        power_val = 0

        if 'x' in term:
            parts = term.split('x')
            coeff_str = parts[0]
            
            # Determine coefficient
            if coeff_str == '': coeff_val = 1
            elif coeff_str == '+': coeff_val = 1
            elif coeff_str == '-': coeff_val = -1
            else: coeff_val = int(coeff_str)
            
            # Determine power
            if len(parts) > 1 and parts[1]: # x^N
                power_val = int(parts[1].replace('^', ''))
            else: # x (power is 1)
                power_val = 1
        else: # Constant term
            coeff_val = int(term)
            power_val = 0
        
        coeffs_dict[power_val] = coeffs_dict.get(power_val, 0) + coeff_val
    
    # Remove zero coefficients, but keep {0:0} if it's the only term for "0"
    cleaned_coeffs = {p: c for p, c in coeffs_dict.items() if c != 0}
    if not cleaned_coeffs: # If all coeffs are zero (e.g., "x-x")
        return {0: 0}
    return cleaned_coeffs

def _compare_algebraic_expressions(user_expr, correct_expr):
    """
    Compares two algebraic expressions by converting them to a canonical
    coefficient dictionary representation and comparing the dictionaries.
    """
    user_coeffs = _parse_poly_to_coeffs_dict(user_expr)
    correct_coeffs = _parse_poly_to_coeffs_dict(correct_expr)

    if user_coeffs is None or correct_coeffs is None:
        # If parsing failed for either, fall back to simple string comparison
        return user_expr == correct_expr

    # Compare the dictionaries: first, check if they have the same set of powers
    if set(user_coeffs.keys()) != set(correct_coeffs.keys()):
        return False

    # Then, compare coefficients for each power using a tolerance for floats
    for power in user_coeffs:
        if not math.isclose(user_coeffs[power], correct_coeffs[power], rel_tol=1e-5):
            return False
            
    return True


    """
    Checks the user's answer against the correct answer.
    Handles both single algebraic expressions and "商式為...，餘式為..." formats.
    It uses robust algebraic comparison.
    """
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格, normalize signs)
    def clean_for_check(s):
        s = str(s).strip().replace(" ", "")
        s = s.replace("$", "").replace("\\", "")
        s = s.replace("＋", "+").replace("－", "-") # Normalize Chinese plus/minus
        s = re.sub(r'^[a-z]+=', '', s) # Remove k=, x=, y= prefixes
        return s
    
    user_answer_cleaned = clean_for_check(user_answer)
    correct_answer_cleaned = clean_for_check(correct_answer)
    
    # Special handling for "商式為 ...，餘式為 ..." format
    if "商式為" in correct_answer and "餘式為" in correct_answer:
        # Use regex to extract quotient and remainder from both user and correct answers
        c_match = re.match(r"商式為\s*(.*?)\s*，餘式為\s*(.*)", correct_answer_cleaned)
        u_match = re.match(r"商式為\s*(.*?)\s*，餘式為\s*(.*)", user_answer_cleaned)

        if not c_match or not u_match:
            # If parsing fails due to format mismatch, fall back to simple string comparison
            is_correct = user_answer_cleaned == correct_answer_cleaned
            return {"correct": is_correct, "result": "正確！" if is_correct else "答案錯誤。格式不符。"}
        
        c_q_raw = c_match.group(1).strip()
        c_r_raw = c_match.group(2).strip()
        u_q_raw = u_match.group(1).strip()
        u_r_raw = u_match.group(2).strip()

        # Compare quotient using robust algebraic comparison
        quotient_match = _compare_algebraic_expressions(u_q_raw, c_q_raw)

        # Compare remainder using robust algebraic comparison
        remainder_match = _compare_algebraic_expressions(u_r_raw, c_r_raw)

        if quotient_match and remainder_match:
            return {"correct": True, "result": "正確！"}
        else:
            return {"correct": False, "result": f"答案錯誤。商式或餘式不正確。"}

    else: # Single expression comparison (Type 1)
        # Try numerical comparison first if it's a simple number or fraction
        try:
            def parse_val_numeric(val_str):
                # Ensure the string is purely numeric or a fraction before attempting float conversion
                if re.fullmatch(r"^-?\d+(\.\d+)?$", val_str): # Integer or decimal
                    return float(val_str)
                elif re.fullmatch(r"^-?\d+/\d+$", val_str): # Fraction
                    n, d = map(float, val_str.split("/"))
                    return n/d
                raise ValueError("Not a simple numerical value") # Not a simple number/fraction
            
            u_val = parse_val_numeric(user_answer_cleaned)
            c_val = parse_val_numeric(correct_answer_cleaned)
            
            if math.isclose(u_val, c_val, rel_tol=1e-5):
                return {"correct": True, "result": "正確！"}
        except ValueError:
            pass # Not purely numerical, proceed to algebraic comparison
            
        # Fallback to algebraic expression comparison for polynomials
        if _compare_algebraic_expressions(user_answer_cleaned, correct_answer_cleaned):
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
            
            # 4. 確保欄位完整性
            if 'answer' not in res and 'correct_answer' in res:
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
