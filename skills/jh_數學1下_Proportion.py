# ==============================================================================
# ID: jh_數學1下_Proportion
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 49.09s | RAG: 4 examples
# Created At: 2026-01-16 14:39:46
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



from datetime import datetime
import base64

# --- Helper Functions (遵循 V10.2, V13.1, V13.5 規範) ---

def _gcd(a, b):
    """Helper to compute greatest common divisor."""
    while b:
        a, b = b, a % b
    return a

def _get_number_data_and_latex(numerator, denominator):
    """
    Returns (float_value, (int_part, num_frac, den_frac, is_neg), latex_string)
    Following V10.2 A for structured data and V13.1/V10.2 C for LaTeX.
    - float_value: The actual numeric value (e.g., -2.5)
    - int_part: Absolute integer part (e.g., for -2 1/2, int_part=2). For pure integers, it's the signed integer itself.
    - num_frac: Numerator of the proper fractional part. 0 if integer.
    - den_frac: Denominator of the proper fractional part. 0 if integer.
    - is_neg: True if the overall number is negative.
    """
    if denominator == 0:
        raise ValueError("Denominator cannot be zero.")

    is_negative_overall = (numerator < 0) != (denominator < 0)
    num_abs = abs(numerator)
    den_abs = abs(denominator)

    # Simplify the fraction
    common_divisor = _gcd(num_abs, den_abs)
    num_simp = num_abs // common_divisor
    den_simp = den_abs // common_divisor

    float_val = float(numerator) / float(denominator)

    latex_str = ""
    int_part_struct = 0
    num_frac_struct = 0
    den_frac_struct = 0

    if den_simp == 1:
        # Integer case
        val = num_simp if not is_negative_overall else -num_simp
        latex_str = str(val)
        # V10.2 A: num/den are 0 for integers
        coordinate_data_tuple = (val, 0, 0, val < 0) 
    else:
        # Mixed number or proper fraction
        int_part_abs = num_simp // den_simp
        frac_num = num_simp % den_simp

        if frac_num == 0:
            # It's an integer after all (e.g., 4/2)
            val = num_simp if not is_negative_overall else -num_simp
            latex_str = str(val)
            coordinate_data_tuple = (val, 0, 0, val < 0)
        else:
            # Proper fraction or mixed number
            sign_str = "-" if is_negative_overall else ""
            
            int_part_struct = int_part_abs
            num_frac_struct = frac_num
            den_frac_struct = den_simp
            
            if int_part_abs > 0:
                # Mixed number
                latex_str = r"{sign}{int_part}\frac{{{frac_num}}}{{{den}}}".replace("{sign}", sign_str).replace("{int_part}", str(int_part_abs)).replace("{frac_num}", str(frac_num)).replace("{den}", str(den_simp))
            else:
                # Proper fraction
                latex_str = r"{sign}\frac{{{frac_num}}}{{{den}}}".replace("{sign}", sign_str).replace("{frac_num}", str(frac_num)).replace("{den}", str(den_simp))
            
            # V10.2 A: int_part is absolute for mixed numbers/fractions
            coordinate_data_tuple = (int_part_abs, num_frac_struct, den_frac_struct, is_negative_overall)

    return float_val, coordinate_data_tuple, latex_str

# Placeholder for image generation (not used for this skill, but required for structure)
def _create_image_base64(points=None, labels=None, title="", x_range=(-10, 10), y_range=(-10, 10)):
    """
    Generates a blank image base64 string, as this skill does not require plotting.
    Adheres to V6. [防洩漏原則] - no answer data passed.
    """
    # For skills that don't need an image, return an empty string.
    return ""


# --- Problem Type Generators ---

def _generate_type_1_data():
    """
    Type 1 (Maps to Example 1: Simple Proportion a:b = c:x)
    問題描述: 求解 $a:b = c:x$，求 $x$ 的值。
    """
    # Generate a, b, c. Ensure a is not zero.
    a = random.randint(1, 10) * random.choice([-1, 1])
    b = random.randint(1, 10) * random.choice([-1, 1])
    c = random.randint(1, 10) * random.choice([-1, 1])

    while a == 0:
        a = random.randint(1, 10) * random.choice([-1, 1])

    # Calculate x: a*x = b*c => x = (b*c)/a
    x_num = b * c
    x_den = a
    
    # Format x for display and get its float value
    x_float, _, x_latex_str = _get_number_data_and_latex(x_num, x_den)

    question_text = r"求解比例式 $ {a}:{b} = {c}:x $，求 $ x $ 的值。".replace("{a}", str(a)).replace("{b}", str(b)).replace("{c}", str(c))
    correct_answer_str = str(x_float) # V12.6, V13.5: numerical sequence for check.
    
    return {
        "question_text": question_text,
        "correct_answer": correct_answer_str,
        "answer": x_latex_str
    }

def _generate_type_2_data():
    """
    Type 2 (Maps to Example 1: Proportion with Expressions (ax+b):c = (dx+e):f)
    問題描述: 求解 $(ax+b):c = (dx+e):f$，求 $x$ 的值。
    """
    max_attempts = 50
    for _ in range(max_attempts):
        a = random.randint(1, 5) * random.choice([-1, 1])
        b = random.randint(1, 5) * random.choice([-1, 1])
        c = random.randint(1, 5) * random.choice([-1, 1])
        d = random.randint(1, 5) * random.choice([-1, 1])
        e = random.randint(1, 5) * random.choice([-1, 1])
        f = random.randint(1, 5) * random.choice([-1, 1])

        while c == 0: c = random.randint(1, 5) * random.choice([-1, 1])
        while f == 0: f = random.randint(1, 5) * random.choice([-1, 1])

        # Calculate x = (ce - bf) / (af - cd)
        denominator_for_x = (a * f - c * d)
        if denominator_for_x == 0: # Avoid division by zero for x
            continue

        numerator_for_x = (c * e - b * f)

        x_num = numerator_for_x
        x_den = denominator_for_x
        
        # Check if x is a simple K12 number (e.g., integer or small denominator fraction)
        common_divisor = _gcd(abs(x_num), abs(x_den))
        simplified_den = abs(x_den // common_divisor)

        if simplified_den == 1 or simplified_den <= 10: # Denominator <= 10 for proper fractions
            break
    else:
        # Fallback to a guaranteed simple case if random generation fails
        # Example: (x-2):6=(x+8):8 => x=32
        a, b, c, d, e, f = 1, -2, 6, 1, 8, 8
        x_num, x_den = 32, 1

    x_float, _, x_latex_str = _get_number_data_and_latex(x_num, x_den)

    # LaTeX for expressions - strictly using .replace() and manual string building (V14.0 系統底層鐵律 1)
    # Build expr1_str for (ax+b)
    expr1_parts = []
    if a != 0:
        if abs(a) == 1:
            expr1_parts.append("x" if a == 1 else "-x")
        else:
            expr1_parts.append(str(a) + "x")
    
    if b != 0:
        if b > 0 and expr1_parts: # If ax_term exists, add sign
            expr1_parts.append(" + " + str(b))
        elif b < 0 and expr1_parts: # If ax_term exists, add sign
            expr1_parts.append(" - " + str(abs(b)))
        else: # If ax_term doesn't exist, just add the number (with its sign)
            expr1_parts.append(str(b))
            
    expr1_str = "".join(expr1_parts)
    if not expr1_str.strip(): expr1_str = "0" # Handle a=0, b=0 case

    # Build expr2_str for (dx+e)
    expr2_parts = []
    if d != 0:
        if abs(d) == 1:
            expr2_parts.append("x" if d == 1 else "-x")
        else:
            expr2_parts.append(str(d) + "x")
    
    if e != 0:
        if e > 0 and expr2_parts: # If dx_term exists, add sign
            expr2_parts.append(" + " + str(e))
        elif e < 0 and expr2_parts: # If dx_term exists, add sign
            expr2_parts.append(" - " + str(abs(e)))
        else: # If dx_term doesn't exist, just add the number (with its sign)
            expr2_parts.append(str(e))

    expr2_str = "".join(expr2_parts)
    if not expr2_str.strip(): expr2_str = "0"

    # Define a helper for robust expression wrapping (V13.5 aesthetic)
    def _wrap_expression(expr_content):
        # Only wrap if it's not a simple variable (x, -x), a simple number, or 0
        is_simple_var = expr_content in ["x", "-x"]
        is_simple_num = expr_content.lstrip('-').isdigit() and float(expr_content) == int(float(expr_content))
        
        if is_simple_var or is_simple_num or expr_content == "0":
            return expr_content
        return r"({expr})".replace("{expr}", expr_content)

    expr1_str_wrapped = _wrap_expression(expr1_str)
    expr2_str_wrapped = _wrap_expression(expr2_str)

    # Final question_text construction, using the wrapped expressions
    question_text = r"求解比例式 $ {expr1}:{c} = {expr2}:{f} $，求 $ x $ 的值。".replace("{expr1}", expr1_str_wrapped).replace("{c}", str(c)).replace("{expr2}", expr2_str_wrapped).replace("{f}", str(f))
    correct_answer_str = str(x_float)
    
    return {
        "question_text": question_text,
        "correct_answer": correct_answer_str,
        "answer": x_latex_str
    }

def _generate_type_3_data():
    """
    Type 3 (Maps to Example 3: Given Ax=By, find x:y or Cx:Dy)
    問題描述: 設 x、y 皆不為 0，且 Ax=By，求下列各比的最簡整數比。(1) x：y (2) Cx：Dy
    This function will randomly choose to ask for either (1) or (2).
    """
    max_attempts = 50
    for _ in range(max_attempts):
        A = random.randint(1, 10) * random.choice([-1, 1])
        B = random.randint(1, 10) * random.choice([-1, 1])
        
        while A == 0 or B == 0: # Ensure A and B are non-zero
            A = random.randint(1, 10) * random.choice([-1, 1])
            B = random.randint(1, 10) * random.choice([-1, 1])

        ask_type = random.choice([1, 2]) 

        if ask_type == 1: # Ask for x:y
            # Ax=By => x/y = B/A => x:y = B:A
            ratio_num = B
            ratio_den = A
            
            common = _gcd(abs(ratio_num), abs(ratio_den))
            simplified_num = ratio_num // common
            simplified_den = ratio_den // common
            
            # Adjust signs for standard ratio representation (first term positive if possible)
            if simplified_num < 0 and simplified_den < 0:
                simplified_num = abs(simplified_num)
                simplified_den = abs(simplified_den)
            elif simplified_num < 0 and simplified_den > 0:
                # If simplified_num is negative, make it positive and put the negative sign on simplified_den
                # e.g., -4:7 becomes 4:-7. This is a common convention for ratios with negative values.
                simplified_num = abs(simplified_num)
                simplified_den = -abs(simplified_den)
            
            question_text = r"設 $ x、y $ 皆不為 $ 0 $，且 $ {A}x={B}y $，求 $ x:y $ 的最簡整數比。".replace("{A}", str(A)).replace("{B}", str(B))
            answer_display_str = "{num}:{den}".replace("{num}", str(simplified_num)).replace("{den}", str(simplified_den))
            correct_answer_value = float(simplified_num) / simplified_den
            
        else: # Ask for Cx:Dy
            C = random.randint(1, 5) * random.choice([-1, 1])
            D = random.randint(1, 5) * random.choice([-1, 1])
            
            while C == 0 or D == 0:
                C = random.randint(1, 5) * random.choice([-1, 1])
                D = random.randint(1, 5) * random.choice([-1, 1])

            # Ax=By => x/y = B/A.
            # Cx:Dy = (C*x) : (D*y)
            # Replace x with B and y with A (conceptually for ratio value)
            ratio_num = C * B
            ratio_den = D * A
            
            common = _gcd(abs(ratio_num), abs(ratio_den))
            simplified_num = ratio_num // common
            simplified_den = ratio_den // common
            
            # Adjust signs for standard ratio representation
            if simplified_num < 0 and simplified_den < 0:
                simplified_num = abs(simplified_num)
                simplified_den = abs(simplified_den)
            elif simplified_num < 0 and simplified_den > 0:
                simplified_num = abs(simplified_num)
                simplified_den = -abs(simplified_den)

            # Build the {C}x:{D}y part of the question text carefully using string concatenation
            Cx_term = ""
            if C == 1: Cx_term = "x"
            elif C == -1: Cx_term = "-x"
            else: Cx_term = str(C) + "x"

            Dy_term = ""
            if D == 1: Dy_term = "y"
            elif D == -1: Dy_term = "-y"
            else: Dy_term = str(D) + "y"

            question_text = r"設 $ x、y $ 皆不為 $ 0 $，且 $ {A}x={B}y $，求 $ {Cx_term}:{Dy_term} $ 的最簡整數比。".replace("{A}", str(A)).replace("{B}", str(B)).replace("{Cx_term}", Cx_term).replace("{Dy_term}", Dy_term)
            
            answer_display_str = "{num}:{den}".replace("{num}", str(simplified_num)).replace("{den}", str(simplified_den))
            correct_answer_value = float(simplified_num) / simplified_den

        # Check for simple ratios (small numbers for display)
        if abs(simplified_num) <= 20 and abs(simplified_den) <= 20: 
            break
    else: # Fallback to a guaranteed simple case
        A, B = 7, 4 # From Ex 3
        ask_type = 1
        simplified_num, simplified_den = 4, 7
        question_text = r"設 $ x、y $ 皆不為 $ 0 $，且 $ {A}x={B}y $，求 $ x:y $ 的最簡整數比。".replace("{A}", str(A)).replace("{B}", str(B))
        answer_display_str = "{num}:{den}".replace("{num}", str(simplified_num)).replace("{den}", str(simplified_den))
        correct_answer_value = float(simplified_num) / simplified_den
        
    return {
        "question_text": question_text,
        "correct_answer": str(correct_answer_value), # Ensure it's a string for the check function
        "answer": answer_display_str
    }

# --- Top-level Functions ---

def generate(level=1):
    """
    Generates a proportion problem based on the specified level.
    """
    problem_type_selector = random.choice([1, 2, 3]) # Randomly select problem type

    if problem_type_selector == 1:
        problem_data = _generate_type_1_data()
    elif problem_type_selector == 2:
        problem_data = _generate_type_2_data()
    else: # problem_type_selector == 3
        problem_data = _generate_type_3_data()

    # V7. Standard Fields
    return {
        "question_text": problem_data["question_text"],
        "correct_answer": problem_data["correct_answer"],
        "answer": problem_data["answer"],
        "image_base64": _create_image_base64(), # Empty for this skill
        "created_at": datetime.now().isoformat(),
        "version": "1"
    }


    """
    Checks the user's answer against the correct answer.
    Adheres to V12.6, V13.5, V13.6 for numerical sequence comparison.
    """
    # V13.6 Exact Check Logic (4-line check logic)
    try:
        user_float = float(user_answer)
        correct_float = float(correct_answer)
        # Use a small epsilon for float comparison to account for precision issues
        return abs(user_float - correct_float) < 1e-9
    except ValueError:
        return False

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
