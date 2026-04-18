# ==============================================================================
# ID: gh_FundamentalTheoremOfCalculus
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 148.73s | RAG: 5 examples
# Created At: 2026-01-29 19:22:03
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
import re
 # For math.isclose in check function

# Placeholder for coordinate generation, not directly used in this calculus skill
def _generate_coordinate_value():
    """
    Generates an integer coordinate value.
    Adheres to V10.2 Coordinate Hardening Spec for structured data generation,
    though only the integer part is relevant for this calculus skill's coefficients/limits.
    """
    val = random.randint(-8, 8)
    # Return format (float_val, (int_part, num, den, is_neg)) for strict adherence
    return (float(val), (val, 0, 0, val < 0))

def generate(level=1):
    """
    Generates a K12 calculus problem related to the Fundamental Theorem of Calculus,
    strictly mirroring RAG examples.

    Args:
        level (int): Difficulty level (not directly used for randomization in this spec, but kept for API consistency).

    Returns:
        dict: A dictionary containing the question text, correct answer, solution, and image data.
    """
    # [CRITICAL RULE: Variant Support] - Randomly choose problem type
    # Each problem type strictly maps to a RAG example as per rule 2.
    problem_type = random.choice([
        "RAG_Ex1_DefinitePoly",
        "RAG_Ex2_DefinitePoly",
        "RAG_Ex3_FindTwoConstants",
        "RAG_Ex4_IntegralProperties",
        "RAG_Ex5_FindFxAndA"
    ])

    question_text = ""
    correct_answer = ""
    solution_text = ""
    image_base64 = None # No images for these types of calculus problems

    # Helper for formatting polynomial expressions with signs and coefficients (e.g., "x^2 - 3x + 5")
    def format_polynomial_expression(terms, var='x'):
        parts = []
        for i, (coeff, power) in enumerate(terms):
            if coeff == 0:
                continue
            
            term_str_val = ""
            if abs(coeff) == 1 and power > 0: # For 'x^2' instead of '1x^2'
                term_str_val = "-" if coeff == -1 else ""
            else:
                term_str_val = str(coeff)

            if power == 0: # Constant term
                pass
            elif power == 1: # Linear term
                term_str_val += var
            else: # Higher power term
                term_str_val += f"{var}^{power}"
            
            if i > 0 and coeff > 0: # Add '+' for subsequent positive terms
                parts.append(f"+ {term_str_val}")
            elif i > 0 and coeff < 0: # Add '-' for subsequent negative terms (after removing its own negative sign)
                parts.append(f"- {term_str_val[1:]}")
            else: # First term (handle its own sign)
                parts.append(term_str_val)
                
        return " ".join(parts) if parts else "0"


    if problem_type == "RAG_Ex1_DefinitePoly":
        # Type 1 MUST use the EXACT mathematical model of RAG Ex 1.
        # RAG Ex 1: $\int_{-2}^3 (4x^3 - 2x) dx$. Model: Integral of (Ax^3 + Bx) dx from c to d
        A = random.randint(1, 5) * random.choice([-1, 1])
        B = random.randint(1, 5) * random.choice([-1, 1])
        c = random.randint(-3, 0)
        d = random.randint(1, 4)
        while c >= d: # Ensure distinct limits and d > c
            d = random.randint(1, 4)
        
        poly_terms = []
        if A != 0: poly_terms.append((A, 3))
        if B != 0: poly_terms.append((B, 1))
        poly_str = format_polynomial_expression(poly_terms)
        if not poly_str: poly_str = "0" # Should not be empty if A or B is non-zero

        question_text_template = r"求下列各式之值。$\int_{{{c}}}^{{{d}}} ({poly_str}) dx$。"
        question_text = question_text_template.replace("{c}", str(c))\
                                             .replace("{d}", str(d))\
                                             .replace("{poly_str}", poly_str)

        # Antiderivative F(x) = (A/4)x^4 + (B/2)x^2
        def F_antiderivative(x_val):
            return (A/4) * (x_val**4) + (B/2) * (x_val**2)
        
        ans_val_float = F_antiderivative(d) - F_antiderivative(c)
        correct_answer = str(round(ans_val_float, 5)) # [CRITICAL RULE: Answer Data Purity]

        solution_text_template = r"根據微積分基本定理第二部分，$\int_{{c}}^{{d}} f(x) dx = F(d) - F(c)$，其中 $F'(x) = f(x)$。" \
                                 r"本題中，$f(x) = {poly_str}$。" \
                                 r"其不定積分為 $F(x) = \frac{{{A}}}{4}x^4 + \frac{{{B}}}{2}x^2$。" \
                                 r"將上下限代入：$F({d}) = \frac{{{A}}}{4}({d})^4 + \frac{{{B}}}{2}({d})^2$" \
                                 r"且 $F({c}) = \frac{{{A}}}{4}({c})^4 + \frac{{{B}}}{2}({c})^2$。" \
                                 r"計算 $F({d}) - F({c}) = {ans_val}$。"
        
        solution_text = solution_text_template.replace("{c}", str(c))\
                                             .replace("{d}", str(d))\
                                             .replace("{A}", str(A))\
                                             .replace("{B}", str(B))\
                                             .replace("{poly_str}", poly_str)\
                                             .replace("{ans_val}", correct_answer)

    elif problem_type == "RAG_Ex2_DefinitePoly":
        # Type 2 MUST use the EXACT mathematical model of RAG Ex 2.
        # RAG Ex 2: $\int_{-1}^2 (x^2+6x-1) dx$. Model: Integral of (Px^2 + Qx + R) dx from a to b
        P = random.randint(1, 3) * random.choice([-1, 1])
        Q = random.randint(1, 5) * random.choice([-1, 1])
        R = random.randint(1, 5) * random.choice([-1, 1])
        
        a = random.randint(-2, 0)
        b = random.randint(1, 3)
        while a >= b: # Ensure distinct limits and b > a
            b = random.randint(1, 3)

        poly_terms = []
        if P != 0: poly_terms.append((P, 2))
        if Q != 0: poly_terms.append((Q, 1))
        if R != 0: poly_terms.append((R, 0))
        poly_str = format_polynomial_expression(poly_terms)
        if not poly_str: poly_str = "0"

        question_text_template = r"求下列各式之值。$\int_{{{a}}}^{{{b}}} ({poly_str}) dx$。"
        question_text = question_text_template.replace("{a}", str(a))\
                                             .replace("{b}", str(b))\
                                             .replace("{poly_str}", poly_str)

        # Antiderivative F(x) = (P/3)x^3 + (Q/2)x^2 + Rx
        def F_antiderivative(x_val):
            return (P/3) * (x_val**3) + (Q/2) * (x_val**2) + R * x_val
        
        ans_val_float = F_antiderivative(b) - F_antiderivative(a)
        correct_answer = str(round(ans_val_float, 5)) # [CRITICAL RULE: Answer Data Purity]

        solution_text_template = r"根據微積分基本定理第二部分，$\int_{{a}}^{{b}} f(x) dx = F(b) - F(a)$，其中 $F'(x) = f(x)$。" \
                                 r"本題中，$f(x) = {poly_str}$。" \
                                 r"其不定積分為 $F(x) = \frac{{{P}}}{3}x^3 + \frac{{{Q}}}{2}x^2 + {R}x$。" \
                                 r"將上下限代入：$F({b}) = \frac{{{P}}}{3}({b})^3 + \frac{{{Q}}}{2}({b})^2 + {R}({b})$" \
                                 r"且 $F({a}) = \frac{{{P}}}{3}({a})^3 + \frac{{{Q}}}{2}({a})^2 + {R}({a})$。" \
                                 r"計算 $F({b}) - F({a}) = {ans_val}$。"
        
        solution_text = solution_text_template.replace("{a}", str(a))\
                                             .replace("{b}", str(b))\
                                             .replace("{P}", str(P))\
                                             .replace("{Q}", str(Q))\
                                             .replace("{R}", str(R))\
                                             .replace("{poly_str}", poly_str)\
                                             .replace("{ans_val}", correct_answer)

    elif problem_type == "RAG_Ex3_FindTwoConstants":
        # Type 3 MUST use the EXACT mathematical model of RAG Ex 3.
        # RAG Ex 3: 已知 $\int_{-1}^1 (ax^2+2x-b) dx = \frac{4}{3}$ 且 $\int_1^2 (ax+b) dx = \frac{44}{3}$，求實數 $a, b$ 的值。
        
        # Choose target a and b values first to ensure clean results
        a_ans = random.randint(-3, 3)
        while a_ans == 0: # Ensure 'a' is non-zero
            a_ans = random.randint(-3, 3)
        b_ans = random.randint(-3, 3)

        # Calculate V1 = int_{-1}^1 (a_ans*x^2 + 2x - b_ans) dx
        # F1(x) = (a_ans/3)x^3 + x^2 - b_ans*x
        # F1(1) - F1(-1) = ((a_ans/3) + 1 - b_ans) - (-(a_ans/3) + 1 + b_ans) = (2/3)a_ans - 2b_ans
        V1_float = (2/3) * a_ans - 2 * b_ans
        
        # Calculate V2 = int_1^2 (a_ans*x + b_ans) dx
        # F2(x) = (a_ans/2)x^2 + b_ans*x
        # F2(2) - F2(1) = ( (a_ans/2)*4 + b_ans*2 ) - ( (a_ans/2)*1 + b_ans*1 ) = (3/2)a_ans + b_ans
        V2_float = (3/2) * a_ans + b_ans

        # Display V1 and V2 as fractions if possible, or floats
        # Multiplying by 6 to get common denominator for (2/3) and (3/2)
        V1_num_for_frac = V1_float * 6
        V2_num_for_frac = V2_float * 6

        V1_str = f"\\frac{{{int(V1_num_for_frac)}}}{{6}}" if V1_num_for_frac % 1 == 0 else str(round(V1_float, 5))
        V2_str = f"\\frac{{{int(V2_num_for_frac)}}}{{6}}" if V2_num_for_frac % 1 == 0 else str(round(V2_float, 5))

        # Using the exact polynomial forms from RAG Ex 3
        question_text_template = r"已知 $\int_{{-1}}^{{1}} (ax^2+2x-b) dx = {V1_str}$ 且 $\int_{{1}}^{{2}} (ax+b) dx = {V2_str}$，求實數 $a$ 之值。"
        
        question_text = question_text_template.replace("{V1_str}", V1_str)\
                                             .replace("{V2_str}", V2_str)

        correct_answer = str(round(a_ans, 5)) # [CRITICAL RULE: Answer Data Purity] - Asking only for 'a'

        solution_text_template = r"首先計算第一個定積分：$\int_{{-1}}^{{1}} (ax^2+2x-b) dx$。" \
                                 r"其不定積分為 $F_1(x) = \frac{{a}}{3}x^3 + x^2 - bx$。" \
                                 r"$F_1(1) - F_1(-1) = (\frac{{a}}{3} + 1 - b) - (-\frac{{a}}{3} + 1 + b) = \frac{{2a}}{3} - 2b$。" \
                                 r"所以我們得到第一個方程式：$\frac{{2a}}{3} - 2b = {V1_str}$ (1)" \
                                 r"接著計算第二個定積分：$\int_{{1}}^{{2}} (ax+b) dx$。" \
                                 r"其不定積分為 $F_2(x) = \frac{{a}}{2}x^2 + bx$。" \
                                 r"$F_2(2) - F_2(1) = (\frac{{a}}{2}(2)^2 + b(2)) - (\frac{{a}}{2}(1)^2 + b(1)) = (2a + 2b) - (\frac{{a}}{2} + b) = \frac{{3a}}{2} + b$。" \
                                 r"所以我們得到第二個方程式：$\frac{{3a}}{2} + b = {V2_str}$ (2)" \
                                 r"解聯立方程式 (1) 和 (2)：" \
                                 r"由 (2) 得 $b = {V2_float} - \frac{{3a}}{2}$。" \
                                 r"代入 (1)：$\frac{{2a}}{3} - 2({V2_float} - \frac{{3a}}{2}) = {V1_float}$" \
                                 r"$\frac{{2a}}{3} - 2 \cdot {V2_float} + 3a = {V1_float}$" \
                                 r"$(\frac{{2}}{3} + 3)a = {V1_float} + 2 \cdot {V2_float}$" \
                                 r"$\frac{{11}}{3}a = {V1_float} + 2 \cdot {V2_float}$" \
                                 r"$a = \frac{{3}}{{11}} \cdot ({V1_float} + 2 \cdot {V2_float}) = {a_ans}$。"
        
        solution_text = solution_text_template.replace("{V1_str}", V1_str)\
                                             .replace("{V2_str}", V2_str)\
                                             .replace("{V1_float}", str(round(V1_float, 5)))\
                                             .replace("{V2_float}", str(round(V2_float, 5)))\
                                             .replace("{a_ans}", str(round(a_ans, 5)))

    elif problem_type == "RAG_Ex4_IntegralProperties":
        # Type 4 MUST use the EXACT mathematical model of RAG Ex 4.
        # RAG Ex 4: 已知函數 $f(x)$ 滿足 $\int_1^3 f(x) dx = 2$ 且 $\int_3^5 f(x) dx = 6$，求 $\int_1^5 f(x) dx$。
        # (Simplified to ask for only one part for a single numerical answer)
        
        # Generate limits and values
        A = random.randint(1, 2)
        B = A + random.randint(2, 3)
        C = B + random.randint(2, 3)
        
        V_AB = random.randint(1, 10) * random.choice([-1, 1])
        V_BC = random.randint(1, 10) * random.choice([-1, 1])

        # Question asks for $\int_A^C f(x) dx$
        question_text_template = r"已知函數 $f(x)$ 滿足 $\int_{{{A}}}^{{{B}}} f(x) dx = {V_AB}$ 且 $\int_{{{B}}}^{{{C}}} f(x) dx = {V_BC}$，求 $\int_{{{A}}}^{{{C}}} f(x) dx$ 之值。"
        
        question_text = question_text_template.replace("{A}", str(A))\
                                             .replace("{B}", str(B))\
                                             .replace("{C}", str(C))\
                                             .replace("{V_AB}", str(V_AB))\
                                             .replace("{V_BC}", str(V_BC))

        ans_val = V_AB + V_BC
        correct_answer = str(ans_val) # [CRITICAL RULE: Answer Data Purity]

        solution_text_template = r"根據定積分的性質，$\int_{{A}}^{{C}} f(x) dx = \int_{{A}}^{{B}} f(x) dx + \int_{{B}}^{{C}} f(x) dx$。" \
                                 r"將已知條件代入：$\int_{{{A}}}^{{{C}}} f(x) dx = {V_AB} + {V_BC} = {ans_val}$。"
        
        solution_text = solution_text_template.replace("{A}", str(A))\
                                             .replace("{B}", str(B))\
                                             .replace("{C}", str(C))\
                                             .replace("{V_AB}", str(V_AB))\
                                             .replace("{V_BC}", str(V_BC))\
                                             .replace("{ans_val}", str(ans_val))

    elif problem_type == "RAG_Ex5_FindFxAndA":
        # Type 5 MUST use the EXACT mathematical model of RAG Ex 5.
        # RAG Ex 5: 已知 $a$ 為實數，且函數 $f(x)$ 滿足 $\int_a^x f(t) dt = -x^2 - 3x - 10$。(1)求 $f(x)$。(2)求 $a$ 的值。
        
        # Ensure G(x) has real roots for 'a'
        a_ans = random.randint(-3, 3)
        r2 = random.randint(-3, 3) # Another root, could be same as a_ans
        
        # Coefficient K for G(x)
        K = random.randint(1, 3) * random.choice([-1, 1])
        
        # G(x) = K * (x - a_ans) * (x - r2) = Kx^2 - K(a_ans + r2)x + K*a_ans*r2
        coeff_A = K
        coeff_B = -K * (a_ans + r2)
        coeff_C = K * a_ans * r2

        G_x_terms = []
        if coeff_A != 0: G_x_terms.append((coeff_A, 2))
        if coeff_B != 0: G_x_terms.append((coeff_B, 1))
        if coeff_C != 0: G_x_terms.append((coeff_C, 0))
        G_x_formatted_str = format_polynomial_expression(G_x_terms)
        if not G_x_formatted_str: G_x_formatted_str = "0"

        # Question asks for 'a'
        question_text_template = r"已知 $a$ 為實數，且函數 $f(x)$ 滿足 $\int_{{a}}^{{x}} f(t) dt = {G_x_formatted_str}$。" \
                                 r"試求 $a$ 之值。"
        
        question_text = question_text_template.replace("{G_x_formatted_str}", G_x_formatted_str)

        correct_answer = str(round(a_ans, 5)) # [CRITICAL RULE: Answer Data Purity]

        # Format f(x) for solution (f(x) = G'(x))
        f_x_coeff_A = 2 * coeff_A
        f_x_coeff_B = coeff_B
        
        f_x_terms = []
        if f_x_coeff_A != 0: f_x_terms.append((f_x_coeff_A, 1))
        if f_x_coeff_B != 0: f_x_terms.append((f_x_coeff_B, 0))
        f_x_formatted_str = format_polynomial_expression(f_x_terms)
        if not f_x_formatted_str: f_x_formatted_str = "0"

        # Replace 'x' with 'a' in G_x_formatted_str for the equation G(a)=0
        G_x_formatted_str_at_a = G_x_formatted_str.replace("x^2", "a^2").replace("x", "a")

        solution_text_template = r"根據微積分基本定理第一部分，若 $\int_{{a}}^{{x}} f(t) dt = G(x)$，則 $f(x) = G'(x)$。" \
                                 r"本題中，$G(x) = {G_x_formatted_str}$。" \
                                 r"所以 $f(x) = \frac{{d}}{{dx}}({G_x_formatted_str}) = {f_x_formatted_str}$。" \
                                 r"此外，當 $x=a$ 時，$\int_{{a}}^{{a}} f(t) dt = 0$。" \
                                 r"因此，將 $x=a$ 代入給定的等式，得到 $0 = {G_x_formatted_str_at_a}$。" \
                                 r"解此二次方程式 ${G_x_formatted_str_at_a} = 0$。" \
                                 r"此方程式的根為 $a = {a_ans}$ 或 $a = {r2}$。" \
                                 r"題目要求 $a$ 的值，其中一個解為 ${a_ans}$。"

        solution_text = solution_text_template.replace("{G_x_formatted_str}", G_x_formatted_str)\
                                             .replace("{f_x_formatted_str}", f_x_formatted_str)\
                                             .replace("{G_x_formatted_str_at_a}", G_x_formatted_str_at_a)\
                                             .replace("{a_ans}", str(round(a_ans, 5)))\
                                             .replace("{r2}", str(round(r2, 5)))

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": solution_text, # `answer` field is used for detailed solution text
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0" # Initial version
    }

# Universal Check Function Template (as per CRITICAL CODING STANDARDS)

    import re, math
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        # Remove common non-numeric/non-decimal/non-slash characters for parsing numerical answers
        return re.sub(r'[\$\s\(\)\{\}\[\]\\a-zA-Z=,;:\u4e00-\u9fff]', '', s) 

    u_str = str(user_answer).strip()
    c_str = str(correct_answer).strip()
    
    yes_group = ["是", "yes", "true", "1", "o", "right"]
    no_group = ["否", "no", "false", "0", "x", "wrong"]
    
    # [V18.13 Update] 支援中英文是非題互通
    # Convert input to lowercase for case-insensitive comparison
    u_str_lower = u_str.lower()
    c_str_lower = c_str.lower()

    if c_str_lower in yes_group:
        return {"correct": u_str_lower in yes_group, "result": "正確！" if u_str_lower in yes_group else "答案錯誤"}
    if c_str_lower in no_group:
        return {"correct": u_str_lower in no_group, "result": "正確！" if u_str_lower in no_group else "答案錯誤"}

    # 3. 數值與字串比對
    try:
        # 解析分數與浮點數
        def parse(v):
           if "/" in v: 
               parts = v.split("/")
               if len(parts) == 2 and parts[1] != '0': # Avoid division by zero
                   return float(parts[0]) / float(parts[1])
               else: # Invalid fraction format or division by zero
                   raise ValueError("Invalid fraction format or division by zero")
           return float(v)
        
        u_val = parse(clean(u_str))
        c_val = parse(clean(c_str))
        
        # Use a small tolerance for floating-point comparisons
        # Added abs_tol for better handling of values close to zero
        if math.isclose(u_val, c_val, rel_tol=1e-5, abs_tol=1e-8): 
            return {"correct": True, "result": "正確！"}
    except ValueError: # Catch conversion errors from parse() or float()
        pass
        
    # Fallback to strict string comparison if numerical parsing fails or is not applicable
    if u_str == c_str: return {"correct": True, "result": "正確！"}
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
