# ==============================================================================
# ID: jh_數學2下_TriangleCongruenceProperties
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 123.66s | RAG: 5 examples
# Created At: 2026-01-23 14:35:55
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



import base64
import io
import matplotlib.pyplot as plt
import numpy as np
import re
from datetime import datetime

# --- Helper Functions ---

def _generate_coordinate_value(min_val, max_val, allow_fraction=False):
    """
    功能: 生成一個座標值,可以是整數或半整數（若 allow_fraction=True）
    回傳格式: (float_val, (int_part, num, den, is_neg))
    規範:
        - random.randint(min_val, max_val) 生成整數部分
        - 若 allow_fraction 且隨機條件滿足,則生成 0.5 的分數部分 (num=1, den=2)
        - 若為整數,num 與 den 設為 0
        - 若為分數,必須檢查 numerator < denominator 且 denominator > 1 (V13.1 禁絕假分數)
    """
    int_part = random.randint(min_val, max_val)
    float_val = float(int_part)
    num, den = 0, 0
    is_neg = int_part < 0

    # For K12, only 0.5 fractions are generally considered "allow_fraction"
    if allow_fraction and random.random() < 0.5:
        float_val += 0.5 if int_part >= 0 else -0.5
        num = 1
        den = 2
    
    return (float_val, (int_part, num, den, is_neg))

def _format_coordinate(coord_data):
    """
    功能: 將 _generate_coordinate_value 的回傳格式轉換為字串
    規範:
        - 若為整數，使用 str(int(float_val)) 確保輸出如 "5" 而非 "5.0" (V13.0)
        - 若為分數,使用 LaTeX 格式 \frac{n}{d} 或帶分數格式
        - LaTeX 模板必須使用單層大括號 (V10.2 C)
    """
    float_val, (int_part, num, den, is_neg) = coord_data
    if num == 0: # It's an integer
        return str(int(float_val))
    else: # It's a fraction (e.g., X.5, which is int_part + 0.5)
        abs_int_part = abs(int_part)
        frac_str = r"\frac{{{}}}{{{}}}".replace("{n}", str(num)).replace("{d}", str(den))
        
        if abs_int_part == 0:
            # Pure fraction like 1/2, -1/2
            return ("-" if is_neg and float_val != 0 else "") + frac_str
        else:
            # Mixed fraction like 1 1/2, -1 1/2
            return ("-" if is_neg else "") + str(abs_int_part) + frac_str

def _calculate_distance(p1, p2):
    """
    功能: 計算兩點 p1(x1, y1) 和 p2(x2, y2) 之間的歐幾里得距離
    回傳: 浮點數
    """
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def _calculate_angle(p1, p_vertex, p2):
    """
    功能: 使用餘弦定理計算以 p_vertex 為頂點的夾角
    回傳: 角度（浮點數,單位度）
    """
    v1 = np.array(p1) - np.array(p_vertex)
    v2 = np.array(p2) - np.array(p_vertex)
    
    dot_product = np.dot(v1, v2)
    magnitudes = np.linalg.norm(v1) * np.linalg.norm(v2)
    
    if magnitudes == 0:
        return 0 # Degenerate case
    
    cosine_angle = dot_product / magnitudes
    # Clip to avoid floating point errors leading to domain issues for arccos
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    
    angle_radians = np.arccos(cosine_angle)
    return np.degrees(angle_radians)

def _rotate_point(point, angle_degrees, origin=(0, 0)):
    """
    功能: 將點 point 繞 origin 旋轉 angle_degrees
    回傳: 新的座標 (qx, qy)
    """
    ox, oy = origin
    px, py = point

    angle_radians = math.radians(angle_degrees)
    
    qx = ox + math.cos(angle_radians) * (px - ox) - math.sin(angle_radians) * (py - oy)
    qy = oy + math.sin(angle_radians) * (px - ox) + math.cos(angle_radians) * (py - oy)
    
    return (round(qx, 2), round(qy, 2)) # Round to handle float precision, though with 90/180/270 it will be integers

def _reflect_point(point, axis='y'):
    """
    功能: 將點 point 沿指定軸 ('x' 或 'y') 反射
    回傳: 新的座標 (qx, qy)
    """
    px, py = point
    if axis == 'y': # Reflect across y-axis (x -> -x)
        return (-px, py)
    elif axis == 'x': # Reflect across x-axis (y -> -y)
        return (px, -py)
    return point # No reflection

def _mark_side(ax, p1, p2, marks, color):
    """
    功能: 在圖形上標記邊的等長符號（例如:一條線段或多條短線）
    參數: ax (matplotlib axes), p1, p2 (邊的兩端點), marks (標記數量,如 1, 2, 3), color
    """
    mid_x, mid_y = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length == 0: return

    unit_dx, unit_dy = dx / length, dy / length
    perp_dx, perp_dy = -unit_dy, unit_dx # Perpendicular vector

    offset = 0.15 # Offset from the side
    mark_len = 0.2 # Length of each mark
    spacing = 0.1 # Spacing between multiple marks

    for i in range(marks):
        mark_center_offset = (i - (marks - 1) / 2) * spacing
        mx = mid_x + mark_center_offset * unit_dx + offset * perp_dx
        my = mid_y + mark_center_offset * unit_dy + offset * perp_dy
        
        mark_p1 = (mx - mark_len / 2 * perp_dx, my - mark_len / 2 * perp_dy)
        mark_p2 = (mx + mark_len / 2 * perp_dx, my + mark_len / 2 * perp_dy)
        
        ax.plot([mark_p1[0], mark_p2[0]], [mark_p1[1], mark_p2[1]], color=color, linewidth=1.5)

def _mark_angle(ax, points, vertex_idx, marks, color):
    """
    功能: 在圖形上標記角的等角符號（例如:一個或多個弧線）
    參數: ax (matplotlib axes), points (三角形所有點的列表), vertex_idx (頂點在 points 中的索引), marks (標記數量,如 1, 2, 3), color
    """
    p_prev = np.array(points[(vertex_idx - 1) % len(points)])
    p_vertex = np.array(points[vertex_idx])
    p_next = np.array(points[(vertex_idx + 1) % len(points)])

    v1 = p_prev - p_vertex
    v2 = p_next - p_vertex

    angle_radians = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    angle_degrees = np.degrees(angle_radians)

    radius = 0.8
    
    if math.isclose(angle_degrees, 90, abs_tol=0.1):
        # Right angle mark
        v1_scaled = v1 / np.linalg.norm(v1) * radius * 0.6
        v2_scaled = v2 / np.linalg.norm(v2) * radius * 0.6
        
        p_v1_arm = p_vertex + v1_scaled
        p_v2_arm = p_vertex + v2_scaled
        p_corner = p_vertex + v1_scaled + v2_scaled
        
        ax.plot([p_v1_arm[0], p_corner[0], p_v2_arm[0]], 
                [p_v1_arm[1], p_corner[1], p_v2_arm[1]], color=color, linewidth=1.5)
    else:
        # Arc marks for other angles
        angle_start_rad = np.arctan2(v1[1], v1[0])
        angle_end_rad = np.arctan2(v2[1], v2[0])

        if angle_end_rad < angle_start_rad:
            angle_end_rad += 2 * np.pi
        
        # Adjust for interior angle if reflex angle is calculated
        if angle_end_rad - angle_start_rad > np.pi + 1e-6:
            angle_start_rad, angle_end_rad = angle_end_rad - 2*np.pi, angle_start_rad

        arc_spacing = 0.08
        for i in range(marks):
            current_radius = radius + (i - (marks - 1) / 2) * arc_spacing
            num_segments = 50
            theta = np.linspace(angle_start_rad, angle_end_rad, num_segments)
            x_arc = p_vertex[0] + current_radius * np.cos(theta)
            y_arc = p_vertex[1] + current_radius * np.sin(theta)
            ax.plot(x_arc, y_arc, color=color, linewidth=1.5)

def draw_triangle_congruence(points1, labels1, points2, labels2, marked_sides1, marked_angles1, marked_sides2, marked_angles2):
    """
    功能: 繪製兩個三角形及其標籤、等長/等角標記
    規範: 遵循所有視覺標準 (V6, V10.2 D, V13.0, V13.5, V13.6, CRITICAL RULE: Visual Solvability, V11.6)
    """
    fig, ax = plt.subplots(figsize=(8, 8), dpi=300)
    
    max_coord = 8
    ax.set_xlim(-max_coord, max_coord)
    ax.set_ylim(-max_coord, max_coord)
    ax.set_aspect('equal') # V11.6
    ax.grid(True, linestyle='--', alpha=0.6)

    # Set ticks for all integers within range (CRITICAL RULE: Visual Solvability, Mandatory Axis Ticks)
    ax.set_xticks(range(-max_coord, max_coord + 1))
    ax.set_yticks(range(-max_coord, max_coord + 1))
    ax.tick_params(axis='both', which='major', labelsize=12)

    # Hide default tick labels but show '0' (V10.2 D)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.text(0, 0, '0', color='black', ha='center', va='center', fontsize=18, fontweight='bold', # V10.2 D
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))

    # Draw axis lines and arrows (V13.6, Axis Visibility)
    # Hide default spines and draw custom lines and arrows
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    
    # X-axis arrow
    ax.plot(max_coord, 0, ">k", clip_on=False, markersize=8)
    # Y-axis arrow
    ax.plot(0, max_coord, "^k", clip_on=False, markersize=8)

    # Hide axis labels
    ax.set_xlabel('')
    ax.set_ylabel('')

    # Draw triangles and labels
    for i, (points, labels) in enumerate([(points1, labels1), (points2, labels2)]):
        color = 'blue' if i == 0 else 'red'
        # Draw sides
        for j in range(len(points)):
            p1 = points[j]
            p2 = points[(j + 1) % len(points)]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=2)
        
        # Draw points and labels (V13.0, V13.1, V13.5)
        for j, p in enumerate(points):
            ax.plot(p[0], p[1], 'o', color=color, markersize=5)
            ax.text(p[0] + 0.3, p[1] + 0.3, labels[j], color='black', fontsize=14, fontweight='bold',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2')) # V10.2 D
    
    # Apply marks
    for points, marked_sides, marked_angles, color in [
        (points1, marked_sides1, marked_angles1, 'blue'),
        (points2, marked_sides2, marked_angles2, 'red')
    ]:
        for p1_idx, p2_idx, marks in marked_sides:
            _mark_side(ax, points[p1_idx], points[p2_idx], marks, color)
        for vertex_idx, marks in marked_angles:
            _mark_angle(ax, points, vertex_idx, marks, color)

    plt.tight_layout()
    
    # Convert plot to base64 image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    
    return image_base64


# --- Generate Function ---

def generate(level=1):
    """
    功能: 生成三角形全等性質的題目
    隨機分流 (Problem Mirroring): 內部使用 random.choice 隨機選擇一種全等類型來構造題目
    """
    problem_types = ["SSS_missing_side", "SAS_missing_angle", "ASA_missing_side", "AAS_missing_angle", "RHS_missing_side"]
    problem_type = random.choice(problem_types)

    # Labels for triangles
    labels1 = ['A', 'B', 'C']
    labels2 = ['D', 'E', 'F']

    # Generate points for triangle ABC
    def generate_non_degenerate_triangle_coords_and_check_range():
        while True:
            if problem_type == "RHS_missing_side":
                # For RHS, ensure a right angle at A for ABC
                # A=(x1,y1), B=(x2,y1), C=(x1,y2) to guarantee a right angle at A.
                x1 = _generate_coordinate_value(-4, 4, allow_fraction=False)[0]
                y1 = _generate_coordinate_value(-4, 4, allow_fraction=False)[0]
                
                # Ensure legs have non-zero length and points are distinct
                x2 = x1
                while x2 == x1:
                    x2 = _generate_coordinate_value(x1 - 3, x1 + 3, allow_fraction=False)[0]
                
                y2 = y1
                while y2 == y1:
                    y2 = _generate_coordinate_value(y1 - 3, y1 + 3, allow_fraction=False)[0]

                pA = (x1, y1)
                pB = (x2, y1)
                pC = (x1, y2)
            else:
                pA = (_generate_coordinate_value(-5, 5, allow_fraction=False)[0], _generate_coordinate_value(-5, 5, allow_fraction=False)[0])
                pB = (_generate_coordinate_value(-5, 5, allow_fraction=False)[0], _generate_coordinate_value(-5, 5, allow_fraction=False)[0])
                pC = (_generate_coordinate_value(-5, 5, allow_fraction=False)[0], _generate_coordinate_value(-5, 5, allow_fraction=False)[0])

            # Check for non-degenerate (non-zero area)
            area = 0.5 * abs(pA[0]*(pB[1]-pC[1]) + pB[0]*(pC[1]-pA[1]) + pC[0]*(pA[1]-pB[1]))
            if area > 0.5: # Small positive area to avoid near-degenerate triangles
                # Generate points for triangle DEF by transformation
                current_points1 = [pA, pB, pC]
                
                # Apply rotation
                rotation_angle = random.choice([0, 90, 180, 270])
                rotated_points = [_rotate_point(p, rotation_angle) for p in current_points1]

                # Apply reflection (optional)
                if random.random() < 0.5: # 50% chance to reflect
                    reflection_axis = random.choice(['x', 'y'])
                    current_points2 = [_reflect_point(p, reflection_axis) for p in rotated_points]
                else:
                    current_points2 = rotated_points
                
                # Ensure all coordinates are within displayable range [-7, 7]
                all_coords = [c for p in current_points1 + current_points2 for c in p]
                if all(abs(c) <= 7 for c in all_coords): # Max coord for plot is 8, so points up to 7 is safe
                    return current_points1, current_points2
    
    points1_raw, points2_raw = generate_non_degenerate_triangle_coords_and_check_range()
    
    # Calculate sides and angles for both triangles
    # Sides: AB, BC, CA ; DE, EF, FD (corresponding order)
    sides1 = [
        _calculate_distance(points1_raw[0], points1_raw[1]), # AB
        _calculate_distance(points1_raw[1], points1_raw[2]), # BC
        _calculate_distance(points1_raw[2], points1_raw[0])  # CA
    ]
    sides2 = [
        _calculate_distance(points2_raw[0], points2_raw[1]), # DE
        _calculate_distance(points2_raw[1], points2_raw[2]), # EF
        _calculate_distance(points2_raw[2], points2_raw[0])  # FD
    ]

    # Angles: A, B, C ; D, E, F (corresponding order)
    angles1 = [
        _calculate_angle(points1_raw[2], points1_raw[0], points1_raw[1]), # Angle A
        _calculate_angle(points1_raw[0], points1_raw[1], points1_raw[2]), # Angle B
        _calculate_angle(points1_raw[1], points1_raw[2], points1_raw[0])  # Angle C
    ]
    angles2 = [
        _calculate_angle(points2_raw[2], points2_raw[0], points2_raw[1]), # Angle D
        _calculate_angle(points2_raw[0], points2_raw[1], points2_raw[2]), # Angle E
        _calculate_angle(points2_raw[1], points2_raw[2], points2_raw[0])  # Angle F
    ]

    question_text = ""
    correct_answer = ""
    solution_steps = []
    
    # Marked conditions for drawing (p1_idx, p2_idx, marks) for sides, (vertex_idx, marks) for angles
    marked_sides1 = [] 
    marked_angles1 = [] 
    marked_sides2 = []
    marked_angles2 = []

    # Randomly assign marks (1, 2, or 3) for visual distinction
    mark1 = random.randint(1, 3)
    mark2 = random.randint(1, 3)
    mark3 = random.randint(1, 3)

    if problem_type == "SSS_missing_side":
        # Given: AB, BC, CA for ABC. DE, EF for DEF. Ask for FD.
        marked_sides1.append((0,1, mark1)) # AB
        marked_sides1.append((1,2, mark2)) # BC
        marked_sides1.append((2,0, mark3)) # CA

        marked_sides2.append((0,1, mark1)) # DE
        marked_sides2.append((1,2, mark2)) # EF
        marked_sides2.append((2,0, mark3)) # FD

        question_text = r"已知△ABC 與△DEF，其各邊長度如右圖所示。若$AB={AB_val}$，$BC={BC_val}$，$CA={CA_val}$。且$DE={DE_val}$，$EF={EF_val}$。試問：$FD$的長度為何？".replace(
            "{AB_val}", str(round(sides1[0], 2))
        ).replace(
            "{BC_val}", str(round(sides1[1], 2))
        ).replace(
            "{CA_val}", str(round(sides1[2], 2))
        ).replace(
            "{DE_val}", str(round(sides2[0], 2))
        ).replace(
            "{EF_val}", str(round(sides2[1], 2))
        )
        correct_answer = str(round(sides2[2], 2)) # FD corresponds to CA
        solution_steps = [
            r"由已知條件可知：$AB={AB_val}$，$BC={BC_val}$，$CA={CA_val}$。".replace("{AB_val}", str(round(sides1[0], 2))).replace("{BC_val}", str(round(sides1[1], 2))).replace("{CA_val}", str(round(sides1[2], 2))),
            r"且$DE={DE_val}$，$EF={EF_val}$。".replace("{DE_val}", str(round(sides2[0], 2))).replace("{EF_val}", str(round(sides2[1], 2))),
            r"根據圖中標記，可推斷出$AB=DE$，$BC=EF$，$CA=FD$。",
            r"因此，根據SSS全等性質，△ABC ≅ △DEF。",
            r"所以$FD$的長度應與$CA$的長度相等，即$FD = {CA_val} = {answer}$。".replace("{CA_val}", str(round(sides1[2], 2))).replace("{answer}", correct_answer)
        ]

    elif problem_type == "SAS_missing_angle":
        # Given: AB, BC, Angle B for ABC. DE, EF, Angle E for DEF. Ask for Angle F.
        marked_sides1.append((0,1, mark1)) # AB
        marked_sides1.append((1,2, mark2)) # BC
        marked_angles1.append((1, mark3)) # Angle B

        marked_sides2.append((0,1, mark1)) # DE
        marked_sides2.append((1,2, mark2)) # EF
        marked_angles2.append((1, mark3)) # Angle E
        
        question_text = r"已知△ABC 與△DEF，其部分邊長與角度如右圖所示。若$AB={AB_val}$，$BC={BC_val}$，$\angle B={B_val}^\circ$。且$DE={DE_val}$，$EF={EF_val}$，$\angle E={E_val}^\circ$。試問：$\angle F$的度數為何？".replace(
            "{AB_val}", str(round(sides1[0], 2))
        ).replace(
            "{BC_val}", str(round(sides1[1], 2))
        ).replace(
            "{B_val}", str(round(angles1[1], 2))
        ).replace(
            "{DE_val}", str(round(sides2[0], 2))
        ).replace(
            "{EF_val}", str(round(sides2[1], 2))
        ).replace(
            "{E_val}", str(round(angles2[1], 2))
        )
        correct_answer = str(round(angles2[2], 2)) # Angle F corresponds to Angle C
        solution_steps = [
            r"由已知條件可知：$AB={AB_val}$，$BC={BC_val}$，$\angle B={B_val}^\circ$。".replace("{AB_val}", str(round(sides1[0], 2))).replace("{BC_val}", str(round(sides1[1], 2))).replace("{B_val}", str(round(angles1[1], 2))),
            r"且$DE={DE_val}$，$EF={EF_val}$，$\angle E={E_val}^\circ$。".replace("{DE_val}", str(round(sides2[0], 2))).replace("{EF_val}", str(round(sides2[1], 2))).replace("{E_val}", str(round(angles2[1], 2))),
            r"根據圖中標記，可推斷出$AB=DE$，$BC=EF$，以及夾角$\angle B = \angle E$。",
            r"因此，根據SAS全等性質，△ABC ≅ △DEF。",
            r"所以$\angle F$的度數應與$\angle C$的度數相等，即$\angle F = \angle C = {C_val}^\circ = {answer}^\circ$。".replace("{C_val}", str(round(angles1[2], 2))).replace("{answer}", correct_answer)
        ]

    elif problem_type == "ASA_missing_side":
        # Given: Angle B, BC, Angle C for ABC. Angle E, EF, Angle F for DEF. Ask for FD.
        marked_angles1.append((1, mark1)) # Angle B
        marked_sides1.append((1,2, mark2)) # BC
        marked_angles1.append((2, mark3)) # Angle C

        marked_angles2.append((1, mark1)) # Angle E
        marked_sides2.append((1,2, mark2)) # EF
        marked_angles2.append((2, mark3)) # Angle F
        
        question_text = r"已知△ABC 與△DEF，其部分邊長與角度如右圖所示。若$\angle B={B_val}^\circ$，$BC={BC_val}$，$\angle C={C_val}^\circ$。且$\angle E={E_val}^\circ$，$EF={EF_val}$，$\angle F={F_val}^\circ$。試問：$FD$的長度為何？".replace(
            "{B_val}", str(round(angles1[1], 2))
        ).replace(
            "{BC_val}", str(round(sides1[1], 2))
        ).replace(
            "{C_val}", str(round(angles1[2], 2))
        ).replace(
            "{E_val}", str(round(angles2[1], 2))
        ).replace(
            "{EF_val}", str(round(sides2[1], 2))
        ).replace(
            "{F_val}", str(round(angles2[2], 2))
        )
        correct_answer = str(round(sides2[2], 2)) # FD corresponds to CA
        solution_steps = [
            r"由已知條件可知：$\angle B={B_val}^\circ$，$BC={BC_val}$，$\angle C={C_val}^\circ$。".replace("{B_val}", str(round(angles1[1], 2))).replace("{BC_val}", str(round(sides1[1], 2))).replace("{C_val}", str(round(angles1[2], 2))),
            r"且$\angle E={E_val}^\circ$，$EF={EF_val}$，$\angle F={F_val}^\circ$。".replace("{E_val}", str(round(angles2[1], 2))).replace("{EF_val}", str(round(sides2[1], 2))).replace("{F_val}", str(round(angles2[2], 2))),
            r"根據圖中標記，可推斷出$\angle B = \angle E$，$\angle C = \angle F$，以及夾邊$BC=EF$。",
            r"因此，根據ASA全等性質，△ABC ≅ △DEF。",
            r"所以$FD$的長度應與$CA$的長度相等，即$FD = CA = {CA_val} = {answer}$。".replace("{CA_val}", str(round(sides1[2], 2))).replace("{answer}", correct_answer)
        ]

    elif problem_type == "AAS_missing_angle":
        # Given: Angle A, Angle B, BC for ABC. Angle D, Angle E, EF for DEF. Ask for Angle F.
        marked_angles1.append((0, mark1)) # Angle A
        marked_angles1.append((1, mark2)) # Angle B
        marked_sides1.append((1,2, mark3)) # BC (non-included)

        marked_angles2.append((0, mark1)) # Angle D
        marked_angles2.append((1, mark2)) # Angle E
        marked_sides2.append((1,2, mark3)) # EF (non-included)
        
        question_text = r"已知△ABC 與△DEF，其部分邊長與角度如右圖所示。若$\angle A={A_val}^\circ$，$\angle B={B_val}^\circ$，$BC={BC_val}$。且$\angle D={D_val}^\circ$，$\angle E={E_val}^\circ$，$EF={EF_val}$。試問：$\angle F$的度數為何？".replace(
            "{A_val}", str(round(angles1[0], 2))
        ).replace(
            "{B_val}", str(round(angles1[1], 2))
        ).replace(
            "{BC_val}", str(round(sides1[1], 2))
        ).replace(
            "{D_val}", str(round(angles2[0], 2))
        ).replace(
            "{E_val}", str(round(angles2[1], 2))
        ).replace(
            "{EF_val}", str(round(sides2[1], 2))
        )
        correct_answer = str(round(angles2[2], 2)) # Angle F corresponds to Angle C
        solution_steps = [
            r"由已知條件可知：$\angle A={A_val}^\circ$，$\angle B={B_val}^\circ$，$BC={BC_val}$。".replace("{A_val}", str(round(angles1[0], 2))).replace("{B_val}", str(round(angles1[1], 2))).replace("{BC_val}", str(round(sides1[1], 2))),
            r"且$\angle D={D_val}^\circ$，$\angle E={E_val}^\circ$，$EF={EF_val}$。".replace("{D_val}", str(round(angles2[0], 2))).replace("{E_val}", str(round(angles2[1], 2))).replace("{EF_val}", str(round(sides2[1], 2))),
            r"根據圖中標記，可推斷出$\angle A = \angle D$，$\angle B = \angle E$，以及對應邊$BC=EF$。",
            r"因此，根據AAS全等性質，△ABC ≅ △DEF。",
            r"所以$\angle F$的度數應與$\angle C$的度數相等，即$\angle F = \angle C = {C_val}^\circ = {answer}^\circ$。".replace("{C_val}", str(round(angles1[2], 2))).replace("{answer}", correct_answer)
        ]

    elif problem_type == "RHS_missing_side":
        # Given: Angle A = Angle D = 90, BC=EF (hypotenuse), AB=DE (leg). Ask for FD.
        # Vertex 0 (A) is the right angle for ABC, and Vertex 0 (D) for DEF.
        marked_angles1.append((0, 1)) # Angle A is 90 degrees (single mark for right angle)
        marked_sides1.append((1,2, mark1)) # BC (hypotenuse)
        marked_sides1.append((0,1, mark2)) # AB (leg)

        marked_angles2.append((0, 1)) # Angle D is 90 degrees
        marked_sides2.append((1,2, mark1)) # EF (hypotenuse)
        marked_sides2.append((0,1, mark2)) # DE (leg)
        
        question_text = r"已知△ABC 與△DEF 皆為直角三角形，其部分邊長如右圖所示。若直角$\angle A=90^\circ$，$BC={BC_val}$，$AB={AB_val}$。且直角$\angle D=90^\circ$，$EF={EF_val}$，$DE={DE_val}$。試問：$FD$的長度為何？".replace(
            "{BC_val}", str(round(sides1[1], 2))
        ).replace(
            "{AB_val}", str(round(sides1[0], 2))
        ).replace(
            "{EF_val}", str(round(sides2[1], 2))
        ).replace(
            "{DE_val}", str(round(sides2[0], 2))
        )
        correct_answer = str(round(sides2[2], 2)) # FD corresponds to CA
        solution_steps = [
            r"由已知條件可知：△ABC 與△DEF 皆為直角三角形，直角$\angle A=90^\circ$，直角$\angle D=90^\circ$。",
            r"且斜邊$BC={BC_val}$，一股$AB={AB_val}$。對應斜邊$EF={EF_val}$，一股$DE={DE_val}$。".replace("{BC_val}", str(round(sides1[1], 2))).replace("{AB_val}", str(round(sides1[0], 2))).replace("{EF_val}", str(round(sides2[1], 2))).replace("{DE_val}", str(round(sides2[0], 2))),
            r"根據圖中標記，可推斷出斜邊$BC=EF$，一股$AB=DE$。",
            r"因此，根據RHS全等性質（斜邊及一股），△ABC ≅ △DEF。",
            r"所以$FD$的長度應與$CA$的長度相等，即$FD = CA = {CA_val} = {answer}$。".replace("{CA_val}", str(round(sides1[2], 2))).replace("{answer}", correct_answer)
        ]

    image_base64 = draw_triangle_congruence(
        points1_raw, labels1, points2_raw, labels2,
        marked_sides1, marked_angles1, marked_sides2, marked_angles2
    )

    return {
        "skill_id": "jh_數學2下_TriangleCongruenceProperties",
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "\n".join(solution_steps),
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


# --- Check Function ---


    """
    強韌閱卷邏輯 (Robust Check Logic):
    1. 輸入清洗 (Input Sanitization): 使用 Regex 移除使用者輸入中的 LaTeX 符號、變數前綴、所有空白字元
    2. 數值序列比對 (Numerical Sequence Comparison): 轉換為浮點數,使用 math.isclose 進行模糊比對
    3. 降級為字串比對: 若數值比對失敗,則進行字串比對
    """
    import re, math
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=
        s = s.replace("$", "").replace("\\", "")
        # Additional cleaning for specific LaTeX commands if they somehow remain
        s = s.replace("frac", "").replace("{", "").replace("}", "")
        return s
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 嘗試數值比對 (支援分數與小數)
    try:
        def parse_val(val_str):
            if "/" in val_str:
                n, d = map(float, val_str.split("/"))
                return n/d
            return float(val_str)
        
        if math.isclose(parse_val(u), parse_val(c), rel_tol=1e-5, abs_tol=1e-5):
            return {"correct": True, "result": "正確！"}
    except:
        pass
        
    # 3. 降級為字串比對
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
