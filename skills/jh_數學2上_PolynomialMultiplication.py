# ==============================================================================
# ID: jh_數學2上_PolynomialMultiplication
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 81.34s | RAG: 5 examples
# Created At: 2026-01-18 14:39:25
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
import base64
 

# 輔助函式定義 (Helper functions) 必須在此處定義，不允許使用 class

def _generate_polynomial_latex(coeffs):
    """
    輔助函式：根據係數列表生成多項式的 LaTeX 表示。
    例如：[3, -2, 1] -> "3x^2 - 2x + 1"
    [1, 0, -5] -> "x^2 - 5"
    [0, 2, 0] -> "2x"
    [0, 0, 0, 5] -> "5" (for degree 0)
    [1, 0, -2, 1] -> "x^3 - 2x + 1"
    
    coeffs: list of coefficients in descending order of power
            e.g., [coeff_x^n, coeff_x^(n-1), ..., coeff_x, const_term]
            Coefficients should be integers or floats.
    """
    if not coeffs:
        return "0"

    terms = []
    degree = len(coeffs) - 1

    for i, coeff in enumerate(coeffs):
        # Use a small tolerance for checking if a coefficient is effectively zero
        if abs(coeff) < 1e-9:
            continue

        power = degree - i
        term_str = ""

        # Handle sign
        if coeff > 0 and len(terms) > 0:
            term_str += "+"
        elif coeff < 0:
            term_str += "-"

        # Handle coefficient value
        abs_coeff = abs(coeff)
        
        # Format coefficient: integer if possible, otherwise float
        coeff_display = int(round(abs_coeff)) if abs(abs_coeff - round(abs_coeff)) < 1e-9 else abs_coeff

        if power == 0:  # Constant term
            term_str += str(coeff_display)
        elif coeff_display == 1: # Coefficient is 1 or -1 (after abs)
            if power == 1:
                term_str += "x"
            else:
                term_str += f"x^{power}"
        else: # Other coefficients
            if power == 1:
                term_str += f"{coeff_display}x"
            else:
                term_str += f"{coeff_display}x^{power}"
        
        terms.append(term_str)

    if not terms:
        return "0"
    
    # The logic correctly handles leading signs without needing special startswith checks
    return "".join(terms)


def _parse_polynomial_string(poly_str):
    """
    輔助函式：將多項式字串解析為標準係數列表。
    支援多種格式，例如 "3x^2+2x-1", "2x-1+3x^2", "-x^2+5", "5"
    回傳形式為 [coeff_x^3, coeff_x^2, coeff_x, const_term] (最高次數為3)
    然後會移除前導零，例如 [0, 3, 2, -1] -> [3, 2, -1]
    """
    # Initialize coefficients for degree 3 polynomial: [x^3, x^2, x^1, x^0]
    coeffs_map = {3: 0.0, 2: 0.0, 1: 0.0, 0: 0.0}

    if not poly_str:
        return [0.0]
    
    # Normalize operators for easier splitting, e.g., "x-1" -> "x+-1"
    normalized_poly_str = poly_str.replace('-', '+-')
    terms = [t.strip() for t in normalized_poly_str.split('+') if t.strip()]

    for term in terms:
        # Handle empty string after split, or just a sign
        if not term or term == '-' or term == '+':
            continue
        
        coeff_val = 1.0 # Default coefficient for 'x' or 'x^2' etc.
        sign = 1 # Default sign
        
        if term.startswith('-'):
            sign = -1
            term = term[1:].strip() # Remove leading '-'
        elif term.startswith('+'):
            term = term[1:].strip() # Remove leading '+'

        # Match x^N term (e.g., "3x^3", "x^2", "-x^2")
        match_x_n = re.match(r'(\d*\.?\d*)x\^(\d+)$', term)
        if match_x_n:
            coeff_str = match_x_n.group(1)
            power = int(match_x_n.group(2))
            if coeff_str == '': coeff_val = 1.0
            else: coeff_val = float(coeff_str)
            coeffs_map[power] += sign * coeff_val
            continue

        # Match x term (e.g., "3x", "x", "-x")
        match_x1 = re.match(r'(\d*\.?\d*)x$', term)
        if match_x1:
            coeff_str = match_x1.group(1)
            if coeff_str == '': coeff_val = 1.0
            else: coeff_val = float(coeff_str)
            coeffs_map[1] += sign * coeff_val
            continue

        # Match constant term (e.g., "5", "-2")
        match_const = re.match(r'(\d*\.?\d+)$', term)
        if match_const:
            coeff_str = match_const.group(1)
            coeff_val = float(coeff_str)
            coeffs_map[0] += sign * coeff_val
            continue
            
    # Convert map to list [coeff_x^3, coeff_x^2, coeff_x, const_term]
    full_coeffs = [coeffs_map[3], coeffs_map[2], coeffs_map[1], coeffs_map[0]]

    # Remove leading zeros if not a constant polynomial
    first_nonzero = -1
    for i in range(len(full_coeffs)):
        if abs(full_coeffs[i]) > 1e-9: # Use tolerance for float comparison
            first_nonzero = i
            break
    
    if first_nonzero == -1: # All zeros
        return [0.0]
    
    return full_coeffs[first_nonzero:]


def generate(level=1):
    """
    生成多項式乘法運算題目。
    根據 level 調整係數範圍和題目複雜度。
    """
    coeff_range_min, coeff_range_max = -3, 3
    if level == 2:
        coeff_range_min, coeff_range_max = -5, 5
    elif level == 3:
        coeff_range_min, coeff_range_max = -8, 8

    def _get_coeff(allow_zero=True):
        c = random.randint(coeff_range_min, coeff_range_max)
        if not allow_zero and c == 0:
            # Ensure non-zero coefficients for leading terms
            attempts = 0
            while c == 0 and attempts < 10: # Retry a few times
                c = random.randint(coeff_range_min, coeff_range_max)
                attempts += 1
            if c == 0: # If still zero after retries, force to 1 or -1
                c = random.choice([-1, 1])
        return c

    problem_type = random.choice(range(1, 8)) # Types 1-7
    question_text = ""
    correct_coeffs_raw = [] # Store the raw calculated coefficients before trimming

    # Helper for polynomial operations (coeffs are in descending power order)
    def poly_mult(poly1_coeffs, poly2_coeffs):
        deg1 = len(poly1_coeffs) - 1
        deg2 = len(poly2_coeffs) - 1
        result_deg = deg1 + deg2
        result_coeffs = [0.0] * (result_deg + 1) # Initialize with zeros for highest possible degree

        # Perform convolution
        for i in range(deg1 + 1):
            for j in range(deg2 + 1):
                result_coeffs[i + j] += poly1_coeffs[i] * poly2_coeffs[j]
        return result_coeffs

    def poly_add(poly1_coeffs, poly2_coeffs):
        # Pad shorter polynomial with leading zeros to match max degree
        max_deg = max(len(poly1_coeffs), len(poly2_coeffs))
        
        padded_poly1 = [0.0] * (max_deg - len(poly1_coeffs)) + poly1_coeffs
        padded_poly2 = [0.0] * (max_deg - len(poly2_coeffs)) + poly2_coeffs
        
        res = [p1 + p2 for p1, p2 in zip(padded_poly1, padded_poly2)]
        return res

    def poly_sub(poly1_coeffs, poly2_coeffs):
        # Pad shorter polynomial with leading zeros to match max degree
        max_deg = max(len(poly1_coeffs), len(poly2_coeffs))
        
        padded_poly1 = [0.0] * (max_deg - len(poly1_coeffs)) + poly1_coeffs
        padded_poly2 = [0.0] * (max_deg - len(poly2_coeffs)) + poly2_coeffs
        
        res = [p1 - p2 for p1, p2 in zip(padded_poly1, padded_poly2)]
        return res

    if problem_type == 1: # Monomial by Polynomial: (ax) * (bx+c) or (ax) * (bx^2+cx+d)
        a = _get_coeff(allow_zero=False)
        
        if random.choice([True, False]): # (ax) * (bx+c) - Maps to RAG Ex 2, 3
            b = _get_coeff(allow_zero=False)
            c = _get_coeff()
            poly1_coeffs = [a, 0] # ax (degree 1)
            poly2_coeffs = [b, c] # bx+c (degree 1)
            
            question_template = r"計算 $(P_1) \times (P_2)$ 的結果，並將答案按降冪排列。"
            question_text = question_template.replace("P_1", _generate_polynomial_latex(poly1_coeffs)).replace("P_2", _generate_polynomial_latex(poly2_coeffs))
            correct_coeffs_raw = poly_mult(poly1_coeffs, poly2_coeffs)
        else: # (ax) * (bx^2+cx+d)
            b = _get_coeff(allow_zero=False)
            c = _get_coeff()
            d = _get_coeff()
            poly1_coeffs = [a, 0] # ax (degree 1)
            poly2_coeffs = [b, c, d] # bx^2+cx+d (degree 2)
            
            question_template = r"計算 $(P_1) \times (P_2)$ 的結果，並將答案按降冪排列。"
            question_text = question_template.replace("P_1", _generate_polynomial_latex(poly1_coeffs)).replace("P_2", _generate_polynomial_latex(poly2_coeffs))
            correct_coeffs_raw = poly_mult(poly1_coeffs, poly2_coeffs)

    elif problem_type == 2: # Binomial by Binomial: (ax+b)(cx+d) - Maps to RAG Ex 5 (part 1)
        a = _get_coeff(allow_zero=False)
        b = _get_coeff()
        c = _get_coeff(allow_zero=False)
        d = _get_coeff()
        
        poly1_coeffs = [a, b] # degree 1
        poly2_coeffs = [c, d] # degree 1
        
        question_template = r"計算 $(P_1) \times (P_2)$ 的結果，並將答案按降冪排列。"
        question_text = question_template.replace("P_1", _generate_polynomial_latex(poly1_coeffs)).replace("P_2", _generate_polynomial_latex(poly2_coeffs))
        correct_coeffs_raw = poly_mult(poly1_coeffs, poly2_coeffs)

    elif problem_type == 3: # Binomial by Trinomial: (ax+b)(cx^2+dx+e) - Maps to RAG Ex 4, 5 (part 2)
        a = _get_coeff(allow_zero=False)
        b = _get_coeff()
        c = _get_coeff(allow_zero=False)
        d = _get_coeff()
        e = _get_coeff()
        
        poly1_coeffs = [a, b] # degree 1
        poly2_coeffs = [c, d, e] # degree 2
        
        question_template = r"計算 $(P_1) \times (P_2)$ 的結果，並將答案按降冪排列。"
        question_text = question_template.replace("P_1", _generate_polynomial_latex(poly1_coeffs)).replace("P_2", _generate_polynomial_latex(poly2_coeffs))
        correct_coeffs_raw = poly_mult(poly1_coeffs, poly2_coeffs)
        
    elif problem_type == 4: # Special Product Formula - (A+B)^2: (ax+b)^2
        a = _get_coeff(allow_zero=False)
        b = _get_coeff()
        
        poly_coeffs = [a, b] # degree 1
        
        question_template = r"計算 $(P_1)^2$ 的結果，並將答案按降冪排列。"
        question_text = question_template.replace("P_1", _generate_polynomial_latex(poly_coeffs))
        correct_coeffs_raw = poly_mult(poly_coeffs, poly_coeffs)

    elif problem_type == 5: # Special Product Formula - (A-B)^2: (ax-b)^2
        a = _get_coeff(allow_zero=False)
        b = _get_coeff()
        
        poly_coeffs = [a, -b] # Represents (ax - b)
        
        question_template = r"計算 $(P_1)^2$ 的結果，並將答案按降冪排列。"
        question_text = question_template.replace("P_1", _generate_polynomial_latex(poly_coeffs))
        correct_coeffs_raw = poly_mult(poly_coeffs, poly_coeffs)

    elif problem_type == 6: # Special Product Formula - (A+B)(A-B): (ax+b)(ax-b)
        a = _get_coeff(allow_zero=False)
        b = _get_coeff(allow_zero=False) # b must not be zero for a meaningful (A+B)(A-B)
        
        poly1_coeffs = [a, b] # degree 1
        poly2_coeffs = [a, -b] # degree 1
        
        question_template = r"計算 $(P_1) \times (P_2)$ 的結果，並將答案按降冪排列。"
        question_text = question_template.replace("P_1", _generate_polynomial_latex(poly1_coeffs)).replace("P_2", _generate_polynomial_latex(poly2_coeffs))
        correct_coeffs_raw = poly_mult(poly1_coeffs, poly2_coeffs)

    elif problem_type == 7: # Combination of Formulas/Multiplication
        # Example: (ax+b)^2 - (cx+d)(ex+f)
        a = _get_coeff(allow_zero=False)
        b = _get_coeff()
        c = _get_coeff(allow_zero=False)
        d = _get_coeff()
        e = _get_coeff(allow_zero=False)
        f = _get_coeff()

        poly1_coeffs = [a, b]
        poly2_coeffs = [c, d]
        poly3_coeffs = [e, f]

        term1_coeffs = poly_mult(poly1_coeffs, poly1_coeffs) # (ax+b)^2
        term2_coeffs = poly_mult(poly2_coeffs, poly3_coeffs) # (cx+d)(ex+f)
        
        correct_coeffs_raw = poly_sub(term1_coeffs, term2_coeffs)
        
        poly1_str = _generate_polynomial_latex(poly1_coeffs)
        poly2_str = _generate_polynomial_latex(poly2_coeffs)
        poly3_str = _generate_polynomial_latex(poly3_coeffs)

        question_template = r"計算 $(P_1)^2 - (P_2)(P_3)$ 的結果，並將答案按降冪排列。"
        question_text = question_template.replace("P_1", poly1_str).replace("P_2", poly2_str).replace("P_3", poly3_str)
    
    # Trim leading zeros from the raw correct coefficients
    first_nonzero = -1
    for i in range(len(correct_coeffs_raw)):
        if abs(correct_coeffs_raw[i]) > 1e-9: # Use tolerance for float comparison
            first_nonzero = i
            break
    
    if first_nonzero == -1: # All zeros
        final_correct_coeffs = [0]
    else:
        # Round to integer if very close to integer, otherwise keep float
        final_correct_coeffs = [int(round(c)) if abs(c - round(c)) < 1e-9 else c for c in correct_coeffs_raw[first_nonzero:]]

    correct_answer_str = ",".join(map(str, final_correct_coeffs))

    return {
        "question_text": question_text,
        "correct_answer": correct_answer_str,
        "answer": None, # As per spec, 'answer' should be None
        "image_base64": None, # As per spec, 'image_base64' should be None
        "created_at": datetime.now().isoformat(),
        "version": "1.0",
    }



    """
    檢查使用者答案的正確性。
    """
    # 1. Input Sanitization (Coder 實作上述 Regex 邏輯)
    cleaned_input = str(user_answer)
    cleaned_input = re.sub(r'\$[^\$]*\$', '', cleaned_input) # 移除所有 $...$ 內容
    cleaned_input = re.sub(r'[\\\{\}]', '', cleaned_input) # 移除 \ { }
    cleaned_input = re.sub(r'(x|y|k|Ans):?=', '', cleaned_input, flags=re.IGNORECASE) # 移除 x=, Ans: 等
    cleaned_input = re.sub(r'\s+', '', cleaned_input) # 移除所有空白字元
    cleaned_input = re.sub(r'=.*$', '', cleaned_input) # 移除 = 及之後所有內容
    
    # Normalize signs for parsing, e.g., "x+-2" -> "x-2"
    cleaned_input = cleaned_input.replace('+-', '-')

    # 2. Parse user_answer into canonical form (coefficient list)
    user_coeffs = _parse_polynomial_string(cleaned_input)

    # 3. Parse correct_answer into canonical form (coefficient list)
    correct_coeffs = [float(c) for c in correct_answer.split(',')]

    # 4. Compare coefficient lists
    # Adjust lengths for comparison by padding with leading zeros to the maximum degree.
    # This correctly aligns coefficients if one polynomial is of lower degree than the other.
    max_len = max(len(user_coeffs), len(correct_coeffs))
    
    padded_user_coeffs = [0.0] * (max_len - len(user_coeffs)) + user_coeffs
    padded_correct_coeffs = [0.0] * (max_len - len(correct_coeffs)) + correct_coeffs

    if len(padded_user_coeffs) != len(padded_correct_coeffs):
        return False

    # Allow floating point comparison tolerance as per spec (1e-9)
    tolerance = 1e-9
    for u_coeff, c_coeff in zip(padded_user_coeffs, padded_correct_coeffs):
        if abs(u_coeff - c_coeff) > tolerance:
            return False
    return True

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
