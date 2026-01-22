# ==============================================================================
# ID: jh_數學2上_PolynomialFactorAndMultiple
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 96.29s | RAG: 2 examples
# Created At: 2026-01-18 21:59:30
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
from datetime import datetime
 # Added for math.isclose in check function

# Helper function to format polynomial strings for display
# This function takes a list of coefficients [a_n, a_{n-1}, ..., a_1, a_0]
# and returns a LaTeX string representation of the polynomial.
def _format_poly(coeffs, var='x'):
    terms = []
    degree = len(coeffs) - 1
    
    # Handle the zero polynomial case
    if not coeffs or all(c == 0 for c in coeffs):
        return "0"

    for i, coeff in enumerate(coeffs):
        if coeff == 0:
            continue
        
        current_degree = degree - i
        term_str = ""
        
        # Coefficient part
        coeff_abs = abs(coeff)
        
        # Variable part
        if current_degree == 0: # Constant term
            term_str = str(coeff_abs)
        elif current_degree == 1: # x term
            term_str = var
        else: # x^n term (n > 1)
            term_str = var + r"^{" + str(current_degree) + r"}"
        
        # Combine coefficient and variable part, handling signs and '1' coefficients
        if coeff_abs != 1 or current_degree == 0: # If coeff is not 1/-1 or it's a constant
            term_str = str(coeff_abs) + term_str
        
        # Add sign for the term
        if coeff > 0:
            if terms: # If not the first term, prepend '+'
                terms.append(" + " + term_str)
            else: # First term, no '+'
                terms.append(term_str)
        else: # coeff < 0
            if terms: # If not the first term, prepend '-'
                terms.append(" - " + term_str)
            else: # First term, prepend '-'
                terms.append("-" + term_str)
                
    return "".join(terms).replace("+ -", "- ") # Clean up " + - " to " - "

# Helper function to parse a polynomial string into coefficients
# This is a basic parser and assumes well-formatted polynomials like "x^2+2x-3" or "2x-3"
def _parse_poly_str_to_coeffs(poly_str):
    poly_str = poly_str.replace(' ', '').lower()
    if not poly_str:
        return [0]

    # Handle single 'x' or 'ax' or a constant number
    if poly_str == 'x': return [1, 0]
    if poly_str == '-x': return [-1, 0]
    if re.fullmatch(r'-?\d+', poly_str): return [int(poly_str)]
    if re.fullmatch(r'-?\d*x', poly_str): # e.g. 2x, -3x, x
        coeff_part = poly_str.replace('x', '')
        if coeff_part == '': coeff = 1
        elif coeff_part == '-': coeff = -1
        else: coeff = int(coeff_part)
        return [coeff, 0]

    # Normalize signs for splitting
    poly_str = poly_str.replace('-', '+-')
    terms = [t for t in poly_str.split('+') if t]
    
    coeffs_dict = {}
    
    for term in terms:
        term = term.strip()
        if not term:
            continue
            
        coeff = 1
        degree = 0
        
        if 'x' in term:
            parts = term.split('x')
            coeff_part = parts[0]
            if coeff_part == '-':
                coeff = -1
            elif coeff_part and coeff_part != '-':
                coeff = int(coeff_part)
            elif not coeff_part: # "x" or "+x"
                coeff = 1
            
            if '^' in term:
                degree = int(parts[1].replace('^', '').replace('{', '').replace('}', ''))
            else:
                degree = 1
        else: # Constant term
            coeff = int(term)
            degree = 0
            
        coeffs_dict[degree] = coeffs_dict.get(degree, 0) + coeff

    max_degree = max(coeffs_dict.keys()) if coeffs_dict else 0
    
    # Fill in missing degrees with 0
    coeffs = [0] * (max_degree + 1)
    for deg, val in coeffs_dict.items():
        coeffs[max_degree - deg] = val
        
    return coeffs

# Helper function to multiply two polynomials (represented by coefficient lists)
def _multiply_polys(poly1_coeffs, poly2_coeffs):
    if not poly1_coeffs or all(c == 0 for c in poly1_coeffs): poly1_coeffs = [0]
    if not poly2_coeffs or all(c == 0 for c in poly2_coeffs): poly2_coeffs = [0]

    # Handle cases where one poly is just [0]
    if poly1_coeffs == [0] or poly2_coeffs == [0]:
        return [0]

    deg1 = len(poly1_coeffs) - 1
    deg2 = len(poly2_coeffs) - 1
    result_deg = deg1 + deg2
    result_coeffs = [0] * (result_deg + 1)

    for i, c1 in enumerate(poly1_coeffs):
        for j, c2 in enumerate(poly2_coeffs):
            result_coeffs[i + j] += c1 * c2
            
    # Remove leading zeros if not just '0'
    while len(result_coeffs) > 1 and result_coeffs[0] == 0:
        result_coeffs.pop(0)
            
    return result_coeffs

# Robust helper for Type 2 check: expands factorization string to coefficient list
def _expand_factors_to_coeffs(factor_str_raw):
    # 1. Basic Cleaning and Standardization
    factor_str = factor_str_raw.replace(' ', '').lower()
    
    # Handle implicit multiplication: e.g., "x(2x+3)" -> "(x)*(2x+3)" ; "(x-1)(x+2)" -> "(x-1)*(x+2)"
    factor_str = factor_str.replace('x(', '(x)*(').replace(')(', ')*(')
    
    # If it starts with a number like "2(x+1)", convert to "2*(x+1)"
    factor_str = re.sub(r'^(\d+)\(', r'\1*(', factor_str)
    factor_str = re.sub(r'^-(\d+)\(', r'-\1*(', factor_str) # Handle -2(x+1)

    # Handle powers: (x+a)^2 -> (x+a)*(x+a)
    def expand_power(match):
        base = match.group(1)
        power = int(match.group(2))
        return '*'.join([base] * power)
    factor_str = re.sub(r'(\([^\)]+\))\^(\d+)', expand_power, factor_str)

    # Now split by '*' to get individual terms/factors
    components = factor_str.split('*')
    
    # Initialize with a constant 1 polynomial
    current_poly_coeffs = [1] 

    for comp in components:
        comp = comp.strip()
        if not comp:
            continue
            
        coeffs_to_multiply = []
        
        # Handle constants (e.g., from leading common factor like 2)
        if re.fullmatch(r'-?\d+', comp):
            coeffs_to_multiply = [int(comp)]
        # Handle simple 'x' or 'ax'
        elif re.fullmatch(r'-?\d*x', comp):
            coeffs_to_multiply = _parse_poly_str_to_coeffs(comp)
        # Handle parenthesized expressions like (x+a), (ax+b)
        elif re.fullmatch(r'\([^\)]+\)', comp):
            inner_poly_str = comp.strip('()')
            coeffs_to_multiply = _parse_poly_str_to_coeffs(inner_poly_str)
        else:
            # Fallback: try parsing as a general poly (might happen if user enters e.g. "x^2+2x+1" directly for factorization)
            coeffs_to_multiply = _parse_poly_str_to_coeffs(comp)
            
        current_poly_coeffs = _multiply_polys(current_poly_coeffs, coeffs_to_multiply)
            
    # Normalize coefficients (remove leading zeros if not just '0')
    while len(current_poly_coeffs) > 1 and current_poly_coeffs[0] == 0:
        current_poly_coeffs.pop(0)
    
    return current_poly_coeffs

# The `check` function provided by the architect's spec, adapted.

    # 1. Input Sanitization
    user_answer_cleaned = re.sub(r'[$\\\{\}]|x=|y=|k=|Ans:|ans:|答案:|\s+', '', str(user_answer)).lower()
    correct_answer_cleaned = re.sub(r'[$\\\{\}]|x=|y=|k=|Ans:|ans:|答案:|\s+', '', str(correct_answer)).lower()

    # 2. Robust Check Logic based on problem type
    if correct_answer_cleaned in ["是", "否"]: # Type 1: Yes/No questions
        if correct_answer_cleaned == "是" and user_answer_cleaned in ["是", "yes", "對"]:
            return True
        elif correct_answer_cleaned == "否" and user_answer_cleaned in ["否", "no", "錯"]:
            return True
        else:
            return False
    # Type 3: Numeric answer (k value). Check if it's purely numeric (can be negative)
    # This regex ensures it's a number, optionally starting with '-'
    elif re.fullmatch(r'-?\d+', correct_answer_cleaned):
        try:
            return math.isclose(float(user_answer_cleaned), float(correct_answer_cleaned), rel_tol=1e-5)
        except ValueError:
            return False
    else: # Type 2: Factorization (more complex string comparison)
        try:
            user_coeffs = _expand_factors_to_coeffs(user_answer_cleaned)
            correct_coeffs = _expand_factors_to_coeffs(correct_answer_cleaned)
            return user_coeffs == correct_coeffs
        except Exception as e:
            # In a production environment, this might log the error.
            # print(f"Error during factorization comparison: {e}") 
            return False


def generate(level=1):
    problem_type = random.choice([1, 2, 3])
    question_text = ""
    correct_answer = ""
    
    if problem_type == 1:
        # Type 1: Identifying Factors/Multiples (Maps to Example 1)
        
        # Coefficients for the factor (ax+b)
        a_val = random.randint(1, 3) * random.choice([-1, 1])
        b_val = random.randint(1, 5) * random.choice([-1, 1])
        while b_val == 0: b_val = random.randint(1, 5) * random.choice([-1, 1]) # Ensure b is non-zero
        
        factor_poly_coeffs = [a_val, b_val] # e.g., ax+b
        factor_poly_str = _format_poly(factor_poly_coeffs)

        # Coefficients for the quotient (cx+d)
        q_val_coeffs_c = random.randint(1, 2) * random.choice([-1, 1])
        q_val_coeffs_d = random.randint(-3, 3)
        
        quotient_poly_coeffs = [q_val_coeffs_c, q_val_coeffs_d] # e.g., cx+d

        # Multiply them to get the base target polynomial: (ax+b)(cx+d)
        target_poly_coeffs_base = _multiply_polys(factor_poly_coeffs, quotient_poly_coeffs)
        target_poly_str_base = _format_poly(target_poly_coeffs_base)

        is_factor_case = random.choice([True, False])
        if is_factor_case:
            # P(x) is a factor of Q(x)
            question_text_template = r"判斷多項式 $ {factor_p} $ 是否為 $ {target_p} $ 的因式？"
            question_text = question_text_template.replace("{factor_p}", factor_poly_str).replace("{target_p}", target_poly_str_base)
            correct_answer = "是"
        else:
            # P(x) is NOT a factor of Q(x)
            remainder = random.randint(1, 5) * random.choice([-1, 1])
            # Add remainder to the constant term of the target polynomial
            target_poly_coeffs_modified = list(target_poly_coeffs_base) # Create a mutable copy
            
            # Ensure the list is not empty before modifying the last element
            if not target_poly_coeffs_modified or target_poly_coeffs_modified == [0]:
                target_poly_coeffs_modified = [remainder]
            else:
                target_poly_coeffs_modified[-1] += remainder
            
            target_poly_with_remainder_str = _format_poly(target_poly_coeffs_modified)
            
            question_text_template = r"判斷多項式 $ {factor_p} $ 是否為 $ {target_p} $ 的因式？"
            question_text = question_text_template.replace("{factor_p}", factor_poly_str).replace("{target_p}", target_poly_with_remainder_str)
            correct_answer = "否"

    elif problem_type == 2:
        # Type 2: Simple Polynomial Factorization (Maps to Example 2, 3, 4)
        sub_type = random.choice([1, 2, 3, 4])

        if sub_type == 1: # Common Factor: ax^2 + bx (or ax^3 + bx^2)
            a = random.randint(2, 8) * random.choice([-1, 1])
            b = random.randint(1, 8) * random.choice([-1, 1])
            while b == 0: b = random.randint(1, 8) * random.choice([-1, 1])
            
            degree_choice = random.choice([2, 3]) # ax^2+bx or ax^3+bx^2
            
            if degree_choice == 2:
                question_poly_coeffs = [a, b, 0] # ax^2 + bx
                question_poly_str = _format_poly(question_poly_coeffs)
                
                # Canonical form for check: x(ax+b)
                factor_inner_str = _format_poly([a, b])
                correct_answer = r"x({inner})".replace("{inner}", factor_inner_str)
            else: # ax^3 + bx^2
                question_poly_coeffs = [a, b, 0, 0] # ax^3 + bx^2
                question_poly_str = _format_poly(question_poly_coeffs)
                
                # Canonical form for check: x^2(ax+b)
                factor_inner_str = _format_poly([a, b])
                correct_answer = r"x^2({inner})".replace("{inner}", factor_inner_str)


        elif sub_type == 2: # Difference of Squares: x^2 - a^2 or (ax)^2 - b^2
            a_val = random.randint(2, 9)
            
            # Decide if it's x^2 - a^2 or (ax)^2 - b^2
            form_choice = random.choice([1, 2])
            
            if form_choice == 1: # x^2 - a^2
                question_poly_coeffs = [1, 0, -a_val*a_val] # x^2 - a^2
                question_poly_str = _format_poly(question_poly_coeffs)
                correct_answer = r"(x-{a})(x+{a})".replace("{a}", str(a_val))
            else: # (ax)^2 - b^2
                b_coeff = random.randint(2, 7) # For (bx)^2
                c_const = random.randint(2, 9) # For c^2
                
                # (bx)^2 - c^2
                question_poly_coeffs = [b_coeff*b_coeff, 0, -c_const*c_const]
                question_poly_str = _format_poly(question_poly_coeffs)
                
                # Correct answer for (bx)^2 - c^2 is (bx-c)(bx+c)
                correct_answer = r"({bx}-{c})({bx}+{c})".replace("{bx}", str(b_coeff) + "x").replace("{c}", str(c_const))


        elif sub_type == 3: # Perfect Square Trinomial: x^2 +/- 2ax + a^2
            a = random.randint(1, 7)
            sign = random.choice([-1, 1])
            question_poly_coeffs = [1, 2*a*sign, a*a] # x^2 + 2ax + a^2 or x^2 - 2ax + a^2
            question_poly_str = _format_poly(question_poly_coeffs)
            
            if sign == 1:
                correct_answer = r"(x+{a})^2".replace("{a}", str(a))
            else:
                correct_answer = r"(x-{a})^2".replace("{a}", str(a))

        elif sub_type == 4: # Quadratic Trinomial (Cross-multiplication): x^2 + bx + c
            p = random.randint(-5, 5)
            q = random.randint(-5, 5)
            # Ensure p and q are distinct and not both zero.
            while p == q or (p == 0 and q == 0): 
                p = random.randint(-5, 5)
                q = random.randint(-5, 5)
            
            # Ensure p < q for canonical form
            if p > q: p, q = q, p

            question_poly_coeffs = [1, p+q, p*q] # x^2 + (p+q)x + pq
            question_poly_str = _format_poly(question_poly_coeffs)
            
            # Construct correct_answer string for _expand_factors_to_coeffs
            if p == 0:
                correct_answer = r"x(x+{q})".replace("{q}", str(q))
                if q < 0: correct_answer = correct_answer.replace(r"+{q}", str(q)) # x(x-3)
            else:
                factor1_str = r"x+{p}".replace("{p}", str(p))
                factor2_str = r"x+{q}".replace("{q}", str(q))
                # Handle negative numbers for display (x-3) not (x+-3)
                if p < 0: factor1_str = factor1_str.replace(r"+{p}", str(p))
                if q < 0: factor2_str = factor2_str.replace(r"+{q}", str(q))
                correct_answer = r"({f1})({f2})".replace("{f1}", factor1_str).replace("{f2}", factor2_str)
            
        question_template = r"因式分解下列多項式： $ {poly} $"
        question_text = question_template.replace("{poly}", question_poly_str)

    elif problem_type == 3:
        # Type 3: Finding Unknown Coefficients (Maps to Example 5)
        root_val = random.randint(-4, 4)
        while root_val == 0: # Ensure root is not zero for more varied problems
            root_val = random.randint(-4, 4)

        coeff_x2 = random.randint(1, 3) # Coefficient of x^2
        coeff_x = random.randint(-5, 5) # Coefficient of x
        
        # P(x) = coeff_x2 * x^2 + coeff_x * x + k
        # If (x - root_val) is a factor, then P(root_val) = 0
        # coeff_x2 * (root_val)^2 + coeff_x * root_val + k = 0
        # k = -(coeff_x2 * (root_val)^2 + coeff_x * root_val)
        
        k_val = -(coeff_x2 * (root_val**2) + coeff_x * root_val)
        
        # Ensure k_val is within a reasonable range and not trivially zero too often
        attempts = 0
        while (abs(k_val) > 20 or k_val == 0) and attempts < 10:
            root_val = random.randint(-4, 4)
            while root_val == 0: root_val = random.randint(-4, 4)
            coeff_x2 = random.randint(1, 3)
            coeff_x = random.randint(-5, 5)
            k_val = -(coeff_x2 * (root_val**2) + coeff_x * root_val)
            attempts += 1
        if attempts >= 10: # Fallback if loop doesn't find a suitable k
            k_val = random.choice([1, -1, 2, -2]) # Ensure k is non-zero and small

        # Display the polynomial correctly with k
        poly_display_parts = []
        
        # x^2 term
        poly_display_parts.append(str(coeff_x2) + r"x^2")
        
        # x term
        if coeff_x > 0:
            poly_display_parts.append(r" + " + str(coeff_x) + r"x")
        elif coeff_x < 0:
            poly_display_parts.append(r" - " + str(abs(coeff_x)) + r"x")
        
        # Constant term 'k'
        poly_display_parts.append(r" + k")
        
        poly_display_str = "".join(poly_display_parts)
        
        # Factor display (x - root_val)
        factor_display_str_template = r"x {sign} {val}"
        if root_val < 0:
            factor_display_str = factor_display_str_template.replace("{sign}", "+").replace("{val}", str(abs(root_val)))
        else:
            factor_display_str = factor_display_str_template.replace("{sign}", "-").replace("{val}", str(root_val))

        question_template = r"如果 $ {factor} $ 是多項式 $ {poly} $ 的因式，那麼 $k$ 的值是多少？"
        question_text = question_template.replace("{factor}", factor_display_str).replace("{poly}", poly_display_str)
        correct_answer = str(k_val)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "",
        "image_base64": None,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
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
