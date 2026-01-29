# ==============================================================================
# ID: jh_數學2下_MeaningAndPropertiesOfParallelograms
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 83.37s | RAG: 5 examples
# Created At: 2026-01-24 13:29:59
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
import io
import matplotlib.pyplot as plt
from datetime import datetime
import re

import numpy as np

# --- Helper Functions (Generic, follow V11.8+ rules) ---

def _generate_coordinate_value(min_val=-8, max_val=8, allow_half=True):
    """
    Generates a coordinate value, either integer or x.5, and returns it in a specific format.
    Returns: (float_val, (int_part, num, den, is_neg))
    """
    is_neg = random.choice([True, False])
    val_abs = random.randint(1, max_val) # Absolute value part

    if allow_half and random.random() < 0.3: # 30% chance of being x.5
        float_val = val_abs + 0.5
        int_part = val_abs
        num = 1
        den = 2
    else:
        float_val = float(val_abs)
        int_part = val_abs
        num = 0
        den = 0

    if is_neg:
        float_val = -float_val
        int_part = -int_part # Keep int_part negative for display purposes if it's the main part

    return (float_val, (int_part, num, den, is_neg))

def _format_coordinate_for_display(coord_data):
    """
    Formats a coordinate value for display in LaTeX.
    coord_data: (float_val, (int_part, num, den, is_neg))
    """
    float_val, (int_part, num, den, is_neg) = coord_data

    if num == 0 and den == 0: # Integer
        return str(int(float_val))
    else: # Fraction (x.5)
        # For x.5, we want to display as N.5 or N 1/2
        # The sign should be applied to the whole number if it's negative.
        # e.g., -2.5 should be -2\frac{1}{2}
        abs_val = abs(float_val)
        integer_part = int(abs_val)
        sign = "-" if float_val < 0 else ""

        if integer_part == 0: # e.g., 0.5 or -0.5
            return sign + r"\frac{1}{2}"
        else: # e.g., 2.5 or -2.5
            return sign + str(integer_part) + r"\frac{1}{2}"

def _draw_coordinate_plane(points_with_labels=None, min_coord=-10, max_coord=10, highlight_points=None):
    """
    Draws a coordinate plane with specified points and labels.
    points_with_labels: list of tuples `(x, y, label)`
    highlight_points: list of tuples `(x, y)` to draw as larger, distinct points.
    Returns: base64 encoded image.
    """
    if points_with_labels is None:
        points_with_labels = []
    if highlight_points is None:
        highlight_points = []

    fig, ax = plt.subplots(figsize=(8, 8), dpi=300) # Added dpi=300 as per ULTRA VISUAL STANDARDS

    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.6)

    ax.set_xlim(min_coord, max_coord)
    ax.set_ylim(min_coord, max_coord)

    # Set ticks and labels for major integer points
    ax.set_xticks(range(min_coord, max_coord + 1, 1))
    ax.set_yticks(range(min_coord, max_coord + 1, 1))
    ax.tick_params(axis='both', which='major', labelsize=10)

    # Draw x and y axes with arrows
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axvline(0, color='black', linewidth=1.5)

    # Add arrows to the ends of the axes using ax.plot as arrowprops is banned
    ax.plot(max_coord, 0, ">k", clip_on=False, transform=ax.get_yaxis_transform(), markersize=8) # X-axis arrow
    ax.plot(0, max_coord, "^k", clip_on=False, transform=ax.get_xaxis_transform(), markersize=8) # Y-axis arrow

    # Label x and y axes
    ax.text(max_coord + 0.2, -0.5, 'x', fontsize=12, ha='center', va='top')
    ax.text(-0.5, max_coord + 0.2, 'y', fontsize=12, ha='right', va='center')

    # Label the origin '0'
    ax.text(0, -0.8, '0', fontsize=18, ha='center', va='top', fontweight='bold')

    # Plot and label points
    label_whitelist = ['A', 'B', 'C', 'D', 'O', 'x', 'y', '0']
    for x, y, label in points_with_labels:
        if label in label_whitelist:
            ax.plot(x, y, 'o', color='blue', markersize=6)
            ax.text(x + 0.3, y + 0.3, label, fontsize=12,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", lw=0, alpha=0.8))

    # Plot highlight points
    for x, y in highlight_points:
        ax.plot(x, y, 'o', color='red', markersize=8, zorder=5)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def _draw_parallelogram(vertices, labels=None, show_diagonals=False, show_height=False, height_line=None):
    """
    Draws a parallelogram.
    vertices: List of (x, y) tuples for the vertices.
    labels: List of strings for vertex labels (e.g., ['A', 'B', 'C', 'D']).
    show_diagonals: Boolean to draw diagonals.
    show_height: Boolean to draw height line.
    height_line: Tuple (base_point_x, base_point_y, height_point_x, height_point_y)
    Returns: base64 encoded image.
    """
    fig, ax = plt.subplots(figsize=(6, 6), dpi=300)

    all_x = [v[0] for v in vertices]
    all_y = [v[1] for v in vertices]
    min_x, max_x = min(all_x) - 1, max(all_x) + 1
    min_y, max_y = min(all_y) - 1, max(all_y) + 1

    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')

    # Draw the parallelogram
    poly_coords = vertices + [vertices[0]]
    xs, ys = zip(*poly_coords)
    ax.plot(xs, ys, 'k-')

    # Plot vertices and labels
    label_whitelist = ['A', 'B', 'C', 'D', 'O']
    for i, (x, y) in enumerate(vertices):
        ax.plot(x, y, 'o', color='blue', markersize=5)
        if labels and i < len(labels) and labels[i] in label_whitelist:
            ax.text(x + 0.2, y + 0.2, labels[i], fontsize=12, ha='left', va='bottom',
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", lw=0, alpha=0.8))

    # Draw diagonals
    if show_diagonals and len(vertices) == 4:
        ax.plot([vertices[0][0], vertices[2][0]], [vertices[0][1], vertices[2][1]], 'k--')
        ax.plot([vertices[1][0], vertices[3][0]], [vertices[1][1], vertices[3][1]], 'k--')
        
        Ox = (vertices[0][0] + vertices[2][0]) / 2
        Oy = (vertices[0][1] + vertices[2][1]) / 2
        ax.plot(Ox, Oy, 'o', color='red', markersize=5)
        ax.text(Ox + 0.2, Oy - 0.4, 'O', fontsize=12, ha='left', va='top',
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", lw=0, alpha=0.8))

    # Draw height
    if show_height and height_line:
        hx1, hy1, hx2, hy2 = height_line
        ax.plot([hx1, hx2], [hy1, hy2], 'r--')
        
        if abs(hy1 - hy2) < 1e-6 and abs(vertices[0][1] - vertices[1][1]) < 1e-6:
            mark_x = hx2
            mark_y = hy1
            size = 0.3
            ax.plot([mark_x, mark_x, mark_x + size], [mark_y, mark_y + size, mark_y + size], 'k-', linewidth=1)
            ax.plot([mark_x + size, mark_x + size], [mark_y + size, mark_y], 'k-', linewidth=1)
        
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- Main Functions ---

def generate(level=1):
    # Strictly follow "MANDATORY MIRRORING RULES" for problem_type mapping
    problem_type = random.choice([1, 2, 3, 4, 5])
    question_text = ""
    correct_answer = ""
    image_base64 = None
    solution_text = ""

    # Generate generic parallelogram vertices for image (not tied to actual problem values)
    base_len = random.uniform(5, 10)
    slant_len = random.uniform(3, 7)
    slant_angle_deg = random.uniform(30, 70)
    
    x_offset = slant_len * math.cos(math.radians(slant_angle_deg))
    y_offset = slant_len * math.sin(math.radians(slant_angle_deg))
    
    generic_vertices = [
        (0, 0),
        (base_len, 0),
        (base_len + x_offset, y_offset),
        (x_offset, y_offset)
    ]
    generic_labels = ['A', 'B', 'C', 'D']
    
    image_base64 = _draw_parallelogram(generic_vertices, generic_labels)

    if problem_type == 1: # Maps to RAG Ex 1: ∠A=( x＋25 )°、∠C=( 3x-15 )°，則∠B=？
        # Ensure actual_angle_a is acute and x, N1, N2 are positive
        while True:
            val_x = random.randint(10, 30) # value for x
            val_n1 = random.randint(10, 40) # N1
            K = random.choice([2, 3]) # multiplier for C, RAG example uses 3
            
            actual_angle_a = val_x + val_n1
            if actual_angle_a >= 90 or actual_angle_a <= 20: # Ensure A is acute and reasonable
                continue
            
            # Derive N2 such that (K*x - N2) == actual_angle_a
            val_n2 = K * val_x - actual_angle_a
            
            if val_n2 > 0: # Ensure N2 is positive for "minus N2" phrasing
                break
        
        angle_a_expr_formatted = r"(x + {n1_val})".replace("{n1_val}", str(val_n1))
        angle_c_expr_formatted = r"({k_val}x - {n2_val})".replace("{k_val}", str(K)).replace("{n2_val}", str(val_n2))
        
        question_text_template = r"如右圖，平行四邊形 $ABCD$ 中，$\angle A={angle_a_expr_formatted}^\circ$、$\angle C={angle_c_expr_formatted}^\circ$，則 $\angle B=？$"
        question_text = question_text_template.replace("{angle_a_expr_formatted}", angle_a_expr_formatted).replace("{angle_c_expr_formatted}", angle_c_expr_formatted)
        
        correct_angle_b = 180 - actual_angle_a
        correct_answer = str(correct_angle_b)
        
        solution_text_template = (
            r"在平行四邊形 $ABCD$ 中，對角相等，所以 $\angle A = \angle C$。"
            r"$x + {n1_val} = {k_val}x - {n2_val}$"
            r"解此方程式，得 $({k_val}-1)x = {n1_val} + {n2_val}$"
            r"${diff_k_val}x = {sum_n_val}$"
            r"$x = {val_x_sol}$"
            r"將 $x$ 值代入 $\angle A$ 得到 $\angle A = {val_x_sol} + {n1_val} = {actual_angle_a}^\circ$。"
            r"平行四邊形的鄰角互補，所以 $\angle B = 180^\circ - \angle A = 180^\circ - {actual_angle_a}^\circ = {correct_angle_b}^\circ$。"
        )
        solution_text = solution_text_template.replace("{n1_val}", str(val_n1)) \
                            .replace("{k_val}", str(K)).replace("{n2_val}", str(val_n2)) \
                            .replace("{diff_k_val}", str(K-1)).replace("{sum_n_val}", str(val_n1+val_n2)) \
                            .replace("{val_x_sol}", str(val_x)).replace("{actual_angle_a}", str(actual_angle_a)) \
                            .replace("{correct_angle_b}", str(correct_angle_b))
            

    elif problem_type == 2: # Maps to RAG Ex 2: ∠B=24°，求其他三個內角的度數為多少？
        angle_b_val = random.randint(20, 80)
        
        correct_angle_d = angle_b_val
        correct_angle_a = 180 - angle_b_val
        correct_angle_c = correct_angle_a
        
        question_text_template = r"下圖中的建築是德國 易北河旁的碼頭辦公室，其形狀為一個平行四邊形，已知圖中 $ABCD$ 的 $\angle B={angle_b_val}^\circ$，求其他三個內角的度數為多少？"
        question_text = question_text_template.replace("{angle_b_val}", str(angle_b_val))
        
        correct_answer = f"{correct_angle_d}, {correct_angle_a}, {correct_angle_c}"
        solution_text_template = (
            r"在平行四邊形中，對角相等，鄰角互補。"
            r"$\angle D = \angle B = {angle_b_val}^\circ$。"
            r"$\angle A = 180^\circ - \angle B = 180^\circ - {angle_b_val}^\circ = {angle_a_val}^\circ$。"
            r"$\angle C = \angle A = {angle_a_val}^\circ$。"
        )
        solution_text = solution_text_template.replace("{angle_b_val}", str(angle_b_val)).replace("{angle_a_val}", str(correct_angle_a))

    elif problem_type == 3: # Maps to RAG Ex 3: ∠B 比∠A 的 3 倍少 20°
        while True:
            k_val = random.choice([2, 3, 4])
            angle_a_val = random.randint(30, 70) # Acute angle for A
            angle_b_val = 180 - angle_a_val
            
            # offset = k*A - B
            offset_val = k_val * angle_a_val - angle_b_val
            
            if offset_val > 0 and k_val * angle_a_val > angle_b_val: # Ensure "少" (less than) is meaningful and offset is positive
                break
        
        question_text_template = r"如右圖，平行四邊形 $ABCD$ 中，$\angle B$ 比 $\angle A$ 的 ${k_val}$ 倍少 ${offset_val}^\circ$，則這個平行四邊形的四個內角分別是幾度？"
        question_text = question_text_template.replace("{k_val}", str(k_val)).replace("{offset_val}", str(offset_val))
        
        correct_angle_c = angle_a_val
        correct_angle_d = angle_b_val
        
        correct_answer = f"{angle_a_val}, {angle_b_val}, {correct_angle_c}, {correct_angle_d}"
        solution_text_template = (
            r"設 $\angle A = x^\circ$。"
            r"根據題意，$\angle B = ({k_val}x - {offset_val})^\circ$。"
            r"在平行四邊形中，鄰角互補，所以 $\angle A + \angle B = 180^\circ$。"
            r"$x + ({k_val}x - {offset_val}) = 180$"
            r"${sum_k_val}x = 180 + {offset_val}$"
            r"${sum_k_val}x = {sum_180_offset}$"
            r"$x = \frac{{{sum_180_offset}}}{{{sum_k_val}}} = {angle_a_val}$。"
            r"所以 $\angle A = {angle_a_val}^\circ$。"
            r"$\angle B = 180^\circ - {angle_a_val}^\circ = {angle_b_val}^\circ$。"
            r"對角相等，所以 $\angle C = \angle A = {angle_a_val}^\circ$，$\angle D = \angle B = {angle_b_val}^\circ$。"
        )
        solution_text = solution_text_template.replace("{k_val}", str(k_val)).replace("{offset_val}", str(offset_val)) \
                            .replace("{sum_k_val}", str(1+k_val)).replace("{sum_180_offset}", str(180+offset_val)) \
                            .replace("{angle_a_val}", str(angle_a_val)).replace("{angle_b_val}", str(angle_b_val))

    elif problem_type == 4: # Maps to RAG Ex 4: 周長為 36 公分，AB=2BC
        k_val = random.choice([2, 3])
        
        bc_len = random.randint(4, 10)
        ab_len = k_val * bc_len
        
        perimeter = 2 * (ab_len + bc_len)
        
        question_text_template = r"如右圖，已知平行四邊形 $ABCD$ 的周長為 ${perimeter} \text{ 公分}$，$AB={k_val}BC$，則各邊的長度分別為多少公分？"
        question_text = question_text_template.replace("{perimeter}", str(perimeter)).replace("{k_val}", str(k_val))
        
        correct_ad_len = bc_len
        correct_cd_len = ab_len
        
        correct_answer = f"{bc_len}, {ab_len}, {correct_ad_len}, {correct_cd_len}"
        solution_text_template = (
            r"設 $BC = x \text{ 公分}$。"
            r"根據題意，$AB = {k_val}x \text{ 公分}$。"
            r"平行四邊形的周長公式為 $2 \times (AB + BC)$。"
            r"$2 \times ({k_val}x + x) = {perimeter}$"
            r"$2 \times ({sum_k_val}x) = {perimeter}$"
            r"${total_k_val}x = {perimeter}$"
            r"$x = \frac{{{perimeter}}}{{{total_k_val}}} = {bc_len}$。"
            r"所以 $BC = {bc_len} \text{ 公分}$。"
            r"$AB = {k_val} \times {bc_len} = {ab_len} \text{ 公分}$。"
            r"在平行四邊形中，對邊相等，所以 $AD = BC = {bc_len} \text{ 公分}$，"
            r"$CD = AB = {ab_len} \text{ 公分}$。"
        )
        solution_text = solution_text_template.replace("{perimeter}", str(perimeter)).replace("{k_val}", str(k_val)) \
                            .replace("{sum_k_val}", str(k_val+1)).replace("{total_k_val}", str(2*(k_val+1))) \
                            .replace("{bc_len}", str(bc_len)).replace("{ab_len}", str(ab_len))

    elif problem_type == 5: # Maps to RAG Ex 5: AB 比 BC 的 2 倍多 5 公分，CD 比 AD 的 3 倍少 6 公分
        while True:
            bc_len = random.randint(5, 15)
            ab_len = random.randint(bc_len + 5, bc_len + 15)
            
            k1 = random.choice([2, 3])
            offset1 = ab_len - k1 * bc_len
            
            k2 = random.choice([2, 3, 4])
            offset2 = k2 * bc_len - ab_len
            
            # Ensure offsets are positive and k1 != k2 for a solvable equation
            if offset1 > 0 and offset2 > 0 and k1 != k2:
                break
            
        perimeter = 2 * (ab_len + bc_len)
        
        question_text_template = r"平行四邊形 $ABCD$ 中，$AB$ 比 $BC$ 的 ${k1_val}$ 倍多 ${offset1_val} \text{ 公分}$，$CD$ 比 $AD$ 的 ${k2_val}$ 倍少 ${offset2_val} \text{ 公分}$，則 $ABCD$ 的周長為多少公分？"
        question_text = question_text_template.replace("{k1_val}", str(k1)).replace("{offset1_val}", str(offset1)) \
                            .replace("{k2_val}", str(k2)).replace("{offset2_val}", str(offset2))
        
        correct_answer = str(perimeter)
        solution_text_template = (
            r"在平行四邊形 $ABCD$ 中，對邊相等，所以 $AB = CD$ 且 $BC = AD$。"
            r"設 $BC = x \text{ 公分}$，則 $AD = x \text{ 公分}$。"
            r"根據題意：$AB = {k1_val}x + {offset1_val}$。"
            r"又 $CD = {k2_val}x - {offset2_val}$。"
            r"因為 $AB = CD$，所以 ${k1_val}x + {offset1_val} = {k2_val}x - {offset2_val}$。"
            r"${k2_val}x - {k1_val}x = {offset1_val} + {offset2_val}$"
            r"${diff_k_val}x = {sum_offset_val}$"
            r"$x = \frac{{{sum_offset_val}}}{{{diff_k_val}}} = {bc_len}$。"
            r"所以 $BC = {bc_len} \text{ 公分}$。"
            r"$AB = {k1_val} \times {bc_len} + {offset1_val} = {ab_len} \text{ 公分}$。"
            r"平行四邊形的周長 $= 2 \times (AB + BC) = 2 \times ({ab_len} + {bc_len}) = 2 \times {sum_ab_bc} = {perimeter} \text{ 公分}$。"
        )
        solution_text = solution_text_template.replace("{k1_val}", str(k1)).replace("{offset1_val}", str(offset1)) \
                            .replace("{k2_val}", str(k2)).replace("{offset2_val}", str(offset2)) \
                            .replace("{diff_k_val}", str(k2-k1)).replace("{sum_offset_val}", str(offset1+offset2)) \
                            .replace("{bc_len}", str(bc_len)).replace("{ab_len}", str(ab_len)) \
                            .replace("{sum_ab_bc}", str(ab_len+bc_len)).replace("{perimeter}", str(perimeter))

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": solution_text,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1"
    }


    # CRITICAL CODING RULE: Local Imports
    import re
    

    # Robust Check Logic, returning True/False as per "閱卷與反饋" rule.
    
    # Clean user and correct answers
    # This regex is more permissive, allowing numbers, commas, periods, and negative signs.
    # It removes common non-numeric/non-separator characters and Chinese units.
    user_answer_cleaned = re.sub(r'[\\$}{kxya=Ans:度公分]', '', user_answer).strip()
    user_answer_cleaned = re.sub(r'\s+', '', user_answer_cleaned) # Remove all whitespace

    correct_answer_cleaned = re.sub(r'[\\$}{kxya=Ans:度公分]', '', correct_answer).strip()
    correct_answer_cleaned = re.sub(r'\s+', '', correct_answer_cleaned)

    # Handle boolean/Yes-No standardization if applicable (though not for this skill currently)
    yes_group = ["是", "Yes", "TRUE", "True", "1", "O", "right"]
    no_group = ["否", "No", "FALSE", "False", "0", "X", "wrong"]
    
    if correct_answer_cleaned in yes_group:
        return user_answer_cleaned in yes_group
    if correct_answer_cleaned in no_group:
        return user_answer_cleaned in no_group

    # Split by common delimiters for multiple answers (e.g., "3,4" or "3 4")
    user_parts = re.split(r'[,;\s]+', user_answer_cleaned)
    correct_parts = re.split(r'[,;\s]+', correct_answer_cleaned)

    if len(user_parts) != len(correct_parts):
        return False

    # Compare each part numerically
    for u_part, c_part in zip(user_parts, correct_parts):
        try:
            u_val = float(u_part)
            c_val = float(c_part)
            if not math.isclose(u_val, c_val, rel_tol=1e-5, abs_tol=1e-5):
                return False
        except ValueError:
            # If conversion to float fails, it's not a valid number, so not equal
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
