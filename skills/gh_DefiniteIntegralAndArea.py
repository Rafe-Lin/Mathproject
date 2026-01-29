# ==============================================================================
# ID: gh_DefiniteIntegralAndArea
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 243.41s | RAG: 5 examples
# Created At: 2026-01-29 19:26:09
# Fix Status: [Repaired]
# Fixes: Regex=5, Logic=0
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
import base64
import matplotlib.pyplot as plt
import numpy as np
import re
from io import BytesIO

# --- Helper Functions (由 Code Generator 實作) ---
# 這些輔助函數的簽名和邏輯已由 Code Generator 實作並提供，嚴禁修改其簽名。
# 它們主要用於處理二次多項式 (ax^2 + bx + c)。
# 對於三次多項式，將在 generate 函數內部進行 LaTeX 字串的手動建構，以避免創建新的全局函數模型。

def _format_polynomial_latex(a_val, b_val, c_val, var='x'):
    """
    Helper function to format a polynomial string (ax^2 + bx + c) into LaTeX.
    Ensures correct signs and handles coefficients of 1 or -1, and zero terms.
    """
    parts = []
    # x^2 term
    if a_val != 0:
        if a_val == 1:
            parts.append(f"{var}^2")
        elif a_val == -1:
            parts.append(f"-{var}^2")
        else:
            parts.append(f"{a_val}{var}^2")
    
    # x term
    if b_val != 0:
        term_val = abs(b_val)
        term_str = f"{term_val}{var}"
        if b_val > 0:
            parts.append(f"+{term_str}") if parts else parts.append(term_str)
        else: # b_val < 0
            parts.append(f"-{term_str}") if parts else parts.append(f"-{term_str}")
    
    # Constant term
    if c_val != 0:
        term_val = abs(c_val)
        term_str = f"{term_val}"
        if c_val > 0:
            parts.append(f"+{term_str}") if parts else parts.append(term_str)
        else: # c_val < 0
            parts.append(f"-{term_str}") if parts else parts.append(f"-{term_str}")
    
    if not parts:
        return "0"
    return "".join(parts)

def _format_integral_term_latex(a_val, b_val, c_val, var='x'):
    """
    Helper function to format the indefinite integral of a polynomial
    (A/3)x^3 + (B/2)x^2 + Cx into LaTeX.
    Ensures correct signs and handles fractional coefficients.
    """
    integral_parts = []
    
    # x^3 term
    if a_val != 0:
        if a_val % 3 == 0:
            coeff_str = str(a_val // 3)
        else:
            coeff_str = r"\frac{" + str(a_val) + "}{3}"
        integral_parts.append(f"{coeff_str}{var}^3")
    
    # x^2 term
    if b_val != 0:
        coeff_str = ""
        if abs(b_val) % 2 == 0:
            coeff_str = str(abs(b_val) // 2)
        else:
            coeff_str = r"\frac{" + str(abs(b_val)) + "}{2}"
        
        term_str = f"{coeff_str}{var}^2"
        if b_val > 0:
            integral_parts.append(f"+{term_str}") if integral_parts else integral_parts.append(term_str)
        else:
            integral_parts.append(f"-{term_str}") if integral_parts else integral_parts.append(f"-{term_str}")

    # x term
    if c_val != 0:
        term_str = f"{abs(c_val)}{var}"
        if c_val > 0:
            integral_parts.append(f"+{term_str}") if integral_parts else integral_parts.append(term_str)
        else:
            integral_parts.append(f"-{term_str}") if integral_parts else integral_parts.append(f"-{term_str}")
    
    if not integral_parts:
        return "0"
    return "".join(integral_parts)

# --- Core Functions ---

def generate(level=1):
    """
    Generates a definite integral and area problem, strictly mirroring RAG examples.
    The problem_type choices directly map to the RAG examples' mathematical models.
    """
    # 根據最高權限指令，問題類型直接映射 RAG 範例的數學模型。
    # RAG Ex 1, 2, 3, 4 共享「函數與 x 軸圍成面積」的核心數學模型，但問題表述和特定參數不同。
    # RAG Ex 5 是「相等面積求未知參數」的獨立數學模型。
    problem_type = random.choice([
        'RAG_Ex1_Area_f_x_axis_with_limits', 
        'RAG_Ex2_Area_f_x_axis_with_limits', 
        'RAG_Ex3_Area_f_x_axis_from_origin', 
        'RAG_Ex4_Area_f_x_axis_by_roots', 
        'RAG_Ex5_Equal_Areas_Find_a_value'
    ])

    question_text = ""
    correct_answer = ""
    solution_text = ""
    image_base64 = ""
    
    # Common plotting range (will be adjusted dynamically)
    x_min_plot_default, x_max_plot_default = -5, 5
    y_min_plot_default, y_max_plot_default = -5, 5

    # Function to find real roots of a quadratic equation
    def find_quadratic_roots(a, b, c):
        if a == 0: # Linear case: bx + c = 0
            return [-c/b] if b != 0 else ([] if c != 0 else [0]) # Return [0] if 0=0 (constant 0 function)
        delta = b**2 - 4*a*c
        if delta < 0: return []
        elif delta == 0: return [-b / (2*a)]
        else: return sorted([(-b - math.sqrt(delta)) / (2*a), (-b + math.sqrt(delta)) / (2*a)])

    # Function to calculate definite integral of a polynomial (up to cubic)
    # F(x) = (a3/4)x^4 + (a2/3)x^3 + (a1/2)x^2 + a0*x
    def indefinite_integral_val(x_val, a3, a2, a1, a0):
        return (a3/4) * (x_val**4) + (a2/3) * (x_val**3) + (a1/2) * (x_val**2) + a0 * x_val
    
    # Inline function to format cubic polynomial to LaTeX string
    def _format_cubic_latex_inline(a3, a2, a1, a0, var='x'):
        parts = []
        if a3 != 0:
            if a3 == 1: parts.append(f"{var}^3")
            elif a3 == -1: parts.append(f"-{var}^3")
            else: parts.append(f"{a3}{var}^3")
        
        if a2 != 0:
            term_val = abs(a2)
            term_str = f"{term_val}{var}^2"
            if a2 > 0: parts.append(f"+{term_str}") if parts else parts.append(term_str)
            else: parts.append(f"-{term_str}")
        
        if a1 != 0:
            term_val = abs(a1)
            term_str = f"{term_val}{var}"
            if a1 > 0: parts.append(f"+{term_str}") if parts else parts.append(term_str)
            else: parts.append(f"-{term_str}")
        
        if a0 != 0:
            term_val = abs(a0)
            term_str = f"{term_val}"
            if a0 > 0: parts.append(f"+{term_str}") if parts else parts.append(term_str)
            else: parts.append(f"-{term_str}")
        
        if not parts: return "0"
        return "".join(parts)

    # Inline function to format indefinite integral of cubic polynomial to LaTeX string
    def _format_integral_cubic_latex_inline(a3, a2, a1, a0, var='x'):
        integral_parts = []
        
        # x^4 term
        if a3 != 0:
            if a3 % 4 == 0: coeff_str = str(a3 // 4)
            else: coeff_str = r"\frac{" + str(a3) + "}{4}"
            integral_parts.append(f"{coeff_str}{var}^4")
        
        # x^3 term
        if a2 != 0:
            coeff_str = ""
            if abs(a2) % 3 == 0: coeff_str = str(abs(a2) // 3)
            else: coeff_str = r"\frac{" + str(abs(a2)) + "}{3}"
            term_str = f"{coeff_str}{var}^3"
            if a2 > 0: integral_parts.append(f"+{term_str}") if integral_parts else integral_parts.append(term_str)
            else: integral_parts.append(f"-{term_str}")

        # x^2 term
        if a1 != 0:
            coeff_str = ""
            if abs(a1) % 2 == 0: coeff_str = str(abs(a1) // 2)
            else: coeff_str = r"\frac{" + str(abs(a1)) + "}{2}"
            term_str = f"{coeff_str}{var}^2"
            if a1 > 0: integral_parts.append(f"+{term_str}") if integral_parts else integral_parts.append(term_str)
            else: integral_parts.append(f"-{term_str}")
        
        # x term
        if a0 != 0:
            term_str = f"{abs(a0)}{var}"
            if a0 > 0: integral_parts.append(f"+{term_str}") if integral_parts else integral_parts.append(term_str)
            else: integral_parts.append(f"-{term_str}")
        
        if not integral_parts: return "0"
        return "".join(integral_parts)

    # RAG Ex 1, 2, 3, 4 all share the core mathematical model:
    # Calculate the total positive area between f(x) and the x-axis within given (or implied) limits.
    # This involves finding roots, splitting intervals, and summing absolute values of sub-integrals.
    if problem_type in ['RAG_Ex1_Area_f_x_axis_with_limits', 'RAG_Ex2_Area_f_x_axis_with_limits', 
                        'RAG_Ex3_Area_f_x_axis_from_origin', 'RAG_Ex4_Area_f_x_axis_by_roots']:
        
        is_cubic = False
        a3, a2, a1, a0 = 0, 0, 0, 0
        current_roots = [] # Real roots of the function f(x)

        if problem_type == 'RAG_Ex4_Area_f_x_axis_by_roots': # RAG Ex 4 is always cubic and factored
            is_cubic = True
            # Generate cubic function in the form x(ax^2+bx+c) to ensure x=0 is a root and other roots are easily found.
            r_quad1 = random.choice([-2, -1, 1, 2])
            r_quad2 = random.choice([-3, -1, 1, 3])
            while r_quad1 == r_quad2: r_quad2 = random.choice([-3, -1, 1, 3]) # Ensure distinct
            
            a_quad = random.choice([-1, 1]) # Leading coeff for quadratic factor
            b_quad = -a_quad * (r_quad1 + r_quad2)
            c_quad = a_quad * r_quad1 * r_quad2
            
            a3 = a_quad
            a2 = b_quad
            a1 = c_quad
            a0 = 0 # Ensures x=0 is a root
            
            current_roots = sorted(list(set([0] + find_quadratic_roots(a_quad, b_quad, c_quad))))
            # Filter roots to be within a reasonable range for plotting
            current_roots = [r for r in current_roots if -6 <= r <= 6]
            if len(current_roots) < 2: # Ensure at least two distinct roots for area bounding
                current_roots = sorted(list(set([0, random.choice([-3, 3])])))
                if a3 == 0: a3 = 1 # Ensure it's cubic
                a2, a1, a0 = 0, 0, 0 # Simplify to x^3
                if current_roots[1] != 0: a0 = -a3 * (current_roots[1]**3) # Ensure current_roots[1] is a root of x^3+a0/a3=0

        else: # RAG Ex 1, 2, 3 can be quadratic or cubic (simple cubic)
            if random.random() < 0.6: # More likely to be quadratic
                a2 = random.choice([-2, -1, 1, 2])
                a1 = random.randint(-4, 4)
                a0 = random.randint(-8, 8)
                current_roots = find_quadratic_roots(a2, a1, a0)
            else: # Simple cubic x^3 - k or x^3 + k
                is_cubic = True
                a3 = random.choice([-1, 1])
                a0 = random.choice([-8, -1, 1, 8])
                a2, a1 = 0, 0
                
                if -a0 / a3 > 0: current_roots.append(round(pow(-a0 / a3, 1/3), 4))
                elif -a0 / a3 < 0: current_roots.append(round(-pow(abs(-a0 / a3), 1/3), 4))
                else: current_roots.append(0)
            
            # Filter roots to be within a reasonable range
            current_roots = [r for r in current_roots if -6 <= r <= 6]

        # Define the function for calculation and plotting
        def f(x):
            return a3 * x**3 + a2 * x**2 + a1 * x + a0

        # Determine integration limits based on problem type
        x1_limit, x2_limit = -5, 5 # Default wide range
        if problem_type == 'RAG_Ex1_Area_f_x_axis_with_limits': # Ex 1 specific limits
            x1_limit = random.choice([-5, -4, -3])
            x2_limit = random.choice([3, 4, 5])
        elif problem_type == 'RAG_Ex2_Area_f_x_axis_with_limits': # Ex 2 specific limits
            x1_limit = random.choice([-2, -1])
            x2_limit = random.choice([1, 2])
        elif problem_type == 'RAG_Ex3_Area_f_x_axis_from_origin': # Ex 3 specific limits (0 to a root or a small positive value)
            # Find a positive root or set a small positive upper bound
            positive_roots_in_range = [r for r in current_roots if r > 0.1 and r <= 5]
            x1_limit = 0
            x2_limit = random.choice(positive_roots_in_range or [random.randint(1, 4)])
            if x1_limit >= x2_limit: x2_limit = x1_limit + random.randint(1, 3) # Ensure x1 < x2
        elif problem_type == 'RAG_Ex4_Area_f_x_axis_by_roots': # Ex 4: bounded by x-axis, limits are min/max roots
            if not current_roots or len(current_roots) < 2:
                # Fallback to a default range if roots are not sufficient
                x1_limit = random.choice([-2, -1])
                x2_limit = random.choice([1, 2])
            else:
                x1_limit = min(current_roots)
                x2_limit = max(current_roots)
                
        # Ensure x1_limit and x2_limit are distinct and ordered
        if x1_limit >= x2_limit:
            x1_limit, x2_limit = x2_limit, x1_limit
            if x1_limit == x2_limit: x2_limit += random.choice([1, 2]) # Ensure distinct limits

        # Collect all relevant x-values for splitting intervals: given limits and roots within limits
        integration_points_raw = [x1_limit, x2_limit] + [r for r in current_roots if x1_limit <= r <= x2_limit]
        integration_points = sorted(list(set([round(p, 6) for p in integration_points_raw]))) # Round to avoid float precision issues with exact roots
        
        total_area = 0
        detailed_integrals = []
        
        for i in range(len(integration_points) - 1):
            lower_bound = integration_points[i]
            upper_bound = integration_points[i+1]
            
            if abs(upper_bound - lower_bound) < 1e-6: continue # Skip very small intervals

            integral_val = indefinite_integral_val(upper_bound, a3, a2, a1, a0) - indefinite_integral_val(lower_bound, a3, a2, a1, a0)
            total_area += abs(integral_val)
            
            # For solution text
            func_str_for_integral = _format_cubic_latex_inline(a3, a2, a1, a0, 'x') if is_cubic else _format_polynomial_latex(a2, a1, a0, 'x')
            detailed_integrals.append(f"\\left| \\int_{{{round(lower_bound, 2)}}}^{{{round(upper_bound, 2)}}} ({func_str_for_integral}) dx \\right|")
        
        correct_answer = str(round(total_area, 4))

        # Generate question text
        func_str = _format_cubic_latex_inline(a3, a2, a1, a0, 'x') if is_cubic else _format_polynomial_latex(a2, a1, a0, 'x')
        
        if problem_type == 'RAG_Ex4_Area_f_x_axis_by_roots':
             question_text = r"求函數 $f(x) = {func_str}$ 的圖形與 $x$ 軸所圍成的區域面積。".replace("{func_str}", func_str)
        else:
            question_text = r"求函數 $f(x) = {func_str}$ 的圖形與 $x$ 軸、 $x={x1_round}$ 及 $x={x2_round}$ 所圍成區域的面積。".replace("{func_str}", func_str) \
                             .replace("{x1_round}", str(round(x1_limit, 2))).replace("{x2_round}", str(round(x2_limit, 2)))

        # Generate solution text
        integral_func_str = _format_integral_cubic_latex_inline(a3, a2, a1, a0, 'x') if is_cubic else _format_integral_term_latex(a2, a1, a0, 'x')
        
        solution_template = r"首先找出函數 $f(x) = {func_str}$ 的根，並結合給定區間 $[{x1_round}, {x2_round}]$ 的上下限，將積分區間劃分為子區間。\n" \
                            r"$\int ({func_str}) dx = {integral_func_str} + C$\n" \
                            r"計算各子區間的定積分絕對值並加總：\n" \
                            r"Area $= " + " + ".join(detailed_integrals) + r"$\n" \
                            r"$= {final_area}$"
        solution_text = solution_template.replace("{func_str}", func_str) \
                                 .replace("{x1_round}", str(round(x1_limit, 2))).replace("{x2_round}", str(round(x2_limit, 2))) \
                                 .replace("{integral_func_str}", integral_func_str) \
                                 .replace("{final_area}", str(round(total_area, 4)))
        
        # Plotting
        x_min_plot = min(x1_limit, x2_limit, x_min_plot_default) - 1
        x_max_plot = max(x1_limit, x2_limit, x_max_plot_default) + 1
        
        x_plot = np.linspace(x_min_plot, x_max_plot, 400)
        y_plot = f(x_plot)
        
        y_min_val_func = np.min(y_plot)
        y_max_val_func = np.max(y_plot)
        y_min_plot = min(y_min_val_func, 0, y_min_plot_default) - 1
        y_max_plot = max(y_max_val_func, 0, y_max_plot_default) + 1
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        ax.plot(x_plot, y_plot, label=f"$f(x) = {func_str}$")
        
        # Shade the area
        x_shade = np.linspace(x1_limit, x2_limit, 400)
        y_shade = f(x_shade)
        ax.fill_between(x_shade, y_shade, where=(y_shade > 0), color='skyblue', alpha=0.4, interpolate=True)
        ax.fill_between(x_shade, y_shade, where=(y_shade < 0), color='salmon', alpha=0.4, interpolate=True)
        
        ax.axhline(0, color='black', linewidth=0.8)
        ax.axvline(0, color='black', linewidth=0.8)
        ax.plot(x_max_plot, 0, ">k", clip_on=False, transform=ax.get_yaxis_transform())
        ax.plot(0, y_max_plot, "^k", clip_on=False, transform=ax.get_xaxis_transform())

        ax.set_xlabel('$x$', fontsize=12)
        ax.set_ylabel('$y$', fontsize=12)
        ax.set_title(r"函數 $f(x)$ 與 $x$ 軸所圍成的面積")
        ax.grid(True, linestyle='--', alpha=0.6)
        
        ax.set_xticks(np.arange(math.floor(x_min_plot), math.ceil(x_max_plot) + 1, 1))
        ax.set_yticks(np.arange(math.floor(y_min_plot), math.ceil(y_max_plot) + 1, 1))
        
        ax.set_xlim(x_min_plot, x_max_plot)
        ax.set_ylim(y_min_plot, y_max_plot)
        ax.set_aspect('equal')
        
        ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.7))
        ax.legend()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    elif problem_type == 'RAG_Ex5_Equal_Areas_Find_a_value':
        # RAG Ex 5: Equal areas problem. Find 'a' such that A1 = A2.
        # Model: Integral from starting point to 'a' of f(x) dx = 0.
        # Function: f(x) = a2*x^2 + a1*x (ensures x=0 is a root)
        
        # Generate coefficients to ensure integer 'a' and distinct roots
        while True:
            a2_coeff = random.choice([-1, 1])
            a1_coeff = random.choice([-8, -6, -4, -2, 2, 4, 6, 8]) # Must be even for integer 'a'
            a0_coeff = 0 # Ensures x=0 is a root
            
            # Roots of f(x) = a2_coeff*x^2 + a1_coeff*x = x(a2_coeff*x + a1_coeff) are 0 and -a1_coeff/a2_coeff
            x_root_val = -a1_coeff / a2_coeff
            
            # 'a' value such that integral from 0 to 'a' is 0:
            # (a2_coeff/3)a^3 + (a1_coeff/2)a^2 = 0
            # a^2 * ((a2_coeff/3)a + (a1_coeff/2)) = 0
            # a = -3 * a1_coeff / (2 * a2_coeff)
            a_val_calc = -3 * a1_coeff / (2 * a2_coeff)
            
            # Ensure a_val_calc is distinct from 0 and x_root_val, and reasonable range
            if abs(a_val_calc) > 1 and abs(x_root_val) > 1 and \
               abs(a_val_calc - x_root_val) > 1 and \
               -12 <= a_val_calc <= 12 and -12 <= x_root_val <= 12:
                break # Found suitable coefficients
        
        correct_answer = str(round(a_val_calc, 4))
        
        func_str = _format_polynomial_latex(a2_coeff, a1_coeff, a0_coeff, 'x')
        question_text = r"函數 $f(x) = {func_str}$ 的圖形與 $x$ 軸圍成兩個區域 $A_1$ 與 $A_2$。其中 $A_1$ 是由 $x=0$ 到 $x={x_root_round}$ 所圍成，而 $A_2$ 是由 $x={x_root_round}$ 到 $x=a$ 所圍成。已知 $A_1$ 的面積與 $A_2$ 的面積相等，求 $a$ 的值。".replace("{func_str}", func_str) \
                        .replace("{x_root_round}", str(round(x_root_val, 2)))

        integral_func_str = _format_integral_term_latex(a2_coeff, a1_coeff, a0_coeff, 'x')
        
        # Format coefficients for solution text fractions
        a2_div_3 = f"\\frac{{a2_coeff}}{3}" if a2_coeff % 3 != 0 else str(a2_coeff // 3)
        a1_div_2 = f"\\frac{{a1_coeff}}{2}" if a1_coeff % 2 != 0 else str(a1_coeff // 2)

        solution_template = r"函數 $f(x) = {func_str}$ 的根為 $x=0$ 與 $x={x_root_round}$。\n" \
                            r"區域 $A_1$ 的面積為 $\left| \int_{0}^{{x_root_round}} ({func_str}) dx \right|$。\n" \
                            r"區域 $A_2$ 的面積為 $\left| \int_{{x_root_round}}^{a} ({func_str}) dx \right|$。\n" \
                            r"已知 $A_1 = A_2$，這表示從 $0$ 到 $a$ 的定積分為零： $\int_{0}^{a} ({func_str}) dx = 0$。\n" \
                            r"$\int_{0}^{a} ({func_str}) dx = \left[ {integral_func_str} \right]_{0}^{a} = \left( {a2_div_3}a^3 + {a1_div_2}a^2 \right) - (0) = 0$\n" \
                            r"即 ${a2_div_3}a^3 + {a1_div_2}a^2 = 0$\n" \
                            r"$a^2 \left( {a2_div_3}a + {a1_div_2} \right) = 0$\n" \
                            r"解得 $a=0$ 或 $a = {final_a_val}$。\n" \
                            r"根據題意，$a$ 應為非零值且與 $x={x_root_round}$ 不同，因此 $a = {final_a_val}$。"
        
        solution_text = solution_template.replace("{func_str}", func_str) \
                                 .replace("{x_root_round}", str(round(x_root_val, 2))) \
                                 .replace("{integral_func_str}", integral_func_str) \
                                 .replace("{a2_div_3}", a2_div_3) \
                                 .replace("{a1_div_2}", a1_div_2) \
                                 .replace("{final_a_val}", str(round(a_val_calc, 4)))
        
        # Plotting
        def f_plot(x): # Redefine f for plotting scope
            return a2_coeff * x**2 + a1_coeff * x + a0_coeff

        x_min_plot = min(0, x_root_val, a_val_calc, x_min_plot_default) - 1
        x_max_plot = max(0, x_root_val, a_val_calc, x_max_plot_default) + 1
        
        x_plot = np.linspace(x_min_plot, x_max_plot, 400)
        y_plot = f_plot(x_plot)
        
        y_min_val_func = np.min(y_plot)
        y_max_val_func = np.max(y_plot)
        y_min_plot = min(y_min_val_func, 0, y_min_plot_default) - 1
        y_max_plot = max(y_max_val_func, 0, y_max_plot_default) + 1
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        ax.plot(x_plot, y_plot, label=f"$f(x) = {func_str}$")
        
        # Shade A1 (from 0 to x_root_val)
        x_shade_a1 = np.linspace(0, x_root_val, 400)
        y_shade_a1 = f_plot(x_shade_a1)
        ax.fill_between(x_shade_a1, y_shade_a1, where=(y_shade_a1 > 0), color='skyblue', alpha=0.4, interpolate=True, label='$A_1$')
        ax.fill_between(x_shade_a1, y_shade_a1, where=(y_shade_a1 < 0), color='salmon', alpha=0.4, interpolate=True)
        
        # Shade A2 (from x_root_val to a_val_calc)
        x_shade_a2 = np.linspace(x_root_val, a_val_calc, 400)
        y_shade_a2 = f_plot(x_shade_a2)
        ax.fill_between(x_shade_a2, y_shade_a2, where=(y_shade_a2 > 0), color='lightgreen', alpha=0.4, interpolate=True, label='$A_2$')
        ax.fill_between(x_shade_a2, y_shade_a2, where=(y_shade_a2 < 0), color='purple', alpha=0.4, interpolate=True)
        
        # Mark roots and 'a'
        ax.axvline(0, color='gray', linestyle=':', linewidth=1)
        ax.axvline(x_root_val, color='gray', linestyle=':', linewidth=1)
        ax.axvline(a_val_calc, color='red', linestyle='--', linewidth=1, label=f"$x=a \\approx {{round(a_val_calc,2)}}$")

        ax.axhline(0, color='black', linewidth=0.8)
        ax.axvline(0, color='black', linewidth=0.8)
        ax.plot(x_max_plot, 0, ">k", clip_on=False, transform=ax.get_yaxis_transform())
        ax.plot(0, y_max_plot, "^k", clip_on=False, transform=ax.get_xaxis_transform())

        ax.set_xlabel('$x$', fontsize=12)
        ax.set_ylabel('$y$', fontsize=12)
        ax.set_title(r"函數 $f(x)$ 與 $x$ 軸圍成的兩個相等區域")
        ax.grid(True, linestyle='--', alpha=0.6)
        
        ax.set_xticks(np.arange(math.floor(x_min_plot), math.ceil(x_max_plot) + 1, 1))
        ax.set_yticks(np.arange(math.floor(y_min_plot), math.ceil(y_max_plot) + 1, 1))
        
        ax.set_xlim(x_min_plot, x_max_plot)
        ax.set_ylim(y_min_plot, y_max_plot)
        ax.set_aspect('equal')
        
        ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.7))
        ax.legend()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')


    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": solution_text, # 'answer' field is used for solution_text/display
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1"
    }


    """
    Robust check function for numerical answers, strictly following CRITICAL CODING STANDARDS.
    Returns True/False as per "閱卷與反饋" rule.
    """
    import re, math
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        # Only keep digits, dot, slash, minus sign for numerical parsing
        s = re.sub(r'[^\d./-]', '', s) 
        return s

    u_str = str(user_answer).strip()
    c_str = str(correct_answer).strip()
    
    yes_group = ["是", "yes", "true", "1", "o", "right"]
    no_group = ["否", "no", "false", "0", "x", "wrong"]
    
    # Check for boolean/yes-no answers first
    if c_str.lower() in yes_group:
        return u_str.lower() in yes_group
    if c_str.lower() in no_group:
        return u_str.lower() in no_group

    # Numerical comparison
    try:
        def parse(v):
            if "/" in v: 
                parts = v.split("/")
                if len(parts) == 2 and parts[1] != '0':
                    return float(parts[0]) / float(parts[1])
                else:
                    raise ValueError("Invalid fraction format or division by zero")
            return float(v)
        
        u_val = parse(clean(u_str))
        c_val = parse(clean(c_str))
        
        # Use math.isclose for robust floating point comparison with tolerance
        tolerance = 1e-5 # Standard tolerance for mathematical calculations
        if math.isclose(u_val, c_val, rel_tol=tolerance, abs_tol=tolerance):
            return True
    except (ValueError, TypeError):
        # If parsing to float fails, it's not a numerical answer, or invalid format.
        pass
        
    # Fallback to direct string comparison if numerical comparison fails
    return u_str == c_str

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
