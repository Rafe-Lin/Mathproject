# ==============================================================================
# ID: gh_AreaUnderFunctionGraph
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 143.46s | RAG: 3 examples
# Created At: 2026-01-29 19:15:10
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



import base64
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Helper function for coordinate generation (V10.2, V13.0, V13.1, V13.5)
# This function is designed to return both the float value and a tuple
# representing the integer part, numerator, denominator, and sign for robust LaTeX formatting.
def _generate_coordinate_value(min_val, max_val, allow_fraction=False):
    """
    Generates a coordinate value, either integer or a proper fraction.
    Returns the float value and a tuple for LaTeX formatting.
    (V10.2, V13.0, V13.1, V13.5)
    
    CRITICAL RULE: "座標值僅限整數或 0.5".
    For this specific problem generation, we will prioritize integers to strictly
    mirror the RAG examples which implicitly use integer coefficients and bounds.
    If 'allow_fraction' is True, it will generate X.5 values.
    """
    if allow_fraction and random.random() < 0.5: # 50% chance for X.5 if allowed
        int_part = random.randint(math.floor(min_val), math.floor(max_val))
        float_val = int_part + random.choice([-0.5, 0.5])
        
        # Ensure the final float_val is strictly within the desired range
        if not (min_val <= float_val <= max_val):
            return _generate_coordinate_value(min_val, max_val, allow_fraction=False) # Fallback to integer
            
        return float_val, (int_part, 1, 2, float_val < 0 and int_part == 0) # (int_part, num, den, is_negative)
    else:
        val = random.randint(math.floor(min_val), math.ceil(max_val))
        return float(val), (int(val), 0, 0, val < 0) # For integers, num and den are 0

# Drawing helper function (V13.5, V13.6, CRITICAL RULE: Visual Solvability)
def _draw_coordinate_plane(points_to_plot, function_data=None, x_range=(-10, 10), y_range=(-10, 10), area_polygon=None):
    """
    Draws a coordinate plane with function graph, area highlight, and points.
    Ensures visual solvability with clear ticks and labels.
    (V10.2, V13.0, V13.1, V13.5, V13.6, CRITICAL RULE: Visual Solvability)
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal') # V10.2 Pure Style

    # Set symmetric integer ticks and labels (CRITICAL RULE: Visual Solvability, Mandatory Axis Ticks)
    x_min_tick = math.floor(x_range[0])
    x_max_tick = math.ceil(x_range[1])
    y_min_tick = math.floor(y_range[0])
    y_max_tick = math.ceil(y_range[1])

    ax.set_xticks(np.arange(x_min_tick, x_max_tick + 1, 1))
    ax.set_yticks(np.arange(y_min_tick, y_max_tick + 1, 1))
    ax.grid(True, linestyle='--', alpha=0.6) # Grid Lines

    ax.set_xlim(x_range[0], x_range[1])
    ax.set_ylim(y_range[0], y_range[1])

    # Draw arrows for axes (V13.6 API Hardened Spec)
    ax.plot(x_range[1], 0, ">k", clip_on=False, markersize=8) # x-axis arrow
    ax.plot(0, y_range[1], "^k", clip_on=False, markersize=8) # y-axis arrow

    ax.plot([x_range[0], x_range[1]], [0, 0], 'k-', lw=1) # x-axis line
    ax.plot([0, 0], [y_range[0], y_range[1]], 'k-', lw=1) # y-axis line

    # Label origin (V10.2 Pure Style)
    ax.text(0, -0.5, '0', color='black', ha='center', va='top', fontsize=18, fontweight='bold')

    # Plot function if provided
    if function_data:
        x_vals_plot = np.linspace(x_range[0], x_range[1], 400) # Use full plot range for function
        if function_data['type'] == 'linear':
            m, c = function_data['params']
            ax.plot(x_vals_plot, m * x_vals_plot + c, 'b-', label=f"$y = {int(m) if m.is_integer() else m}x + {int(c) if c.is_integer() else c}$")
        elif function_data['type'] == 'abs_value':
            a, h, k = function_data['params']
            ax.plot(x_vals_plot, a * np.abs(x_vals_plot - h) + k, 'b-', label=f"$y = {int(a) if a.is_integer() else a}|x - {int(h) if h.is_integer() else h}| + {int(k) if k.is_integer() else k}$")
        elif function_data['type'] == 'horizontal':
            c = function_data['params'][0]
            ax.plot(x_vals_plot, np.full_like(x_vals_plot, c), 'b-', label=f"$y = {int(c) if c.is_integer() else c}$")
        elif function_data['type'] == 'piecewise_linear':
            segments = function_data['params']
            for i in range(len(segments)):
                x1, y1 = segments[i]['p1']
                x2, y2 = segments[i]['p2']
                ax.plot([x1, x2], [y1, y2], 'b-')

    # Highlight area if polygon is provided
    if area_polygon is not None and len(area_polygon) > 0:
        ax.fill(area_polygon[:, 0], area_polygon[:, 1], 'skyblue', alpha=0.5)

    # Plot points (V10.2 Anti-Leak Protocol for plotting type)
    for label, x, y in points_to_plot:
        ax.plot(x, y, 'ro')
        # Labeling (V13.0, V13.1, V13.5: ax.text only for point names, not coordinates)
        ax.text(x, y + 0.5, label, fontsize=12, ha='center', va='bottom',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.3')) # V10.2 Pure Style

    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Function Graph and Area')
    plt.legend()

    # Convert plot to base64 string (ULTRA VISUAL STANDARDS: Resolution dpi=300)
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# Main generate function
def generate(level=1):
    """
    Generates a K12 math problem for "Area Under Function Graph", strictly
    mirroring the RAG examples for mathematical models.
    (V11.8 Mirror Enhanced Edition)
    """
    # Mapping problem types to RAG examples:
    # 'linear_function_x_axis', 'bounded_by_multiple_lines', 'rectangle_area' -> RAG Ex 1 (Trapezoid/Rectangle Area)
    # 'absolute_value_function_x_axis' -> RAG Ex 2 (Triangle Area)
    # 'riemann_sum_template_area' -> RAG Ex 3 (Area with Riemann Sum context)
    problem_type = random.choice([
        'linear_function_x_axis',
        'absolute_value_function_x_axis',
        'bounded_by_multiple_lines',
        'rectangle_area',
        'riemann_sum_template_area'
    ])

    question_text = ""
    correct_answer = ""
    answer_display = ""
    image_base64 = ""
    function_data = None
    area_polygon = None
    points_to_plot = []
    
    # V13.0 Coordinate selection control: symmetric and wide range
    min_coord_val = -8
    max_coord_val = 8
    
    # Initialize x_range and y_range with default values that will be adjusted
    x_range = (min_coord_val - 2, max_coord_val + 2) 
    y_range = (min_coord_val - 2, max_coord_val + 2)

    # For all coordinate generations, setting allow_fraction=False to adhere to "座標值僅限整數"
    # as per RAG examples and strict interpretation of the rule.

    if problem_type == 'linear_function_x_axis':
        # Maps to Example 1: Area under y=mx+c and x-axis.
        m_val, _ = _generate_coordinate_value(-2, 2, allow_fraction=False)
        while m_val == 0: # Ensure slope is not zero
            m_val, _ = _generate_coordinate_value(-2, 2, allow_fraction=False)
        
        c_val, _ = _generate_coordinate_value(-5, 5, allow_fraction=False)
        
        x1_val, _ = _generate_coordinate_value(min_coord_val, max_coord_val - 1, allow_fraction=False)
        x2_val, _ = _generate_coordinate_value(x1_val + 1, max_coord_val, allow_fraction=False)

        y1 = m_val * x1_val + c_val
        y2 = m_val * x2_val + c_val
        
        area = 0.0
        
        x_intercept = -c_val / m_val if m_val != 0 else None
        
        if x_intercept is not None and x1_val < x_intercept < x2_val:
            # Two triangles (one above, one below x-axis)
            area1 = 0.5 * abs(y1) * abs(x_intercept - x1_val)
            area2 = 0.5 * abs(y2) * abs(x2_val - x_intercept)
            area = area1 + area2

            # Polygon for visual fill (V13.5: labels only, values in text)
            area_polygon = np.array([
                [x1_val, 0], [x1_val, y1], [x_intercept, 0], [x2_val, y2], [x2_val, 0]
            ])
        else:
            # Single trapezoid (or triangle if one y is 0)
            area = 0.5 * (abs(y1) + abs(y2)) * (x2_val - x1_val)
            area_polygon = np.array([[x1_val, 0], [x1_val, y1], [x2_val, y2], [x2_val, 0]])
            
        function_data = {'type': 'linear', 'params': (m_val, c_val)}
        
        question_text_template = r"下圖顯示函數 $y = {m_val_str}x + {c_val_str}$ 的圖形。計算在 $x = {x1_val_str}$ 到 $x = {x2_val_str}$ 之間，函數圖形與 $x$ 軸所圍成的面積。 (取絕對值)"
        question_text = question_text_template.replace("{m_val_str}", str(int(m_val)) if m_val.is_integer() else str(m_val))\
                                             .replace("{c_val_str}", str(int(c_val)) if c_val.is_integer() else str(c_val))\
                                             .replace("{x1_val_str}", str(int(x1_val)) if x1_val.is_integer() else str(x1_val))\
                                             .replace("{x2_val_str}", str(int(x2_val)) if x2_val.is_integer() else str(x2_val))
        
        correct_answer = str(round(area, 2)) # Pure data (CRITICAL RULE: Answer Data Purity)
        answer_display = f"面積為 {round(area, 2)}"
        
        # Points for visualization (V13.6: Strict Labeling)
        points_to_plot.append(('A', x1_val, y1))
        points_to_plot.append(('B', x2_val, y2))
        points_to_plot.append(('C', x1_val, 0))
        points_to_plot.append(('D', x2_val, 0))
        if x_intercept is not None and x1_val < x_intercept < x2_val:
            points_to_plot.append(('X', x_intercept, 0))
        
        # Adjust x_range and y_range for plot (V13.5)
        x_values_for_range = [x1_val, x2_val, x_intercept if x_intercept is not None else x1_val]
        y_values_for_range = [y1, y2, 0]
        x_range = (min(x_values_for_range) - 2, max(x_values_for_range) + 2)
        y_range = (min(y_values_for_range) - 2, max(y_values_for_range) + 2)
        y_range = (min(y_range[0], -2), max(y_range[1], 2)) # Ensure some y-axis visibility even if all y >= 0


    elif problem_type == 'absolute_value_function_x_axis':
        # Maps to Example 2: Area under y=a|x-h|+k and x-axis (forms a triangle).
        a_val, _ = _generate_coordinate_value(1, 2, allow_fraction=False)
        h_val, _ = _generate_coordinate_value(-3, 3, allow_fraction=False)
        k_val, _ = _generate_coordinate_value(-5, -1, allow_fraction=False) # Must be negative for intersection with x-axis
        
        # Find x-intercepts: a|x-h| + k = 0 => |x-h| = -k/a
        abs_val_term = -k_val / a_val
        x_int1 = h_val - abs_val_term
        x_int2 = h_val + abs_val_term
        
        base = abs(x_int2 - x_int1)
        height = abs(k_val)
        area = 0.5 * base * height
        
        function_data = {'type': 'abs_value', 'params': (a_val, h_val, k_val)}
        
        question_text_template = r"下圖顯示函數 $y = {a_val_str}|x - {h_val_str}| + {k_val_str}$ 的圖形。計算函數圖形與 $x$ 軸所圍成的面積。"
        question_text = question_text_template.replace("{a_val_str}", str(int(a_val)) if a_val.is_integer() else str(a_val))\
                                             .replace("{h_val_str}", str(int(h_val)) if h_val.is_integer() else str(h_val))\
                                             .replace("{k_val_str}", str(int(k_val)) if k_val.is_integer() else str(k_val))
        
        correct_answer = str(round(area, 2)) # Pure data
        answer_display = f"面積為 {round(area, 2)}"
        
        poly_points = [[x_int1, 0], [h_val, k_val], [x_int2, 0]]
        area_polygon = np.array(poly_points)

        # Points for visualization (V13.6: Strict Labeling)
        points_to_plot.append(('V', h_val, k_val)) # Vertex
        points_to_plot.append(('X1', x_int1, 0))
        points_to_plot.append(('X2', x_int2, 0))
        
        # Adjust x_range and y_range for plot (V13.5)
        x_range = (min(x_int1, x_int2, h_val) - 2, max(x_int1, x_int2, h_val) + 2)
        y_range = (k_val - 2, max(0.0, k_val + 5)) # Ensure y_range includes vertex y and 0


    elif problem_type == 'bounded_by_multiple_lines':
        # Maps to Example 1 (multiple trapezoids): Area under a piecewise linear function.
        x0_val, _ = _generate_coordinate_value(-6, -3, allow_fraction=False)
        x1_val, _ = _generate_coordinate_value(x0_val + 2, x0_val + 5, allow_fraction=False)
        x2_val, _ = _generate_coordinate_value(x1_val + 2, x1_val + 5, allow_fraction=False)
        
        y0_val, _ = _generate_coordinate_value(1, 5, allow_fraction=False)
        y1_val, _ = _generate_coordinate_value(1, 5, allow_fraction=False)
        y2_val, _ = _generate_coordinate_value(1, 5, allow_fraction=False)

        area1 = 0.5 * (y0_val + y1_val) * (x1_val - x0_val)
        area2 = 0.5 * (y1_val + y2_val) * (x2_val - x1_val)
        area = area1 + area2
        
        segments = [
            {'p1': (x0_val, y0_val), 'p2': (x1_val, y1_val)},
            {'p1': (x1_val, y1_val), 'p2': (x2_val, y2_val)}
        ]
        function_data = {'type': 'piecewise_linear', 'params': segments}
        
        poly_points = [[x0_val, 0], [x0_val, y0_val], [x1_val, y1_val], [x2_val, y2_val], [x2_val, 0]]
        area_polygon = np.array(poly_points)
        
        question_text_template = r"下圖顯示一個由直線段組成的函數圖形。計算函數圖形與 $x$ 軸所圍成的面積。"
        question_text = question_text_template
        
        correct_answer = str(round(area, 2)) # Pure data
        answer_display = f"面積為 {round(area, 2)}"

        # Points for visualization (V13.6: Strict Labeling)
        points_to_plot.append(('P1', x0_val, y0_val))
        points_to_plot.append(('P2', x1_val, y1_val))
        points_to_plot.append(('P3', x2_val, y2_val))
        points_to_plot.append(('X0', x0_val, 0))
        points_to_plot.append(('X2', x2_val, 0))
        
        # Adjust x_range and y_range for plot (V13.5)
        x_range = (x0_val - 2, x2_val + 2)
        y_range = (0, max(y0_val, y1_val, y2_val) + 2)


    elif problem_type == 'rectangle_area':
        # Maps to Example 1 (special case): Area of a rectangle formed by y=c, x-axis, and two vertical lines.
        c_val, _ = _generate_coordinate_value(1, 7, allow_fraction=False) # Height, must be positive
        x1_val, _ = _generate_coordinate_value(-6, 0, allow_fraction=False)
        x2_val, _ = _generate_coordinate_value(x1_val + 2, x1_val + 8, allow_fraction=False) # Ensure width > 0
        
        width = x2_val - x1_val
        height = c_val
        area = width * height
        
        function_data = {'type': 'horizontal', 'params': (c_val,)}
        
        question_text_template = r"下圖顯示函數 $y = {c_val_str}$ 的圖形。計算在 $x = {x1_val_str}$ 到 $x = {x2_val_str}$ 之間，函數圖形與 $x$ 軸所圍成的面積。"
        question_text = question_text_template.replace("{c_val_str}", str(int(c_val)) if c_val.is_integer() else str(c_val))\
                                             .replace("{x1_val_str}", str(int(x1_val)) if x1_val.is_integer() else str(x1_val))\
                                             .replace("{x2_val_str}", str(int(x2_val)) if x2_val.is_integer() else str(x2_val))
        
        correct_answer = str(round(area, 2)) # Pure data
        answer_display = f"面積為 {round(area, 2)}"
        
        poly_points = [[x1_val, 0], [x1_val, c_val], [x2_val, c_val], [x2_val, 0]]
        area_polygon = np.array(poly_points)

        # Points for visualization (V13.6: Strict Labeling)
        points_to_plot.append(('A', x1_val, c_val))
        points_to_plot.append(('B', x2_val, c_val))
        points_to_plot.append(('C', x1_val, 0))
        points_to_plot.append(('D', x2_val, 0))
        
        # Adjust x_range and y_range for plot (V13.5)
        x_range = (x1_val - 2, x2_val + 2)
        y_range = (0, c_val + 2)
        
    elif problem_type == 'riemann_sum_template_area':
        # Maps to Example 3: Area under f(x)=mx with Riemann Sum context.
        # Strict mirroring of RAG Ex 3: f(x) = x, x=0 to x=a
        # Generalize f(x) = mx for variety, but the question context will be strict.
        m_val, _ = _generate_coordinate_value(1, 3, allow_fraction=False) # m > 0
        a_val, _ = _generate_coordinate_value(2, 6, allow_fraction=False) # a > 0

        # Area is a triangle: 0.5 * base * height = 0.5 * a_val * (m_val * a_val)
        area = 0.5 * m_val * (a_val ** 2)

        function_data = {'type': 'linear', 'params': (m_val, 0.0)} # y = mx + 0

        # CONTEXT RETENTION: Use the exact wording from RAG Ex 3.
        # The problem asks for part (2) area, but includes the Riemann sum setup for context.
        question_text_template = r"已知 $a={a_val_str}>0$，且 $R$ 為函數 $f(x)={m_val_str}x$ 的圖形與 $x$ 軸、 $x=0$ 及 $x={a_val_str}$ 所圍成的區域，回答下列問題。(1) 將區間 $[0,{a_val_str}]$ 平分成 $n$ 等分，分割點為 $x_k = \frac{{a_val_str}k}{n}$。令 $\Delta x = \frac{{a_val_str}}{n}$，在區間 $[x_{k-1}, x_k]$ 中取 $c_k = x_k$ （右端點），得黎曼和 $R_n$ [　　　　]。 (2) 求 $R$ 的面積。"
        
        # Replace placeholders using .replace for LaTeX single curly braces
        question_text = question_text_template.replace("{a_val_str}", str(int(a_val)) if a_val.is_integer() else str(a_val))\
                                             .replace("{m_val_str}", str(int(m_val)) if m_val.is_integer() else str(m_val))

        correct_answer = str(round(area, 2))
        answer_display = f"面積為 {round(area, 2)}"

        poly_points = [[0, 0], [a_val, m_val * a_val], [a_val, 0]]
        area_polygon = np.array(poly_points)

        # Points for visualization (V13.6: Strict Labeling)
        points_to_plot.append(('O', 0, 0))
        points_to_plot.append(('P', a_val, m_val * a_val))
        points_to_plot.append(('Q', a_val, 0))
        
        # Adjust x_range and y_range for plot (V13.5)
        x_range = (min(0, a_val) - 2, max(0, a_val) + 2)
        y_range = (0, m_val * a_val + 2)


    image_base64 = _draw_coordinate_plane(points_to_plot, function_data, x_range, y_range, area_polygon)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1"
    }

# Check function (V18.8, V18.9 CRITICAL CODING RULES)

    """
    Checks the user's answer against the correct answer.
    Includes robust input sanitization and float comparison.
    (CRITICAL RULE: Robust Check Logic, V18.8, V18.9, Universal Check Template)
    """
    import re, math

    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        # Keep numbers, decimal points, and division symbols. Remove other chars.
        return re.sub(r'[^\d./-]+', '', s)

    u_str = str(user_answer).strip()
    c_str = str(correct_answer).strip()

    # [V18.13 Update] 支援中英文是非題互通
    yes_group = ["是", "Yes", "TRUE", "True", "1", "O", "right"]
    no_group = ["否", "No", "FALSE", "False", "0", "X", "wrong"]

    if c_str in yes_group:
        return {"correct": u_str in yes_group, "result": "正確！" if u_str in yes_group else "答案錯誤"}
    if c_str in no_group:
        return {"correct": u_str in no_group, "result": "正確！" if u_str in no_group else "答案錯誤"}

    # 3. 數值與字串比對
    try:
        # 解析分數與浮點數
        def parse(v):
            if "/" in v:
                parts = v.split("/")
                if len(parts) == 2 and parts[1] != '0': # Avoid division by zero
                    return float(parts[0]) / float(parts[1])
                else:
                    raise ValueError("Invalid fraction format or division by zero")
            return float(v)
        
        u_val = parse(clean(u_str))
        c_val = parse(clean(c_str))
        if math.isclose(u_val, c_val, rel_tol=1e-5):
            return {"correct": True, "result": "正確！"}
    except ValueError: # Catch ValueErrors from float conversion or parse function
        pass # Fall through to string comparison
        
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
