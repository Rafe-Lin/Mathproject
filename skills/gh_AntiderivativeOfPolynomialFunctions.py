# ==============================================================================
# ID: gh_AntiderivativeOfPolynomialFunctions
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 147.98s | RAG: 2 examples
# Created At: 2026-01-29 19:19:33
# Fix Status: [Repaired]
# Fixes: Regex=2, Logic=0
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



from datetime import datetime
import re # Required for check function, but good practice to have at top if helpers might use it

# --- Helper Functions ---

# Helper function to generate a polynomial term (coefficient, exponent)
# Ensures non-zero coefficient for main terms, and non-negative exponent
def _generate_polynomial_term(min_coeff=-8, max_coeff=8, min_exp=0, max_exp=5, allow_zero_coeff=False):
    coeff = random.randint(min_coeff, max_coeff)
    if not allow_zero_coeff:
        while coeff == 0: # Ensure coefficient is not zero for a displayed term
            coeff = random.randint(min_coeff, max_coeff)
    exp = random.randint(min_exp, max_exp)
    return coeff, exp

# Helper to format a polynomial term for LaTeX (e.g., "+3x^2" or "-5")
# is_first_term: if True, doesn't add leading '+' for positive terms.
def _format_term_latex(coeff, exp, is_first_term=False):
    if coeff == 0:
        return ""
    
    coeff_abs = abs(coeff)
    
    coeff_str = ""
    if exp == 0: # Constant term
        coeff_str = str(coeff_abs)
    elif coeff_abs == 1: # For x^n, not 1x^n
        coeff_str = ""
    else:
        coeff_str = str(coeff_abs)

    term_body = ""
    if exp == 0:
        term_body = coeff_str
    elif exp == 1:
        term_body = f"{coeff_str}x"
    else:
        term_body = f"{coeff_str}x^{exp}"
    
    if coeff > 0:
        return term_body if is_first_term else f"+{term_body}"
    else: # coeff < 0
        return f"-{term_body}"

# Helper to format the antiderivative term for LaTeX (e.g., "+\frac{1}{2}x^2" or "-3x")
# Takes original_coeff and original_exp from f(x)
def _format_antiderivative_term_latex(original_coeff, original_exp, is_first_term=False):
    if original_coeff == 0:
        return ""
    
    new_exp = original_exp + 1
    
    sign_str = "+" if original_coeff > 0 else "-"
    
    num = abs(original_coeff)
    den = new_exp
    
    # Simplify fraction
    common_divisor = math.gcd(num, den)
    num //= common_divisor
    den //= common_divisor
    
    coeff_str = ""
    if den == 1:
        coeff_str = str(num)
    else:
        coeff_str = r"\frac{" + str(num) + r"}{" + str(den) + r"}"

    term_body = ""
    if new_exp == 1:
        term_body = f"{coeff_str}x"
    else:
        term_body = f"{coeff_str}x^{new_exp}"
    
    if is_first_term:
        return term_body if original_coeff > 0 else f"-{term_body}"
    else:
        return f"{sign_str}{term_body}"

# Helper to get the numerical value of the antiderivative coefficient
def _get_antiderivative_coeff_value(coeff, exp):
    if coeff == 0:
        return 0.0
    new_exp = exp + 1
    return float(coeff) / new_exp


def generate(level=1):
    # [隨機分流]: 使用 random.choice 選擇題型變體
    # Problem type mapping adjusted to strictly mirror RAG examples and architect's spec descriptions.
    # 'monomial_general_antiderivative': Corresponds to Architect's Spec's *description* of Type 1 (單項式).
    # 'multi_term_general_antiderivative': Corresponds to RAG Ex 1 (multi-term polynomial, general antiderivative).
    # 'multi_term_specific_antiderivative': Corresponds to RAG Ex 2 (multi-term polynomial, specific antiderivative with initial condition).
    problem_type = random.choice([
        'monomial_general_antiderivative', 
        'multi_term_general_antiderivative', 
        'multi_term_specific_antiderivative'
    ])
    
    question_text = ""
    correct_answer = ""
    answer = "" # This will be the solution_text/answer_display
    image_base64 = None
    
    created_at = datetime.now().isoformat()
    version = "1.0"

    if problem_type == 'monomial_general_antiderivative':
        # Corresponds to Architect's Spec's *description* of Type 1: 基礎多項式單項式的反導函數。
        
        coeff, exp = _generate_polynomial_term(min_coeff=-8, max_coeff=8, min_exp=0, max_exp=5, allow_zero_coeff=False)
        
        # Build f(x) string
        f_x_str = _format_term_latex(coeff, exp, is_first_term=True)
        
        question_text_template = r"試求函數 $f(x) = {fx_expr}$ 的所有反導函數 $F(x)$。"
        question_text = question_text_template.replace("{fx_expr}", f_x_str)

        # Build F(x) string for display
        F_x_str = _format_antiderivative_term_latex(coeff, exp, is_first_term=True)
        answer_template = r"$F(x) = {Fx_expr} + C$"
        answer = answer_template.replace("{Fx_expr}", F_x_str)

        # Correct answer: coefficients of F(x) without C.
        antideriv_coeffs_dict = {} # {exp: value}
        if coeff != 0:
            antideriv_coeffs_dict[exp + 1] = _get_antiderivative_coeff_value(coeff, exp)
        
        max_antideriv_exp = max(antideriv_coeffs_dict.keys()) if antideriv_coeffs_dict else 0

        answer_parts = []
        for e in range(max_antideriv_exp, 0, -1): # From max_antideriv_exp down to 1
            answer_parts.append(str(antideriv_coeffs_dict.get(e, 0.0)))
        
        correct_answer = ",".join(answer_parts)

    elif problem_type == 'multi_term_general_antiderivative':
        # Corresponds to RAG Ex 1: 求 $x^2 + 5x - 4$ 的所有反導函數。
        # (Multi-term polynomial, general antiderivative)
        
        num_terms = random.randint(2, 3) # 2 or 3 terms
        f_x_terms = []
        
        # Generate terms for f(x), ensuring unique exponents and non-zero coefficients
        exponents_used = set()
        for i in range(num_terms):
            coeff_i, exp_i = _generate_polynomial_term(min_coeff=-8, max_coeff=8, min_exp=0, max_exp=5, allow_zero_coeff=False)
            while exp_i in exponents_used: # Ensure exponent is unique
                exp_i = random.randint(0, 5)
            f_x_terms.append((coeff_i, exp_i))
            exponents_used.add(exp_i)
        
        # Sort terms by exponent in descending order for display
        f_x_terms.sort(key=lambda x: x[1], reverse=True)

        # Build f(x) string
        f_x_str_parts = []
        for i, (coeff, exp) in enumerate(f_x_terms):
            f_x_str_parts.append(_format_term_latex(coeff, exp, is_first_term=(i==0)))
        f_x_str = "".join(f_x_str_parts)

        question_text_template = r"試求函數 $f(x) = {fx_expr}$ 的所有反導函數 $F(x)$。"
        question_text = question_text_template.replace("{fx_expr}", f_x_str)

        # Build F(x) string for display
        F_x_str_parts = []
        # Sort terms by their antiderivative exponent for display
        antideriv_terms_sorted_for_display = sorted(f_x_terms, key=lambda x: x[1]+1, reverse=True)

        for i, (coeff, exp) in enumerate(antideriv_terms_sorted_for_display):
            F_x_str_parts.append(_format_antiderivative_term_latex(coeff, exp, is_first_term=(i==0)))
        
        F_x_str = "".join(F_x_str_parts)
        answer_template = r"$F(x) = {Fx_expr} + C$"
        answer = answer_template.replace("{Fx_expr}", F_x_str)

        # Correct answer: coefficients of F(x) without C.
        antideriv_coeffs_dict = {} # {exp: value}
        for coeff, exp in f_x_terms:
            if coeff != 0:
                antideriv_coeffs_dict[exp + 1] = _get_antiderivative_coeff_value(coeff, exp)
        
        max_antideriv_exp = max(antideriv_coeffs_dict.keys()) if antideriv_coeffs_dict else 0

        answer_parts = []
        for e in range(max_antideriv_exp, 0, -1): # From max_antideriv_exp down to 1
            answer_parts.append(str(antideriv_coeffs_dict.get(e, 0.0)))
        
        correct_answer = ",".join(answer_parts)

    elif problem_type == 'multi_term_specific_antiderivative':
        # Corresponds to RAG Ex 2: 已知 $F(x)$ 為 $f(x) = 3x^2 - 2x + 1$ 的一個反導函數且 $F(2) = 4$，求 $F(x)$。
        # (Multi-term polynomial, specific antiderivative with initial condition)
        
        num_terms = random.randint(1, 2) # 1 or 2 terms for f'(x)
        f_prime_x_terms = []
        
        # Generate terms for f'(x), ensuring unique exponents and non-zero coefficients
        exponents_used = set()
        for i in range(num_terms):
            coeff_i, exp_i = _generate_polynomial_term(min_coeff=-8, max_coeff=8, min_exp=0, max_exp=4, allow_zero_coeff=False)
            while exp_i in exponents_used: # Ensure unique exponents
                exp_i = random.randint(0, 4)
            f_prime_x_terms.append((coeff_i, exp_i))
            exponents_used.add(exp_i)
        
        # If there's only one term and it's a constant, ensure its coefficient is not zero
        # (Already handled by _generate_polynomial_term(allow_zero_coeff=False))
        
        # Sort terms by exponent in descending order for display
        f_prime_x_terms.sort(key=lambda x: x[1], reverse=True)

        # Build f'(x) string
        f_prime_x_str_parts = []
        for i, (coeff, exp) in enumerate(f_prime_x_terms):
            f_prime_x_str_parts.append(_format_term_latex(coeff, exp, is_first_term=(i==0)))
        f_prime_x_str = "".join(f_prime_x_str_parts)

        # Generate initial condition (x0, y0)
        x0 = random.randint(-3, 3)
        y0 = random.randint(-10, 10)

        question_text_template = r"已知函數 $f(x)$ 滿足 $f'(x) = {f_prime_x_expr}$ 且 $f({x0}) = {y0}$，試求 $f(x)$。"
        question_text = question_text_template.replace("{f_prime_x_expr}", f_prime_x_str).replace("{x0}", str(x0)).replace("{y0}", str(y0))

        # Calculate general antiderivative F(x) + C
        antideriv_coeffs_dict = {} # {exp: value} for F(x) excluding C
        for coeff, exp in f_prime_x_terms:
            if coeff != 0:
                antideriv_coeffs_dict[exp + 1] = _get_antiderivative_coeff_value(coeff, exp)
        
        # Get max exponent in antiderivative
        max_antideriv_exp = max(antideriv_coeffs_dict.keys()) if antideriv_coeffs_dict else 0

        # Calculate F(x0)
        F_x0_val = 0.0
        for exp_val, coeff_val in antideriv_coeffs_dict.items():
            F_x0_val += coeff_val * (x0 ** exp_val)
        
        # Solve for C: F(x0) + C = y0 => C = y0 - F(x0)
        C_val = y0 - F_x0_val

        # Build F(x) string for display (with calculated C)
        F_x_display_parts = []
        # Sort f_prime_x_terms by their antiderivative exponent for display
        antideriv_terms_sorted_for_display = sorted(f_prime_x_terms, key=lambda x: x[1]+1, reverse=True)

        for i, (coeff, exp) in enumerate(antideriv_terms_sorted_for_display):
            F_x_display_parts.append(_format_antiderivative_term_latex(coeff, exp, is_first_term=(i==0)))

        # Add C_val to display string
        C_str_display = ""
        if C_val != 0:
            # Format C_val: integer if whole, otherwise up to 4 significant figures.
            if C_val.is_integer():
                C_str_display = f"+{int(C_val)}" if C_val > 0 else f"{int(C_val)}"
            else:
                C_str_display = f"+{C_val:.4g}" if C_val > 0 else f"{C_val:.4g}"
        
        F_x_display = "".join(F_x_display_parts) + C_str_display
        
        # Ensure F_x_display doesn't start with '+'.
        if F_x_display.startswith('+'):
            F_x_display = F_x_display[1:]

        answer_template = r"$f(x) = {Fx_expr}$"
        answer = answer_template.replace("{Fx_expr}", F_x_display)

        # Correct answer: coefficients of F(x) including the calculated C.
        answer_parts = []
        for e in range(max_antideriv_exp, 0, -1): # From max_antideriv_exp down to 1
            answer_parts.append(str(antideriv_coeffs_dict.get(e, 0.0)))
        answer_parts.append(str(C_val)) # Add C as the last element (constant term)
        
        correct_answer = ",".join(answer_parts)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer, # This is the solution_text/answer_display
        "image_base64": image_base64,
        "created_at": created_at,
        "version": version,
    }



    import re
    

    # CRITICAL CODING RULES (V18.8, V18.9): Local Imports - Done.
    # CRITICAL CODING STANDARDS: Verification & Stability - Deterministic Grading is ensured.

    # 1. Input Sanitization: Custom cleaning for coefficient lists.
    # This cleaning removes LaTeX symbols, curly braces, common variable/prefix strings, and spaces.
    # It *retains* numbers, decimals, signs, and commas, which are essential for coefficient lists.
    def clean_coefficient_string(s):
        s = str(s).strip()
        # Remove common LaTeX, variable, and formatting noise
        s = re.sub(r'[\\$}{kx=y=Ans:\s]', '', s)
        # Remove 'C' if user might have included it in their raw answer, as correct_answer does not have 'C'.
        s = re.sub(r'[cC]', '', s) 
        return s

    cleaned_user_answer_str = clean_coefficient_string(user_answer)
    cleaned_correct_answer_str = clean_coefficient_string(correct_answer)

    # 2. Numerical Sequence Comparison (adapted from the original check function)
    user_coeffs_str = cleaned_user_answer_str.split(',')
    correct_coeffs_str = cleaned_correct_answer_str.split(',')

    try:
        # Convert to floats, filtering out any empty strings from splitting
        user_coeffs = [float(c) for c in user_coeffs_str if c.strip()]
        correct_coeffs = [float(c) for c in correct_coeffs_str if c.strip()]
    except ValueError:
        return {"correct": False, "result": "答案格式錯誤，請檢查數字輸入。"}

    # V12.6 邏輯驗證硬化規約: 結構鎖死 - 數值序列比對
    # Check if the number of coefficients matches
    if len(user_coeffs) != len(correct_coeffs):
        return {"correct": False, "result": "答案項數不符。"}

    # Compare each coefficient, considering floating point precision (Universal Check Template principle)
    tolerance = 1e-6 # Define a small tolerance for floating-point comparisons
    for u_coeff, c_coeff in zip(user_coeffs, correct_coeffs):
        if not math.isclose(u_coeff, c_coeff, rel_tol=tolerance, abs_tol=tolerance):
            return {"correct": False, "result": "答案數值不符。"}
            
    return {"correct": True, "result": "正確！"}


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
