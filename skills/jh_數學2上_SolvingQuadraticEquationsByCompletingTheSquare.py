# ==============================================================================
# ID: jh_數學2上_SolvingQuadraticEquationsByCompletingTheSquare
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 163.23s | RAG: 5 examples
# Created At: 2026-01-19 12:09:37
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

# --- Helper Functions (Coder MUST implement as module-level functions) ---

def _gcd(a, b):
    """
    Calculates the greatest common divisor of two integers.
    """
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a

def _simplify_fraction(numerator, denominator):
    """
    Simplifies a fraction and ensures the denominator is positive.
    Returns (simplified_numerator, simplified_denominator).
    Handles float inputs by converting to fractions with a common denominator if possible.
    """
    if denominator == 0:
        raise ValueError("Denominator cannot be zero.")
    if numerator == 0:
        return (0, 1)

    # If inputs are floats, convert to common fraction representation
    if isinstance(numerator, float) or isinstance(denominator, float):
        # Find a common multiplier to turn floats into integers
        multiplier = 1
        if isinstance(numerator, float):
            s_num = str(numerator)
            if '.' in s_num: multiplier = max(multiplier, 10**(len(s_num) - s_num.index('.') - 1))
        if isinstance(denominator, float):
            s_den = str(denominator)
            if '.' in s_den: multiplier = max(multiplier, 10**(len(s_den) - s_den.index('.') - 1))
        
        numerator = round(numerator * multiplier)
        denominator = round(denominator * multiplier)

    common = _gcd(numerator, denominator)
    num = numerator // common
    den = denominator // common

    # Ensure denominator is positive
    if den < 0:
        num = -num
        den = -den
    return (num, den)

def _simplify_sqrt_value(n):
    """
    Simplifies sqrt(n) into a*sqrt(b) form.
    Returns (coefficient, radicand) where sqrt(n) = coefficient * sqrt(radicand).
    e.g., _simplify_sqrt_value(8) -> (2, 2) for 2*sqrt(2)
          _simplify_sqrt_value(12) -> (2, 3) for 2*sqrt(3)
          _simplify_sqrt_value(5) -> (1, 5) for 1*sqrt(5)
    """
    if n < 0:
        raise ValueError("Cannot simplify sqrt of a negative number for real solutions.")
    if n == 0:
        return (0, 0)
    
    coeff = 1
    i = 2
    while i * i <= n:
        while n % (i * i) == 0:
            coeff *= i
            n //= (i * i)
        i += 1
    return (coeff, n)

def _format_solution_value_for_pure_data(sol_data):
    """
    Formats a single solution for the 'correct_answer' pure data string.
    Input sol_data can be:
    - int or float: 5 -> "5", 0.5 -> "1/2"
    - tuple (num, den): (1, 2) -> "1/2"
    - tuple (integer_part, sqrt_value_int): (2, 3) -> "2+sqrt(3)", (2, -3) -> "2-sqrt(3)"
                                            (0, 5) -> "sqrt(5)", (0, -5) -> "-sqrt(5)"
    Note: This function does NOT handle (A +/- B*sqrt(C))/D directly.
          For such cases, the generate function should construct the string directly.
    """
    if isinstance(sol_data, (int, float)):
        # Convert float to fraction if it's not an integer, otherwise just stringify
        if isinstance(sol_data, float) and not sol_data.is_integer():
            num, den = _simplify_fraction(sol_data, 1.0) # Convert float to fraction
            if den == 1:
                return str(num)
            return f"{num}/{den}"
        return str(int(sol_data) if sol_data.is_integer() else sol_data)
    elif isinstance(sol_data, tuple) and len(sol_data) == 2:
        # Fraction (num, den)
        if isinstance(sol_data[0], int) and isinstance(sol_data[1], int):
            num, den = _simplify_fraction(sol_data[0], sol_data[1])
            if den == 1:
                return str(num)
            return f"{num}/{den}"
        # Irrational (integer_part, sqrt_value_int) for A +/- sqrt(B) or A +/- C*sqrt(B)
        elif isinstance(sol_data[0], (int, float)) and isinstance(sol_data[1], (int, float)):
            int_part = sol_data[0]
            sqrt_val_raw = sol_data[1] # Can be positive or negative for +/- sqrt

            if sqrt_val_raw == 0:
                return str(int(int_part))
            
            sign = 1 if sqrt_val_raw > 0 else -1
            abs_sqrt_val = abs(sqrt_val_raw)
            
            coeff, radicand = _simplify_sqrt_value(abs_sqrt_val)

            if radicand == 0: # Should only happen if abs_sqrt_val was 0
                return str(int(int_part))
            if coeff == 0: # Should not happen if radicand is not 0
                 return str(int(int_part))

            sqrt_str_part = ""
            if coeff == 1:
                sqrt_str_part = f"sqrt({radicand})"
            else:
                sqrt_str_part = f"{coeff}*sqrt({radicand})"

            if int_part == 0:
                return f"-{sqrt_str_part}" if sign == -1 else sqrt_str_part
            else:
                op = "+" if sign == 1 else "-"
                return f"{int(int_part)}{op}{sqrt_str_part}"
    raise ValueError(f"Unsupported solution data format: {sol_data}")

# --- Problem Generation Logic ---

def generate(level=1):
    problem_type = random.choice([1, 2, 3, 4, 5]) 
    # problem_type = 5 # For testing specific type

    question_text_template = ""
    solution_text_parts = []
    correct_answers_list = [] # Store parsed solution values for formatting

    # Ensure current_time is in ISO format
    current_time = datetime.now().isoformat()

    if problem_type == 1:
        # Type 1 (Maps to RAG Ex 1): x² + Bx + ____ (fill in the blank)
        # ⑴ x²＋12x＋____⑵ x²-7x＋____ -> ⑴ 36, (x+6)², ⑵ 49/4, (x-7/2)²
        b_coeff = random.randint(-12, 12)
        while b_coeff == 0: # Ensure b is not 0
            b_coeff = random.randint(-12, 12)
        
        # 30% chance for b to be fractional (b_num/den)
        if random.random() < 0.3:
            b_den = random.choice([2, 3, 4])
            b_num = random.choice([-1, 1]) * random.randint(1, 11)
            b_num, b_den = _simplify_fraction(b_num, b_den)
            b_val_for_calc = b_num / b_den
            b_latex = r"\frac{" + str(b_num) + r"}{" + str(b_den) + r"}"
        else:
            b_val_for_calc = b_coeff
            b_latex = str(b_coeff)

        missing_term_val = (b_val_for_calc / 2) ** 2
        
        # Format for correct_answer (pure data)
        correct_answers_list.append(_format_solution_value_for_pure_data(missing_term_val))

        # Format for solution_text (LaTeX)
        b_half_val = b_val_for_calc / 2
        b_half_latex = ""
        if isinstance(b_half_val, float) and not b_half_val.is_integer():
            num_bh, den_bh = _simplify_fraction(b_half_val, 1)
            b_half_latex = r"\frac{" + str(num_bh) + r"}{" + str(den_bh) + r"}"
        else:
            b_half_latex = str(int(b_half_val))

        missing_term_latex_val = ""
        if isinstance(missing_term_val, float) and not missing_term_val.is_integer():
            num_mt, den_mt = _simplify_fraction(missing_term_val, 1)
            missing_term_latex_val = r"\frac{" + str(num_mt) + r"}{" + str(den_mt) + r"}"
        else:
            missing_term_latex_val = str(int(missing_term_val))

        perfect_square_form_latex = r"\left(x {sign_bh}{b_half_latex_abs}\right)^2".replace(
            "{sign_bh}", "+" if b_half_val >= 0 else ""
        ).replace(
            "{b_half_latex_abs}", b_half_latex if b_half_val >= 0 else b_half_latex.replace("-", "")
        )

        question_text_template = r"在下列各式中，填入適當的數，使其成為完全平方式：$x^2 {b_sign}{b_latex}x + \underline{{\quad}}$"
        question_text = question_text_template.replace("{b_sign}", "+" if b_val_for_calc > 0 else "").replace("{b_latex}", b_latex if b_val_for_calc > 0 else b_latex.replace("-", ""))

        solution_text_parts.append(r"解：對於 $x^2 + Bx + C$ 形式的二次式，若要使其成為完全平方式，則 $C = \left(\frac{B}{2}\right)^2$。")
        solution_text_parts.append(r"題目中，一次項係數 $B = {b_latex}$。".replace("{b_latex}", b_latex))
        solution_text_parts.append(r"因此，應填入的常數項為 $\left(\frac{{{b_latex}}}{{2}}\right)^2 = \left({b_half_latex}\right)^2 = {missing_term_latex_val}$。".replace("{b_latex}", b_latex).replace("{b_half_latex}", b_half_latex).replace("{missing_term_latex_val}", missing_term_latex_val))
        solution_text_parts.append(r"完全平方式為 ${perfect_square_form_latex}$。".replace("{perfect_square_form_latex}", perfect_square_form_latex))
        solution_text = "".join(solution_text_parts)


    elif problem_type == 2:
        # Type 2 (Maps to RAG Ex 2): x² + Bx + ____ = (x + ____)² (fill in two blanks)
        # ⑴ x²-6x＋____=(x-____)²⑵ x²＋(1/3)x＋____=(x＋____)² -> ⑴ 9, 3, ⑵ 1/36, 1/6
        b_coeff = random.randint(-10, 10)
        while b_coeff == 0:
            b_coeff = random.randint(-10, 10)

        # 50% chance for b to be fractional (b_num/den)
        if random.random() < 0.5:
            b_den = random.choice([2, 3, 4])
            b_num = random.choice([-1, 1]) * random.randint(1, 10)
            b_num, b_den = _simplify_fraction(b_num, b_den)
            b_val_for_calc = b_num / b_den
            b_latex = r"\frac{" + str(b_num) + r"}{" + str(b_den) + r"}"
        else:
            b_val_for_calc = b_coeff
            b_latex = str(b_coeff)
        
        missing_term_c = (b_val_for_calc / 2) ** 2
        missing_term_half_b = b_val_for_calc / 2

        # Format for correct_answer (pure data)
        correct_answers_list.append(_format_solution_value_for_pure_data(missing_term_c))
        correct_answers_list.append(_format_solution_value_for_pure_data(missing_term_half_b))
        
        # Sort for consistent output in correct_answer
        correct_answers_list.sort() # Sorts by string value, which is fine for pure data

        # Format for question_text and solution_text
        b_sign_for_x_term = "+" if b_val_for_calc > 0 else ""
        b_latex_abs = b_latex if b_val_for_calc > 0 else b_latex.replace("-", "")
        
        c_latex = _format_solution_value_for_pure_data(missing_term_c)
        hb_latex = _format_solution_value_for_pure_data(missing_term_half_b)
        
        hb_sign_for_paren = "+" if missing_term_half_b >= 0 else ""
        hb_latex_abs_paren = hb_latex if missing_term_half_b >= 0 else hb_latex.replace("-", "")

        question_text_template = r"在下列各式中，填入適當的數，使其成為完全平方式：$x^2 {b_sign}{b_latex_abs}x + \underline{{\quad}} = \left(x {hb_sign}{hb_latex_abs}\right)^2$"
        question_text = question_text_template.replace("{b_sign}", b_sign_for_x_term).replace("{b_latex_abs}", b_latex_abs).replace("{hb_sign}", hb_sign_for_paren).replace("{hb_latex_abs}", hb_latex_abs_paren)

        solution_text_parts.append(r"解：對於 $x^2 + Bx + C = (x+D)^2$ 形式的完全平方式，我們知道 $D = \frac{B}{2}$ 且 $C = D^2 = \left(\frac{B}{2}\right)^2$。")
        solution_text_parts.append(r"題目中，一次項係數 $B = {b_latex}$。".replace("{b_latex}", b_latex))
        
        solution_text_parts.append(r"第一個空格應填入 $C = \left(\frac{{{b_latex}}}{{2}}\right)^2 = \left({hb_latex}\right)^2 = {c_latex}$。".replace("{b_latex}", b_latex).replace("{hb_latex}", hb_latex).replace("{c_latex}", c_latex))
        solution_text_parts.append(r"第二個空格應填入 $D = \frac{{{b_latex}}}{{2}} = {hb_latex}$。".replace("{b_latex}", b_latex).replace("{hb_latex}", hb_latex))
        solution_text_parts.append(r"所以，原式可寫為 $x^2 {b_sign}{b_latex_abs}x + {c_latex} = \left(x {hb_sign}{hb_latex_abs}\right)^2$。".replace("{b_sign}", b_sign_for_x_term).replace("{b_latex_abs}", b_latex_abs).replace("{c_latex}", c_latex).replace("{hb_sign}", hb_sign_for_paren).replace("{hb_latex_abs}", hb_latex_abs_paren))
        solution_text = "".join(solution_text_parts)

    elif problem_type == 3:
        # Type 3 (Maps to RAG Ex 3): x^2 + bx + c = 0 (irrational roots)
        # ⑴ x²＋2x-2=0⑵ x²=x＋1 -> ⑴ x=-1±√3, ⑵ x=(1±√5)/2
        
        # Start from (x-h)^2 = k, where k is a positive non-perfect square
        h = random.randint(-5, 5)
        non_perfect_squares = [2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20]
        k = random.choice(non_perfect_squares)

        # Expand to x^2 - 2hx + h^2 - k = 0
        b = -2 * h
        c = h*h - k

        # Format for question_text
        b_str = f"{'+' if b > 0 else ''}{b}x" if b != 0 else ""
        c_str = f"{'+' if c > 0 else ''}{c}" if c != 0 else ""
        if b == 0 and c == 0:
            question_text = r"利用配方法解下列一元二次方程式：$x^2 = 0$"
        else:
            question_text = r"利用配方法解下列一元二次方程式：$x^2 {b_str} {c_str} = 0$".replace("{b_str}", b_str).replace("{c_str}", c_str)

        # Solutions: x = h +/- sqrt(k)
        sol1 = (h, k) # (integer_part, sqrt_value_int)
        sol2 = (h, -k)
        correct_answers_list = sorted([_format_solution_value_for_pure_data(sol1), _format_solution_value_for_pure_data(sol2)])

        # Format for solution_text
        b_half_val = b / 2
        b_half_sq = b_half ** 2
        
        b_half_latex = str(int(b_half_val))
        b_half_sq_latex = str(int(b_half_sq))

        # Simplify sqrt(k) for solution text
        coeff_k, radicand_k = _simplify_sqrt_value(k)
        sqrt_k_latex = ""
        if coeff_k == 1:
            sqrt_k_latex = r"\sqrt{" + str(radicand_k) + r"}"
        else:
            sqrt_k_latex = str(coeff_k) + r"\sqrt{" + str(radicand_k) + r"}"
        
        solution_text_parts.append(r"解：")
        solution_text_parts.append(question_text.replace(" = 0", r" = 0\\"))
        solution_text_parts.append(r"將常數項移到等號右邊：$x^2 {b_str} = {neg_c_str}\\".replace("{b_str}", b_str).replace("{neg_c_str}", str(-c) if -c != 0 else "0"))
        solution_text_parts.append(r"等號兩邊同加 $\left(\frac{{{b}}}{{2}}\right)^2 = \left({b_half_latex}\right)^2 = {b_half_sq_latex}$：".replace("{b}", str(b)).replace("{b_half_latex}", b_half_latex).replace("{b_half_sq_latex}", b_half_sq_latex))
        solution_text_parts.append(r"$x^2 {b_str} {b_half_sq_latex} = {neg_c_str} + {b_half_sq_latex}\\".replace("{b_str}", b_str).replace("{b_half_sq_latex}", b_half_sq_latex).replace("{neg_c_str}", str(-c) if -c != 0 else "0"))
        
        right_side_val = -c + b_half_sq
        right_side_latex = str(int(right_side_val))
        
        solution_text_parts.append(r"整理成完全平方形式：$\left(x {b_half_sign}{b_half_abs_latex}\right)^2 = {right_side_latex}\\".replace("{b_half_sign}", "+" if b_half_val > 0 else "").replace("{b_half_abs_latex}", str(abs(int(b_half_val)))).replace("{right_side_latex}", right_side_latex))
        solution_text_parts.append(r"開平方根：$x {b_half_sign}{b_half_abs_latex} = \pm {sqrt_k_latex}\\".replace("{b_half_sign}", "+" if b_half_val > 0 else "").replace("{b_half_abs_latex}", str(abs(int(b_half_val)))).replace("{sqrt_k_latex}", sqrt_k_latex))
        solution_text_parts.append(r"$x = {-h_val} \pm {sqrt_k_latex}\\".replace("{-h_val}", str(-h)).replace("{sqrt_k_latex}", sqrt_k_latex))
        solution_text_parts.append(r"因此，$x = {-h_val} + {sqrt_k_latex}$ 或 $x = {-h_val} - {sqrt_k_latex}$。".replace("{-h_val}", str(-h)).replace("{sqrt_k_latex}", sqrt_k_latex))
        solution_text = "".join(solution_text_parts)


    elif problem_type == 4:
        # Type 4 (Maps to RAG Ex 4): x^2 - 4x - 396 = 0 (integer roots, potentially large constant)
        # Generate two integer roots
        r1 = random.randint(-15, 15)
        r2 = random.randint(-15, 15)
        while r1 == r2 or r1 == 0 or r2 == 0: # Avoid duplicate or zero roots
            r1 = random.randint(-15, 15)
            r2 = random.randint(-15, 15)

        # To make it more like RAG Ex 4, sometimes make c a larger absolute value
        if random.random() < 0.5:
            # Shift roots to make c larger
            shift = random.randint(5, 10)
            r1 += shift
            r2 += shift
            
        b = -(r1 + r2)
        c = r1 * r2

        # Format for question_text
        b_str = f"{'+' if b > 0 else ''}{b}x" if b != 0 else ""
        c_str = f"{'+' if c > 0 else ''}{c}" if c != 0 else ""
        if b == 0 and c == 0:
            question_text = r"利用配方法解下列一元二次方程式：$x^2 = 0$"
        else:
            question_text = r"利用配方法解下列一元二次方程式：$x^2 {b_str} {c_str} = 0$".replace("{b_str}", b_str).replace("{c_str}", c_str)

        correct_answers_list = sorted([_format_solution_value_for_pure_data(r1), _format_solution_value_for_pure_data(r2)])

        # Format for solution_text
        b_half = b / 2
        b_half_sq = b_half ** 2
        
        b_half_latex = str(int(b_half))
        b_half_sq_latex = str(int(b_half_sq))

        right_side_val = -c + b_half_sq
        right_side_latex = str(int(right_side_val))

        solution_text_parts.append(r"解：")
        solution_text_parts.append(question_text.replace(" = 0", r" = 0\\"))
        solution_text_parts.append(r"將常數項移到等號右邊：$x^2 {b_str} = {neg_c_val}\\".replace("{b_str}", b_str).replace("{neg_c_val}", str(-c) if -c != 0 else "0"))
        solution_text_parts.append(r"等號兩邊同加 $\left(\frac{{{b}}}{{2}}\right)^2 = \left({b_half_latex}\right)^2 = {b_half_sq_latex}$：".replace("{b}", str(b)).replace("{b_half_latex}", b_half_latex).replace("{b_half_sq_latex}", b_half_sq_latex))
        solution_text_parts.append(r"$x^2 {b_str} {b_half_sq_latex} = {neg_c_val} + {b_half_sq_latex}\\".replace("{b_str}", b_str).replace("{b_half_sq_latex}", b_half_sq_latex).replace("{neg_c_val}", str(-c) if -c != 0 else "0"))
        solution_text_parts.append(r"整理成完全平方形式：$\left(x {b_half_sign}{b_half_abs_latex}\right)^2 = {right_side_latex}\\".replace("{b_half_sign}", "+" if b_half > 0 else "").replace("{b_half_abs_latex}", str(abs(int(b_half)))).replace("{right_side_latex}", right_side_latex))
        
        if right_side_val < 0:
            solution_text_parts.append(r"由於等號右邊為負數，因此無實數解。")
            correct_answers_list = ["無實數解"] # Override if no real solution
        else:
            sqrt_right_side = int(math.sqrt(right_side_val))
            solution_text_parts.append(r"開平方根：$x {b_half_sign}{b_half_abs_latex} = \pm \sqrt{{{right_side_latex}}}\\".replace("{b_half_sign}", "+" if b_half > 0 else "").replace("{b_half_abs_latex}", str(abs(int(b_half)))).replace("{right_side_latex}", right_side_latex))
            solution_text_parts.append(r"$x {b_half_sign}{b_half_abs_latex} = \pm {sqrt_right_side}\\".replace("{b_half_sign}", "+" if b_half > 0 else "").replace("{b_half_abs_latex}", str(abs(int(b_half)))).replace("{sqrt_right_side}", str(sqrt_right_side)))
            solution_text_parts.append(r"$x = {-b_half_val} \pm {sqrt_right_side}\\".replace("{-b_half_val}", str(int(-b_half))).replace("{sqrt_right_side}", str(sqrt_right_side)))
            
            sol1_val = int(-b_half + sqrt_right_side)
            sol2_val = int(-b_half - sqrt_right_side)
            solution_text_parts.append(r"因此，$x = {sol1_val}$ 或 $x = {sol2_val}$。".replace("{sol1_val}", str(sol1_val)).replace("{sol2_val}", str(sol2_val)))
        
        solution_text = "".join(solution_text_parts)


    elif problem_type == 5:
        # Type 5 (Maps to RAG Ex 5): ax^2 + bx + c = 0 (a != 1, potentially irrational or no real roots)
        # ⑴ 2x²-8x＋3=0⑵ 3x²＋6x=-3⑶ -2x²＋4x-7=0 -> ⑴ x=2±(√10)/2, ⑵ x=-1 (重根), ⑶ 無解
        
        # Generate roots of the form (A +/- sqrt(B))/C or single rational/integer root, or no real roots.
        
        choice_case = random.choice(['irrational', 'rational', 'no_real'])
        
        if choice_case == 'irrational':
            # Roots of the form (A +/- sqrt(B))/C
            A_part = random.randint(-4, 4)
            B_radicand = random.choice([2, 3, 5, 6, 7, 10]) # Simplified radicand (non-perfect square)
            C_den = random.choice([1, 2, 3]) # Denominator
            
            # Ensure A^2 - B_radicand is not zero
            while A_part**2 == B_radicand:
                B_radicand = random.choice([2, 3, 5, 6, 7, 10])

            a_factor = random.choice([1, 2, 3]) # Multiplier for coefficients to get a != 1
            
            # Equation: x^2 - (2A/C)x + (A^2-B)/C^2 = 0
            # Multiply by a_factor * C^2 to get integer coefficients:
            a = a_factor * C_den**2
            b = -a_factor * 2 * A_part * C_den
            c = a_factor * (A_part**2 - B_radicand)
            
            # Simplify sqrt(B_radicand) for display
            coeff_b, simp_b = _simplify_sqrt_value(B_radicand)
            
            sol_str1 = ""
            sol_str2 = ""
            
            # Format solutions for correct_answer
            # x = (A_part +/- coeff_b * sqrt(simp_b)) / C_den
            
            # Simplify the expression (A_part +/- coeff_b * sqrt(simp_b)) / C_den
            # Check if C_den divides A_part and coeff_b
            if C_den != 1 and A_part % C_den == 0 and coeff_b % C_den == 0:
                A_new = A_part // C_den
                coeff_b_new = coeff_b // C_den
                if coeff_b_new == 1:
                    sol_str1 = f"{A_new}+sqrt({simp_b})"
                    sol_str2 = f"{A_new}-sqrt({simp_b})"
                else:
                    sol_str1 = f"{A_new}+{coeff_b_new}*sqrt({simp_b})"
                    sol_str2 = f"{A_new}-{coeff_b_new}*sqrt({simp_b})"
            else:
                # Use the (A +/- sqrt(B))/C format for check function
                if coeff_b == 1:
                    sol_str1 = f"({A_part}+sqrt({simp_b}))/{C_den}"
                    sol_str2 = f"({A_part}-sqrt({simp_b}))/{C_den}"
                else:
                    sol_str1 = f"({A_part}+{coeff_b}*sqrt({simp_b}))/{C_den}"
                    sol_str2 = f"({A_part}-{coeff_b}*sqrt({simp_b}))/{C_den}"
            
            correct_answers_list = sorted([sol_str1, sol_str2])

        elif choice_case == 'rational':
            # Generate rational roots, including possible repeated roots (重根)
            r1 = random.randint(-4, 4)
            r2 = random.randint(-4, 4)
            if random.random() < 0.3: # 30% chance for repeated roots
                r2 = r1
            
            # Introduce fractions for roots
            if random.random() < 0.4:
                den1 = random.choice([2, 3, 4])
                r1_num = r1 * den1 + random.choice([-1, 1]) * random.randint(1, den1 - 1)
                r1_num, den1 = _simplify_fraction(r1_num, den1)
                r1 = r1_num / den1
            
            if random.random() < 0.4 and r1 != r2:
                den2 = random.choice([2, 3, 4])
                r2_num = r2 * den2 + random.choice([-1, 1]) * random.randint(1, den2 - 1)
                r2_num, den2 = _simplify_fraction(r2_num, den2)
                r2 = r2_num / den2
            
            a_factor = random.choice([2, 3, -2, -3])
            
            # Equation: a_factor * (x-r1)(x-r2) = 0
            # a_factor * (x^2 - (r1+r2)x + r1*r2) = 0
            
            sum_roots = r1 + r2
            prod_roots = r1 * r2
            
            # To get integer coefficients for a, b, c
            # Find common denominator for sum_roots and prod_roots
            sum_num, sum_den = _simplify_fraction(sum_roots, 1)
            prod_num, prod_den = _simplify_fraction(prod_roots, 1)
            
            lcm_den = sum_den * prod_den // _gcd(sum_den, prod_den)
            
            a = a_factor * lcm_den
            b = -a_factor * sum_num * (lcm_den // sum_den)
            c = a_factor * prod_num * (lcm_den // prod_den)
            
            correct_answers_list = sorted([_format_solution_value_for_pure_data(r1), _format_solution_value_for_pure_data(r2)])
            if r1 == r2: correct_answers_list = [_format_solution_value_for_pure_data(r1)] # For repeated roots, only list once

        else: # no_real
            # Ensure no real solution: a(x-h)^2 + k_pos = 0
            a_factor = random.choice([2, 3, -2, -3])
            h_val = random.randint(-4, 4)
            k_pos = random.randint(1, 10) # Positive constant term after moving to right side
            
            # a(x^2 - 2hx + h^2) + k_pos = 0
            # ax^2 - 2ahx + ah^2 + k_pos = 0
            a = a_factor
            b = -2 * a * h_val
            c = a * h_val * h_val + k_pos
            
            correct_answers_list = ["無實數解"]

        # Format question_text
        a_str = f"{a}" if a != 1 else ""
        if a == -1: a_str = "-"
        b_str = f"{'+' if b > 0 else ''}{b}x" if b != 0 else ""
        c_str = f"{'+' if c > 0 else ''}{c}" if c != 0 else ""
        
        question_text_template = r"利用配方法解下列一元二次方程式：${a_str}x^2 {b_str} {c_str} = 0$"
        question_text = question_text_template.replace("{a_str}", a_str).replace("{b_str}", b_str).replace("{c_str}", c_str)
        
        if a == 1: question_text = question_text.replace("1x^2", "x^2")
        if a == -1: question_text = question_text.replace("-1x^2", "-x^2")
        
        # Format solution_text
        solution_text_parts.append(r"解：")
        solution_text_parts.append(question_text.replace(" = 0", r" = 0\\"))
        
        if a != 1:
            solution_text_parts.append(r"將方程式兩邊同除以 ${a}$：".replace("{a}", str(a)))
            
            b_div_a_val = b / a
            c_div_a_val = c / a
            
            b_div_a_latex = ""
            if b_div_a_val.is_integer(): b_div_a_latex = str(int(b_div_a_val))
            else:
                num, den = _simplify_fraction(b_div_a_val, 1)
                b_div_a_latex = r"\frac{" + str(num) + r"}{" + str(den) + r"}"
            
            c_div_a_latex = ""
            if c_div_a_val.is_integer(): c_div_a_latex = str(int(c_div_a_val))
            else:
                num, den = _simplify_fraction(c_div_a_val, 1)
                c_div_a_latex = r"\frac{" + str(num) + r"}{" + str(den) + r"}"
            
            b_div_a_str = f"{'+' if b_div_a_val > 0 else ''}{b_div_a_latex}x" if b_div_a_val != 0 else ""
            c_div_a_str = f"{'+' if c_div_a_val > 0 else ''}{c_div_a_latex}" if c_div_a_val != 0 else ""
            
            solution_text_parts.append(r"$x^2 {b_div_a_str} {c_div_a_str} = 0\\".replace("{b_div_a_str}", b_div_a_str).replace("{c_div_a_str}", c_div_a_str))
            
            b_for_steps = b_div_a_val
            c_for_steps = c_div_a_val
        else:
            b_for_steps = b
            c_for_steps = c
        
        b_for_steps_latex = ""
        if b_for_steps.is_integer(): b_for_steps_latex = str(int(b_for_steps))
        else:
            num, den = _simplify_fraction(b_for_steps, 1)
            b_for_steps_latex = r"\frac{" + str(num) + r"}{" + str(den) + r"}"
        
        c_for_steps_latex = ""
        if c_for_steps.is_integer(): c_for_steps_latex = str(int(c_for_steps))
        else:
            num, den = _simplify_fraction(c_for_steps, 1)
            c_for_steps_latex = r"\frac{" + str(num) + r"}{" + str(den) + r"}"

        solution_text_parts.append(r"將常數項移到等號右邊：$x^2 {b_for_steps_sign}{b_for_steps_latex_abs}x = {neg_c_for_steps_val}\\".replace("{b_for_steps_sign}", "+" if b_for_steps > 0 else "").replace("{b_for_steps_latex_abs}", b_for_steps_latex if b_for_steps > 0 else b_for_steps_latex.replace("-", "")).replace("{neg_c_for_steps_val}", f"-{c_for_steps_latex}" if c_for_steps > 0 else f"+{c_for_steps_latex.replace('-', '')}" if c_for_steps < 0 else "0"))

        # Calculate (b/2)^2
        b_half = b_for_steps / 2
        b_half_sq = b_half ** 2
        
        b_half_latex = ""
        if b_half.is_integer(): b_half_latex = str(int(b_half))
        else:
            num, den = _simplify_fraction(b_half, 1)
            b_half_latex = r"\frac{" + str(num) + r"}{" + str(den) + r"}"
        
        b_half_sq_latex = ""
        if b_half_sq.is_integer(): b_half_sq_latex = str(int(b_half_sq))
        else:
            num, den = _simplify_fraction(b_half_sq, 1)
            b_half_sq_latex = r"\frac{" + str(num) + r"}{" + str(den) + r"}"
        
        solution_text_parts.append(r"等號兩邊同加 $\left(\frac{{{b_for_steps_latex}}}{{2}}\right)^2 = \left({b_half_latex}\right)^2 = {b_half_sq_latex}$：".replace("{b_for_steps_latex}", b_for_steps_latex).replace("{b_half_latex}", b_half_latex).replace("{b_half_sq_latex}", b_half_sq_latex))
        solution_text_parts.append(r"$x^2 {b_for_steps_sign}{b_for_steps_latex_abs}x + {b_half_sq_latex} = {neg_c_for_steps_val} + {b_half_sq_latex}\\".replace("{b_for_steps_sign}", "+" if b_for_steps > 0 else "").replace("{b_for_steps_latex_abs}", b_for_steps_latex if b_for_steps > 0 else b_for_steps_latex.replace("-", "")).replace("{b_half_sq_latex}", b_half_sq_latex).replace("{neg_c_for_steps_val}", f"-{c_for_steps_latex}" if c_for_steps > 0 else f"+{c_for_steps_latex.replace('-', '')}" if c_for_steps < 0 else "0"))
        
        right_side_val = -c_for_steps + b_half_sq
        right_side_latex = ""
        if right_side_val.is_integer(): right_side_latex = str(int(right_side_val))
        else:
            num, den = _simplify_fraction(right_side_val, 1)
            right_side_latex = r"\frac{" + str(num) + r"}{" + str(den) + r"}"
        
        solution_text_parts.append(r"整理成完全平方形式：$\left(x {b_half_sign}{b_half_abs_latex}\right)^2 = {right_side_latex}\\".replace("{b_half_sign}", "+" if b_half > 0 else "").replace("{b_half_abs_latex}", b_half_latex if b_half > 0 else b_half_latex.replace("-", "")).replace("{right_side_latex}", right_side_latex))
        
        if right_side_val < 0:
            solution_text_parts.append(r"由於等號右邊為負數，因此無實數解。")
        else:
            # Simplify sqrt(right_side_val)
            sqrt_val_num, sqrt_val_den = _simplify_fraction(right_side_val, 1)
            
            coeff_s, radicand_s = _simplify_sqrt_value(sqrt_val_num * sqrt_val_den)
            sqrt_den_final = sqrt_val_den
            
            sqrt_right_side_latex = ""
            if radicand_s == 1: # Perfect square
                sqrt_right_side_latex = str(coeff_s)
                if sqrt_den_final != 1:
                    num, den = _simplify_fraction(coeff_s, sqrt_den_final)
                    if den == 1: sqrt_right_side_latex = str(num)
                    else: sqrt_right_side_latex = r"\frac{" + str(num) + r"}{" + str(den) + r"}"
            else:
                if coeff_s == 1:
                    sqrt_part_latex = r"\sqrt{" + str(radicand_s) + r"}"
                else:
                    sqrt_part_latex = str(coeff_s) + r"\sqrt{" + str(radicand_s) + r"}"
                
                if sqrt_den_final == 1:
                    sqrt_right_side_latex = sqrt_part_latex
                else:
                    sqrt_right_side_latex = r"\frac{" + sqrt_part_latex + r"}{" + str(sqrt_den_final) + r"}"

            solution_text_parts.append(r"開平方根：$x {b_half_sign}{b_half_abs_latex} = \pm {sqrt_right_side_latex}\\".replace("{b_half_sign}", "+" if b_half > 0 else "").replace("{b_half_abs_latex}", b_half_latex if b_half > 0 else b_half_latex.replace("-", "")).replace("{sqrt_right_side_latex}", sqrt_right_side_latex))
            solution_text_parts.append(r"$x = {-b_half_val} \pm {sqrt_right_side_latex}\\".replace("{-b_half_val}", f"{'-' if b_half > 0 else '+'}{b_half_latex}").replace("{sqrt_right_side_latex}", sqrt_right_side_latex))
            
            if correct_answers_list[0] == "無實數解": # This path should not be taken if it's no_real
                pass
            elif len(correct_answers_list) == 1: # Repeated roots
                 solution_text_parts.append(r"因此，$x = {sol_text}$ (重根)。".replace("{sol_text}", correct_answers_list[0]))
            else: # Distinct roots (rational or irrational)
                solution_text_parts.append(r"因此，$x = {-b_half_val} + {sqrt_right_side_latex}$ 或 $x = {-b_half_val} - {sqrt_right_side_latex}$。".replace("{-b_half_val}", f"{'-' if b_half > 0 else '+'}{b_half_latex}").replace("{sqrt_right_side_latex}", sqrt_right_side_latex))
        
        solution_text = "".join(solution_text_parts)


    # Final correct_answer formatting
    if correct_answers_list and correct_answers_list[0] != "無實數解":
        final_correct_answer = ", ".join(correct_answers_list)
    else:
        final_correct_answer = "無實數解" if correct_answers_list else "" # default to empty string if no solutions were added

    return {
        "question_text": question_text,
        "correct_answer": final_correct_answer,
        "answer": final_correct_answer, # Mirror correct_answer
        "solution_text": solution_text,
        "image_base64": None,
        "created_at": current_time,
        "version": "1.0"
    }

# --- Check Function (Coder MUST implement) ---


    # 1. Input Sanitization (CRITICAL RULE: Robust Check Logic)
    # 移除 LaTeX 符號、變數前綴、所有空白字元
    # Updated regex to handle parentheses for complex fractions/sqrt terms like (A+sqrt(B))/C
    sanitized_user_answer = re.sub(r'[\\$}{x=y=k=Ans:\s]', '', user_answer).strip()

    # 2. Handle "無實數解" case
    if correct_answer == "無實數解":
        return sanitized_user_answer.lower() in ["無實數解", "no實數解", "no real solution", "norealsolution"]

    # Helper function to parse a single solution string into a comparable numerical value
    # Enhanced to handle (A +/- B*sqrt(C))/D and A +/- B*sqrt(C) and B*sqrt(C)/D
    def parse_single_solution(s):
        s = s.strip()
        
        # Handle simple fractions like "1/2" (must not be part of sqrt/division like "sqrt(10)/2")
        if '/' in s and not ('sqrt' in s and '/' in s.split('sqrt(')[-1]):
            try:
                num, den = map(float, s.split('/'))
                if den == 0: return float('nan')
                return num / den
            except ValueError:
                pass # Try next pattern

        # Handle expressions like (A +/- B*sqrt(C))/D or (A +/- sqrt(C))/D
        # e.g., (2+sqrt(3))/2, (1-2*sqrt(5))/3
        match_complex_surd_div = re.match(r'^\((-?\d+(\.\d+)?)([+-])((\d*\*)?sqrt\((\d+)\))\)/(-?\d+(\.\d+)?)$', s)
        if match_complex_surd_div:
            A_str, _, op, surd_part_str, B_coeff_str, C_val_str, D_str, _ = match_complex_surd_div.groups()
            A = float(A_str)
            D = float(D_str)
            if D == 0: return float('nan')

            B_coeff = float(B_coeff_str.strip('*')) if B_coeff_str else 1.0
            C_val = int(C_val_str)
            if C_val < 0: return float('nan')
            
            surd_val = B_coeff * math.sqrt(C_val)
            if op == '-':
                surd_val = -surd_val
            
            return (A + surd_val) / D

        # Handle expressions like A +/- B*sqrt(C) or A +/- sqrt(C) or B*sqrt(C) or sqrt(C)
        # e.g., 2+sqrt(3), -sqrt(5), 1+2*sqrt(3)
        # This regex is designed to capture:
        # 1. An optional initial number (integer or float, possibly negative)
        # 2. An optional operator (+ or -)
        # 3. An optional coefficient for sqrt (e.g., "2*")
        # 4. "sqrt(" followed by an integer and ")"
        match_surd_general = re.match(r'^(-?\d+(\.\d+)?|)([+-]?)((\d*\*)?sqrt\((\d+)\))$', s)
        if match_surd_general:
            int_part_str, _, op, _, B_coeff_str, C_val_str = match_surd_general.groups()
            
            int_part = float(int_part_str) if int_part_str else 0.0
            
            B_coeff = float(B_coeff_str.strip('*')) if B_coeff_str else 1.0
            C_val = int(C_val_str)
            if C_val < 0: return float('nan')
            
            val = B_coeff * math.sqrt(C_val)
            if op == '-':
                val = -val
            elif op == '': # Case like "sqrt(X)" or "2*sqrt(X)"
                if int_part_str: return float('nan') # Malformed, e.g., "2sqrt(3)" without an operator
                return val
            
            return int_part + val
        
        # Handle cases like "sqrt(X)/Y" or "B*sqrt(C)/D"
        # e.g., sqrt(10)/2, 2*sqrt(3)/5
        match_pure_surd_div = re.match(r'^((\d*\*)?sqrt\((\d+)\))/(-?\d+(\.\d+)?)$', s)
        if match_pure_surd_div:
            _, B_coeff_str, C_val_str, D_str, _ = match_pure_surd_div.groups()
            D = float(D_str)
            if D == 0: return float('nan')

            B_coeff = float(B_coeff_str.strip('*')) if B_coeff_str else 1.0
            C_val = int(C_val_str)
            if C_val < 0: return float('nan')
            
            return (B_coeff * math.sqrt(C_val)) / D

        # Handle simple integers or floats
        try:
            return float(s)
        except ValueError:
            return float('nan') # Parsing failed for this part

    # Helper function to parse a comma-separated string of solutions
    # Handles commas outside of parentheses.
    def parse_solutions_list(s_list_str):
        if not s_list_str:
            return []
        
        parts = []
        balance = 0
        current_part_chars = []
        for char in s_list_str:
            if char == '(':
                balance += 1
            elif char == ')':
                balance -= 1
            
            if char == ',' and balance == 0:
                parts.append("".join(current_part_chars).strip())
                current_part_chars = []
            else:
                current_part_chars.append(char)
        parts.append("".join(current_part_chars).strip()) # Add the last part

        solutions = [parse_single_solution(p) for p in parts]
        # Filter out NaN values if any parsing failed, or return None to indicate overall failure
        if any(math.isnan(sol) for sol in solutions):
            return None # Indicate a parsing error
        return solutions

    # Parse both correct and user answers
    correct_solutions_parsed = parse_solutions_list(correct_answer)
    user_solutions_parsed = parse_solutions_list(sanitized_user_answer)

    if correct_solutions_parsed is None or user_solutions_parsed is None:
        return False # Parsing error in either answer

    # CRITICAL RULE: Numerical sequence comparison (adapted for order invariance)
    # Check if lengths are equal
    if len(correct_solutions_parsed) != len(user_solutions_parsed):
        return False

    # For quadratic equations, roots order does not matter. Compare as sets using tolerance.
    tolerance = 1e-9

    # Sort both lists of floats for comparison
    correct_solutions_sorted = sorted(correct_solutions_parsed)
    user_solutions_sorted = sorted(user_solutions_parsed)

    for i in range(len(correct_solutions_sorted)):
        if abs(correct_solutions_sorted[i] - user_solutions_sorted[i]) > tolerance:
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
