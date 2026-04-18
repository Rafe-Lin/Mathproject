# ==============================================================================
# ID: jh_數學1下_PerpendicularBisectorsAndLineSymmetricFigures
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 39.43s | RAG: 5 examples
# Created At: 2026-01-17 23:30:17
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
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

# --- Helper Functions (輔助函式) ---

def _generate_coordinate_value(is_fraction=False, integer_only=False, range_min=-8, range_max=8):
    """
    功能: 生成單一座標值 (x 或 y)，可為整數或分數。
    遵循 V10.2 A 規範。
    """
    while True:
        base_int = random.randint(range_min, range_max)
        
        if integer_only or not is_fraction:
            val_float = float(base_int)
            int_part = base_int
            num = 0
            den = 0
        else:
            # Generate a non-zero base_int if it's purely fractional to avoid 0.5 like 0.5
            # Or allow 0.5 if base_int is 0
            if base_int == 0:
                fraction_part = random.choice([0.5, -0.5])
                val_float = fraction_part
                int_part = 0
                num = 1
                den = 2
            else:
                fraction_sign = random.choice([-1, 1])
                numerator = 1 # Only allow 0.5 fractions for now as per V13.5
                denominator = 2
                val_float = base_int + fraction_sign * (numerator / denominator)
                int_part = int(val_float)
                num = numerator
                den = denominator
            
        is_neg = (val_float < 0)
        
        # Ensure that if it's a fraction, it's not an integer
        if is_fraction and val_float.is_integer():
            continue
        
        # Ensure the value is within range after fraction addition
        if not (range_min <= val_float <= range_max):
            continue

        return (val_float, (int_part, num, den, is_neg))

def _format_coordinate_for_display(val):
    """
    功能: 將浮點數座標值格式化為字串，確保整數以整數形式顯示 (e.g., "5"而非"5.0")。
    遵循 V13.0, V13.5 規範。
    """
    if val.is_integer():
        return str(int(val))
    else:
        # For fractions like X.5, display as X.5
        return str(val)

def _draw_coordinate_plane(points_to_plot, axis_of_symmetry_line=None, x_range=(-8, 8), y_range=(-8, 8), show_labels=True, plot_points_only=False, invisible_points_for_bounds=None):
    """
    功能: 繪製帶有座標軸、網格、點和對稱軸的座標平面圖，並回傳 base64 編碼圖片。
    遵循 V10.2 B, V10.2 D, V13.0, V13.1, V13.5, V13.6, CRITICAL RULE: Visual Solvability, ULTRA VISUAL STANDARDS 規範。
    """
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # 確保中文字體顯示
    plt.rcParams['axes.unicode_minus'] = False # 正常顯示負號

    fig, ax = plt.subplots(figsize=(8, 8), dpi=300) # ULTRA VISUAL STANDARDS: dpi=300

    # Set axis limits with padding
    # [Dynamic Scaling] Calculate bounds from points
    all_x = [p['coord'][0] for p in points_to_plot]
    all_y = [p['coord'][1] for p in points_to_plot]
    
    # [View Context] Ensure Origin (0,0) is always included so axes are visible
    all_x.append(0)
    all_y.append(0)
    
    # [V16.28 Viewport Inclusion] Include invisible solution points in bounds calculation
    if invisible_points_for_bounds:
        for p in invisible_points_for_bounds:
            all_x.append(p[0])
            all_y.append(p[1])
    
    # Include axis of symmetry in bounds if relevant
    # (Simplified: we trust points cover the area mostly, but ensure at least -5 to 5 if nothing)
    
    if all_x and all_y:
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        
        # Add padding (at least 2 units)
        pad = 2
        view_min_x, view_max_x = min_x - pad, max_x + pad
        view_min_y, view_max_y = min_y - pad, max_y + pad
    else:
        view_min_x, view_max_x = -6, 6
        view_min_y, view_max_y = -6, 6

    # Override with input x_range only if it is wider? No, let's enforce dynamic view for better visibility.
    # Actually, respecting input x_range might be needed if it was intentionally set. 
    # But user reported "shrunk to corner", implying fixed huge range vs small data.
    # Let's use the calculated view bounds.
    
    ax.set_xlim(view_min_x, view_max_x)
    ax.set_ylim(view_min_y, view_max_y)

    ax.set_aspect('equal') # ULTRA VISUAL STANDARDS: Aspect Ratio

    # Draw grid lines
    # Draw grid lines
    ax.grid(True, linestyle=':', alpha=0.6) # Grid Lines

    # Draw x, y axes
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axvline(0, color='black', linewidth=1.5)

    # Draw axis arrows (V13.6 API Hardened Spec)
    # Draw axis arrows (V13.6 API Hardened Spec)
    ax.plot(view_max_x, 0, ">k", clip_on=False, markersize=8, transform=ax.transData)
    ax.plot(0, view_max_y, "^k", clip_on=False, markersize=8, transform=ax.transData)

    # Label origin '0' (V10.2 D)
    ax.text(0.1, 0.1, '0', color='black', ha='center', va='center', fontsize=12, fontweight='bold',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=0.5))

    # Set xticks and yticks for explicit integer labels (CRITICAL RULE: Visual Solvability, V13.0)
    # Set xticks and yticks for explicit integer labels (CRITICAL RULE: Visual Solvability, V13.0)
    # Generate ticks based on the DYNAMIC view range
    start_tick_x = math.ceil(view_min_x)
    end_tick_x = math.floor(view_max_x)
    start_tick_y = math.ceil(view_min_y)
    end_tick_y = math.floor(view_max_y)

    ax.set_xticks(np.arange(start_tick_x, end_tick_x + 1))
    ax.set_yticks(np.arange(start_tick_y, end_tick_y + 1))
    ax.tick_params(axis='both', which='major', labelsize=12) # Increased font size

    # Hide '0' tick label to avoid overlap with origin '0' text
    ax.set_xticklabels([str(int(t)) if t != 0 else '' for t in ax.get_xticks()])
    ax.set_yticklabels([str(int(t)) if t != 0 else '' for t in ax.get_yticks()])

    # Plot points
    point_label_whitelist = ['A', 'B', 'C', 'D', 'P', 'Q', 'M', 'N', "A'", "B'", "C'", "D'", "巴奈"] # V13.6
    for p in points_to_plot:
        x, y = p['coord']
        label = p.get('label', '')
        ax.plot(x, y, 'o', color='blue', markersize=6)
        if show_labels and label in point_label_whitelist: # V13.6
            # V10.2 D, V13.0, V13.1, V13.5: text for label only, white halo
            ax.text(x + 0.3, y + 0.3, label, color='black', fontsize=12,
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))

    # Draw axis of symmetry line (if not plot_points_only)
    if axis_of_symmetry_line and not plot_points_only:
        line_type = axis_of_symmetry_line[0]
        if line_type == 'x': # Vertical line x = val
            x_val = axis_of_symmetry_line[1]
            ax.axvline(x_val, color='red', linestyle='--', linewidth=2, alpha=0.7)
        elif line_type == 'y': # Horizontal line y = val
            y_val = axis_of_symmetry_line[1]
            ax.axhline(y_val, color='red', linestyle='--', linewidth=2, alpha=0.7)
        elif line_type == 'y=x':
            ax.plot([x_range[0], x_range[1]], [x_range[0], x_range[1]], color='red', linestyle='--', linewidth=2, alpha=0.7)
        elif line_type == 'y=-x':
            ax.plot([x_range[0], x_range[1]], [-x_range[0], -x_range[1]], color='red', linestyle='--', linewidth=2, alpha=0.7)
        elif line_type == 'y=mx+c' and len(axis_of_symmetry_line) == 3:
            m, c = axis_of_symmetry_line[1], axis_of_symmetry_line[2]
            x_vals = np.array([x_range[0], x_range[1]])
            y_vals = m * x_vals + c
            ax.plot(x_vals, y_vals, color='red', linestyle='--', linewidth=2, alpha=0.7)

    # Save to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig) # Clear figure to avoid memory leaks
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64

# --- generate() 函式 ---

def generate(level=1):
    """
    功能: 根據不同的題型隨機生成中垂線與線對稱圖形相關的數學題目。
    遵循 Problem Mirroring 規範。
    """
    problem_type = random.choice([1, 2, 3, 4]) # Randomly choose one of the four types

    question_text = ""
    correct_answer = ""
    image_base64 = None

    if problem_type == 1:
        # Type 1: 中垂線性質計算 (Maps to RAG Ex 1: Perpendicular distance application)
        length_pa = random.randint(5, 15)
        question_template = r"已知直線L是線段AB的中垂線，P點在直線L上。若 $\overline{PA} = {val_pa}$，則 $\overline{PB} = ?$ "
        question_text = question_template.replace("{val_pa}", str(length_pa))
        correct_answer = str(length_pa) # Answer Data Purity

    elif problem_type == 2:
        # Type 2: 點的對稱點坐標 (Maps to RAG Ex 2: Symmetric point using reflection)
        p_x_float, _ = _generate_coordinate_value(is_fraction=random.choice([True, False]), range_min=-5, range_max=5)
        p_y_float, _ = _generate_coordinate_value(is_fraction=random.choice([True, False]), range_min=-5, range_max=5)
        point_P = (p_x_float, p_y_float)

        axis_type = random.choice(['x-axis', 'y-axis', 'y=x', 'y=-x'])

        sym_x, sym_y = 0, 0
        if axis_type == 'x-axis':
            sym_x = p_x_float
            sym_y = -p_y_float
            axis_for_drawing = ('y', 0)
        elif axis_type == 'y-axis':
            sym_x = -p_x_float
            sym_y = p_y_float
            axis_for_drawing = ('x', 0)
        elif axis_type == 'y=x':
            sym_x = p_y_float
            sym_y = p_x_float
            axis_for_drawing = ('y=x',)
        elif axis_type == 'y=-x':
            sym_x = -p_y_float
            sym_y = -p_x_float
            axis_for_drawing = ('y=-x',)
        symmetric_point = (sym_x, sym_y)

        # [Localization] Translate axis names
        axis_display_map = {
            'x-axis': r'$x$ 軸',
            'y-axis': r'$y$ 軸',
            'y=x': r'直線 $y=x$',
            'y=-x': r'直線 $y=-x$'
        }
        axis_display = axis_display_map.get(axis_type, axis_type)

        pt_P_display = r"P({x}, {y})".replace("{x}", _format_coordinate_for_display(point_P[0])).replace("{y}", _format_coordinate_for_display(point_P[1]))
        question_template = r"已知平面上有一點 {pt_P}。若以 {axis} 為對稱軸，則 $P$ 點的對稱點坐標為何？"
        question_text = question_template.replace("{pt_P}", pt_P_display).replace("{axis}", axis_display)

        correct_answer = "{x},{y}".replace("{x}", _format_coordinate_for_display(symmetric_point[0])).replace("{y}", _format_coordinate_for_display(symmetric_point[1]))

        points_for_drawing = [{'coord': point_P, 'label': 'P'}]
        # Pass answer point to ensure plot bounds cover it
        image_base64 = _draw_coordinate_plane(points_for_drawing, axis_of_symmetry_line=axis_for_drawing, x_range=(-7, 7), y_range=(-7, 7), show_labels=True, invisible_points_for_bounds=[symmetric_point])

    elif problem_type == 3:
        # Type 3: 補齊線對稱圖形 (繪圖題，僅提供起始點與對稱軸) (Maps to RAG Ex 3: Symmetric points for a figure)
        while True:
            a_x_float, _ = _generate_coordinate_value(integer_only=True, range_min=-5, range_max=5)
            a_y_float, _ = _generate_coordinate_value(integer_only=True, range_min=-5, range_max=5)
            b_x_float, _ = _generate_coordinate_value(integer_only=True, range_min=-5, range_max=5)
            b_y_float, _ = _generate_coordinate_value(integer_only=True, range_min=-5, range_max=5)
            point_A = (int(a_x_float), int(a_y_float))
            point_B = (int(b_x_float), int(b_y_float))

            axis_type = random.choice(['x-axis', 'y-axis'])

            # Ensure A, B are distinct and not on the axis
            if point_A == point_B:
                continue
            if axis_type == 'x-axis' and (point_A[1] == 0 or point_B[1] == 0):
                continue
            if axis_type == 'y-axis' and (point_A[0] == 0 or point_B[0] == 0):
                continue
            
            # For simplicity, ensure points are not too close to the origin if they are on axes.
            # This is already handled by not being on the axis itself.
            break

        a_prime_x, a_prime_y = 0, 0
        b_prime_x, b_prime_y = 0, 0
        axis_for_drawing = None

        if axis_type == 'x-axis':
            a_prime_x, a_prime_y = point_A[0], -point_A[1]
            b_prime_x, b_prime_y = point_B[0], -point_B[1]
            axis_for_drawing = ('y', 0)
        elif axis_type == 'y-axis':
            a_prime_x, a_prime_y = -point_A[0], point_A[1]
            b_prime_x, b_prime_y = -point_B[0], point_B[1]
            axis_for_drawing = ('x', 0)
        
        symmetric_A_prime = (a_prime_x, a_prime_y)
        symmetric_B_prime = (b_prime_x, b_prime_y)

        # [Localization] Translate axis names
        axis_display_map = {
            'x-axis': r'$x$ 軸',
            'y-axis': r'$y$ 軸'
        }
        axis_display = axis_display_map.get(axis_type, axis_type)

        pt_A_display = r"A({x}, {y})".replace("{x}", str(point_A[0])).replace("{y}", str(point_A[1]))
        pt_B_display = r"B({x}, {y})".replace("{x}", str(point_B[0])).replace("{y}", str(point_B[1]))
        question_template = r"在坐標平面上，已知兩點 {pt_A} 和 {pt_B}。若以 {axis} 為對稱軸，請找出 $A$ 點和 $B$ 點的對稱點 $A'$ 和 $B'$ 的坐標。"
        question_text = question_template.replace("{pt_A}", pt_A_display).replace("{pt_B}", pt_B_display).replace("{axis}", axis_display)

        correct_answer = "{ax},{ay},{bx},{by}".replace("{ax}", str(symmetric_A_prime[0])).replace("{ay}", str(symmetric_A_prime[1])).replace("{bx}", str(symmetric_B_prime[0])).replace("{by}", str(symmetric_B_prime[1]))

        points_for_drawing = [{'coord': point_A, 'label': 'A'}, {'coord': point_B, 'label': 'B'}]
        # Pass answer points to ensure plot bounds cover them
        image_base64 = _draw_coordinate_plane(points_for_drawing, axis_of_symmetry_line=axis_for_drawing, x_range=(-7, 7), y_range=(-7, 7), show_labels=True, invisible_points_for_bounds=[symmetric_A_prime, symmetric_B_prime])

    elif problem_type == 4:
        # Type 4: 軸上點到兩點距離相等 (Maps to RAG Ex 4: Perpendicular bisector intersection)
        while True:
            ax_float, _ = _generate_coordinate_value(integer_only=True, range_min=-5, range_max=5)
            ay_float, _ = _generate_coordinate_value(integer_only=True, range_min=-5, range_max=5)
            bx_float, _ = _generate_coordinate_value(integer_only=True, range_min=-5, range_max=5)
            by_float, _ = _generate_coordinate_value(integer_only=True, range_min=-5, range_max=5)
            point_A = (int(ax_float), int(ay_float))
            point_B = (int(bx_float), int(by_float))

            if point_A == point_B: # Ensure distinct points
                continue

            target_axis = random.choice(['x-axis', 'y-axis'])

            # Robustness check: ensure unique intersection
            if target_axis == 'x-axis': # P is on y=0
                if point_A[1] == point_B[1]: # AB is horizontal, bisector is vertical, no intersection with x-axis unless AB is on x-axis
                    if point_A[1] != 0: # If AB not on x-axis, then no intersection with x-axis
                        continue
                    else: # If AB is on x-axis, then entire x-axis is solution, which is not a unique point.
                        continue
            elif target_axis == 'y-axis': # P is on x=0
                if point_A[0] == point_B[0]: # AB is vertical, bisector is horizontal, no intersection with y-axis unless AB is on y-axis
                    if point_A[0] != 0: # If AB not on y-axis, then no intersection with y-axis
                        continue
                    else: # If AB is on y-axis, then entire y-axis is solution, not unique.
                        continue
            break # If all checks pass, break loop

        # Calculate midpoint M
        M_x = (point_A[0] + point_B[0]) / 2
        M_y = (point_A[1] + point_B[1]) / 2

        # Calculate slope of AB
        delta_x = point_B[0] - point_A[0]
        delta_y = point_B[1] - point_A[1]

        P_x, P_y = 0.0, 0.0

        if delta_x == 0: # AB is a vertical line (x = const)
            # Perpendicular bisector is a horizontal line (y = M_y)
            if target_axis == 'x-axis': # Intersection with y=0
                # If M_y is 0, then the bisector is the x-axis itself, not a unique point.
                # This case should be caught by the robustness check (point_A[1] == point_B[1])
                # However, if delta_x=0 means point_A[0]==point_B[0], so it means we need to ensure point_A[1] != point_B[1]
                # which is guaranteed by the robustness check for target_axis == 'x-axis'
                # If delta_x is 0, point_A[0] == point_B[0], and target_axis is x-axis.
                # The perpendicular bisector is y = M_y.
                # Intersection with y=0 means M_y = 0, which means point P is (point_A[0], 0).
                # This is only possible if M_y = 0.
                if M_y == 0: # Bisector is y=0, which is the x-axis. Not a unique point
                    # This case should be prevented by the robustness check
                    pass 
                P_x = M_x # x-coordinate of P is the x-coordinate of the midpoint
                P_y = 0.0 # P is on the x-axis
            else: # target_axis == 'y-axis', intersection with x=0
                P_x = 0.0 # P is on the y-axis
                P_y = M_y # y-coordinate of P is the y-coordinate of the midpoint
        elif delta_y == 0: # AB is a horizontal line (y = const)
            # Perpendicular bisector is a vertical line (x = M_x)
            if target_axis == 'x-axis': # Intersection with y=0
                P_x = M_x # x-coordinate of P is the x-coordinate of the midpoint
                P_y = 0.0 # P is on the x-axis
            else: # target_axis == 'y-axis', intersection with x=0
                # If M_x is 0, then the bisector is the y-axis itself, not a unique point.
                # This case should be caught by the robustness check (point_A[0] == point_B[0])
                if M_x == 0: # Bisector is x=0, which is the y-axis. Not a unique point
                    pass
                P_x = 0.0 # P is on the y-axis
                P_y = M_y # y-coordinate of P is the y-coordinate of the midpoint
        else: # AB is a slanted line
            m_ab = delta_y / delta_x
            m_perp = -1 / m_ab # Slope of perpendicular bisector

            # Equation of perpendicular bisector: y - M_y = m_perp * (x - M_x)
            if target_axis == 'x-axis': # P is on y=0
                P_y = 0.0
                P_x = M_x - M_y / m_perp
            else: # target_axis == 'y-axis', P is on x=0
                P_x = 0.0
                P_y = M_y - m_perp * M_x

        # Convert to int if it's a whole number
        if P_x.is_integer(): P_x = int(P_x)
        if P_y.is_integer(): P_y = int(P_y)

        point_P = (P_x, P_y)

        pt_A_display = r"A({x}, {y})".replace("{x}", str(point_A[0])).replace("{y}", str(point_A[1]))
        pt_B_display = r"B({x}, {y})".replace("{x}", str(point_B[0])).replace("{y}", str(point_B[1]))
        
        # [Localization] Translate axis names
        axis_display_map = {
            'x-axis': r'$x$ 軸',
            'y-axis': r'$y$ 軸'
        }
        axis_display = axis_display_map.get(target_axis, target_axis)
        
        question_template = r"坐標平面上 $A$ 點為 {pt_A}，$B$ 點為 {pt_B}。若 $P$ 點在 {axis} 上，且 $\overline{PA} = \overline{PB}$，則 $P$ 點的坐標為何？"
        question_text = question_template.replace("{pt_A}", pt_A_display).replace("{pt_B}", pt_B_display).replace("{axis}", axis_display)

        correct_answer = "{x},{y}".replace("{x}", _format_coordinate_for_display(point_P[0])).replace("{y}", _format_coordinate_for_display(point_P[1]))

        correct_answer = "{x},{y}".replace("{x}", _format_coordinate_for_display(point_P[0])).replace("{y}", _format_coordinate_for_display(point_P[1]))

        # [Spoiler Prevention] Do NOT draw the answer point P! Only show A and B.
        points_for_drawing = [{'coord': point_A, 'label': 'A'}, {'coord': point_B, 'label': 'B'}]
        # [V16.28] Ensure bounds include P even though it's hidden
        image_base64 = _draw_coordinate_plane(points_for_drawing, x_range=(-7, 7), y_range=(-7, 7), show_labels=True, invisible_points_for_bounds=[point_P])

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "", # This field is typically for user's input, left empty for generation
        "image_base64": image_base64,
    }

# --- check() 函式 ---


    """
    功能: 檢查使用者答案與正確答案是否一致。
    遵循 V2.0, V12.6, V13.5, V13.6 規範，並使用「通用 Check 函式模板」。
    """
    import re, math
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+\s*=\s*', '', s) # 移除 k=, x=, y=, a=
        s = re.sub(r'[$\\\{\}xXyYkK=aA_sS:\[\]\(\)]', '', s) # 移除 LaTeX, 括號等符號
        return s
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 嘗試數值序列比對 (支援分數與小數)
    u_parts = u.split(',')
    c_parts = c.split(',')

    if len(u_parts) != len(c_parts):
        return {"correct": False, "result": f"答案格式錯誤，預期 {len(c_parts)} 個數值，但得到 {len(u_parts)} 個。"}

    is_correct_sequence = True
    for u_part, c_part in zip(u_parts, c_parts):
        try:
            def parse_val(val_str):
                if "/" in val_str:
                    n, d = map(float, val_str.split("/"))
                    return n/d
                return float(val_str)
            
            if not math.isclose(parse_val(u_part), parse_val(c_part), rel_tol=1e-5, abs_tol=1e-9): # Added abs_tol for values close to zero
                is_correct_sequence = False
                break
        except ValueError:
            is_correct_sequence = False
            break
    
    if is_correct_sequence:
        return {"correct": True, "result": "正確！"}
        
    # 3. 降級為字串比對
    # This part might be redundant if numerical comparison covers all cases,
    # but kept for strict adherence to template.
    if u == c: return {"correct": True, "result": "正確！"}

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
