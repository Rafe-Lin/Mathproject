# ==============================================================================
# ID: jh_數學1下_PointsLinesAnglesAndNotation
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 120.13s | RAG: 2 examples
# Created At: 2026-01-17 23:15:55
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
import io
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
import numpy as np
from fractions import Fraction # For robust fraction parsing in check and midpoint generation

# --- Whitelist for point labels (V13.6 Strict Labeling) ---
POINT_LABELS_WHITELIST = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'P', 'Q', 'R', 'S', 'O', 'X', 'Y', 'Z']

# --- Helper Functions ---

def _generate_coordinate_value(min_val, max_val, allow_fraction=False):
    """
    [V10.2 A Data Structure Locking], [V13.1 No Improper Fractions], [V13.0 Coordinate Selection Control], [V13.5 Integer Preference]
    Generates a coordinate value (float or int) and its LaTeX formatting components.
    """
    if random.random() < 0.7 or not allow_fraction: # 70% chance for integer, or if fractions not allowed
        float_val = random.randint(min_val, max_val)
        return (int(float_val), (int(abs(float_val)), 0, 0, float_val < 0))
    else:
        # Generate fraction
        int_p_abs = random.randint(0, max(abs(min_val), abs(max_val))) # Absolute integer part
        den = random.randint(2, 5) # Denominator must be > 1
        num = random.randint(1, den - 1) # Numerator must be < denominator (true fraction)
        
        # Ensure positive num/den for calculation, apply sign later
        float_val_abs = int_p_abs + num / den
        
        is_neg = random.random() < 0.5
        float_val = -float_val_abs if is_neg else float_val_abs
        
        # V13.5 Integer Preference: If by chance it results in an integer, convert to int type
        if float_val.is_integer():
            return (int(float_val), (int(abs(float_val)), 0, 0, float_val < 0))

        # int_part for LaTeX formatting should be absolute value's integer part
        return (float_val, (int_p_abs, num, den, is_neg))


def _format_coordinate_for_latex(coord_data):
    """
    [V10.2 C LaTeX Template], [V13.0 Format Precision], [V13.1 No Improper Fractions]
    Formats (int_part, num, den, is_neg) into a LaTeX string.
    """
    int_part_abs, num, den, is_neg = coord_data
    
    if num == 0: # It's an integer
        return str(int_part_abs) if not is_neg else "-" + str(int_part_abs)
    else: # It's a fraction (possibly mixed)
        latex_str = ""
        
        if is_neg:
            latex_str += "-"
            
        if int_part_abs != 0:
            latex_str += str(int_part_abs)
        
        # [LaTeX 單層大括號]
        fraction_part = r"\frac{n}{d}".replace("{n}", str(num)).replace("{d}", str(den))
        latex_str += fraction_part
        
        return latex_str


def draw_coordinate_plane(points_with_labels, x_range, y_range, title="", plot_arrows=True, is_number_line=False):
    """
    [V10.2 D Visual Consistency], [V10.2 B Anti-Leak Protocol], [V13.0 Coordinate Teaching Logic],
    [V13.1 Label Purity], [V13.5 Label Isolation], [V13.6 API Hardened Spec], [CRITICAL RULE: Visual Solvability]
    Generates a Base64 encoded PNG image of a coordinate plane.
    """
    fig, ax = plt.subplots(figsize=(8, 8), dpi=300) # ULTRA VISUAL STANDARDS: dpi=300
    ax.set_aspect('equal') # ULTRA VISUAL STANDARDS: ax.set_aspect('equal')
    
    # [V13.0 Grid Alignment] & [CRITICAL RULE: Visual Solvability] & [強制顯示刻度 (Mandatory Axis Ticks)]
    ax.set_xlim(x_range)
    ax.set_ylim(y_range)
    
    # [Mandatory Ticks] Force integer ticks for readability
    start_x, end_x = math.floor(x_range[0]), math.ceil(x_range[1])
    start_y, end_y = math.floor(y_range[0]), math.ceil(y_range[1])
    
    # Ensure reasonable number of ticks if range is large, otherwise every integer
    if end_x - start_x <= 20:
        x_ticks = np.arange(start_x, end_x + 1)
        ax.set_xticks(x_ticks)
    if end_y - start_y <= 20:
        y_ticks = np.arange(start_y, end_y + 1)
        ax.set_yticks(y_ticks)

    ax.tick_params(axis='both', which='major', labelsize=14) # Increased fontsize

    # [網格線輔助 (Grid Lines)]
    ax.grid(True, linestyle=':', alpha=0.7)
    
    # [座標軸優化 (Axis Visibility)]
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    
    # [V13.6 Arrow Ban] - using ax.plot for arrows
    if plot_arrows:
        ax.plot(x_range[1], 0, ">k", clip_on=False, markersize=8) # X-axis positive arrow
        ax.plot(0, y_range[1], "^k", clip_on=False, markersize=8) # Y-axis positive arrow
    
    # [V10.2 D Origin Label]
    # Adjust position slightly to avoid overlap with axis lines/ticks
    ax.text(0.1, 0.1, '0', fontsize=18, fontweight='bold', ha='left', va='bottom')
    
    # Plot points and labels
    for x, y, label in points_with_labels:
        ax.plot(x, y, 'o', color='red', markersize=8) # Increased markersize & Red color
        # [V13.5 Label Isolation] & [V13.6 Strict Labeling]
        # [ULTRA VISUAL STANDARDS: Label Halo]
        ax.text(x + 0.4, y + 0.4, label, fontsize=16, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7))
        
    ax.set_title(title)
    ax.set_xlabel('X', loc='right') # Place label at the end of the axis
    ax.set_ylabel('Y', loc='top')   # Place label at the end of the axis

    # Special case for number line (Type 3 Subtype B)
    if is_number_line:
        ax.set_yticks([]) # Hide Y-axis ticks
        ax.set_ylabel('') # Hide Y-axis label
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.set_ylim(-1, 1) # Ensure minimal y-range to make it a flat line
        ax.axhline(0, color='black', linewidth=1) # Redraw X-axis as the number line
        if plot_arrows: # For number line, only X-axis arrows
            ax.plot(x_range[1], 0, ">k", clip_on=False, markersize=8)
            ax.plot(x_range[0], 0, "<k", clip_on=False, markersize=8) # Left arrow for number line

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def draw_geometry_figure(points_with_labels, lines_to_draw, title="", plot_rays=None, plot_lines=None):
    """
    [V13.5 Label Isolation], [V13.6 Strict Labeling]
    Draws a generic geometric figure with points, segments, rays, and lines.
    """
    fig, ax = plt.subplots(figsize=(8, 8), dpi=300) # ULTRA VISUAL STANDARDS: dpi=300
    ax.set_aspect('equal') # ULTRA VISUAL STANDARDS: ax.set_aspect('equal')
    
    all_x = [p[0] for p in points_with_labels]
    all_y = [p[1] for p in points_with_labels]
    
    # Extend bounds for lines, rays, etc.
    if lines_to_draw:
        for (x1, y1), (x2, y2) in lines_to_draw:
            all_x.extend([x1, x2])
            all_y.extend([y1, y2])
    if plot_rays:
        for (x1, y1), (x2, y2) in plot_rays:
            all_x.extend([x1, x2])
            all_y.extend([y1, y2])
    if plot_lines:
        for (x1, y1), (x2, y2) in plot_lines:
            all_x.extend([x1, x2])
            all_y.extend([y1, y2])

    # Calculate padding based on data spread or default if no data
    # Calculate padding based on data spread or default if no data
    if all_x and all_y:
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        x_range_len = max_x - min_x
        y_range_len = max_y - min_y
        
        # [Dynamic Scaling] Add 20% padding
        # Ensure minimum padding if range is 0 (single point)
        padding_x = max(1.5, x_range_len * 0.2)
        padding_y = max(1.5, y_range_len * 0.2)
        
        ax.set_xlim(min_x - padding_x, max_x + padding_x)
        ax.set_ylim(min_y - padding_y, max_y + padding_y)
    else:
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)

    ax.axis('off') # Hide coordinate axes for general geometry figures
    
    # Draw segments
    for (x1, y1), (x2, y2) in lines_to_draw:
        ax.plot([x1, x2], [y1, y2], 'k-', lw=2) # Increased linewidth
    
    # Draw rays
    if plot_rays:
        for (x_start, y_start), (x_through, y_through) in plot_rays:
            # Calculate direction vector
            dx, dy = x_through - x_start, y_through - y_start
            
            # Extend the ray significantly
            current_xlim = ax.get_xlim()
            current_ylim = ax.get_ylim()
            
            # Use max length from current plot limits
            # Use max length from current plot limits
            # [Fix] Extend significantly enough to look like a ray, but not infinite
            view_w = ax.get_xlim()[1] - ax.get_xlim()[0]
            view_h = ax.get_ylim()[1] - ax.get_ylim()[0]
            max_len = max(view_w, view_h) * 1.5
            
            if dx == 0 and dy == 0: # Avoid division by zero if points are identical
                continue
            
            # Normalize direction vector
            length = math.sqrt(dx**2 + dy**2)
            dx_norm, dy_norm = dx / length, dy / length
            
            # Extend towards the edge of the plot
            x_end = x_start + dx_norm * max_len
            y_end = y_start + dy_norm * max_len
            
            ax.plot([x_start, x_end], [y_start, y_end], 'k-', lw=2)
            # Add an arrowhead
            ax.plot(x_end, y_end, '>k', markersize=8, clip_on=False)
            
    # Draw lines (extend in both directions)
    if plot_lines:
        for (x1, y1), (x2, y2) in plot_lines:
            # Calculate direction vector
            dx, dy = x2 - x1, y2 - y1
            
            if dx == 0 and dy == 0:
                continue
            
            # Extend the line significantly in both directions
            current_xlim = ax.get_xlim()
            current_ylim = ax.get_ylim()
            
            view_w = ax.get_xlim()[1] - ax.get_xlim()[0]
            view_h = ax.get_ylim()[1] - ax.get_ylim()[0]
            max_len = max(view_w, view_h) * 1.5
            
            # Normalize direction vector
            length = math.sqrt(dx**2 + dy**2)
            dx_norm, dy_norm = dx / length, dy / length
            
            # Extend start and end points
            x_start_extended = x1 - dx_norm * max_len
            y_start_extended = y1 - dy_norm * max_len
            x_end_extended = x1 + dx_norm * max_len
            y_end_extended = y1 + dy_norm * max_len
            
            ax.plot([x_start_extended, x_end_extended], [y_start_extended, y_end_extended], 'k-', lw=2)
            # Add arrowheads at both ends
            ax.plot(x_start_extended, y_start_extended, '<k', markersize=8, clip_on=False)
            ax.plot(x_end_extended, y_end_extended, '>k', markersize=8, clip_on=False)

    # Plot points and labels last to ensure they are on top
    for x, y, label in points_with_labels:
        ax.plot(x, y, 'o', color='red', markersize=8, zorder=5) # Increased size
        # [V13.5 Label Isolation] & [V13.6 Strict Labeling]
        # [ULTRA VISUAL STANDARDS: Label Halo]
        ax.text(x + 0.4, y + 0.4, label, fontsize=16, fontweight='bold', zorder=6,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7))
        
    ax.set_title(title)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


# --- Problem Type Generators ---

def generate_type1_identification(level):
    version = 1.0
    created_at = datetime.now()

    # Generate 3-4 random points
    num_points = random.randint(3, 4)
    point_labels = random.sample(POINT_LABELS_WHITELIST, num_points)
    
    # Ensure points are somewhat spread out but can form lines
    coords = []
    for _ in range(num_points):
        x = random.randint(-4, 4)
        y = random.randint(-4, 4)
        coords.append((x, y))
    
    # Ensure points are distinct
    unique_coords = []
    for i, (x, y) in enumerate(coords):
        if (x, y) not in [(uc[0], uc[1]) for uc in unique_coords]:
            unique_coords.append((x, y, point_labels[len(unique_coords)]))
        if len(unique_coords) >= num_points:
            break
    
    # If not enough unique points, regenerate or simplify
    while len(unique_coords) < 3: # Ensure at least 3 points for line/ray/segment if needed
        x = random.randint(-4, 4)
        y = random.randint(-4, 4)
        if (x, y) not in [(uc[0], uc[1]) for uc in unique_coords]:
            unique_coords.append((x, y, point_labels[len(unique_coords)]))
    
    # Randomly choose problem type: point, segment, ray, line
    problem_choice = random.choice(['point', 'segment', 'ray', 'line'])
    
    question_text = ""
    correct_answer = ""
    solution_text = ""
    lines_to_draw_segments = []
    lines_to_draw_rays = []
    lines_to_draw_lines = []

    if problem_choice == 'point':
        chosen_point = random.choice(unique_coords)
        question_text = r"請寫出圖中的點名稱。例如：$A$。"
        correct_answer = chosen_point[2]
        solution_text = r"點"+chosen_point[2]
        # Image will just show points
    elif problem_choice == 'segment':
        p1, p2 = random.sample(unique_coords, 2)
        question_text = r"請寫出圖中連接點 $"+p1[2]+r"$ 和點 $"+p2[2]+r"$ 的線段名稱。例如：線段 $AB$。"
        correct_answer = p1[2] + p2[2] # "AB"
        solution_text = r"線段"+p1[2]+p2[2]+r" 或 線段"+p2[2]+p1[2]
        lines_to_draw_segments.append(((p1[0], p1[1]), (p2[0], p2[1])))
    elif problem_choice == 'ray':
        p_start, p_through = random.sample(unique_coords, 2)
        while p_start == p_through: # Ensure distinct points
             p_start, p_through = random.sample(unique_coords, 2)
        question_text = r"請寫出圖中從點 $"+p_start[2]+r"$ 開始，經過點 $"+p_through[2]+r"$ 的射線名稱。例如：射線 $AB$。"
        correct_answer = p_start[2] + p_through[2] + "射線" # "AB射線"
        solution_text = r"射線"+p_start[2]+p_through[2]
        lines_to_draw_rays.append(((p_start[0], p_start[1]), (p_through[0], p_through[1])))
    elif problem_choice == 'line':
        p1, p2 = random.sample(unique_coords, 2)
        while p1 == p2:
            p1, p2 = random.sample(unique_coords, 2)
        question_text = r"請寫出圖中通過點 $"+p1[2]+r"$ 和點 $"+p2[2]+r"$ 的直線名稱。例如：直線 $AB$。"
        correct_answer = p1[2] + p2[2] + "直線" # "AB直線"
        solution_text = r"直線"+p1[2]+p2[2]+r" 或 直線"+p2[2]+p1[2]
        lines_to_draw_lines.append(((p1[0], p1[1]), (p2[0], p2[1])))

    image_base64 = draw_geometry_figure(unique_coords, lines_to_draw_segments, 
                                        plot_rays=lines_to_draw_rays, plot_lines=lines_to_draw_lines, 
                                        title="幾何圖形識別")
    
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "solution_text": solution_text,
        "image_base64": image_base64,
        "created_at": created_at.isoformat(),
        "version": version,
    }

def generate_type2_angles(level):
    version = 1.0
    created_at = datetime.now()

    # Generate 3 non-collinear points
    # Vertex in the middle, two other points forming arms
    labels = random.sample(POINT_LABELS_WHITELIST, 3)
    p_vertex_label = labels[0]
    p_arm1_label = labels[1]
    p_arm2_label = labels[2]

    # Ensure non-collinearity for angle formation
    while True:
        p_vertex_x = random.randint(-3, 3)
        p_vertex_y = random.randint(-3, 3)
        p_arm1_x = random.randint(-5, 5)
        p_arm1_y = random.randint(-5, 5)
        p_arm2_x = random.randint(-5, 5)
        p_arm2_y = random.randint(-5, 5)

        # Ensure points are distinct
        if (p_vertex_x, p_vertex_y) == (p_arm1_x, p_arm1_y) or \
           (p_vertex_x, p_vertex_y) == (p_arm2_x, p_arm2_y) or \
           (p_arm1_x, p_arm1_y) == (p_arm2_x, p_arm2_y):
            continue
        
        # Check for collinearity: slope(vertex, arm1) != slope(vertex, arm2)
        # Avoid division by zero by checking vertical/horizontal lines
        is_collinear = False
        # Calculate cross product to check collinearity: (x1-x0)*(y2-y0) - (x2-x0)*(y1-y0) == 0
        val = (p_arm1_x - p_vertex_x) * (p_arm2_y - p_vertex_y) - \
              (p_arm2_x - p_vertex_x) * (p_arm1_y - p_vertex_y)
        if abs(val) < 1e-6: # Check if cross product is close to zero
            is_collinear = True

        if not is_collinear:
            break

    points_coords = [
        (p_vertex_x, p_vertex_y, p_vertex_label),
        (p_arm1_x, p_arm1_y, p_arm1_label),
        (p_arm2_x, p_arm2_y, p_arm2_label)
    ]

    # Draw rays from vertex through arm points
    lines_to_draw_rays = [
        ((p_vertex_x, p_vertex_y), (p_arm1_x, p_arm1_y)),
        ((p_vertex_x, p_vertex_y), (p_arm2_x, p_arm2_y))
    ]

    question_text = r"請寫出圖中以點 $"+p_vertex_label+r"$ 為頂點的角度名稱（使用三個字母表示）。例如：$\angle ABC$。"
    correct_answer = r"∠"+p_arm1_label+p_vertex_label+p_arm2_label
    solution_text = r"$\angle "+p_arm1_label+p_vertex_label+p_arm2_label+r"$ 或 $\angle "+p_arm2_label+p_vertex_label+p_arm1_label+r"$"

    image_base64 = draw_geometry_figure(points_coords, [], plot_rays=lines_to_draw_rays, title="角度命名")
    
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "solution_text": solution_text,
        "image_base64": image_base64,
        "created_at": created_at.isoformat(),
        "version": version,
    }

def generate_type3_segment_length(level):
    version = 1.0
    created_at = datetime.now()

    subtype_choice = random.choice(['coordinate_distance', 'segment_addition'])

    if subtype_choice == 'coordinate_distance':
        label1, label2 = random.sample(POINT_LABELS_WHITELIST, 2)
        
        # Generate coordinates, allowing fractions for more challenge
        x1_data = _generate_coordinate_value(-7, 7, allow_fraction=True)
        y1_data = _generate_coordinate_value(-7, 7, allow_fraction=True)
        x2_data = _generate_coordinate_value(-7, 7, allow_fraction=True)
        y2_data = _generate_coordinate_value(-7, 7, allow_fraction=True)

        x1, _ = x1_data
        y1, _ = y1_data
        x2, _ = x2_data
        y2, _ = y2_data

        # Ensure points are distinct
        while (x1 == x2 and y1 == y2):
            x2_data = _generate_coordinate_value(-7, 7, allow_fraction=True)
            y2_data = _generate_coordinate_value(-7, 7, allow_fraction=True)
            x2, _ = x2_data
            y2, _ = y2_data

        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Round to 2 decimal places for answer, but keep float for comparison
        correct_answer_val = round(distance, 2)

        question_text_template = r"已知點 $"+label1+r"({x1_latex}, {y1_latex})$ 和 $"+label2+r"({x2_latex}, {y2_latex})$，求線段 $"+label1+label2+r"$ 的長度。答案請四捨五入至小數點後兩位。"
        question_text = question_text_template.replace("{x1_latex}", _format_coordinate_for_latex(x1_data[1])) \
                                              .replace("{y1_latex}", _format_coordinate_for_latex(y1_data[1])) \
                                              .replace("{x2_latex}", _format_coordinate_for_latex(x2_data[1])) \
                                              .replace("{y2_latex}", _format_coordinate_for_latex(y2_data[1]))
        
        correct_answer = str(correct_answer_val)
        solution_text = r"線段 $"+label1+label2+r"$ 的長度為 $"+str(correct_answer_val)+r"$"
        
        image_base64 = draw_coordinate_plane([(x1, y1, label1), (x2, y2, label2)], (-8, 8), (-8, 8), 
                                             title="線段長度計算 (座標距離)")

    else: # subtype_choice == 'segment_addition'
        labels = random.sample(POINT_LABELS_WHITELIST, 3)
        A_label, B_label, C_label = labels[0], labels[1], labels[2]

        # Generate collinear points on a number line
        # Ensure B is between A and C
        coord_A = random.randint(-8, 0)
        coord_C = random.randint(1, 8)
        coord_B = random.randint(coord_A + 1, coord_C - 1)
        
        # Ensure A, B, C are distinct
        while coord_A == coord_B or coord_B == coord_C or coord_A == coord_C:
            coord_A = random.randint(-8, 0)
            coord_C = random.randint(1, 8)
            coord_B = random.randint(coord_A + 1, coord_C - 1)

        points_on_line = [(coord_A, 0, A_label), (coord_B, 0, B_label), (coord_C, 0, C_label)]
        
        # Randomly ask for AB, BC, or AC
        question_type = random.choice(['AB_plus_BC', 'AC_minus_AB', 'AC_minus_BC'])

        len_AB = abs(coord_B - coord_A)
        len_BC = abs(coord_C - coord_B)
        len_AC = abs(coord_C - coord_A)

        if question_type == 'AB_plus_BC':
            question_text = r"在數線上，已知 $A, B, C$ 三點，$AB = "+str(len_AB)+r"$，$BC = "+str(len_BC)+r"$，且 $B$ 介於 $A, C$ 之間，求 $AC$ 的長度。"
            correct_answer_val = len_AB + len_BC
            solution_text = r"$AC = AB + BC = "+str(len_AB)+r" + "+str(len_BC)+r" = "+str(correct_answer_val)+r"$"
        elif question_type == 'AC_minus_AB':
            question_text = r"在數線上，已知 $A, B, C$ 三點，$AC = "+str(len_AC)+r"$，$AB = "+str(len_AB)+r"$，且 $B$ 介於 $A, C$ 之間，求 $BC$ 的長度。"
            correct_answer_val = len_AC - len_AB
            solution_text = r"$BC = AC - AB = "+str(len_AC)+r" - "+str(len_AB)+r" = "+str(correct_answer_val)+r"$"
        else: # 'AC_minus_BC'
            question_text = r"在數線上，已知 $A, B, C$ 三點，$AC = "+str(len_AC)+r"$，$BC = "+str(len_BC)+r"$，且 $B$ 介於 $A, C$ 之間，求 $AB$ 的長度。"
            correct_answer_val = len_AC - len_BC
            solution_text = r"$AB = AC - BC = "+str(len_AC)+r" - "+str(len_BC)+r" = "+str(correct_answer_val)+r"$"
        
        correct_answer = str(correct_answer_val)

        # For number line, x_range should cover all points
        min_coord = min(coord_A, coord_B, coord_C)
        max_coord = max(coord_A, coord_B, coord_C)
        x_display_range = (min_coord - 2, max_coord + 2) # Add padding
        
        image_base64 = draw_coordinate_plane(points_on_line, x_display_range, (-1, 1), 
                                             title="線段長度計算 (數線)", plot_arrows=True, is_number_line=True)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "solution_text": solution_text,
        "image_base64": image_base64,
        "created_at": created_at.isoformat(),
        "version": version,
    }

def generate_type4_midpoint(level):
    version = 1.0
    created_at = datetime.now()

    label1, label2, mid_label = random.sample(POINT_LABELS_WHITELIST, 3)
    
    # Generate end points, allowing fractions
    x1_data = _generate_coordinate_value(-7, 7, allow_fraction=True)
    y1_data = _generate_coordinate_value(-7, 7, allow_fraction=True)
    x2_data = _generate_coordinate_value(-7, 7, allow_fraction=True)
    y2_data = _generate_coordinate_value(-7, 7, allow_fraction=True)

    x1, _ = x1_data
    y1, _ = y1_data
    x2, _ = x2_data
    y2, _ = y2_data

    # Ensure distinct points
    while (x1 == x2 and y1 == y2):
        x2_data = _generate_coordinate_value(-7, 7, allow_fraction=True)
        y2_data = _generate_coordinate_value(-7, 7, allow_fraction=True)
        x2, _ = x2_data
        y2, _ = y2_data

    # Calculate midpoint
    mid_x_float = (x1 + x2) / 2
    mid_y_float = (y1 + y2) / 2

    # Prepare midpoint coordinates for LaTeX formatting.
    def _parse_float_to_coord_data_for_latex(val):
        # Using Fraction to accurately represent the float as a fraction
        f_val = Fraction(val).limit_denominator(100) # Limit denominator for K12 context
        
        is_neg = f_val < 0
        abs_f_val = abs(f_val)
        
        int_part_abs = int(abs_f_val)
        frac_part_abs = abs_f_val - int_part_abs
        
        if frac_part_abs == 0:
            return (int_part_abs, 0, 0, is_neg)
        
        num = frac_part_abs.numerator
        den = frac_part_abs.denominator
        
        return (int_part_abs, num, den, is_neg)

    mid_x_data_for_latex = _parse_float_to_coord_data_for_latex(mid_x_float)
    mid_y_data_for_latex = _parse_float_to_coord_data_for_latex(mid_y_float)
    
    question_text_template = r"已知線段 $"+label1+label2+r"$ 的兩端點為 $"+label1+r"({x1_latex}, {y1_latex})$ 和 $"+label2+r"({x2_latex}, {y2_latex})$，求該線段中點 $"+mid_label+r"$ 的座標。"
    question_text = question_text_template.replace("{x1_latex}", _format_coordinate_for_latex(x1_data[1])) \
                                          .replace("{y1_latex}", _format_coordinate_for_latex(y1_data[1])) \
                                          .replace("{x2_latex}", _format_coordinate_for_latex(x2_data[1])) \
                                          .replace("{y2_latex}", _format_coordinate_for_latex(y2_data[1]))
    
    # [V13.1 答案格式標準化] for coordinates
    correct_answer = r"{mid_label}({mid_x_ans},{mid_y_ans})".replace("{mid_label}", mid_label) \
                                                          .replace("{mid_x_ans}", _format_coordinate_for_latex(mid_x_data_for_latex)) \
                                                          .replace("{mid_y_ans}", _format_coordinate_for_latex(mid_y_data_for_latex))
    
    solution_text = r"中點 $"+mid_label+r"$ 的座標為 $({mid_x_sol}, {mid_y_sol})$" \
                        .replace("{mid_x_sol}", _format_coordinate_for_latex(mid_x_data_for_latex)) \
                        .replace("{mid_y_sol}", _format_coordinate_for_latex(mid_y_data_for_latex))
    
    image_base64 = draw_coordinate_plane([(x1, y1, label1), (x2, y2, label2), (mid_x_float, mid_y_float, mid_label)], 
                                         (-8, 8), (-8, 8), title="中點座標")
    
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "solution_text": solution_text,
        "image_base64": image_base64,
        "created_at": created_at.isoformat(),
        "version": version,
    }

def generate_type5_coordinate_plane(level):
    version = 1.0
    created_at = datetime.now()

    subtype_choice = random.choice(['plot_point', 'read_coordinate'])
    
    point_label = random.choice(POINT_LABELS_WHITELIST)
    
    # Generate coordinates, allowing fractions
    x_coord_data = _generate_coordinate_value(-7, 7, allow_fraction=True)
    y_coord_data = _generate_coordinate_value(-7, 7, allow_fraction=True)

    x_coord, _ = x_coord_data
    y_coord, _ = y_coord_data

    question_text = ""
    correct_answer = ""
    solution_text = ""
    image_base64 = ""

    if subtype_choice == 'plot_point':
        question_text_template = r"請在座標平面上標示出點 $"+point_label+r"({x_latex}, {y_latex})$。"
        question_text = question_text_template.replace("{x_latex}", _format_coordinate_for_latex(x_coord_data[1])) \
                                              .replace("{y_latex}", _format_coordinate_for_latex(y_coord_data[1]))
        
        # [V10.2 B 標點題防洩漏協定]: points_with_labels must be []
        image_base64 = draw_coordinate_plane([], (-8, 8), (-8, 8), title="標示點")
    else: # 'read_coordinate'
        question_text = r"請寫出座標平面上點 $"+point_label+r"$ 的座標。"
        image_base64 = draw_coordinate_plane([(x_coord, y_coord, point_label)], (-8, 8), (-8, 8), title="讀取座標")
    
    # [V13.1 答案格式標準化] for coordinates
    correct_answer = r"{label}({x_ans},{y_ans})".replace("{label}", point_label) \
                                                .replace("{x_ans}", _format_coordinate_for_latex(x_coord_data[1])) \
                                                .replace("{y_ans}", _format_coordinate_for_latex(y_coord_data[1]))
    
    solution_text = r"點 $"+point_label+r"$ 的座標為 $({x_sol}, {y_sol})$" \
                        .replace("{x_sol}", _format_coordinate_for_latex(x_coord_data[1])) \
                        .replace("{y_sol}", _format_coordinate_for_latex(y_coord_data[1]))
    
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "solution_text": solution_text,
        "image_base64": image_base64,
        "created_at": created_at.isoformat(),
        "version": version,
    }


# --- Main Functions ---

def generate(level=1):
    problem_types = {
        "type1": generate_type1_identification,
        "type2": generate_type2_angles,
        "type3": generate_type3_segment_length,
        "type4": generate_type4_midpoint,
        "type5": generate_type5_coordinate_plane,
    }
    
    chosen_type = random.choice(list(problem_types.keys()))
    
    return problem_types[chosen_type](level)



    # [CRITICAL CODING STANDARDS: Verification & Stability]
    # This check function implements specific logic for geometric questions (coordinates, angles, lines)
    # as allowed by "除非有特殊幾何需求，否則..." rule.

    # Helper to clean and parse LaTeX-formatted coordinate strings
    def _clean_and_parse_latex_coords(raw_string):
        s = str(raw_string).strip().lower()
        s = re.sub(r'^[a-z]+=', '', s) # Remove variable prefixes like "p="
        s = s.replace("$", "").replace(" ", "") # Remove math delimiters and spaces
        s = s.replace("∠", "") # Remove angle symbol

        # Convert LaTeX fractions to a parsable format (e.g., \frac{1}{2} -> 1/2)
        s = re.sub(r'\\frac\{(\-?\d+)\}\{(\-?\d+)\}', r'\1/\2', s)
        # Convert LaTeX mixed fractions to a parsable format (e.g., 1\frac{1}{2} -> 1_1/2)
        s = re.sub(r'(\d+)\\frac\{(\-?\d+)\}\{(\-?\d+)\}', r'\1_\2/\3', s)
        
        s = s.replace("{", "").replace("}", "").replace("\\", "") # Remove remaining LaTeX braces and backslashes

        # Now parse coordinates like A(x,y) where x,y can be integers, decimals, or fractions (1/2 or 1_1/2)
        # This regex handles A(x,y) where x,y can contain '.', '/', or '_' for fractions
        coord_match = re.match(r'([a-z]?)\((-?\d+(\.\d+)?(_\d+/\d+)?)?,(-?\d+(\.\d+)?(_\d+/\d+)?)\)', s)
        
        if coord_match:
            label = coord_match.group(1)
            x_str = coord_match.group(2)
            y_str = coord_match.group(5)

            def parse_number_string(num_str):
                if num_str is None: return None
                num_str = num_str.strip()
                if '_' in num_str: # Mixed fraction (e.g., "1_1/2")
                    parts = num_str.split('_')
                    whole = float(parts[0])
                    frac_parts = parts[1].split('/')
                    num = float(frac_parts[0])
                    den = float(frac_parts[1])
                    return whole + num/den if whole >= 0 else whole - num/den
                elif '/' in num_str: # Pure fraction (e.g., "1/2")
                    parts = num_str.split('/')
                    # Use fractions.Fraction for robust parsing of "1/2", "-1/2"
                    try:
                        return float(Fraction(parts[0]) / Fraction(parts[1]))
                    except (ValueError, ZeroDivisionError):
                        return None
                else: # Integer or decimal (e.g., "3", "3.5")
                    try:
                        return float(num_str)
                    except ValueError:
                        return None
            
            x_val = parse_number_string(x_str)
            y_val = parse_number_string(y_str)
            return label, x_val, y_val
        return None, None, None

    # Define a numerical comparison tolerance
    tolerance = 1e-5 

    # 1. Try to parse as coordinates (e.g., "A(x,y)")
    user_label, user_x, user_y = _clean_and_parse_latex_coords(user_answer)
    correct_label, correct_x, correct_y = _clean_and_parse_latex_coords(correct_answer)

    if user_x is not None and correct_x is not None: # Both answers are valid coordinate formats
        return abs(user_x - correct_x) < tolerance and abs(user_y - correct_y) < tolerance

    # If not coordinates, clean both answers for general comparison
    # This `clean_general` is for non-coordinate, non-angle string/numerical answers.
    def clean_general(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # Remove variable prefixes like "ab="
        s = s.replace("$", "").replace("\\", "").replace("{", "").replace("}", "") # Remove LaTeX formatting
        s = s.replace("∠", "") # Remove angle symbol
        return s
    
    u_cleaned = clean_general(user_answer)
    c_cleaned = clean_general(correct_answer)

    # 2. Try to parse as angle notation (e.g., "ABC" for ∠ABC)
    # The cleaned string will be "abc" or "acb" etc.
    if len(c_cleaned) == 3 and c_cleaned.isalpha():
        if len(u_cleaned) == 3 and u_cleaned.isalpha():
            correct_vertex = c_cleaned[1]
            user_vertex = u_cleaned[1]

            correct_arms = sorted([c_cleaned[0], c_cleaned[2]])
            user_arms = sorted([u_cleaned[0], u_cleaned[2]])

            return (correct_vertex == user_vertex) and (correct_arms == user_arms)

    # 3. Try numerical comparison (e.g., segment length "5", "7.5")
    try:
        # Use fractions.Fraction to handle potential fraction inputs like "1/2"
        user_num = float(Fraction(u_cleaned)) if '/' in u_cleaned else float(u_cleaned)
        correct_num = float(Fraction(c_cleaned)) if '/' in c_cleaned else float(c_cleaned)
        return abs(user_num - correct_num) < tolerance
    except ValueError:
        pass # Not purely numerical, continue to string comparison

    # 4. Fallback to direct string comparison (e.g., "AB", "AB射線", "AB直線", "銳角", "鈍角")
    return u_cleaned == c_cleaned


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
