# ==============================================================================
# ID: jh_數學2上_ApplicationsOfPythagoreanTheorem
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 75.38s | RAG: 5 examples
# Created At: 2026-01-18 21:36:38
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
        # import math  <-- Removed local import
        if math.isclose(float(u), float(c), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
    except: pass
    
    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", c_raw)}



import re
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
import numpy as np
from datetime import datetime

# V10.2 A, V13.0, V13.1, V13.5: 座標值生成與格式化
def _generate_coordinate_value(min_val, max_val, allow_fraction=False):
    """
    Generates a coordinate value, either integer or a simple fraction.
    Returns (float_val, (int_part, num, den, is_neg)).
    V13.1: Ensures proper fractions (numerator < denominator) if fractional.
    """
    is_neg = random.choice([True, False])
    int_part = random.randint(min_val, max_val)
    float_val = float(int_part)
    num, den = 0, 0

    if allow_fraction and random.random() < 0.3: # 30% chance of fraction
        # V13.1: numerator < denominator and denominator > 1
        num = random.randint(1, 3) # Simple numerators
        den = random.choice([2, 3, 4]) # Simple denominators
        while num >= den: # Ensure proper fraction
            num = random.randint(1, 3)
            den = random.choice([2, 3, 4])

        if int_part == 0:
            float_val = num / den
        else:
            float_val = abs(int_part) + (num / den)

        if is_neg and int_part == 0: # If it's a negative fraction like -1/2
             float_val = -float_val
        elif is_neg and int_part != 0: # If it's a negative mixed number like -1 1/2
            float_val = -float_val
        else: # Positive
            pass

    # V13.5: Ensure integers are stored as int
    if float_val.is_integer():
        float_val = int(float_val)
        int_part = int(float_val)
        num, den = 0, 0
        is_neg = float_val < 0

    return (float_val, (abs(int_part) if int_part != 0 else 0, num, den, is_neg))

def _format_coordinate(coord_data):
    """
    Formats the coordinate tuple (float_val, (int_part, num, den, is_neg)) into a string.
    V13.0, V13.5: Ensures integers are formatted as "(5, 4)" not "(5.0, 4.0)".
    """
    float_val, (int_part, num, den, is_neg) = coord_data
    
    if float_val.is_integer():
        return str(int(float_val))
    
    sign = "-" if is_neg else ""
    if int_part == 0:
        return r"\frac{{{n}}}{{{d}}}".replace("{n}", str(num)).replace("{d}", str(den))
    else:
        # V5.1, V5.2, V10.2 C: Use .replace for LaTeX safety
        return r"{s}{i}\frac{{{n}}}{{{d}}}".replace("{s}", sign).replace("{i}", str(int_part)).replace("{n}", str(num)).replace("{d}", str(den))

# V6, V10.2 D, V13.0, V13.1, V13.5, V13.6, V17: 座標平面繪圖函式
def draw_coordinate_plane(points, x_range=(-10, 10), y_range=(-10, 10), fixed_aspect=True, show_grid=True, show_axes=True, labels=None, line_segments=None, shapes=None, dpi=300):
    """
    Draws a coordinate plane with specified points and optional line segments/shapes.
    V6: Returns base64 string.
    V10.2 D: ax.set_aspect('equal'), origin '0' label, point labels with bbox.
    V13.0, V13.5: Symmetric axis range, xticks/yticks interval 1.
    V13.1, V13.5: ax.text only for labels, not coordinate values.
    V13.6: No arrowprops on axhline/axvline. Use ax.plot for arrows.
    V17.1: Ensures x-axis and y-axis have integer labels visible.
    """
    fig, ax = plt.subplots(figsize=(6, 6))

    ax.set_xlim(x_range)
    ax.set_ylim(y_range)

    if fixed_aspect:
        ax.set_aspect('equal', adjustable='box') # V10.2 D

    if show_grid:
        ax.grid(True, linestyle='--', alpha=0.6)

    if show_axes:
        # V13.6: Use ax.plot for arrows instead of arrowprops
        ax.plot(x_range, [0, 0], 'k-', lw=1) # x-axis line
        ax.plot([0, 0], y_range, 'k-', lw=1) # y-axis line
        # Arrows for axes (V13.6)
        ax.plot(x_range[1], 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
        ax.plot(0, y_range[1], "^k", transform=ax.get_xaxis_transform(), clip_on=False)

        # V17.1: Ensure major integer ticks are visible
        ax.set_xticks(np.arange(x_range[0], x_range[1] + 1, 1)) # V13.0
        ax.set_yticks(np.arange(y_range[0], y_range[1] + 1, 1))
        ax.tick_params(axis='both', which='major', labelsize=10)

        # Label origin '0' (V10.2 D)
        ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1))

    # Plot points (V10.2 D, V13.0, V13.1, V13.5)
    for i, (x, y, label) in enumerate(points):
        ax.plot(x, y, 'o', color='red', markersize=8, zorder=5)
        # V13.1, V13.5: ax.text only for labels, not coordinates
        ax.text(x, y + 0.5, label, color='black', ha='center', va='bottom', fontsize=12,
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1)) # V10.2 D: white glow

    # Draw line segments
    if line_segments:
        for seg in line_segments:
            x_coords = [p[0] for p in seg]
            y_coords = [p[1] for p in seg]
            ax.plot(x_coords, y_coords, 'b-', lw=1.5)

    # Draw shapes
    if shapes:
        for shape_type, shape_params in shapes:
            if shape_type == 'rectangle':
                (x, y, width, height) = shape_params
                rect = Rectangle((x, y), width, height, edgecolor='purple', facecolor='none', lw=2)
                ax.add_patch(rect)
            elif shape_type == 'polygon':
                poly = Polygon(shape_params, closed=True, edgecolor='purple', facecolor='none', lw=2)
                ax.add_patch(poly)
            # Add other shapes as needed

    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title('')

    plt.tight_layout()
    # Convert plot to base64 image
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=dpi) # Added dpi
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64

# Helper for drawing general geometric figures (reference only)
# Updated draw_geometric_figure to include bbox for labels and dpi
def draw_geometric_figure(elements, labels, image_size=(6,6), dpi=300):
    """
    Draws a generic geometric figure based on elements and labels.
    Elements can be lines (start_x, start_y, end_x, end_y), points, etc.
    Labels are for text on the figure.
    V5.3, V6, V17: Reference only, no direct answer leakage.
    V11.6: Added bbox for labels and dpi for resolution.
    """
    fig, ax = plt.subplots(figsize=image_size)
    ax.set_aspect('equal', adjustable='box')
    ax.set_axis_off() # Hide axes for general figures

    min_x, max_x, min_y, max_y = 0, 0, 0, 0

    for element_type, params in elements:
        if element_type == 'line':
            x1, y1, x2, y2 = params
            ax.plot([x1, x2], [y1, y2], 'k-', lw=1.5)
            min_x = min(min_x, x1, x2)
            max_x = max(max_x, x1, x2)
            min_y = min(min_y, y1, y2)
            max_y = max(max_y, y1, y2)
        elif element_type == 'point':
            x, y = params
            ax.plot(x, y, 'o', color='blue', markersize=5)
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
        elif element_type == 'dashed_line': # For heights or diagonals
            x1, y1, x2, y2 = params
            ax.plot([x1, x2], [y1, y2], 'k--', lw=1)
            min_x = min(min_x, x1, x2)
            max_x = max(max_x, x1, x2)
            min_y = min(min_y, y1, y2)
            max_y = max(max_y, y1, y2)
        elif element_type == 'right_angle': # For marking right angles
            x, y, corner_x, corner_y = params
            ax.plot([x, corner_x, corner_x, y], [corner_y, corner_y, y, corner_y], 'k-', lw=1) # Simple square corner
            
    # Add text labels (V13.1, V13.5: only label text, not values)
    for text, pos_x, pos_y, ha, va, color, fontsize in labels:
        ax.text(pos_x, pos_y, text, ha=ha, va=va, color=color, fontsize=fontsize,
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1)) # Added bbox for halo

    # Auto-adjust limits to fit all elements with some padding
    padding = 1
    ax.set_xlim(min_x - padding, max_x + padding)
    ax.set_ylim(min_y - padding, max_y + padding)

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=dpi)
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64


### **核心生成函式 (generate)**

def generate(level=1):
    problem_type = random.choice([1, 2, 3, 4, 5]) # V7.1: Randomly select problem type
    question_text = ""
    correct_answer = ""
    image_base64 = ""
    
    # V18.1, V18.2: Ensure grade-level and semantic alignment.
    # All problem types here are appropriate for G8 Pythagorean Theorem applications.

    if problem_type == 1:
        # Type 1: Maps to RAG Ex 1: Right-angled triangle, altitude to hypotenuse
        # 如右圖，直角三角形 ABC 中，∠ABC 為直角，且 AB=10，BC=24。若 BD 為斜邊上的高，則：⑴ 斜邊 AC 的長為多少？⑵ BD 的長為多少？ -> ⑴ 26, ⑵ $\frac{120}{13}$
        
        # Using Pythagorean triples for potentially "nicer" numbers, but not strictly required by RAG.
        # Example: (6, 8, 10), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29)
        triples = [
            (3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29)
        ]
        chosen_triple = random.choice(triples)
        scale = random.randint(1, 3) # Scale up for variety
        
        ab = chosen_triple[0] * scale
        bc = chosen_triple[1] * scale
        ac = chosen_triple[2] * scale # Hypotenuse

        # Calculate altitude BD
        # Area = 0.5 * AB * BC = 0.5 * AC * BD
        bd = (ab * bc) / ac
        
        question_text = r"如右圖，直角三角形 ABC 中，∠ABC 為直角，且 AB={ab_val}，BC={bc_val}。若 BD 為斜邊上的高，則：⑴ 斜邊 AC 的長為多少？⑵ BD 的長為多少？(答案請四捨五入至小數點後兩位，並以逗號分隔)" \
                        .replace("{ab_val}", str(ab)).replace("{bc_val}", str(bc))
        correct_answer = f"{round(ac, 2)}, {round(bd, 2)}"

        # Image generation for Type 1 (Right triangle with altitude)
        # Assuming B is at origin (0,0), A on y-axis, C on x-axis
        B_coords = (0, 0)
        A_coords = (0, ab)
        C_coords = (bc, 0)
        
        # Calculate D, the foot of the altitude from B to AC
        # Line AC: y - 0 = (ab - 0)/(0 - bc) * (x - bc) => y = (-ab/bc)(x - bc)
        # Line BD: y - 0 = (bc/ab) * (x - 0) => y = (bc/ab)x
        # Intersection: (bc/ab)x = (-ab/bc)(x - bc)
        # (bc^2)x = -ab^2 * x + ab^2 * bc
        # (bc^2 + ab^2)x = ab^2 * bc
        # ac^2 * x = ab^2 * bc => x = (ab^2 * bc) / ac^2
        # y = (bc/ab) * x = (bc/ab) * (ab^2 * bc) / ac^2 = (ab * bc^2) / ac^2
        D_x = (ab**2 * bc) / ac**2
        D_y = (ab * bc**2) / ac**2
        D_coords = (D_x, D_y)

        elements = [
            ('line', (A_coords[0], A_coords[1], B_coords[0], B_coords[1])), # AB
            ('line', (B_coords[0], B_coords[1], C_coords[0], C_coords[1])), # BC
            ('line', (C_coords[0], C_coords[1], A_coords[0], A_coords[1])), # AC
            ('dashed_line', (B_coords[0], B_coords[1], D_coords[0], D_coords[1])), # BD (altitude)
            ('right_angle', (B_coords[0]+0.5, B_coords[1], B_coords[0], B_coords[1]+0.5)) # Angle B
        ]
        labels = [
            ('A', A_coords[0]-0.5, A_coords[1], 'right', 'center', 'black', 12),
            ('B', B_coords[0]-0.5, B_coords[1]-0.5, 'right', 'top', 'black', 12),
            ('C', C_coords[0]+0.5, C_coords[1], 'left', 'center', 'black', 12),
            ('D', D_coords[0]+0.5, D_coords[1]-0.5, 'left', 'top', 'black', 12),
            (str(ab), A_coords[0]-0.5, B_coords[1] + ab/2, 'right', 'center', 'darkgreen', 12),
            (str(bc), B_coords[0] + bc/2, C_coords[1]-0.5, 'center', 'top', 'darkgreen', 12)
        ]
        image_base64 = draw_geometric_figure(elements, labels, image_size=(7,5))

    elif problem_type == 2:
        # Type 2: Maps to RAG Ex 2: Isosceles triangle height and area
        # 已知等腰三角形 ABC 中，AB=AC=13，BC=10，則：⑴ BC 上的高為多少？⑵ 等腰三角形 ABC 的面積為何？ -> ⑴ 12, ⑵ 60
        
        equal_side = random.randint(10, 20)
        base = random.randint(6, 2 * equal_side - 2)
        if base % 2 != 0: # Ensure base is even for simpler half-base calculation
            base += 1
        
        # Recalculate if invalid triangle (2 * equal_side > base)
        while 2 * equal_side <= base:
            equal_side = random.randint(10, 20)
            base = random.randint(6, 2 * equal_side - 2)
            if base % 2 != 0:
                base += 1

        half_base = base / 2
        height = math.sqrt(equal_side**2 - half_base**2)
        area = 0.5 * base * height
        
        question_text = r"已知等腰三角形 ABC 中，AB=AC={side_val}，BC={base_val}，則：⑴ BC 上的高為多少？⑵ 等腰三角形 ABC 的面積為何？(答案請四捨五入至小數點後兩位，並以逗號分隔)" \
                        .replace("{side_val}", str(equal_side)).replace("{base_val}", str(base))
        correct_answer = f"{round(height, 2)}, {round(area, 2)}"

        # Image generation for Type 2 (Isosceles triangle with height)
        A_coords = (0, height)
        B_coords = (-half_base, 0)
        C_coords = (half_base, 0)
        D_coords = (0, 0) # Foot of altitude

        elements = [
            ('line', (A_coords[0], A_coords[1], B_coords[0], B_coords[1])),
            ('line', (B_coords[0], B_coords[1], C_coords[0], C_coords[1])),
            ('line', (C_coords[0], C_coords[1], A_coords[0], A_coords[1])),
            ('dashed_line', (A_coords[0], A_coords[1], D_coords[0], D_coords[1])), # Height
            ('right_angle', (D_coords[0]+0.5, D_coords[1], D_coords[0], D_coords[1]+0.5)) # Angle ADC
        ]
        labels = [
            ('A', A_coords[0], A_coords[1]+0.5, 'center', 'bottom', 'black', 12),
            ('B', B_coords[0]-0.5, B_coords[1]-0.5, 'right', 'top', 'black', 12),
            ('C', C_coords[0]+0.5, C_coords[1]-0.5, 'left', 'top', 'black', 12),
            ('D', D_coords[0]-0.5, D_coords[1]-0.5, 'right', 'top', 'black', 12),
            (str(equal_side), (A_coords[0]+B_coords[0])/2 - 0.5, (A_coords[1]+B_coords[1])/2, 'right', 'center', 'darkgreen', 12),
            (str(equal_side), (A_coords[0]+C_coords[0])/2 + 0.5, (A_coords[1]+C_coords[1])/2, 'left', 'center', 'darkgreen', 12),
            (str(base), D_coords[0], D_coords[1]-0.5, 'center', 'top', 'darkgreen', 12)
        ]
        image_base64 = draw_geometric_figure(elements, labels, image_size=(7,5))

    elif problem_type == 3:
        # Type 3: Maps to RAG Ex 3: Equilateral triangle height and area
        # 已知一正三角形的邊長為 8，求此正三角形的高與面積分別為多少？ -> 高為 $4\sqrt{3}$，面積為 $16\sqrt{3}$
        
        side = random.randint(6, 15)
        height = (math.sqrt(3) / 2) * side
        area = (math.sqrt(3) / 4) * side**2
        
        question_text = r"已知一正三角形的邊長為 {side_val}，求此正三角形的高與面積分別為多少？(答案請四捨五入至小數點後兩位，並以逗號分隔)" \
                        .replace("{side_val}", str(side))
        correct_answer = f"{round(height, 2)}, {round(area, 2)}"

        # Image generation for Type 3 (Equilateral triangle with height)
        half_side = side / 2
        A_coords = (0, height)
        B_coords = (-half_side, 0)
        C_coords = (half_side, 0)
        D_coords = (0, 0) # Foot of altitude

        elements = [
            ('line', (A_coords[0], A_coords[1], B_coords[0], B_coords[1])),
            ('line', (B_coords[0], B_coords[1], C_coords[0], C_coords[1])),
            ('line', (C_coords[0], C_coords[1], A_coords[0], A_coords[1])),
            ('dashed_line', (A_coords[0], A_coords[1], D_coords[0], D_coords[1])), # Height
            ('right_angle', (D_coords[0]+0.5, D_coords[1], D_coords[0], D_coords[1]+0.5)) # Angle ADC
        ]
        labels = [
            ('A', A_coords[0], A_coords[1]+0.5, 'center', 'bottom', 'black', 12),
            ('B', B_coords[0]-0.5, B_coords[1]-0.5, 'right', 'top', 'black', 12),
            ('C', C_coords[0]+0.5, C_coords[1]-0.5, 'left', 'top', 'black', 12),
            ('D', D_coords[0]-0.5, D_coords[1]-0.5, 'right', 'top', 'black', 12),
            (str(side), (A_coords[0]+B_coords[0])/2 - 0.5, (A_coords[1]+B_coords[1])/2, 'right', 'center', 'darkgreen', 12),
            (str(side), (A_coords[0]+C_coords[0])/2 + 0.5, (A_coords[1]+C_coords[1])/2, 'left', 'center', 'darkgreen', 12),
            (str(side), D_coords[0], D_coords[1]-0.5, 'center', 'top', 'darkgreen', 12)
        ]
        image_base64 = draw_geometric_figure(elements, labels, image_size=(7,5))

    elif problem_type == 4:
        # Type 4: Maps to RAG Ex 4: Folding phone screen (diagonal difference)
        # 某摺疊手機螢幕大小即為對角線長度。摺疊前螢幕長寬為 6 吋、3 吋；摺疊後為 3 吋、3 吋。計算摺疊前手機的螢幕尺寸比摺疊後多了幾吋？ -> $(3\sqrt{5} - 3\sqrt{2})$ 吋
        
        # Unfolded dimensions
        l1 = random.randint(5, 10)
        w1 = random.randint(2, l1 - 1)
        
        # Folded dimensions (often square or smaller rectangle)
        l2 = random.randint(2, w1)
        w2 = l2 # Assume square after folding for simplicity, like example
        
        diag1 = math.sqrt(l1**2 + w1**2)
        diag2 = math.sqrt(l2**2 + w2**2)
        difference = diag1 - diag2
        
        question_text = r"某摺疊手機螢幕大小即為對角線長度。摺疊前螢幕長寬為 {l1_val} 吋、{w1_val} 吋；摺疊後為 {l2_val} 吋、{w2_val} 吋。計算摺疊前手機的螢幕尺寸比摺疊後多了幾吋？(答案請四捨五入至小數點後兩位)" \
                        .replace("{l1_val}", str(l1)).replace("{w1_val}", str(w1)) \
                        .replace("{l2_val}", str(l2)).replace("{w2_val}", str(w2))
        correct_answer = f"{round(difference, 2)}"

        # Image generation for Type 4 (Two rectangles/squares representing phone screens)
        scale = 0.5
        
        # Unfolded screen
        unfolded_points = [
            (0, w1*scale, 'A'), (l1*scale, w1*scale, 'B'),
            (l1*scale, 0, 'C'), (0, 0, 'D')
        ]
        unfolded_segments = [
            [(0, w1*scale), (l1*scale, w1*scale)],
            [(l1*scale, w1*scale), (l1*scale, 0)],
            [(l1*scale, 0), (0, 0)],
            [(0, 0), (0, w1*scale)],
            [(0, w1*scale), (l1*scale, 0)] # Diagonal
        ]
        unfolded_labels = [
            (str(l1) + ' 吋', l1*scale/2, w1*scale + 0.5, 'center', 'bottom', 'darkgreen', 10),
            (str(w1) + ' 吋', l1*scale + 0.5, w1*scale/2, 'left', 'center', 'darkgreen', 10),
            ('摺疊前', l1*scale/2, w1*scale + 1.5, 'center', 'bottom', 'black', 12)
        ]

        # Folded screen (offset to the right)
        offset_x = l1*scale + 2
        folded_points = [
            (offset_x, w2*scale, 'E'), (offset_x + l2*scale, w2*scale, 'F'),
            (offset_x + l2*scale, 0, 'G'), (offset_x, 0, 'H')
        ]
        folded_segments = [
            [(offset_x, w2*scale), (offset_x + l2*scale, w2*scale)],
            [(offset_x + l2*scale, w2*scale), (offset_x + l2*scale, 0)],
            [(offset_x + l2*scale, 0), (offset_x, 0)],
            [(offset_x, 0), (offset_x, w2*scale)],
            [(offset_x, w2*scale), (offset_x + l2*scale, 0)] # Diagonal
        ]
        folded_labels = [
            (str(l2) + ' 吋', offset_x + l2*scale/2, w2*scale + 0.5, 'center', 'bottom', 'darkgreen', 10),
            (str(w2) + ' 吋', offset_x + l2*scale + 0.5, w2*scale/2, 'left', 'center', 'darkgreen', 10),
            ('摺疊後', offset_x + l2*scale/2, w2*scale + 1.5, 'center', 'bottom', 'black', 12)
        ]
        
        all_elements = []
        for seg in unfolded_segments:
            all_elements.append(('line', (seg[0][0], seg[0][1], seg[1][0], seg[1][1])))
        for seg in folded_segments:
            all_elements.append(('line', (seg[0][0], seg[0][1], seg[1][0], seg[1][1])))

        all_labels = unfolded_labels + folded_labels
        
        image_base64 = draw_geometric_figure(all_elements, all_labels, image_size=(10,6))


    elif problem_type == 5:
        # Type 5: Maps to RAG Ex 5: Ladder against a wall (two parts)
        # 一支長 2.5 公尺的竹竿放在牆角處。⑴ 若牆底和竹竿底端距離為 1.5 公尺，則竹竿頂端距離牆底多少公尺？⑵ 若竹竿頂端往上移動了 0.4 公尺，那竹竿底端往牆底移動了多少公尺？ -> ⑴ 2 公尺, ⑵ 0.8 公尺
        
        # Use simple integer or .5 values for ladder problem realism
        ladder_len_options = [5.0, 7.5, 10.0, 12.5]
        ladder_len = random.choice(ladder_len_options)
        
        # Initial distance from wall (must be less than ladder_len)
        initial_dist_from_wall = random.choice([x for x in [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0] if x < ladder_len])
        
        initial_height = math.sqrt(ladder_len**2 - initial_dist_from_wall**2)
        
        # Move up amount (ensure new height is still less than ladder_len)
        max_move_up = ladder_len - initial_height - 0.1 # Small buffer
        if max_move_up < 0.1: # If already too high, adjust initial dist
            initial_dist_from_wall = random.choice([x for x in [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0] if x < ladder_len/2]) # force lower
            initial_height = math.sqrt(ladder_len**2 - initial_dist_from_wall**2)
            max_move_up = ladder_len - initial_height - 0.1

        move_up = round(random.uniform(0.2, min(0.8, max_move_up)), 1) # Ensure move_up is a simple decimal
        
        new_height = initial_height + move_up
        new_dist_from_wall = math.sqrt(ladder_len**2 - new_height**2)
        moved_dist = new_dist_from_wall - initial_dist_from_wall
        
        question_text = r"一支長 {ladder_val} 公尺的竹竿放在牆角處。⑴ 若牆底和竹竿底端距離為 {dist1_val} 公尺，則竹竿頂端距離牆底多少公尺？⑵ 若竹竿頂端往上移動了 {move_up_val} 公尺，那竹竿底端往牆底移動了多少公尺？(答案請四捨五入至小數點後兩位，並以逗號分隔)" \
                        .replace("{ladder_val}", str(ladder_len)) \
                        .replace("{dist1_val}", str(initial_dist_from_wall)) \
                        .replace("{move_up_val}", str(move_up))
        correct_answer = f"{round(initial_height, 2)}, {round(moved_dist, 2)}"

        # Image generation for Type 5 (Ladder against wall)
        # Initial position
        initial_ladder_top = (0, initial_height)
        initial_ladder_bottom = (initial_dist_from_wall, 0)

        # New position (dashed lines)
        new_ladder_top = (0, new_height)
        new_ladder_bottom = (new_dist_from_wall, 0)

        elements = [
            ('line', (0, 0, 0, max(initial_height, new_height) + 1)), # Wall
            ('line', (0, 0, max(initial_dist_from_wall, new_dist_from_wall) + 1, 0)), # Ground
            ('line', (initial_ladder_top[0], initial_ladder_top[1], initial_ladder_bottom[0], initial_ladder_bottom[1])), # Initial ladder
            ('dashed_line', (new_ladder_top[0], new_ladder_top[1], new_ladder_bottom[0], new_ladder_bottom[1])), # New ladder
            ('right_angle', (0.5, 0, 0, 0.5)) # Right angle at wall/ground
        ]
        labels = [
            ('牆', -0.5, (max(initial_height, new_height) + 1)/2, 'right', 'center', 'gray', 12),
            ('地面', (max(initial_dist_from_wall, new_dist_from_wall) + 1)/2, -0.5, 'center', 'top', 'gray', 12),
            (str(ladder_len) + 'm', initial_ladder_bottom[0]/2 - 0.5, initial_ladder_top[1]/2 + 0.5, 'right', 'bottom', 'darkgreen', 12), # Label ladder length
            (str(initial_dist_from_wall) + 'm', initial_ladder_bottom[0]/2, -0.5, 'center', 'top', 'blue', 10), # Initial dist label
            (str(round(initial_height, 2)) + 'm', -0.5, initial_ladder_top[1]/2, 'right', 'center', 'blue', 10), # Initial height label
            ('移動方向', (new_ladder_bottom[0] + initial_ladder_bottom[0])/2, -1, 'center', 'top', 'red', 10), # Indicate movement
            ('移動方向', -1, (new_ladder_top[1] + initial_ladder_top[1])/2, 'right', 'center', 'red', 10)
        ]
        image_base64 = draw_geometric_figure(elements, labels, image_size=(8,7))

    return {
        "question_text": question_text,
        "correct_answer": correct_answer, # V1.1, V1.2: Pure data
        "answer": "", # This field is typically for student's input or placeholder
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(), # V7.1
        "version": "1.0" # V7.1
    }





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
