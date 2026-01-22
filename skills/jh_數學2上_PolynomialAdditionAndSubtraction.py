# ==============================================================================
# ID: jh_數學2上_PolynomialAdditionAndSubtraction
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 74.51s | RAG: 5 examples
# Created At: 2026-01-18 14:32:31
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

# --- Helper Functions ---

def _normalize_coeffs(coeffs):
    """
    Removes leading zeros from a list of polynomial coefficients.
    If all coefficients are zero, returns [0].
    Example: [0, 0, 3, -1] -> [3, -1]
    Example: [0, 0, 0] -> [0]
    Example: [] -> [0]
    """
    if not coeffs:
        return [0]
    
    first_non_zero_idx = 0
    for i, c in enumerate(coeffs):
        if c != 0:
            first_non_zero_idx = i
            break
    else: # All coeffs are zero
        return [0]
    
    return coeffs[first_non_zero_idx:]

def _format_polynomial_string(coefficients, variable):
    """
    Converts a list of coefficients (descending order) into a LaTeX formatted polynomial string.
    Follows Architect's example for spacing: "3x^2 - 2x + 1".
    Returns raw LaTeX string WITHOUT dollar signs.
    """
    normalized_coeffs = _normalize_coeffs(coefficients) # Ensure coeffs are normalized before formatting
    if not normalized_coeffs or all(c == 0 for c in normalized_coeffs):
        return "0"

    terms = []
    max_degree = len(normalized_coeffs) - 1

    for i, coeff in enumerate(normalized_coeffs):
        degree = max_degree - i
        if coeff == 0:
            continue

        term_str_val = ""
        abs_coeff = abs(coeff)

        # Handle coefficient value: always show for constants, or if not 1/-1
        if degree == 0 or abs_coeff != 1:
            term_str_val += str(abs_coeff)

        # Handle variable and degree
        if degree > 0:
            term_str_val += variable
            if degree > 1:
                term_str_val += r"^{" + str(degree) + r"}"
        
        # Prepend sign with space if it's not the very first term and is positive
        if coeff > 0 and len(terms) > 0:
            terms.append("+ " + term_str_val)
        elif coeff < 0:
            # If it's the first term and negative, just prepend '-'
            if len(terms) == 0:
                terms.append("-" + term_str_val)
            else: # If not the first term and negative, prepend '- '
                terms.append("- " + term_str_val)
        else: # Positive first term (coeff > 0 and len(terms) == 0)
            terms.append(term_str_val)

    # Concatenate terms to form the final polynomial string
    final_poly_str = "".join(terms)
    
    return final_poly_str

def _generate_polynomial_coeffs(max_degree, variable):
    """
    Generates a list of coefficients and its formatted string for a polynomial.
    Ensures at least one non-zero coefficient.
    """
    coeffs = [0] * (max_degree + 1)
    
    # Generate coefficients, ensuring at least one non-zero coefficient initially
    has_non_zero = False
    for i in range(max_degree + 1):
        coeffs[i] = random.randint(-9, 9)
        if coeffs[i] != 0:
            has_non_zero = True
    
    # If all coefficients turned out to be zero, regenerate at least one to be non-zero
    if not has_non_zero:
        coeffs[random.randint(0, max_degree)] = random.choice([-9, -8, -7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9])
            
    # Normalize to remove leading zeros before formatting.
    normalized_coeffs = _normalize_coeffs(coeffs)
    formatted_string = _format_polynomial_string(normalized_coeffs, variable)
    
    return normalized_coeffs, formatted_string

def _add_polynomial_coeffs(coeffs1, coeffs2):
    """Adds two lists of polynomial coefficients."""
    max_len = max(len(coeffs1), len(coeffs2))
    padded_coeffs1 = [0] * (max_len - len(coeffs1)) + coeffs1
    padded_coeffs2 = [0] * (max_len - len(coeffs2)) + coeffs2
    
    result_coeffs = [c1 + c2 for c1, c2 in zip(padded_coeffs1, padded_coeffs2)]
    return _normalize_coeffs(result_coeffs)

def _subtract_polynomial_coeffs(coeffs1, coeffs2):
    """Subtracts the second list of polynomial coefficients from the first (coeffs1 - coeffs2)."""
    max_len = max(len(coeffs1), len(coeffs2))
    padded_coeffs1 = [0] * (max_len - len(coeffs1)) + coeffs1
    padded_coeffs2 = [0] * (max_len - len(coeffs2)) + coeffs2
    
    result_coeffs = [c1 - c2 for c1, c2 in zip(padded_coeffs1, padded_coeffs2)]
    return _normalize_coeffs(result_coeffs)

# --- Main Generation Function ---

def generate(level=1):
    problem_type = random.choice([1, 2, 3]) # Randomly choose problem type

    variable = random.choice(['x', 'y', 'a', 'b'])
    
    question_text = ""
    correct_answer = ""
    solution_text = ""

    # --- Type 1: Sum/Difference of two polynomials ---
    # Maps to RAG Ex 1, 2
    if problem_type == 1:
        max_degree_A = random.randint(2, 4)
        max_degree_B = random.randint(2, 4)
        
        coeffs_A, poly_A_str = _generate_polynomial_coeffs(max_degree_A, variable)
        coeffs_B, poly_B_str = _generate_polynomial_coeffs(max_degree_B, variable)
        
        operation = random.choice(['+', '-'])
        
        if operation == '+':
            result_coeffs = _add_polynomial_coeffs(coeffs_A, coeffs_B)
            # FORCE INLINE MATH: Wrap everything in single $
            question_text_template = r"計算 $({P_A}) + ({P_B})$。"
            question_text = question_text_template.replace("{P_A}", poly_A_str).replace("{P_B}", poly_B_str)
            solution_text_template = r"$({P_A}) + ({P_B}) = {R_S}$"
        else: # operation == '-'
            result_coeffs = _subtract_polynomial_coeffs(coeffs_A, coeffs_B)
            question_text_template = r"計算 $({P_A}) - ({P_B})$。"
            question_text = question_text_template.replace("{P_A}", poly_A_str).replace("{P_B}", poly_B_str)
            solution_text_template = r"$({P_A}) - ({P_B}) = {R_S}$"
        
        result_poly_str = _format_polynomial_string(result_coeffs, variable)
        solution_text = solution_text_template.replace("{P_A}", poly_A_str).replace("{P_B}", poly_B_str).replace("{R_S}", result_poly_str)
        correct_answer = ",".join(map(str, result_coeffs))

    # --- Type 2: Polynomial addition/subtraction with parentheses ---
    # Maps to RAG Ex 3, 4 (interpreted as more complex bracketed operations as per spec)
    elif problem_type == 2:
        max_degree_val = random.randint(2, 3)
        coeffs_A, poly_A_str = _generate_polynomial_coeffs(max_degree_val, variable)
        coeffs_B, poly_B_str = _generate_polynomial_coeffs(max_degree_val, variable)
        coeffs_C, poly_C_str = _generate_polynomial_coeffs(max_degree_val, variable)

        scenario = random.choice([1, 2, 3, 4])
        
        if scenario == 1: # A - (B + C)
            temp_coeffs = _add_polynomial_coeffs(coeffs_B, coeffs_C)
            result_coeffs = _subtract_polynomial_coeffs(coeffs_A, temp_coeffs)
            question_text_template = r"計算 $({P_A}) - [({P_B}) + ({P_C})]$。"
            question_text = question_text_template.replace("{P_A}", poly_A_str).replace("{P_B}", poly_B_str).replace("{P_C}", poly_C_str)
            solution_text_template = r"$({P_A}) - [({P_B}) + ({P_C})] = {R_S}$"
        elif scenario == 2: # A + (B - C)
            temp_coeffs = _subtract_polynomial_coeffs(coeffs_B, coeffs_C)
            result_coeffs = _add_polynomial_coeffs(coeffs_A, temp_coeffs)
            question_text_template = r"計算 $({P_A}) + [({P_B}) - ({P_C})]$。"
            question_text = question_text_template.replace("{P_A}", poly_A_str).replace("{P_B}", poly_B_str).replace("{P_C}", poly_C_str)
            solution_text_template = r"$({P_A}) + [({P_B}) - ({P_C})] = {R_S}$"
        elif scenario == 3: # (A + B) - C
            temp_coeffs = _add_polynomial_coeffs(coeffs_A, coeffs_B)
            result_coeffs = _subtract_polynomial_coeffs(temp_coeffs, coeffs_C)
            question_text_template = r"計算 $[({P_A}) + ({P_B})] - ({P_C})$。"
            question_text = question_text_template.replace("{P_A}", poly_A_str).replace("{P_B}", poly_B_str).replace("{P_C}", poly_C_str)
            solution_text_template = r"$[({P_A}) + ({P_B})] - ({P_C}) = {R_S}$"
        else: # (A - B) + C
            temp_coeffs = _subtract_polynomial_coeffs(coeffs_A, coeffs_B)
            result_coeffs = _add_polynomial_coeffs(temp_coeffs, coeffs_C)
            question_text_template = r"計算 $[({P_A}) - ({P_B})] + ({P_C})$。"
            question_text = question_text_template.replace("{P_A}", poly_A_str).replace("{P_B}", poly_B_str).replace("{P_C}", poly_C_str)
            solution_text_template = r"$[({P_A}) - ({P_B})] + ({P_C}) = {R_S}$"

        result_poly_str = _format_polynomial_string(result_coeffs, variable)
        solution_text = solution_text_template.replace("{P_A}", poly_A_str).replace("{P_B}", poly_B_str).replace("{P_C}", poly_C_str).replace("{R_S}", result_poly_str)
        correct_answer = ",".join(map(str, result_coeffs))

    # --- Type 3: Solve for unknown polynomial ---
    # Maps to RAG Ex 5
    else: # problem_type == 3
        max_degree_val = random.randint(2, 3)
        coeffs_A, poly_A_str = _generate_polynomial_coeffs(max_degree_val, variable)
        coeffs_B, poly_B_str = _generate_polynomial_coeffs(max_degree_val, variable)
        
        scenario = random.choice([1, 2])

        if scenario == 1: # P + A = B  => P = B - A
            result_coeffs = _subtract_polynomial_coeffs(coeffs_B, coeffs_A)
            question_text_template = r"若 $P + ({P_A}) = ({P_B})$，則 $P = ?$。"
            question_text = question_text_template.replace("{P_A}", poly_A_str).replace("{P_B}", poly_B_str)
            solution_text_template = r"$P = ({P_B}) - ({P_A}) = {R_S}$"
        else: # A - P = B  => P = A - B
            result_coeffs = _subtract_polynomial_coeffs(coeffs_A, coeffs_B)
            question_text_template = r"若 $({P_A}) - P = ({P_B})$，則 $P = ?$。"
            question_text = question_text_template.replace("{P_A}", poly_A_str).replace("{P_B}", poly_B_str)
            solution_text_template = r"$P = ({P_A}) - ({P_B}) = {R_S}$"

        result_poly_str = _format_polynomial_string(result_coeffs, variable)
        solution_text = solution_text_template.replace("{P_A}", poly_A_str).replace("{P_B}", poly_B_str).replace("{R_S}", result_poly_str)
        correct_answer = ",".join(map(str, result_coeffs))

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,  # Raw data: comma-separated coefficient string
        "answer_display": solution_text,  # Detailed solution text with LaTeX
        "image_base64": None,  # No graphics for this problem type
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

# --- Check Function ---


    """
    Checks if the user's answer (polynomial string or coefficient list)
    is equivalent to the correct answer (coefficient list).
    """
    # This helper function is defined locally to ensure no global state issues with importlib.reload
    def _local_parse_polynomial_string_to_coeffs(poly_str_input):
        # Clean and normalize input string
        poly_str = poly_str_input.strip().lower()
        poly_str = re.sub(r'[\$\{\}\\\=\[\]]', '', poly_str) # Remove LaTeX symbols
        poly_str = re.sub(r'\s+', '', poly_str) # Remove all whitespace
        
        if not poly_str:
            return [0]

        # Replace any variable (a, b, y) with 'x' for consistent parsing
        poly_str = re.sub(r'[aby]', 'x', poly_str)

        # Add implicit '1' for terms like 'x^2', 'x', '-x'
        # 1. Handle 'x' at the start or not preceded by a digit or sign (e.g., 'x^2' becomes '1x^2')
        poly_str = re.sub(r'(?<!\d)(?<![+-])x', '1x', poly_str)
        # 2. Handle '+x' or '-x' (e.g., '+x^2' becomes '+1x^2', '-x' becomes '-1x')
        poly_str = re.sub(r'([+-])x', r'\11x', poly_str)
        
        terms_map = {} # degree -> coefficient

        # Split into terms: numbers with optional 'x' and '^degree'
        # Regex breakdown:
        # ([+-]?) : Optional sign (+ or -)
        # (\d*)   : Optional digits (coefficient)
        # (x?)    : Optional 'x'
        # (?:\^(\d+))? : Optional non-capturing group for '^' followed by digits (degree)
        term_pattern = r'([+-]?)(\d*)(x?)(?:\^(\d+))?'
        matches = re.findall(term_pattern, poly_str)
        
        # If nothing matched, maybe it was just a constant like "5" or "-3"
        if not matches:
            if re.fullmatch(r'([+-]?\d+)', poly_str):
                try:
                    return _normalize_coeffs([int(poly_str)])
                except ValueError:
                    return [0]
            return [0] # If still no matches, it's unparseable

        for sign_str, coeff_str, var_char, degree_str in matches:
            if not (sign_str or coeff_str or var_char or degree_str): # Skip empty matches
                continue

            coeff_val = 0
            
            # Determine coefficient
            if coeff_str:
                coeff_val = int(coeff_str)
            elif var_char: # If 'x' is present but no explicit coefficient (e.g., "x" already converted to "1x")
                coeff_val = 1 # Should be 1 due to prior re.sub, but as a safeguard
            else: # Must be a constant (no 'x' and no explicit coefficient, like "5")
                # This case is when coeff_str is empty but it's a constant.
                # E.g. for "5", matches is [('', '5', '', '')]. coeff_str is '5', so this block is skipped.
                # If there's no coeff_str and no var_char, it's not a valid term here.
                continue

            if sign_str == '-':
                coeff_val *= -1
            
            # Determine degree
            degree = 0
            if var_char:
                degree = int(degree_str) if degree_str else 1
            else:
                degree = 0 # Constant term

            terms_map[degree] = terms_map.get(degree, 0) + coeff_val

        max_degree = max(terms_map.keys()) if terms_map else 0
        parsed_coeffs = []
        for d in range(max_degree, -1, -1):
            parsed_coeffs.append(int(round(terms_map.get(d, 0))))
        
        return _normalize_coeffs(parsed_coeffs)

    # 1. Try to parse user_answer as a comma-separated list of numbers (direct coefficient input)
    user_coeffs = []
    try:
        # Check if it looks like a comma-separated list
        if re.match(r'^[+-]?\d+(,\s*[+-]?\d+)*$', user_answer.strip()):
            user_coeffs = [int(float(c)) for c in user_answer.split(',') if c.strip()]
            user_coeffs = _normalize_coeffs(user_coeffs)
        else:
            # Otherwise, treat as a polynomial string and parse it
            user_coeffs = _local_parse_polynomial_string_to_coeffs(user_answer)
    except Exception:
        # If any parsing fails, default to [0] to ensure comparison
        user_coeffs = [0]


    # 2. Parse correct answer's coefficient sequence (guaranteed "num1,num2,num3" format)
    correct_coeffs_str_list = correct_answer.split(',')
    correct_coeffs = [int(c.strip()) for c in correct_coeffs_str_list if c.strip()]
    correct_coeffs = _normalize_coeffs(correct_coeffs)

    # 3. Numerical Sequence Comparison
    is_correct = (user_coeffs == correct_coeffs)

    return is_correct


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
