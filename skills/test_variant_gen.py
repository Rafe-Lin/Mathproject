# ==============================================================================
# ID: test_variant_gen
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 59.03s | RAG: 2 examples
# Created At: 2026-01-25 21:43:29
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


import base64
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import datetime
import re

from fractions import Fraction # For robust float to fraction conversion in _get_val_data_from_float

# Helper to generate coordinate values, ensuring fractions are proper
def _generate_coordinate_value():
    is_fraction = random.choice([True, False])
    if is_fraction:
        int_part_raw = random.randint(-5, 5) # Raw integer part
        denominator = random.randint(2, 5) # Denominator between 2 and 5
        numerator = random.randint(1, denominator - 1) # Numerator between 1 and denominator-1

        # Construct the float value based on int_part and fractional part
        if int_part_raw >= 0:
            float_val = int_part_raw + (numerator / denominator)
        else:
            float_val = int_part_raw - (numerator / denominator) # e.g., -1 - 1/2 = -1.5

        is_neg = float_val < 0
        return float_val, (int_part_raw, numerator, denominator, is_neg)
    else:
        val = random.randint(-8, 8)
        return float(val), (int(val), 0, 0, val < 0)

# Helper to convert a float to the (float_val, (int_part, num, den, is_neg)) format
def _get_val_data_from_float(val_float):
    if val_float.is_integer():
        return val_float, (int(val_float), 0, 0, val_float < 0)
    else:
        # Use fractions.Fraction to get a precise fractional representation
        f = Fraction(val_float).limit_denominator(100) # Limit denominator for readability

        # If the denominator is 1, it's an integer (should have been caught by .is_integer() but good safeguard)
        if f.denominator == 1:
            return float(f), (int(f), 0, 0, f < 0)
        else:
            # For mixed number representation (e.g., 1 1/2 or -1 1/2)
            int_part = int(abs(f)) if f >= 0 else -int(abs(f)) # Keep sign of integer part
            num = abs(f.numerator) - abs(int_part) * f.denominator # Numerator of the proper fractional part
            den = f.denominator
            is_neg = f < 0
            
            # If the float was negative, ensure the int_part and num are correctly signed for the tuple
            # The _format_coordinate_latex uses abs(int_part) and abs(num) so internal sign of tuple values doesn't matter much
            # as long as `is_neg` is correct and `int_part` correctly reflects the integer portion.
            return float(f), (int_part, num, den, is_neg)

# Helper to format coordinate for display in LaTeX
def _format_coordinate_latex(val_data):
    float_val, (int_part, num, den, is_neg_flag_tuple) = val_data # `is_neg_flag_tuple` is the 4th element of the tuple, which is `val < 0`.

    if num == 0: # It's an integer
        return str(int(float_val))
    else: # It's a fraction or a mixed number
        display_sign = "-" if float_val < 0 else ""

        # Use absolute values for int_part, num, den for LaTeX formatting
        abs_int_part = abs(int_part)
        abs_num = abs(num)
        abs_den = abs(den)

        if abs_int_part == 0:
            # Pure fraction (e.g., 1/2 or -1/2)
            template = r"{sign}\frac{{{num}}}{{{den}}}"
            return template.replace("{sign}", display_sign).replace("{num}", str(abs_num)).replace("{den}", str(abs_den))
        else:
            # Mixed number (e.g., 1 and 1/2, or -1 and 1/2)
            template = r"{sign}{int_part}\frac{{{num}}}{{{den}}}"
            return template.replace("{sign}", display_sign).replace("{int_part}", str(abs_int_part)).replace("{num}", str(abs_num)).replace("{den}", str(abs_den))

# Helper to draw the coordinate plane
def draw_coordinate_plane(points, x_min=-10, x_max=10, y_min=-10, y_max=10):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')
    # CRITICAL: Grid lines linestyle changed from '--' to ':' as per spec
    ax.grid(True, linestyle=':', alpha=0.6) 

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # CRITICAL: Mandatory Axis Ticks
    ax.set_xticks(range(x_min, x_max + 1))
    ax.set_yticks(range(y_min, y_max + 1))
    ax.tick_params(axis='both', which='major', labelsize=10) # Added labelsize for ticks

    # Hide default tick labels to draw custom ones
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Plot origin '0'
    ax.text(0, 0, '0', color='black', ha='center', va='center', fontsize=18, fontweight='bold',
            bbox=dict(facecolor='white', edgecolor='none', pad=1))

    # Plot custom tick labels for X and Y axes
    for i in range(x_min, x_max + 1):
        if i != 0:
            ax.text(i, -0.5, str(i), ha='center', va='top', fontsize=10)
    for i in range(y_min, y_max + 1):
        if i != 0:
            ax.text(-0.5, i, str(i), ha='right', va='center', fontsize=10)

    # Plot axis arrows (X and Y)
    ax.plot(x_max, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(0, y_max, "^k", transform=ax.get_xaxis_transform(), clip_on=False)

    # Draw X and Y axes lines
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axvline(0, color='black', linewidth=1.5)

    # Plot points and labels with white halo
    for x, y, label in points:
        ax.scatter(x, y, color='red', zorder=5)
        ax.text(x + 0.3, y + 0.3, label, color='blue', fontsize=12, ha='left', va='bottom',
                bbox=dict(facecolor='white', edgecolor='none', pad=1, alpha=0.8))

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# Helper to determine quadrant name
def get_quadrant_name(x, y):
    # Use math.isclose for float comparison to zero
    if math.isclose(x, 0) and math.isclose(y, 0):
        return "原點"
    elif math.isclose(x, 0):
        return "Y軸上"
    elif math.isclose(y, 0):
        return "X軸上"
    elif x > 0 and y > 0:
        return "第一象限"
    elif x < 0 and y > 0:
        return "第二象限"
    elif x < 0 and y < 0:
        return "第三象限"
    else: # x > 0 and y < 0
        return "第四象限"

def generate(level=1):
    problem_type = random.choice(['textbook_midpoint', 'student_upload_quadrant'])
    question_text = ""
    correct_answer = ""
    solution_text = ""
    image_base64 = ""
    points_to_plot = []

    if problem_type == 'textbook_midpoint':
        # Type 1 (Textbook Variant - Maps to Example 1): Find midpoint
        x1_data = _generate_coordinate_value()
        y1_data = _generate_coordinate_value()
        x2_data = _generate_coordinate_value()
        y2_data = _generate_coordinate_value()

        x1, y1 = x1_data[0], y1_data[0]
        x2, y2 = x2_data[0], y2_data[0]

        mid_x_float = (x1 + x2) / 2
        mid_y_float = (y1 + y2) / 2

        x1_str = _format_coordinate_latex(x1_data)
        y1_str = _format_coordinate_latex(y1_data)
        x2_str = _format_coordinate_latex(x2_data)
        y2_str = _format_coordinate_latex(y2_data)

        question_text = r"已知坐標平面上兩點 $A({x1_str}, {y1_str})$ 和 $B({x2_str}, {y2_str})$，求線段 $\overline{AB}$ 的中點 $M$ 的坐標。".replace("{x1_str}", x1_str).replace("{y1_str}", y1_str).replace("{x2_str}", x2_str).replace("{y2_str}", y2_str)

        mid_x_ans = int(mid_x_float) if mid_x_float.is_integer() else mid_x_float
        mid_y_ans = int(mid_y_float) if mid_y_float.is_integer() else mid_y_float
        correct_answer = f"{mid_x_ans},{mid_y_ans}" # Pure data format as string of numbers

        solution_text = r"中點坐標公式為 $M = \left(\frac{x_1+x_2}{2}, \frac{y_1+y_2}{2}\right)$。"
        solution_text += r"將點 $A({x1_str}, {y1_str})$ 和 $B({x2_str}, {y2_str})$ 代入：".replace("{x1_str}", x1_str).replace("{y1_str}", y1_str).replace("{x2_str}", x2_str).replace("{y2_str}", y2_str)
        
        # Format intermediate sums for solution text
        sum_x = x1 + x2
        sum_y = y1 + y2
        
        sum_x_str = _format_coordinate_latex(_get_val_data_from_float(sum_x))
        sum_y_str = _format_coordinate_latex(_get_val_data_from_float(sum_y))

        mid_x_ans_str = _format_coordinate_latex(_get_val_data_from_float(mid_x_float))
        mid_y_ans_str = _format_coordinate_latex(_get_val_data_from_float(mid_y_float))

        solution_text += r"$x_M = \frac{{{x1_str} + {x2_str}}}{{2}} = \frac{{{sum_x_str}}}{{2}} = {mid_x_ans_str}$".replace("{x1_str}", x1_str).replace("{x2_str}", x2_str).replace("{sum_x_str}", sum_x_str).replace("{mid_x_ans_str}", mid_x_ans_str)
        solution_text += r"$y_M = \frac{{{y1_str} + {y2_str}}}{{2}} = \frac{{{sum_y_str}}}{{2}} = {mid_y_ans_str}$".replace("{y1_str}", y1_str).replace("{y2_str}", y2_str).replace("{sum_y_str}", sum_y_str).replace("{mid_y_ans_str}", mid_y_ans_str)
        solution_text += r"因此，中點 $M$ 的坐標為 $({mid_x_ans_str}, {mid_y_ans_str})$。".replace("{mid_x_ans_str}", mid_x_ans_str).replace("{mid_y_ans_str}", mid_y_ans_str)

        points_to_plot.append((x1, y1, 'A'))
        points_to_plot.append((x2, y2, 'B'))
        points_to_plot.append((mid_x_float, mid_y_float, 'M'))

    elif problem_type == 'student_upload_quadrant':
        # Type 2 (Student Upload Variant - Maps to Example 2): Point transformation and quadrant
        x_orig_data = _generate_coordinate_value()
        y_orig_data = _generate_coordinate_value()

        x_orig, y_orig = x_orig_data[0], y_orig_data[0]

        # Transformation: symmetric to Y-axis, then move down 2 units
        x_prime = -x_orig
        y_prime = y_orig - 2

        quadrant_name = get_quadrant_name(x_prime, y_prime)

        x_orig_str = _format_coordinate_latex(x_orig_data)
        y_orig_str = _format_coordinate_latex(y_orig_data)

        question_text = r"已知坐標平面上有一點 $P({x_orig_str}, {y_orig_str})$。若將 $P$ 點對稱於 $y$ 軸，再向下移動 $2$ 個單位長度，得到新的點 $P'$，請問 $P'$ 點落在第幾個象限或哪條軸上？".replace("{x_orig_str}", x_orig_str).replace("{y_orig_str}", y_orig_str)

        correct_answer = quadrant_name # Pure data format (string)

        # For solution text formatting
        x_prime_display_float = x_prime
        y_prime_display_float = y_prime
        
        # Ensure integer representation if applicable for solution text
        x_prime_display = str(int(x_prime_display_float)) if x_prime_display_float.is_integer() else str(x_prime_display_float)
        y_prime_display = str(int(y_prime_display_float)) if y_prime_display_float.is_integer() else str(y_prime_display_float)
        
        x_prime_latex_step1 = _format_coordinate_latex(_get_val_data_from_float(x_prime))
        y_prime_latex_step2 = _format_coordinate_latex(_get_val_data_from_float(y_prime))

        solution_text = r"原始點 $P$ 的坐標為 $({x_orig_str}, {y_orig_str})$。".replace("{x_orig_str}", x_orig_str).replace("{y_orig_str}", y_orig_str)
        solution_text += r"1. 將 $P$ 點對稱於 $y$ 軸：坐標變為 $(-x, y)$。所以中間點 $P_1$ 的坐標為 $({x_prime_latex_step1}, {y_orig_str})$。".replace("{x_prime_latex_step1}", x_prime_latex_step1).replace("{y_orig_str}", y_orig_str)
        solution_text += r"2. 再向下移動 $2$ 個單位長度：$y$ 坐標減去 $2$。所以最終點 $P'$ 的坐標為 $({x_prime_latex_step1}, {y_prime_latex_step2})$。".replace("{x_prime_latex_step1}", x_prime_latex_step1).replace("{y_prime_latex_step2}", y_prime_latex_step2)
        solution_text += r"計算 $P'$ 的坐標：$x' = -({x_orig_str}) = {x_prime_display}$， $y' = ({y_orig_str}) - 2 = {y_prime_display}$。".replace("{x_orig_str}", x_orig_str).replace("{y_orig_str}", y_orig_str).replace("{x_prime_display}", x_prime_display).replace("{y_prime_display}", y_prime_display)
        solution_text += r"因此 $P'({x_prime_display}, {y_prime_display})$ 落在 {quadrant_name}。".replace("{x_prime_display}", x_prime_display).replace("{y_prime_display}", y_prime_display).replace("{quadrant_name}", quadrant_name)

        points_to_plot.append((x_orig, y_orig, 'P'))
        points_to_plot.append((x_prime, y_prime, "P'"))

    image_base64 = draw_coordinate_plane(points_to_plot)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "",
        "image_base64": image_base64,
        "solution_text": solution_text,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    import re, math # CRITICAL CODING RULES (V18.9 Update): Local Imports in Check Function

    sanitized_user_answer = re.sub(r'[$\\\{\}xXyYkK=aAnNsS:]|\s+', '', user_answer).strip()

    # CRITICAL RULE: Handle string answers (like quadrants) first
    if correct_answer in ["第一象限", "第二象限", "第三象限", "第四象限", "X軸上", "Y軸上", "原點"]:
        return sanitized_user_answer == correct_answer
    
    # Otherwise, assume numerical comparison (e.g., coordinates)
    user_numbers = [float(s) for s in re.findall(r'-?\d+\.?\d*', sanitized_user_answer) if s]
    correct_numbers = [float(s) for s in re.findall(r'-?\d+\.?\d*', correct_answer) if s]

    # V13.6 API Hardened Spec: Exact Check Logic (4-line check)
    if len(user_numbers) != len(correct_numbers): 
        return False
    # If correct_answer is numerical, correct_numbers will not be empty.
    # If user_numbers is empty but correct_numbers is not, the len check above handles it.
    return all(math.isclose(u, c, rel_tol=1e-6, abs_tol=1e-6) for u, c in zip(user_numbers, correct_numbers))


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
