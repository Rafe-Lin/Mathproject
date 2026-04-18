# ==============================================================================
# ID: jh_數學1下_SystemOfLinearEquationsInTwoVariables
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 39.45s | RAG: 1 examples
# Created At: 2026-01-15 11:03:59
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

# --- 4. Answer Checker (V11.5 Bi-Directional Hardened Standard) ---
def check(user_answer, correct_answer):
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    
    # [V11.5 雙向清理邏輯] 徹底脫鉤 LaTeX 符號
    def _clean(s):
        if s is None: return ""
        # 移除空格、全形標點、錢字號、反斜線，並統一轉小寫
        return str(s).strip().replace(" ", "").replace("，", ",").replace("$", "").replace("\\", "").lower()
    
    u = _clean(user_answer)
    c = _clean(correct_answer) # 核心修復：標準答案也進場清理
    
    # 強制還原字典格式 (針對商餘題)
    c_raw = correct_answer
    if isinstance(c_raw, str) and c_raw.startswith("{") and "quotient" in c_raw:
        try: import ast; c_raw = ast.literal_eval(c_raw)
        except: pass

    if isinstance(c_raw, dict) and "quotient" in c_raw:
        q, r = str(c_raw.get("quotient", "")), str(c_raw.get("remainder", ""))
        # 字典模式也需要清理
        if u == _clean(q) + "," + _clean(r):
            return {"correct": True, "result": "正確！"}
    
    # 1. 暴力字串比對 (此時 $y=1$ 與 y=1 會變成都等於 y=1)
    if u == c: return {"correct": True, "result": "正確！"}
    
    # 2. 數值近值比對
    try:
        import math
        if math.isclose(float(u), float(c), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
    except: pass
    
    # 3. 科學記號自動比對 (維持原邏輯)
    if "*" in str(c) or "^" in str(c) or "e" in str(c):
        try:
            norm_ans = c.replace("*10^", "e").replace("x10^", "e").replace("^", "")
            norm_user = u.replace("*10^", "e").replace("x10^", "e").replace("^", "")
            if math.isclose(float(norm_ans), float(norm_user), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
        except: pass

    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", str(correct_answer))}


import datetime

# import base64 # Not directly needed for this skill unless drawing is required.
# from io import BytesIO # Not directly needed for this skill unless drawing is required.
# from matplotlib import pyplot as plt # Not directly needed for this skill unless drawing is required.
# from matplotlib.figure import Figure # Not directly needed for this skill unless drawing is required.

# --- Helper Functions ---
# All helper functions must return a value. If used in question_text, return value must be string.
# Visualisation functions (if any) must only receive known data, not answer data.

def _generate_linear_equation(x_coeff, y_coeff, constant):
    """
    Generates a linear equation string in the form Ax + By = C.
    Example: 2x+3y = 5, x-y = -1, -x+2y = 0
    """
    lhs_parts = []

    # X term
    if x_coeff == 1:
        lhs_parts.append("x")
    elif x_coeff == -1:
        lhs_parts.append("-x")
    elif x_coeff != 0:
        lhs_parts.append(str(x_coeff) + "x")

    # Y term
    if y_coeff == 1:
        if lhs_parts: # If X term exists, add '+'
            lhs_parts.append("+y")
        else: # If Y term is the first term
            lhs_parts.append("y")
    elif y_coeff == -1:
        if lhs_parts: # If X term exists, add '-'
            lhs_parts.append("-y")
        else: # If Y term is the first term
            lhs_parts.append("-y")
    elif y_coeff != 0:
        if y_coeff > 0 and lhs_parts: # Positive Y, and X term exists
            lhs_parts.append("+" + str(y_coeff) + "y")
        else: # Negative Y, or Y is the first term
            lhs_parts.append(str(y_coeff) + "y")
            
    if not lhs_parts: # Case: 0x + 0y = C
        return f"0 = {constant}" if constant != 0 else "0 = 0"

    return "".join(lhs_parts) + f" = {constant}"

def _format_fractional_equation(a_coeff, b_coeff, den_x, den_y, const_val):
    """
    Formats a linear equation with fractional coefficients using LaTeX.
    Example: \frac{x}{2} + \frac{y}{3} = 1
    """
    lhs_parts = []
    
    # X term
    if a_coeff != 0:
        if a_coeff == 1:
            lhs_parts.append(r"\frac{x}{" + str(den_x) + r"}")
        elif a_coeff == -1:
            lhs_parts.append(r"-\frac{x}{" + str(den_x) + r"}")
        else:
            lhs_parts.append(r"\frac{" + str(a_coeff) + r"x}{" + str(den_x) + r"}")
    
    # Y term
    if b_coeff != 0:
        term_str = ""
        if b_coeff == 1:
            term_str = r"\frac{y}{" + str(den_y) + r"}"
        elif b_coeff == -1:
            term_str = r"-\frac{y}{" + str(den_y) + r"}"
        else:
            term_str = r"\frac{" + str(b_coeff) + r"y}{" + str(den_y) + r"}"
        
        if b_coeff > 0 and lhs_parts: # Positive Y, and X term exists
            lhs_parts.append("+" + term_str)
        else: # Negative Y, or Y is the first term
            lhs_parts.append(term_str)
            
    # Handle case where both x and y coefficients are 0
    if not lhs_parts:
        const_str = str(int(const_val)) if const_val == int(const_val) else f"{const_val:.2f}"
        return f"0 = {const_str}" if const_val != 0 else "0 = 0"

    # Format constant value: integer if no decimal, otherwise two decimal places, stripped.
    const_str_val = str(int(const_val)) if const_val == int(const_val) else f"{const_val:.2f}".rstrip('0').rstrip('.')
    if not const_str_val: const_str_val = "0" # Handle case where 0.00 becomes ""
    
    return "".join(lhs_parts) + f" = {const_str_val}"

def _format_decimal_equation(a_dec, b_dec, c_dec):
    """
    Formats a linear equation with decimal coefficients.
    Example: 0.2x + 0.3y = 0.5
    """
    lhs_parts = []
    
    # Helper to format decimal coefficients
    def _format_dec_coeff(val):
        s = f"{val:.2f}".rstrip('0') # up to two decimal places, remove trailing zeros
        if s.endswith('.'):
            s = s.rstrip('.')
        return s if s else "0" # Ensure "0" for actual zero values

    a_str = _format_dec_coeff(a_dec)
    b_str = _format_dec_coeff(b_dec)
    c_str = _format_dec_coeff(c_dec)

    # X term
    if a_dec != 0:
        lhs_parts.append(a_str + "x")
    
    # Y term
    if b_dec != 0:
        if b_dec > 0 and lhs_parts:
            lhs_parts.append("+" + b_str + "y")
        else:
            lhs_parts.append(b_str + "y")
            
    # Handle case where both x and y coefficients are 0
    if not lhs_parts:
        return f"0 = {c_str}" if c_dec != 0 else "0 = 0"
        
    return "".join(lhs_parts) + f" = {c_str}"


def generate(level=1):
    """
    Generates a system of linear equations problem.

    Args:
        level (int): Difficulty level. Currently only level 1 is supported.

    Returns:
        dict: A dictionary containing the question text, correct answer,
              answer explanation (for internal use), and image (if any).
    """
    problem_type = random.choice([
        "Type 1",   # Basic integer coefficients
        "Type 2a",  # Fractional coefficients
        "Type 2b",  # Decimal coefficients
        "Type 3"    # Word Problem
    ])

    question_text = ""
    correct_answer = {}
    answer_explanation = "" 
    image_base64 = None
    
    # Ensure coefficients and constants are within a reasonable range for K12.
    # Avoid trivial solutions like (0,0) unless intended for specific learning.
    
    if problem_type == "Type 1":
        # Type 1 (Maps to Example 1): Basic system of linear equations with integer coefficients.
        # Strategy: Generate a solution (x0, y0) first, then generate coefficients
        # to ensure integer coefficients and a solvable system.
        
        # Generate target solution (x0, y0)
        x0 = random.randint(-5, 5)
        y0 = random.randint(-5, 5)
        
        # Ensure x0 and y0 are not both zero for slightly more complex problems.
        if x0 == 0 and y0 == 0:
            x0 = random.choice([-1, 1])
            y0 = random.choice([-1, 1])

        # Generate coefficients for the first equation
        a1 = random.randint(-5, 5)
        b1 = random.randint(-5, 5)
        while a1 == 0 and b1 == 0: # Ensure not 0x + 0y
            a1 = random.randint(-5, 5)
            b1 = random.randint(-5, 5)
        c1 = a1 * x0 + b1 * y0

        # Generate coefficients for the second equation
        # To ensure a unique solution, the determinant (a1*b2 - b1*a2) should not be zero.
        a2 = random.randint(-5, 5)
        b2 = random.randint(-5, 5)
        
        attempts = 0
        while (a1 * b2 - b1 * a2) == 0 and attempts < 10:
            a2 = random.randint(-5, 5)
            b2 = random.randint(-5, 5)
            while a2 == 0 and b2 == 0:
                a2 = random.randint(-5, 5)
                b2 = random.randint(-5, 5)
            attempts += 1
        
        # Fallback to a simpler, guaranteed solvable system if random generation fails too many times.
        if (a1 * b2 - b1 * a2) == 0:
            a1, b1 = 2, 3
            a2, b2 = 1, -1
            c1 = a1 * x0 + b1 * y0
            c2 = a2 * x0 + b2 * y0
        else:
            c2 = a2 * x0 + b2 * y0

        eq1_str = _generate_linear_equation(a1, b1, c1)
        eq2_str = _generate_linear_equation(a2, b2, c2)

        question_text_template = r"解下列聯立方程式：$\begin{cases} {eq1} \\ {eq2} \end{cases}$"
        question_text = question_text_template.replace("{eq1}", eq1_str).replace("{eq2}", eq2_str)
        
        correct_answer = {"x": x0, "y": y0}
        answer_explanation = f"將 $(x, y) = ({x0}, {y0})$ 代入兩個方程式，均成立。"

    elif problem_type == "Type 2a":
        # Type 2a (Maps to Example 3, 4): System of equations involving fractions.
        # Strategy: Generate integer solution and coefficients, then introduce fractions.
        x0 = random.randint(-4, 4)
        y0 = random.randint(-4, 4)
        if x0 == 0 and y0 == 0:
            x0 = random.choice([-1, 1])
            y0 = random.choice([-1, 1])

        # Equation 1: a1*x/den1_x + b1*y/den1_y = c1_prime
        den1_x = random.choice([2, 3, 4, 5])
        den1_y = random.choice([2, 3, 4, 5])
        
        a1_num = random.randint(1, 3) * random.choice([-1, 1])
        b1_num = random.randint(1, 3) * random.choice([-1, 1])
        while a1_num == 0 and b1_num == 0:
            a1_num = random.randint(1, 3) * random.choice([-1, 1])
            b1_num = random.randint(1, 3) * random.choice([-1, 1])

        c1_prime = (a1_num * x0 / den1_x) + (b1_num * y0 / den1_y)
        
        # Equation 2: a2*x/den2_x + b2*y/den2_y = c2_prime
        den2_x = random.choice([2, 3, 4, 5])
        den2_y = random.choice([2, 3, 4, 5])

        a2_num = random.randint(1, 3) * random.choice([-1, 1])
        b2_num = random.randint(1, 3) * random.choice([-1, 1])
        while a2_num == 0 and b2_num == 0:
            a2_num = random.randint(1, 3) * random.choice([-1, 1])
            b2_num = random.randint(1, 3) * random.choice([-1, 1])

        # Check for unique solution (determinant of underlying integer system != 0)
        # The underlying integer system is (a1_num*LCM/den1_x)X + (b1_num*LCM/den1_y)Y = ...
        # Simplified check (cross-multiplied coefficients)
        attempts = 0
        while (a1_num * den1_y * b2_num * den2_x - b1_num * den1_x * a2_num * den2_y) == 0 and attempts < 10:
            a2_num = random.randint(1, 3) * random.choice([-1, 1])
            b2_num = random.randint(1, 3) * random.choice([-1, 1])
            while a2_num == 0 and b2_num == 0:
                a2_num = random.randint(1, 3) * random.choice([-1, 1])
                b2_num = random.randint(1, 3) * random.choice([-1, 1])
            attempts += 1

        if (a1_num * den1_y * b2_num * den2_x - b1_num * den1_x * a2_num * den2_y) == 0:
             # Fallback to a simpler, guaranteed solvable system
            a1_num, b1_num, den1_x, den1_y = 1, 1, 2, 3
            a2_num, b2_num, den2_x, den2_y = 1, -1, 3, 2
            c1_prime = (a1_num * x0 / den1_x) + (b1_num * y0 / den1_y)
            c2_prime = (a2_num * x0 / den2_x) + (b2_num * y0 / den2_y)
        else:
            c2_prime = (a2_num * x0 / den2_x) + (b2_num * y0 / den2_y)

        eq1_str = _format_fractional_equation(a1_num, b1_num, den1_x, den1_y, c1_prime)
        eq2_str = _format_fractional_equation(a2_num, b2_num, den2_x, den2_y, c2_prime)

        question_text_template = r"解下列聯立方程式：$\begin{cases} {eq1} \\ {eq2} \end{cases}$"
        question_text = question_text_template.replace("{eq1}", eq1_str).replace("{eq2}", eq2_str)

        correct_answer = {"x": x0, "y": y0}
        answer_explanation = f"將 $(x, y) = ({x0}, {y0})$ 代入兩個方程式，均成立。"

    elif problem_type == "Type 2b":
        # Type 2b (Maps to Example 3, 4): System of equations involving decimals.
        # Strategy: Generate integer solution and coefficients, then introduce decimals.
        x0 = random.randint(-5, 5)
        y0 = random.randint(-5, 5)
        if x0 == 0 and y0 == 0:
            x0 = random.choice([-1, 1])
            y0 = random.choice([-1, 1])

        # Equation 1: 0.ax + 0.by = 0.c
        a1_int = random.randint(-9, 9)
        b1_int = random.randint(-9, 9)
        while a1_int == 0 and b1_int == 0:
            a1_int = random.randint(-9, 9)
            b1_int = random.randint(-9, 9)

        c1_int = a1_int * x0 + b1_int * y0
        
        dec_places1 = random.choice([1, 2])
        divisor1 = 10 ** dec_places1
        
        a1_dec = a1_int / divisor1
        b1_dec = b1_int / divisor1
        c1_dec = c1_int / divisor1

        # Equation 2: Similar decimal equation
        a2_int = random.randint(-9, 9)
        b2_int = random.randint(-9, 9)
        while a2_int == 0 and b2_int == 0:
            a2_int = random.randint(-9, 9)
            b2_int = random.randint(-9, 9)

        c2_int = a2_int * x0 + b2_int * y0
        
        dec_places2 = random.choice([1, 2])
        divisor2 = 10 ** dec_places2

        a2_dec = a2_int / divisor2
        b2_dec = b2_int / divisor2
        c2_dec = c2_int / divisor2
        
        # Check for unique solution (determinant of underlying integer system != 0)
        attempts = 0
        while (a1_int * b2_int - b1_int * a2_int) == 0 and attempts < 10:
            a2_int = random.randint(-9, 9)
            b2_int = random.randint(-9, 9)
            while a2_int == 0 and b2_int == 0:
                a2_int = random.randint(-9, 9)
                b2_int = random.randint(-9, 9)
            c2_int = a2_int * x0 + b2_int * y0
            a2_dec = a2_int / divisor2
            b2_dec = b2_int / divisor2
            c2_dec = c2_int / divisor2
            attempts += 1
        
        if (a1_int * b2_int - b1_int * a2_int) == 0:
            # Fallback to a simpler, guaranteed solvable system
            a1_dec, b1_dec, c1_dec = 0.2, 0.3, (0.2*x0 + 0.3*y0)
            a2_dec, b2_dec, c2_dec = 0.1, -0.1, (0.1*x0 - 0.1*y0)

        eq1_str = _format_decimal_equation(a1_dec, b1_dec, c1_dec)
        eq2_str = _format_decimal_equation(a2_dec, b2_dec, c2_dec)

        question_text_template = r"解下列聯立方程式：$\begin{cases} {eq1} \\ {eq2} \end{cases}$"
        question_text = question_text_template.replace("{eq1}", eq1_str).replace("{eq2}", eq2_str)

        correct_answer = {"x": x0, "y": y0}
        answer_explanation = f"將 $(x, y) = ({x0}, {y0})$ 代入兩個方程式，均成立。"

    elif problem_type == "Type 3":
        # Type 3 (Maps to Example 5, 6, 7): Word problems.
        
        sub_type = random.choice(["sum_difference", "age_problem", "items_price"])

        if sub_type == "sum_difference":
            # Example: Two numbers sum to S and their difference is D. Find the numbers.
            num1 = random.randint(10, 50)
            num2 = random.randint(5, 40)
            while num1 == num2: # Ensure distinct numbers
                num2 = random.randint(5, 40)
            
            if num1 < num2: # Ensure num1 is the larger number
                num1, num2 = num2, num1

            sum_val = num1 + num2
            diff_val = num1 - num2 

            question_text_template = r"有兩個數，它們的和是 ${sum_val}$，它們的差是 ${diff_val}$。請問這兩個數分別是多少？"
            question_text = question_text_template.replace("{sum_val}", str(sum_val)).replace("{diff_val}", str(diff_val))
            
            correct_answer = {"較大的數": num1, "較小的數": num2}
            answer_explanation = f"設較大的數為 $x$，較小的數為 $y$。則 $x+y={sum_val}$，$x-y={diff_val}$。解得 $x={num1}$，$y={num2}$。"

        elif sub_type == "age_problem":
            # Example: Father and son age problem.
            son_age_now = random.randint(8, 15)
            father_age_now = random.randint(30, 45)
            while father_age_now <= son_age_now + 20: # Ensure reasonable age difference
                father_age_now = random.randint(30, 45)
            
            age_diff = father_age_now - son_age_now
            
            # Generate future_years and ratio such that ratio is an integer and problem is solvable.
            future_years = random.randint(3, 10)
            ratio_int = -1
            attempts = 0
            while attempts < 10:
                current_sum = father_age_now + son_age_now
                future_sum = current_sum + 2 * future_years
                
                # We need (father_age_now + future_years) = ratio_int * (son_age_now + future_years)
                # Let S_f = father_age_now + future_years, S_s = son_age_now + future_years
                # S_f = ratio_int * S_s
                # We also have father_age_now = son_age_now + age_diff
                # (son_age_now + age_diff + future_years) = ratio_int * (son_age_now + future_years)
                
                if (son_age_now + future_years) != 0 and (father_age_now + future_years) % (son_age_now + future_years) == 0:
                    ratio_int = (father_age_now + future_years) // (son_age_now + future_years)
                    if ratio_int >= 2: # Ratio should be at least 2
                        break
                
                future_years = random.randint(3, 10)
                attempts += 1

            if attempts == 10: # Fallback for solvability
                son_age_now = 10
                father_age_now = 40
                age_diff = 30
                future_years = 5
                ratio_int = 3 # (40+5)/(10+5) = 45/15 = 3

            question_text_template = r"爸爸現在比小明大 ${age_diff}$ 歲。再過 ${future_years}$ 年，爸爸的年齡會是小明的 ${ratio_int}$ 倍。請問小明和爸爸現在各是幾歲？"
            question_text = question_text_template.replace("{age_diff}", str(age_diff)).replace("{future_years}", str(future_years)).replace("{ratio_int}", str(ratio_int))
            
            correct_answer = {"小明現在的年齡": son_age_now, "爸爸現在的年齡": father_age_now}
            answer_explanation = f"設小明現在 $y$ 歲，爸爸現在 $x$ 歲。則 $x-y={age_diff}$，且 $x+{future_years}={ratio_int}(y+{future_years})$。解得 $x={father_age_now}$，$y={son_age_now}$。"

        elif sub_type == "items_price":
            # Example: Buying pens and notebooks.
            pen_price = random.randint(5, 15)
            notebook_price = random.randint(15, 30)
            
            num_pens_scenario1 = random.randint(3, 10)
            num_notebooks_scenario1 = random.randint(2, 7)
            total_cost_scenario1 = num_pens_scenario1 * pen_price + num_notebooks_scenario1 * notebook_price

            num_pens_scenario2 = random.randint(5, 12)
            num_notebooks_scenario2 = random.randint(3, 8)
            # Ensure scenario 2 is different enough from scenario 1 and coefficients lead to unique solution
            attempts = 0
            while (num_pens_scenario2 == num_pens_scenario1 and num_notebooks_scenario2 == num_notebooks_scenario1) or \
                  (num_pens_scenario1 * num_notebooks_scenario2 - num_notebooks_scenario1 * num_pens_scenario2 == 0) and attempts < 10:
                 num_pens_scenario2 = random.randint(5, 12)
                 num_notebooks_scenario2 = random.randint(3, 8)
                 attempts += 1
            
            if (num_pens_scenario1 * num_notebooks_scenario2 - num_notebooks_scenario1 * num_pens_scenario2) == 0:
                # Fallback
                num_pens_scenario1, num_notebooks_scenario1 = 3, 2
                num_pens_scenario2, num_notebooks_scenario2 = 5, 3

            total_cost_scenario2 = num_pens_scenario2 * pen_price + num_notebooks_scenario2 * notebook_price

            question_text_template = r"小華去文具店買文具。如果他買 ${num_pens1}$ 枝筆和 ${num_notebooks1}$ 本筆記本，共需花費 ${cost1}$ 元。如果他買 ${num_pens2}$ 枝筆和 ${num_notebooks2}$ 本筆記本，共需花費 ${cost2}$ 元。請問一枝筆和一本筆記本的單價各是多少元？"
            question_text = question_text_template.replace("{num_pens1}", str(num_pens_scenario1)).replace("{num_notebooks1}", str(num_notebooks_scenario1)).replace("{cost1}", str(total_cost_scenario1)).replace("{num_pens2}", str(num_pens_scenario2)).replace("{num_notebooks2}", str(num_notebooks_scenario2)).replace("{cost2}", str(total_cost_scenario2))
            
            correct_answer = {"一枝筆的單價": pen_price, "一本筆記本的單價": notebook_price}
            answer_explanation = f"設一枝筆 $x$ 元，一本筆記本 $y$ 元。則 ${num_pens_scenario1}x + {num_notebooks_scenario1}y = {total_cost_scenario1}$，且 ${num_pens_scenario2}x + {num_notebooks_scenario2}y = {total_cost_scenario2}$。解得 $x={pen_price}$，$y={notebook_price}$。"


    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": str(correct_answer), # String representation of the dict for display
        "image_base64": image_base64,
        "created_at": datetime.datetime.now().isoformat(),
        "version": "1.0"
    }


    """
    Checks the user's answer against the correct answer.

    Args:
        user_answer (dict or str): The user's submitted answer. Expected format:
                                    a dictionary like {"x": 5, "y": 3} or
                                    a string representation of such a dictionary.
        correct_answer (dict): The correct answer generated by the system.

    Returns:
        bool: True if the answer is correct, False otherwise.
    """
    if isinstance(user_answer, str):
        try:
            # Safely evaluate string to dict (limited scope)
            # For production, a more robust parser than eval might be needed.
            user_answer_dict = eval(user_answer) 
        except (SyntaxError, NameError):
            return False # Cannot parse string
    elif isinstance(user_answer, dict):
        user_answer_dict = user_answer
    else:
        return False # Unsupported answer format

    # Check if all keys in correct_answer are present in user_answer_dict
    if not all(key in user_answer_dict for key in correct_answer):
        return False
    
    # Check if values match, allowing for minor floating point discrepancies
    for key, value in correct_answer.items():
        try:
            user_val = float(user_answer_dict.get(key))
            correct_val = float(value)
            if not math.isclose(user_val, correct_val, rel_tol=1e-9, abs_tol=1e-9):
                return False
        except (ValueError, TypeError):
            return False # User answer value is not a valid number
            
    # Also check if user provided extra keys not in correct_answer (optional, but good practice)
    if len(user_answer_dict) != len(correct_answer):
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
            triggers = ['^', '/', ',', '|', '(', '[', '{', '\\']
            
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
