# ==============================================================================
# ID: jh_數學2下_PerpendicularBisectorAndAngleBisectorConstruction
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 105.04s | RAG: 5 examples
# Created At: 2026-01-22 20:18:15
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
    # 隱藏刻度,僅保留 0
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
        # 雙向清理:剝除 LaTeX 符號與空格
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
from io import BytesIO
import matplotlib.pyplot as plt
import re
import numpy as np # For float comparison tolerance

# --- V10.2 Coordinate Hardening Spec A: Data Structure Lock-down ---
def _generate_coordinate_value(min_val=-8, max_val=8, allow_fraction=False):
    """
    Generates a coordinate value (float_val, (int_part, num, den, is_neg)).
    If allow_fraction is True, generates values like N.5.
    V13.1: 禁絕假分數 (numerator < denominator), denominator > 1.
    This implementation generates integers or X.5, satisfying the fraction constraint.
    Ensures the generated value is within [min_val, max_val].
    """
    
    # Generate an integer value within the desired range
    integer_part = random.randint(min_val, max_val)
    
    float_val = float(integer_part)
    num = 0
    den = 0
    is_neg = False
    
    if allow_fraction and random.random() < 0.3: # 30% chance for a .5 fraction
        # Try to add +/- 0.5, but ensure it stays within min_val/max_val
        possible_vals = []
        val_plus_half = integer_part + 0.5
        val_minus_half = integer_part - 0.5

        if min_val <= val_plus_half <= max_val:
            possible_vals.append(val_plus_half)
        if min_val <= val_minus_half <= max_val:
            possible_vals.append(val_minus_half)
        
        # If integer_part itself is the only valid choice (e.g., at boundary), or no fractional choices fit
        if not possible_vals:
            float_val = float(integer_part)
        else:
            float_val = random.choice(possible_vals)
            num = 1
            den = 2
            is_neg = (float_val < 0)
    else:
        # No fraction, just the integer value
        is_neg = (float_val < 0)

    # Determine int_part for the tuple (int_part, num, den, is_neg)
    # final_int_part is the integer part of the number, truncating towards zero.
    final_int_part = int(math.trunc(float_val)) 
    
    return (float_val, (final_int_part, num, den, is_neg))

# Helper to format a single coordinate value for display (V13.0 C: str(int(val)))
def _format_for_display(val):
    """
    Formats a coordinate value for display in question_text.
    Ensures integer values are displayed as integers (e.g., "5" instead of "5.0").
    For floats like 3.5, it displays "3.5".
    """
    if isinstance(val, (float, np.float64)) and val.is_integer():
        return str(int(val))
    return str(val)

# --- Generic Helper for Drawing (V13.6 API Hardened Spec) ---
def draw_coordinate_plane(points_with_labels=None, lines=None, circumcenter=None, incenter=None, x_range=(-10, 10), y_range=(-10, 10), show_ticks=True):
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Set aspect equal (V10.2 D)
    ax.set_aspect('equal')

    # Draw grid
    ax.grid(True, which='both', color='gray', linestyle='--', linewidth=0.5)

    # Set x and y limits (V13.0 D: symmetric range)
    ax.set_xlim(x_range)
    ax.set_ylim(y_range)

    # V13.0 D: xticks interval fixed to 1, symmetric range
    ax.set_xticks(range(x_range[0], x_range[1] + 1))
    ax.set_yticks(range(y_range[0], y_range[1] + 1))

    # V17.1 & V17.2: Ensure x-axis and y-axis have integer labels visible
    if show_ticks:
        ax.tick_params(axis='x', labelsize=10)
        ax.tick_params(axis='y', labelsize=10)
    else:
        ax.set_xticklabels([])
        ax.set_yticklabels([])

    # Draw axes
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axvline(0, color='black', linewidth=1.5)

    # V13.6 API Hardened Spec: Arrow Ban - use ax.plot for arrows
    # X-axis arrow
    ax.plot(x_range[1], 0, ">k", clip_on=False, markersize=8)
    # Y-axis arrow
    ax.plot(0, y_range[1], "^k", clip_on=False, markersize=8)

    # V10.2 D: 原點 '0' (18號加粗)
    ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold')

    # Plot points and labels (V13.0 B & V13.1 & V13.5: Label Isolation)
    if points_with_labels:
        # V13.6: Strict Labeling - Whitelist for labels
        label_whitelist = ['A', 'B', 'C', 'P', 'O', 'I', 'D', 'E', 'F', 'G', 'H', 'M', 'N', 'K', 'L']
        for label, (x, y) in points_with_labels:
            if label not in label_whitelist:
                label = '' # Clear label if not in whitelist
            ax.plot(x, y, 'o', color='blue', markersize=6)
            # V10.2 D: 點標籤須加白色光暈 (bbox)
            ax.text(x + 0.2, y + 0.2, label, fontsize=12, color='black', ha='left', va='bottom',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))
    
    # Plot lines if any (e.g., perpendicular bisectors, angle bisectors)
    if lines:
        for line_eq in lines:
            if line_eq['type'] == 'vertical':
                ax.axvline(line_eq['x_val'], color=line_eq.get('color', 'gray'), linestyle=line_eq.get('linestyle', '--'))
            elif line_eq['type'] == 'horizontal':
                ax.axhline(line_eq['y_val'], color=line_eq.get('color', 'gray'), linestyle=line_eq.get('linestyle', '--'))
            else: # y = mx + c
                x_vals = np.array([x_range[0], x_range[1]])
                y_vals = line_eq['m'] * x_vals + line_eq['c']
                ax.plot(x_vals, y_vals, color=line_eq.get('color', 'gray'), linestyle=line_eq.get('linestyle', '--'))

    # Plot circumcenter or incenter if provided (V13.5: Label Isolation)
    if circumcenter:
        cx, cy = circumcenter
        ax.plot(cx, cy, 'x', color='red', markersize=10, mew=2)
        ax.text(cx + 0.2, cy + 0.2, 'O', fontsize=12, color='red', ha='left', va='bottom',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))

    if incenter:
        ix, iy = incenter
        ax.plot(ix, iy, 'x', color='green', markersize=10, mew=2)
        ax.text(ix + 0.2, iy + 0.2, 'I', fontsize=12, color='green', ha='left', va='bottom',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))

    # Convert plot to base64 string
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig) # V6: Must close figure to prevent memory leaks
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- Geometric Helper Functions ---
def _calculate_distance(p1, p2):
    """Calculates Euclidean distance between two points."""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def _find_midpoint(p1, p2):
    """Finds the midpoint of a segment."""
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

def _find_perpendicular_bisector_equation(p1, p2):
    """
    Finds the equation of the perpendicular bisector of segment P1P2.
    Returns a dictionary: {'type': 'vertical'/'horizontal'/'linear', 'x_val'/'y_val'/'m'/'c'}
    """
    mid_x, mid_y = _find_midpoint(p1, p2)
    
    # Calculate slope of segment (p1, p2)
    if math.isclose(p2[0], p1[0]): # Vertical segment (x1 = x2)
        # Perpendicular bisector is horizontal: y = mid_y
        return {'type': 'horizontal', 'y_val': mid_y}
    elif math.isclose(p2[1], p1[1]): # Horizontal segment (y1 = y2)
        # Perpendicular bisector is vertical: x = mid_x
        return {'type': 'vertical', 'x_val': mid_x}
    else:
        seg_slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
        perp_slope = -1 / seg_slope
        # Equation: y = perp_slope * x + (mid_y - perp_slope * mid_x)
        intercept = mid_y - perp_slope * mid_x
        return {'type': 'linear', 'm': perp_slope, 'c': intercept}

def _find_line_intersection(line1, line2):
    """
    Finds the intersection point of two lines.
    Returns (x, y) or None if lines are parallel/identical.
    Handles float comparison with tolerance.
    """
    # Case 1: Both linear (y = m1x + c1, y = m2x + c2)
    if line1['type'] == 'linear' and line2['type'] == 'linear':
        if math.isclose(line1['m'], line2['m'], rel_tol=1e-9, abs_tol=1e-9): # Parallel slopes
            if math.isclose(line1['c'], line2['c'], rel_tol=1e-9, abs_tol=1e-9): # Identical lines
                return (float('inf'), float('inf')) # Indicate infinitely many intersections
            return None # Parallel and distinct
        x = (line2['c'] - line1['c']) / (line1['m'] - line2['m'])
        y = line1['m'] * x + line1['c']
        return (x, y)
    
    # Case 2: One vertical, one linear (x = x_val, y = mx + c)
    elif line1['type'] == 'vertical' and line2['type'] == 'linear':
        x = line1['x_val']
        y = line2['m'] * x + line2['c']
        return (x, y)
    elif line2['type'] == 'vertical' and line1['type'] == 'linear':
        x = line2['x_val']
        y = line1['m'] * x + line1['c']
        return (x, y)

    # Case 3: One horizontal, one linear (y = y_val, y = mx + c)
    elif line1['type'] == 'horizontal' and line2['type'] == 'linear':
        y = line1['y_val']
        if math.isclose(line2['m'], 0, rel_tol=1e-9, abs_tol=1e-9): # Both horizontal (y=const)
            if math.isclose(line1['y_val'], line2['c'], rel_tol=1e-9, abs_tol=1e-9):
                return (float('inf'), float('inf')) # Identical lines
            return None
        x = (y - line2['c']) / line2['m']
        return (x, y)
    elif line2['type'] == 'horizontal' and line1['type'] == 'linear':
        y = line2['y_val']
        if math.isclose(line1['m'], 0, rel_tol=1e-9, abs_tol=1e-9): # Both horizontal
            if math.isclose(line2['y_val'], line1['c'], rel_tol=1e-9, abs_tol=1e-9):
                return (float('inf'), float('inf'))
            return None
        x = (y - line1['c']) / line1['m']
        return (x, y)

    # Case 4: One vertical, one horizontal (x = x_val, y = y_val)
    elif line1['type'] == 'vertical' and line2['type'] == 'horizontal':
        return (line1['x_val'], line2['y_val'])
    elif line2['type'] == 'vertical' and line1['type'] == 'horizontal':
        return (line2['x_val'], line1['y_val'])

    # Case 5: Both vertical or both horizontal (parallel or identical)
    elif (line1['type'] == 'vertical' and line2['type'] == 'vertical'):
        return (float('inf'), float('inf')) if math.isclose(line1['x_val'], line2['x_val'], rel_tol=1e-9, abs_tol=1e-9) else None
    elif (line1['type'] == 'horizontal' and line2['type'] == 'horizontal'):
        return (float('inf'), float('inf')) if math.isclose(line1['y_val'], line2['y_val'], rel_tol=1e-9, abs_tol=1e-9) else None
    
    return None # Fallback, should not be reached with valid line types

def _generate_non_collinear_points(min_coord=-7, max_coord=7, allow_fraction=False):
    """
    Generates three distinct, non-collinear points for a triangle.
    Coordinates are generated using _generate_coordinate_value.
    """
    attempts = 0
    while attempts < 100: # Limit attempts to prevent infinite loops for rare edge cases
        p1 = (_generate_coordinate_value(min_val=min_coord, max_val=max_coord, allow_fraction=allow_fraction)[0],
              _generate_coordinate_value(min_val=min_coord, max_val=max_coord, allow_fraction=allow_fraction)[0])
        p2 = (_generate_coordinate_value(min_val=min_coord, max_val=max_coord, allow_fraction=allow_fraction)[0],
              _generate_coordinate_value(min_val=min_coord, max_val=max_coord, allow_fraction=allow_fraction)[0])
        p3 = (_generate_coordinate_value(min_val=min_coord, max_val=max_coord, allow_fraction=allow_fraction)[0],
              _generate_coordinate_value(min_val=min_coord, max_val=max_coord, allow_fraction=allow_fraction)[0])

        # Check for distinct points
        if p1 == p2 or p1 == p3 or p2 == p3:
            attempts += 1
            continue

        # Check for collinearity using cross product: (x2-x1)(y3-y1) - (y2-y1)(x3-x1) == 0
        area_double = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])
        if abs(area_double) > 1e-9: # Not collinear (using tolerance for floats)
            return p1, p2, p3
        attempts += 1
    raise RuntimeError("Failed to generate non-collinear points after multiple attempts.")


### 頂層函式 (Top-level Functions)

def generate(level=1):
    problem_type = random.choice([1, 2, 3, 4]) # Randomly select problem type

    question_text = ""
    correct_answer = ""
    image_base64 = ""
    
    x_range = (-10, 10) # V13.0 D: symmetric and wide range
    y_range = (-10, 10)

    if problem_type == 1: # Type 1 (Mirrors RAG Ex 1: Perpendicular Bisector Property - Length Calculation)
        # 題目描述: 給定線段AB的中垂線L,點P在L上,已知PA長度,求PB長度
        # 隨機化: 隨機生成A, B點座標,隨機一個PA長度
        
        ax, ay = _generate_coordinate_value(min_val=-5, max_val=5, allow_fraction=False)[0], \
                 _generate_coordinate_value(min_val=-5, max_val=5, allow_fraction=False)[0]
        bx, by = _generate_coordinate_value(min_val=-5, max_val=5, allow_fraction=False)[0], \
                 _generate_coordinate_value(min_val=-5, max_val=5, allow_fraction=False)[0]
        
        while (ax, ay) == (bx, by): # Ensure distinct points
            bx, by = _generate_coordinate_value(min_val=-5, max_val=5, allow_fraction=False)[0], \
                     _generate_coordinate_value(min_val=-5, max_val=5, allow_fraction=False)[0]

        A = (ax, ay)
        B = (bx, by)

        # 根據中垂線性質,點P到線段兩端點的距離相等 (PA = PB)
        pa_len = random.randint(3, 10) # 隨機生成一個PA長度
        pb_len = pa_len # 答案為PA長度

        # V5: Use .replace() for LaTeX safety
        question_template = r"已知線段 $AB$ 的中垂線為 $L$，點 $P$ 在 $L$ 上。若 $PA = {pa_len}$，則 $PB = ?$。"
        question_text = question_template.replace("{pa_len}", str(pa_len))
        
        # V1.1: correct_answer must be pure data
        correct_answer = str(pb_len)
        
        # Image generation: Draw A, B, and a point P on the perpendicular bisector for illustration.
        # The exact coordinates of P are not tied to the given `pa_len`, just for visual reference.
        mid_x, mid_y = _find_midpoint(A, B)
        bisector_eq = _find_perpendicular_bisector_equation(A, B)
        
        # Find an illustrative point P on the bisector, keeping it within reasonable bounds
        px_illustrative, py_illustrative = mid_x, mid_y 
        
        # If bisector is linear, choose an x slightly offset from midpoint
        if bisector_eq['type'] == 'linear':
            offset_x = random.choice([-1, 1]) * random.uniform(1.0, 2.0)
            px_illustrative = mid_x + offset_x
            py_illustrative = bisector_eq['m'] * px_illustrative + bisector_eq['c']
        elif bisector_eq['type'] == 'vertical':
            offset_y = random.choice([-1, 1]) * random.uniform(1.0, 2.0)
            py_illustrative = mid_y + offset_y
        elif bisector_eq['type'] == 'horizontal':
            offset_x = random.choice([-1, 1]) * random.uniform(1.0, 2.0)
            px_illustrative = mid_x + offset_x

        P_illustrative = (px_illustrative, py_illustrative)
        
        points_to_plot = [('A', A), ('B', B), ('P', P_illustrative)]
        lines_to_plot = [bisector_eq]
        image_base64 = draw_coordinate_plane(points_with_labels=points_to_plot, lines=lines_to_plot, x_range=x_range, y_range=y_range)


    elif problem_type == 2: # Type 2 (Mirrors RAG Ex 4: Angle Bisector Property - Distance/Length Calculation)
        # 題目描述: 給定角ABC的角平分線BD,點P在BD上,已知P到直線AB的距離,求P到直線BC的距離
        # 隨機化: 隨機生成一個距離值
        
        dist_val = random.randint(2, 8) # 隨機生成一個距離值
        
        # 根據角平分線性質,點P到角兩邊的距離相等
        
        # V5: Use .replace() for LaTeX safety
        question_template = r"已知 $\angle ABC$ 的角平分線為 $BD$，點 $P$ 在 $BD$ 上。若點 $P$ 到直線 $AB$ 的距離為 ${dist_val}$，則點 $P$ 到直線 $BC$ 的距離為多少？"
        question_text = question_template.replace("{dist_val}", str(dist_val))
        
        # V1.1: correct_answer must be pure data
        correct_answer = str(dist_val)

        # Image generation: V3.1 - Reference Only Image.
        # 由於此題為性質題,且精確繪製角平分線與距離易洩漏答案,故提供示意圖
        # 圖中不包含具體座標或數值,僅用於概念輔助
        fig, ax = plt.subplots(figsize=(6, 6))
        
        # 繪製一個示意性的角和角平分線
        ax.plot([-5, 0], [2, 0], 'b-', linewidth=1.5) # 直線 AB (示意)
        ax.plot([0, 5], [0, 2], 'b-', linewidth=1.5) # 直線 BC (示意)
        ax.plot([0, 0], [0, 0], 'o', color='black', markersize=5) # 頂點 B
        
        # 繪製角平分線 BD (示意)
        # For an angle like this, a bisector could go up
        ax.plot([0, 3], [0, 3], 'r--', linewidth=1.5) # 角平分線 BD (示意)
        
        # 繪製點 P 和其到兩邊的垂線 (示意)
        px_ref, py_ref = 2, 2 # Illustrative point P
        ax.plot(px_ref, py_ref, 'go', markersize=6) # 點 P (示意)
        
        # P 到 BC 的垂線 (示意)
        # Assuming BC is y = 0.4x (from (0,0) to (5,2)), perp line from (2,2)
        # Slope of BC is 0.4. Perpendicular slope is -1/0.4 = -2.5
        # Line from (2,2) with slope -2.5: y - 2 = -2.5(x - 2) => y = -2.5x + 7
        # Intersection with y = 0.4x: 0.4x = -2.5x + 7 => 2.9x = 7 => x = 7/2.9 ~ 2.41
        # To avoid complex calculations for an "illustrative" diagram, simply draw vertical/horizontal for clarity.
        # For illustrative purposes, we just show lines that *look* perpendicular.
        ax.plot([px_ref, px_ref], [py_ref, 0.4*px_ref], 'g--', linewidth=1) # P to BC (approx)
        ax.plot([px_ref, 0.4*py_ref], [py_ref, py_ref], 'g--', linewidth=1) # P to AB (approx)

        # Labels with white halo
        bbox_props = dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2')
        ax.text(-5, 2, 'A', fontsize=12, bbox=bbox_props)
        ax.text(0, 0, 'B', fontsize=12, bbox=bbox_props)
        ax.text(5, 2, 'C', fontsize=12, bbox=bbox_props)
        ax.text(3.2, 3.2, 'D', fontsize=12, bbox=bbox_props) # Adjust D's position
        ax.text(px_ref + 0.2, py_ref + 0.2, 'P', fontsize=12, bbox=bbox_props)
        
        ax.set_aspect('equal')
        ax.set_xlim(-6, 6)
        ax.set_ylim(-1, 5)
        ax.axis('off') # 關閉座標軸，強調示意圖性質
        
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig) # V6: Must close figure
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')


    elif problem_type == 3: # Type 3 (Application of Perpendicular Bisector: Circumcenter - 外心座標)
        # 題目描述: 給定三角形ABC的三個頂點座標,求外心座標
        # 隨機化: 隨機生成三個非共線頂點座標
        
        A, B, C = _generate_non_collinear_points(min_coord=-7, max_coord=7, allow_fraction=False) # V13.0: -8,8 range

        # 計算兩條邊的中垂線方程式
        bisector_AB = _find_perpendicular_bisector_equation(A, B)
        bisector_BC = _find_perpendicular_bisector_equation(B, C)
        
        # 外心O為中垂線的交點
        O = _find_line_intersection(bisector_AB, bisector_BC)
        
        # Ensure circumcenter exists and is valid (avoid infinite or None)
        if O is None or (O[0] == float('inf") and O[1] == float("inf')):
            return generate(level) # Regenerate problem if lines are parallel/identical

        # V13.5: 整數優先
        ox, oy = O
        if isinstance(ox, (float, np.float64)) and ox.is_integer(): ox = int(ox)
        if isinstance(oy, (float, np.float64)) and oy.is_integer(): oy = int(oy)
        
        # V5 & V13.0: 座標顯示格式化
        question_template = r"已知 $\triangle ABC$ 的三個頂點座標分別為 $A({ax},{ay})$、$B({bx},{by})$、$C({cx},{cy})$。試求 $\triangle ABC$ 的外心座標。"
        question_text = question_template.replace("{ax}", _format_for_display(A[0])).replace("{ay}", _format_for_display(A[1])) \
                                       .replace("{bx}", _format_for_display(B[0])).replace("{by}", _format_for_display(B[1])) \
                                       .replace("{cx}", _format_for_display(C[0])).replace("{cy}", _format_for_display(C[1]))
        
        # V1.1 & V13.1: correct_answer must be pure data, format "x,y"
        correct_answer = f"{_format_for_display(ox)},{_format_for_display(oy)}"

        # Image generation: Draw the triangle and the calculated circumcenter.
        points_to_plot = [('A', A), ('B', B), ('C', C)]
        image_base64 = draw_coordinate_plane(points_with_labels=points_to_plot, circumcenter=(ox, oy), x_range=x_range, y_range=y_range)


    elif problem_type == 4: # Type 4 (Application of Angle Bisector: Incenter - 內心座標)
        # 題目描述: 給定三角形ABC的三個頂點座標,求內心座標
        # 隨機化: 隨機生成三個非共線頂點座標
        
        A, B, C = _generate_non_collinear_points(min_coord=-5, max_coord=5, allow_fraction=False) # Incenter calculation might produce fractions, integer vertices are better

        # Calculate side lengths
        a = _calculate_distance(B, C) # Side opposite A
        b = _calculate_distance(A, C) # Side opposite B
        c = _calculate_distance(A, B) # Side opposite C

        # Incenter coordinates formula: I = (aA + bB + cC) / (a+b+c)
        total_length = a + b + c
        ix = (a * A[0] + b * B[0] + c * C[0]) / total_length
        iy = (a * A[1] + b * B[1] + c * C[1]) / total_length
        
        # V13.5: 整數優先, 但內心座標常為分數。若非整數,則四捨五入至小數點後兩位
        if abs(ix - round(ix)) < 1e-9: # Check if very close to an integer
            ix = int(round(ix))
        else:
            ix = round(ix * 100) / 100.0 # Round to two decimal places
        
        if abs(iy - round(iy)) < 1e-9:
            iy = int(round(iy))
        else:
            iy = round(iy * 100) / 100.0
        
        # V5 & V13.0: 座標顯示格式化
        question_template = r"已知 $\triangle ABC$ 的三個頂點座標分別為 $A({ax},{ay})$、$B({bx},{by})$、$C({cx},{cy})$。試求 $\triangle ABC$ 的內心座標。"
        question_text = question_template.replace("{ax}", _format_for_display(A[0])).replace("{ay}", _format_for_display(A[1])) \
                                       .replace("{bx}", _format_for_display(B[0])).replace("{by}", _format_for_display(B[1])) \
                                       .replace("{cx}", _format_for_display(C[0])).replace("{cy}", _format_for_display(C[1]))
        
        # V1.1 & V13.1: correct_answer must be pure data, format "x,y"
        correct_answer = f"{_format_for_display(ix)},{_format_for_display(iy)}"

        # Image generation: Draw the triangle and the calculated incenter.
        points_to_plot = [('A', A), ('B', B), ('C', C)]
        image_base64 = draw_coordinate_plane(points_with_labels=points_to_plot, incenter=(ix, iy), x_range=x_range, y_range=y_range)
        

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "", # This field is for student's input, not used in generate
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    # V2.2: Robust Check Logic - Input Sanitization
    # Regex to remove LaTeX symbols, variable prefixes, and all whitespace
    # V13.6: Strict Regex for cleaning
    cleaned_user_answer = re.sub(r'[\$\s\(\)\{\}\[\]\\a-zA-Z=,;:\u4e00-\u9fff]', '', user_answer) # Remove common symbols, letters, Chinese chars
    cleaned_correct_answer = re.sub(r'[\$\s\(\)\{\}\[\]\\a-zA-Z=,;:\u4e00-\u9fff]', '', correct_answer)

    # V12.6: 數值序列比對
    # Split by comma for multiple values (e.g., coordinates)
    try:
        user_parts = [float(p) for p in cleaned_user_answer.split(',') if p.strip()]
        correct_parts = [float(p) for p in cleaned_correct_answer.split(',') if p.strip()]
    except ValueError:
        return False # If conversion to float fails, it's an invalid input

    # V13.6: Exact Check Logic (4-line check logic)
    if len(user_parts) != len(correct_parts):
        return False
    
    # Compare each part with a tolerance for float comparison
    for u, c in zip(user_parts, correct_parts):
        if not math.isclose(u, c, rel_tol=1e-6, abs_tol=1e-6): # V2.2: Support multiple math formats
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
                # 僅針對「文字反斜線+n」進行物理換行替換,不進行全局編碼轉換
                import re
                # 解決 r-string 導致的 \n 問題
                res['question_text'] = re.sub(r'\n', '\n', res['question_text'])
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則:若答案包含複雜運算符號,強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            # [V13.1 修復] 移除 '(' 與 ','，允許座標與數列使用純文字輸入
            triggers = ['^', '/', '|', '[', '{', '\\']
            
            # [V11.1 Refined] 僅在題目尚未包含提示時注入,避免重複堆疊
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
