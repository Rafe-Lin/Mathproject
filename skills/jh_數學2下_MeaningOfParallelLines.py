# ==============================================================================
# ID: jh_數學2下_MeaningOfParallelLines
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 86.34s | RAG: 5 examples
# Created At: 2026-01-24 13:20:40
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
    """
    [V18.14 Synonym Check] 針對面積比較題，支援多種「相等」的表達方式。
    Accepts: "一樣", "一樣大", "相等", "相同", "equal", "same"
    """
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    import re
    
    # 1. 預處理
    def clean(s):
        return str(s).strip().replace(" ", "").lower()
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 定義「相等」的關鍵字庫
    equal_keywords = ["一樣", "相同", "相等", "equal", "same"]
    
    # 3. 檢查：若標準答案包含「一樣/相等」且 使用者答案也包含這些詞 -> 判定正確
    # 例如：Correct="面積一樣大" vs User="一樣" -> True
    c_has_keyword = any(k in c for k in equal_keywords)
    u_has_keyword = any(k in u for k in equal_keywords)
    
    if c_has_keyword and u_has_keyword:
        return {"correct": True, "result": "正確！"}

    # 4. 一般比對 (針對其他題型)
    if u == c: 
        return {"correct": True, "result": "正確！"}
        
    return {"correct": False, "result": f"答案錯誤。正確答案為：{correct_answer}"}



import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
import re # 確保 check 函式內部有 import

# 輔助函式：產生隨機角度，確保在合理範圍內且不是0或180
def _generate_angle_value(min_angle=30, max_angle=150):
    """Generates a random angle value for geometry problems."""
    angle = random.randint(min_angle, max_angle)
    return angle

# 輔助函式：繪製基礎平行線與截線圖 (此函式在當前RAG範例中未被直接調用，但依據原始Spec保留)
def _draw_parallel_lines_diagram(line1_y, line2_y, transversal_slope, transversal_x_intercept,
                                   angle_labels=None, highlight_angle_pos=None):
    """
    Draws a diagram with two horizontal lines and a transversal.
    Args:
        line1_y (float): Y-coordinate for the first horizontal line.
        line2_y (float): Y-coordinate for the second horizontal line.
        transversal_slope (float): Slope of the transversal line.
        transversal_x_intercept (float): X-intercept of the transversal line.
        angle_labels (dict): Dictionary mapping angle positions (e.g., 'top_left_1') to labels (e.g., '∠1').
        highlight_angle_pos (str): Key of the angle to highlight with a red arc.
    Returns:
        tuple: (base64_image_string, line_coords)
    """
    fig, ax = plt.subplots(figsize=(6, 6), dpi=300) # Added DPI
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.axis('off') # Hide axes for a cleaner geometry diagram

    # Draw horizontal lines L1 and L2
    ax.plot([-5, 5], [line1_y, line1_y], 'k-', lw=1.5, label='L1')
    ax.plot([-5, 5], [line2_y, line2_y], 'k-', lw=1.5, label='L2')
    ax.text(5.2, line1_y, 'L1', va='center', ha='left', fontsize=12, bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.7))
    ax.text(5.2, line2_y, 'L2', va='center', ha='left', fontsize=12, bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.7))

    # Draw transversal line M
    x_vals = [-5, 5]
    y_vals = [transversal_slope * (x - transversal_x_intercept) for x in x_vals]
    ax.plot(x_vals, y_vals, 'k-', lw=1.5, label='M')
    ax.text(x_vals[1] + 0.2, y_vals[1], 'M', va='center', ha='left', fontsize=12, bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.7))

    # Calculate intersection points for labeling
    x1 = (line1_y / transversal_slope) + transversal_x_intercept if transversal_slope != 0 else transversal_x_intercept
    y1 = line1_y
    x2 = (line2_y / transversal_slope) + transversal_x_intercept if transversal_slope != 0 else transversal_x_intercept
    y2 = line2_y

    line_coords = {
        "L1_y": line1_y, "L2_y": line2_y,
        "M_slope": transversal_slope, "M_x_intercept": transversal_x_intercept,
        "intersection1": (x1, y1), "intersection2": (x2, y2)
    }

    if angle_labels:
        label_positions = {
            'top_left_1': (x1 - 0.5, y1 + 0.3, 135),
            'top_right_1': (x1 + 0.5, y1 + 0.3, 45),
            'bottom_left_1': (x1 - 0.5, y1 - 0.3, 225),
            'bottom_right_1': (x1 + 0.5, y1 - 0.3, 315),
            'top_left_2': (x2 - 0.5, y2 + 0.3, 135),
            'top_right_2': (x2 + 0.5, y2 + 0.3, 45),
            'bottom_left_2': (x2 - 0.5, y2 - 0.3, 225),
            'bottom_right_2': (x2 + 0.5, y2 - 0.3, 315),
        }

        trans_angle_rad = math.atan(transversal_slope)
        trans_angle_deg = math.degrees(trans_angle_rad) % 180
        if trans_angle_deg < 0: trans_angle_deg += 180

        if transversal_slope > 0:
            acute_angle = trans_angle_deg
        else:
            acute_angle = 180 - trans_angle_deg

        for pos_key, label_text in angle_labels.items():
            if pos_key in label_positions:
                px, py, text_angle_offset = label_positions[pos_key]
                intersection_x, intersection_y = line_coords['intersection1'] if '1' in pos_key else line_coords['intersection2']

                ax.text(px, py, label_text, va='center', ha='center', fontsize=12,
                        bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.7))

                if highlight_angle_pos == pos_key:
                    arc_color = 'red'
                    arc_radius = 0.4
                    start_angle = 0
                    end_angle = 0

                    if 'top_left' in pos_key:
                        start_angle = 180 - acute_angle
                        end_angle = 180
                    elif 'top_right' in pos_key:
                        start_angle = 0
                        end_angle = acute_angle
                    elif 'bottom_right' in pos_key:
                        start_angle = 360 - acute_angle
                        end_angle = 360
                    elif 'bottom_left' in pos_key:
                        start_angle = 180
                        end_angle = 180 + acute_angle

                    arc = patches.Arc((intersection_x, intersection_y),
                                      arc_radius * 2, arc_radius * 2,
                                      angle=0, theta1=start_angle, theta2=end_angle,
                                      color=arc_color, lw=1.5)
                    ax.add_patch(arc)

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64, line_coords


# 輔助函式：繪製RAG Ex 2所需的平行線間三角形圖
def _draw_triangles_between_parallel_lines_diagram(line1_y, line2_y, points_L, points_M, highlight_triangles=None):
    """
    Draws a diagram with two horizontal parallel lines, points on each, and specified triangles.
    Args:
        line1_y (float): Y-coordinate for the first horizontal line (L).
        line2_y (float): Y-coordinate for the second horizontal line (M).
        points_L (dict): Dictionary of points on line L, e.g., {'A': (x_A, y_A), 'B': (x_B, y_B)}.
        points_M (dict): Dictionary of points on line M, e.g., {'D': (x_D, y_D), 'E': (x_E, y_E)}.
        highlight_triangles (list of tuples): List of triangle vertex tuples to highlight, e.g., [('A', 'D', 'E')].
    Returns:
        str: base64 encoded image string.
    """
    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(-6, 6)
    ax.set_ylim(-5, 5)
    ax.axis('off')

    # Draw horizontal lines L and M
    ax.plot([-6, 6], [line1_y, line1_y], 'k-', lw=1.5)
    ax.plot([-6, 6], [line2_y, line2_y], 'k-', lw=1.5)
    ax.text(6.2, line1_y, 'L', va='center', ha='left', fontsize=12, bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.7))
    ax.text(6.2, line2_y, 'M', va='center', ha='left', fontsize=12, bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.7))

    all_points = {**points_L, **points_M}

    # Draw points and labels
    for name, (x, y) in all_points.items():
        ax.plot(x, y, 'ko', markersize=4)
        ax.text(x + 0.15, y + 0.15, name, fontsize=12, va='bottom', ha='left',
                bbox=dict(boxstyle="round,pad=0.1", fc='white', ec='none', alpha=0.8))

    # Draw and highlight triangles
    if highlight_triangles:
        for tri_vertices in highlight_triangles:
            if len(tri_vertices) == 3:
                p1 = all_points[tri_vertices[0]]
                p2 = all_points[tri_vertices[1]]
                p3 = all_points[tri_vertices[2]]

                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'b-', lw=1)
                ax.plot([p2[0], p3[0]], [p2[1], p3[1]], 'b-', lw=1)
                ax.plot([p3[0], p1[0]], [p3[1], p1[1]], 'b-', lw=1)
                
                triangle = patches.Polygon([p1, p2, p3], closed=True, color='lightblue', alpha=0.3)
                ax.add_patch(triangle)

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64

# 輔助函式：繪製RAG Ex 3所需的梯形與三角形面積圖
def _draw_trapezoid_triangle_area_diagram(A_coords, E_coords, B_coords, D_coords, C_coords):
    """
    Draws a diagram for the RAG Ex 3 type problem: AE // BD, C on BD.
    Args:
        A_coords (tuple): (x, y) coordinates for point A.
        E_coords (tuple): (x, y) coordinates for point E.
        B_coords (tuple): (x, y) coordinates for point B.
        D_coords (tuple): (x, y) coordinates for point D.
        C_coords (tuple): (x, y) coordinates for point C (on segment BD).
    Returns:
        str: base64 encoded image string.
    """
    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)
    ax.set_aspect('equal', adjustable='box')
    
    all_x = [A_coords[0], E_coords[0], B_coords[0], D_coords[0], C_coords[0]]
    all_y = [A_coords[1], E_coords[1], B_coords[1], D_coords[1], C_coords[1]]
    min_x, max_x = min(all_x) - 1, max(all_x) + 1
    min_y, max_y = min(all_y) - 1, max(all_y) + 1
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    ax.axis('off')

    points = {'A': A_coords, 'E': E_coords, 'B': B_coords, 'D': D_coords, 'C': C_coords}

    # Draw main segments AE and BD
    ax.plot([A_coords[0], E_coords[0]], [A_coords[1], E_coords[1]], 'k-', lw=1.5) # AE
    ax.plot([B_coords[0], D_coords[0]], [B_coords[1], D_coords[1]], 'k-', lw=1.5) # BD
    
    # Draw connecting segments to form the figure
    ax.plot([A_coords[0], B_coords[0]], [A_coords[1], B_coords[1]], 'k-', lw=1.5) # AB
    ax.plot([E_coords[0], D_coords[0]], [E_coords[1], D_coords[1]], 'k-', lw=1.5) # ED

    # Draw segment AC and CE for triangle ACE
    ax.plot([A_coords[0], C_coords[0]], [A_coords[1], C_coords[1]], 'k-', lw=1.5) # AC
    ax.plot([C_coords[0], E_coords[0]], [C_coords[1], E_coords[1]], 'k-', lw=1.5) # CE

    # Draw and label points
    for name, (x, y) in points.items():
        ax.plot(x, y, 'ko', markersize=4)
        ax.text(x + 0.15, y + 0.15, name, fontsize=12, va='bottom', ha='left',
                bbox=dict(boxstyle="round,pad=0.1", fc='white', ec='none', alpha=0.8))

    # Highlight triangle ABD and ACE
    tri_abd = patches.Polygon([A_coords, B_coords, D_coords], closed=True, color='lightgreen', alpha=0.3)
    ax.add_patch(tri_abd)
    tri_ace = patches.Polygon([A_coords, C_coords, E_coords], closed=True, color='lightblue', alpha=0.3)
    ax.add_patch(tri_ace)

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64


# 主生成函式
def generate(level=1):
    problem_type = random.choice([1, 2, 3])
    question_text = ""
    correct_answer = ""
    image_base64 = None
    solution_text = ""
    answer_display = ""

    if problem_type == 1:
        # Type 1 (Maps to RAG Example 1, 4, 5: Definition/Identification of Parallel Lines - True/False or Property)
        statements = [
            ("若兩直線永不相交，則稱這兩直線互相平行。", "是", "這是平行線的定義，敘述正確。"),
            ("兩直線被一截線所截，若同位角相等，則這兩直線互相平行。", "是", "這是判斷兩直線平行的重要條件之一，敘述正確。"),
            ("兩直線被一截線所截，若內錯角相等，則這兩直線互相平行。", "是", "這是判斷兩直線平行的重要條件之一，敘述正確。"),
            ("兩直線被一截線所截，若同側內角互補，則這兩直線互相平行。", "是", "這是判斷兩直線平行的重要條件之一，敘述正確。"),
            ("若兩直線互相平行，則它們之間的距離處處相等。", "是", "這是平行線的重要性質，敘述正確。"),
            ("若兩直線被一截線所截，且其同位角互補，則這兩直線互相平行。", "否", "同位角必須相等才能判斷平行，互補則不一定。"),
            ("若兩直線被一截線所截，且其內錯角互補，則這兩直線互相平行。", "否", "內錯角必須相等才能判斷平行，互補則不一定。"),
            ("若兩直線被一截線所截，且其同側內角相等，則這兩直線互相平行。", "否", "同側內角必須互補才能判斷平行，相等則不一定。"),
            ("長方形的四個內角都是 $90^\circ$，那麼長方形的對邊會互相平行嗎？", "是", "長方形的對邊互相平行，這是其性質之一，因為內角為90度，可推得同側內角互補。"), # RAG Ex 5
            ("在同一平面上，若兩直線都垂直於同一條直線，則這兩直線互相平行。", "是", "這是一個判斷兩直線平行的重要條件（同位角相等或同側內角互補）。"),
            ("在同一平面上有相異三直線 L1、L2、L3，若 L1⊥L2、L2⊥L3，則 L1 與 L3 有什麼關係？", "L1 // L3", "若兩直線都垂直於同一條直線，則這兩直線互相平行。"), # RAG Ex 4
        ]
        
        chosen_statement, correct_answer_val, solution_text = random.choice(statements)
        
        # Special handling for RAG Ex 4's question format
        if chosen_statement.startswith("在同一平面上有相異三直線"):
            question_text = chosen_statement
            correct_answer = correct_answer_val
            answer_display = correct_answer_val
        else:
            question_text = f"判斷以下敘述是否正確：{chosen_statement}"
            correct_answer = correct_answer_val
            answer_display = correct_answer_val

        image_base64 = None 

    elif problem_type == 2:
        # Type 2 (Maps to RAG Example 2: Triangle Area between Parallel Lines)
        # 如右圖，L // M，且 A、B、C 在直線 L 上，D、E 在直線 M 上，則△ADE、△BDE、△CDE 中，哪一個面積最大？ -> None
        
        line1_y = 3
        line2_y = -3

        x_A, x_B, x_C = sorted(random.sample(range(-4, 5), 3))
        x_D, x_E = sorted(random.sample(range(-4, 5), 2))

        points_L = {'A': (x_A, line1_y), 'B': (x_B, line1_y), 'C': (x_C, line1_y)}
        points_M = {'D': (x_D, line2_y), 'E': (x_E, line2_y)}

        highlight_triangles = [('A', 'D', 'E'), ('B', 'D', 'E'), ('C', 'D', 'E')]

        image_base64 = _draw_triangles_between_parallel_lines_diagram(
            line1_y, line2_y, points_L, points_M, highlight_triangles
        )
        
        question_text = r"如右圖，直線 $L // M$，且 $A、B、C$ 在直線 $L$ 上，$D、E$ 在直線 $M$ 上，則 $\triangle ADE、\triangle BDE、\triangle CDE$ 中，哪一個面積最大？"
        correct_answer = "面積一樣大"
        solution_text = "因為直線 $L // M$，所以 $L$ 與 $M$ 之間的距離處處相等。$\triangle ADE、\triangle BDE、\triangle CDE$ 都以 $\overline{DE}$ 為底，且它們的高都是 $L$ 與 $M$ 之間的距離，因此這三個三角形的面積都相等。"
        answer_display = correct_answer

    elif problem_type == 3:
        # Type 3 (Maps to RAG Example 3: Area calculation with AE // BD)
        # 如右圖，AE // BD，C 在 BD 上。若 AE=5，BD=8，△ABD 的面積為 24，則△ACE 的面積為多少？ -> C
        
        line_AE_y = random.randint(2, 4)
        line_BD_y = random.randint(-4, -2)

        x_A = random.randint(-4, -2)
        x_E = x_A + random.randint(4, 7) # AE_length
        
        x_B = random.randint(-4, -2)
        x_D = x_B + random.randint(7, 10) # BD_length

        A_coords = (x_A, line_AE_y)
        E_coords = (x_E, line_AE_y)
        B_coords = (x_B, line_BD_y)
        D_coords = (x_D, line_BD_y)

        # C is on BD, with 0.5 precision for coordinates
        min_x_BD = min(x_B, x_D)
        max_x_BD = max(x_B, x_D)
        
        # Ensure C is strictly between B and D
        if max_x_BD - min_x_BD < 1: # If segment is too short, adjust for C to be distinct
            x_C = min_x_BD + 0.5
        else:
            x_C = round(random.uniform(min_x_BD + 0.5, max_x_BD - 0.5) * 2) / 2
            # If rounding causes C to be on B or D, re-roll or adjust slightly
            if x_C == min_x_BD: x_C += 0.5
            if x_C == max_x_BD: x_C -= 0.5

        C_coords = (x_C, line_BD_y)

        h = abs(line_AE_y - line_BD_y)

        actual_BD_length = abs(D_coords[0] - B_coords[0])
        area_ABD = round(0.5 * actual_BD_length * h)
        if area_ABD == 0: area_ABD = h # Ensure non-zero area if lengths are small after rounding
        
        actual_AE_length = abs(E_coords[0] - A_coords[0])

        correct_area_ACE = int(round(0.5 * actual_AE_length * h))
        if correct_area_ACE == 0: correct_area_ACE = h # Ensure non-zero area

        image_base64 = _draw_trapezoid_triangle_area_diagram(A_coords, E_coords, B_coords, D_coords, C_coords)

        question_text_template = r"如右圖，已知 $AE // BD$，點 $C$ 在 $\overline{BD}$ 上。若 $\overline{AE}={ae_val}$，$\overline{BD}={bd_val}$，$\triangle ABD$ 的面積為 ${area_abd_val}$，則 $\triangle ACE$ 的面積為多少？"
        question_text = question_text_template.replace("{ae_val}", str(actual_AE_length)) \
                                             .replace("{bd_val}", str(actual_BD_length)) \
                                             .replace("{area_abd_val}", str(area_ABD))

        correct_answer = str(correct_area_ACE)
        answer_display = correct_answer
        solution_text = f"因為 $AE // BD$，所以直線 $AE$ 與直線 $BD$ 之間的距離處處相等。設此距離為 $h$。\n已知 $\\triangle ABD$ 的面積為 {area_ABD}，且 $\overline{BD}={actual_BD_length}$。\n所以 $0.5 \\times \\overline{BD} \\times h = {area_ABD}$ \n$0.5 \\times {actual_BD_length} \\times h = {area_ABD}$ \n$h = {area_ABD} / (0.5 \\times {actual_BD_length}) = {h}$。\n$\\triangle ACE$ 以 $\overline{AE}$ 為底，高為 $h$。\n所以 $\\triangle ACE$ 的面積 $= 0.5 \\times \\overline{AE} \\times h = 0.5 \\times {actual_AE_length} \\times {h} = {correct_area_ACE}$。"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "solution": solution_text,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "18.9"
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
