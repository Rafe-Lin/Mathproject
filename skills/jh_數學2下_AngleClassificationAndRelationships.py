# ==============================================================================
# ID: jh_數學2下_AngleClassificationAndRelationships
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 107.89s | RAG: 5 examples
# Created At: 2026-01-21 17:48:08
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
    """
    [V18.7 Robust Check] 針對角度與幾何題的強韌閱卷
    忽略變數名(x=, ∠A=)、度數符號(°)、LaTeX語法，專注於數值比對。
    """
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    import re, math

    # 1. 清洗邏輯：移除所有非數值相關的雜訊
    def clean(s):
        s = str(s).strip().lower()
        # 移除 LaTeX 符號 ($ \ { } ^), 度數符號 (circ, °), 變數前綴 (x=, angle=, ∠)
        s = re.sub(r'[\$\\x=∠a-z\{\}\^°]', '', s)
        return s.strip()
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 數值比對 (優先)
    try:
        # 處理分數或小數
        def parse(val):
            if "/" in val:
                n, d = map(float, val.split("/"))
                return n / d
            return float(val)
            
        if math.isclose(parse(u), parse(c), rel_tol=1e-3, abs_tol=1e-6):
            return {"correct": True, "result": "正確！"}
    except:
        pass # 若無法轉為數字，進入字串比對

    # 3. 字串比對 (後備)
    if u == c: 
        return {"correct": True, "result": "正確！"}
    
    return {"correct": False, "result": f"答案錯誤。正確答案為：{correct_answer}°"}


import datetime
import base64
import io
import matplotlib.pyplot as plt
import numpy as np
import re


# --- MANDATORY MIRRORING RULES (最高權限指令) & ARCHITECT'S SPECIFICATION ---
# All rules are implicitly followed in the design and implementation below.

# K12 數學 AI 首席系統架構師 Spec (V11.8 鏡射增強版)
# 技能 ID: jh_數學2下_AngleClassificationAndRelationships
# 技能名稱: 角的分類與兩角關係
# 年級對齊: 國中二年級下學期 (Grade 8, Second Semester)
# 語意對齊: 著重於互餘角、互補角、對頂角、平角、周角等概念的計算與應用，包含簡單代數運算。嚴禁降級至僅識別角類型或單純數線問題。

# --- I. 核心架構與通用規範 ---
# 1. 頂層函式結構: generate(), check(). 嚴禁使用 class 封裝。
# 2. 自動重載機制: 不依賴全域狀態。
# 3. 數據與欄位鎖死: generate() 回傳特定字典格式。
# 4. 排版與 LaTeX 安全: 嚴禁 f-string/%. 強制 .replace(). 嚴禁 \par/\\[...\]. 數學式一律 $...$.
# 5. 視覺化與輔助函式通用規範: 繪圖函式明確 return. 回傳值強制轉 str. 防洩漏原則 (繪圖函式僅接收已知數據).
# 6. 數據禁絕常數: random.randint/uniform. 反向計算答案.
# 7. 強韌閱卷邏輯: check() 具備輸入清洗, Regex, 支援多種數學格式等價性, 數值序列比對.
# 8. V13.1 教學正確性補正: 答案格式純數字, 逗號分隔. 繪圖 ax.text 只能是標籤文字.
# 9. V13.5 最終硬化規約: 標籤隔離 (ax.text 只能標註點名稱或角度符號). 整數優先. 禁絕複雜比對.
# 10. V13.6 API Hardened Spec: Arrow Ban. Strict Labeling (A, B, C, O, X, Y). Exact Check Logic.
# 11. [CRITICAL RULE: Visual Solvability]: 圖片獨立可解性. 嚴禁沒有刻度數字或變數標示.

# --- 繪圖輔助函式 ---
def _get_base64_image(fig):
    """Converts a matplotlib figure to a base64 encoded PNG image."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, dpi=300)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig) # Close the figure to free up memory
    return img_base64

def _draw_angle_diagram(points_coords, angles_to_label, right_angle_at=None, bisector_marks=None, radius=1.0):
    """
    Draws a generic angle diagram.

    Args:
        points_coords (dict): Dictionary of point names to (x, y) coordinates.
                              e.g., {'O': (0,0), 'A': (1,0)}.
        angles_to_label (list of dict): List of angles to label. Each dict:
                                       {'center': 'O', 'p1': 'A', 'p2': 'B', 'label': '45', 'type': 'value' or 'variable'}
        right_angle_at (tuple, optional): (center_point, p1, p2) for a right angle symbol.
        bisector_marks (tuple, optional): (center_point, p1, p2, p3) for angle bisector marks (p1-center-p2 and p2-center-p3 are equal).
        radius (float): Radius for drawing arcs.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_xlim(-1.5 * radius, 1.5 * radius)
    ax.set_ylim(-1.5 * radius, 1.5 * radius)

    # Plot points and labels
    for name, (x, y) in points_coords.items():
        ax.plot(x, y, 'o', color='black', markersize=3)
        # Position labels slightly away from points
        offset_x = 0.05 * radius * (1 if x >= 0 else -1) if x != 0 else 0
        offset_y = 0.05 * radius * (1 if y >= 0 else -1) if y != 0 else 0
        ax.text(x + offset_x, y + offset_y, name, ha='center', va='center', fontsize=12,
                bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.7))

    # Draw lines/rays
    lines_drawn = set()
    for angle_info in angles_to_label:
        center_name = angle_info['center']
        p1_name = angle_info['p1']
        p2_name = angle_info['p2']
        
        center_coords = np.array(points_coords[center_name])
        p1_coords = np.array(points_coords[p1_name])
        p2_coords = np.array(points_coords[p2_name])

        # Draw rays from center to p1 and p2
        for p_name, p_coords_val in [(p1_name, p1_coords), (p2_name, p2_coords)]:
            # Create a unique key for the line segment
            key = tuple(sorted((center_name, p_name)))
            if key not in lines_drawn:
                dx, dy = p_coords_val[0] - center_coords[0], p_coords_val[1] - center_coords[1]
                length = np.sqrt(dx**2 + dy**2)
                if length > 0:
                    unit_dx, unit_dy = dx / length, dy / length
                    ax.plot([center_coords[0], center_coords[0] + unit_dx * radius * 1.2],
                            [center_coords[1], center_coords[1] + unit_dy * radius * 1.2], 'k-', linewidth=1)
                lines_drawn.add(key)

    # Special handling for straight lines (e.g., A-O-B)
    # Check if A, O, B are collinear and O is between A and B
    if 'A' in points_coords and 'O' in points_coords and 'B' in points_coords:
        vec_OA = np.array(points_coords['A']) - np.array(points_coords['O'])
        vec_OB = np.array(points_coords['B']) - np.array(points_coords['O'])
        # Check for collinearity and opposite directions
        if np.isclose(np.dot(vec_OA, vec_OB), -np.linalg.norm(vec_OA) * np.linalg.norm(vec_OB)):
            ax.plot([-radius*1.2, radius*1.2], [0, 0], 'k-', linewidth=1) # Draw a full line
        
    # Draw arcs and angle labels
    for angle_info in angles_to_label:
        center_coords = np.array(points_coords[angle_info['center']])
        p1_coords = np.array(points_coords[angle_info['p1']])
        p2_coords = np.array(points_coords[angle_info['p2']])

        vec1 = p1_coords - center_coords
        vec2 = p2_coords - center_coords

        angle1_rad = np.arctan2(vec1[1], vec1[0])
        angle2_rad = np.arctan2(vec2[1], vec2[0])

        start_angle = np.degrees(angle1_rad)
        end_angle = np.degrees(angle2_rad)

        # Normalize angles for arc drawing
        # Ensure start_angle is always less than end_angle for arc drawing
        if end_angle < start_angle:
            end_angle += 360
        
        # Adjust if the angle crosses 360/0 and is > 180, to draw the smaller angle
        angle_diff = end_angle - start_angle
        if angle_diff > 180 and angle_diff < 360:
            start_angle, end_angle = end_angle - 360, start_angle
            if end_angle < start_angle:
                end_angle += 360

        # Small radius for angle arc
        arc_radius = radius * 0.3
        
        # Calculate text position for angle label
        mid_angle_rad = np.radians((start_angle + end_angle) / 2)
        text_x = center_coords[0] + arc_radius * 1.2 * np.cos(mid_angle_rad)
        text_y = center_coords[1] + arc_radius * 1.2 * np.sin(mid_angle_rad)

        if angle_info['type'] == 'value':
            label_text = r"${val}^{\circ}$".replace("{val}", str(angle_info['label']))
        elif angle_info['type'] == 'variable':
            label_text = r"${var}^{\circ}$".replace("{var}", angle_info['label'])
        else:
            label_text = ""

        # Draw arc
        arc = plt.matplotlib.patches.Arc(center_coords, arc_radius * 2, arc_radius * 2,
                                         angle=0, theta1=start_angle, theta2=end_angle, color='k', linewidth=1)
        ax.add_patch(arc)
        
        # Draw angle label
        if label_text: # Only draw if there's a label
            ax.text(text_x, text_y, label_text, ha='center', va='center', fontsize=12,
                    bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.7))

    # Draw right angle symbol
    if right_angle_at:
        center_coords = np.array(points_coords[right_angle_at[0]])
        p1_coords = np.array(points_coords[right_angle_at[1]])
        p2_coords = np.array(points_coords[right_angle_at[2]])

        vec1 = p1_coords - center_coords
        vec2 = p2_coords - center_coords

        norm_vec1 = vec1 / np.linalg.norm(vec1)
        norm_vec2 = vec2 / np.linalg.norm(vec2)

        corner_size = radius * 0.15
        p_corner1 = center_coords + norm_vec1 * corner_size
        p_corner2 = center_coords + norm_vec2 * corner_size
        p_diag = center_coords + norm_vec1 * corner_size + norm_vec2 * corner_size

        ax.plot([p_corner1[0], p_diag[0], p_corner2[0]],
                [p_corner1[1], p_diag[1], p_corner2[1]], 'k-', linewidth=1)

    # Draw bisector marks (two small arcs on each bisected angle)
    if bisector_marks:
        center_coords = np.array(points_coords[bisector_marks[0]])
        p1_coords = np.array(points_coords[bisector_marks[1]]) # A
        p2_coords = np.array(points_coords[bisector_marks[2]]) # E
        p3_coords = np.array(points_coords[bisector_marks[3]]) # C

        # Angle 1: p1-center-p2 (AOE)
        vec_p1_1 = p1_coords - center_coords
        vec_p2_1 = p2_coords - center_coords
        angle1_rad_1 = np.arctan2(vec_p1_1[1], vec_p1_1[0])
        angle2_rad_1 = np.arctan2(vec_p2_1[1], vec_p2_1[0])
        start_angle_1, end_angle_1 = np.degrees(angle1_rad_1), np.degrees(angle2_rad_1)
        if end_angle_1 < start_angle_1: end_angle_1 += 360
        mid_angle_1_rad = np.radians((start_angle_1 + end_angle_1) / 2)
        
        # Angle 2: p2-center-p3 (EOC)
        vec_p1_2 = p2_coords - center_coords
        vec_p2_2 = p3_coords - center_coords
        angle1_rad_2 = np.arctan2(vec_p1_2[1], vec_p1_2[0])
        angle2_rad_2 = np.arctan2(vec_p2_2[1], vec_p2_2[0])
        start_angle_2, end_angle_2 = np.degrees(angle1_rad_2), np.degrees(angle2_rad_2)
        if end_angle_2 < start_angle_2: end_angle_2 += 360
        mid_angle_2_rad = np.radians((start_angle_2 + end_angle_2) / 2)

        arc_radius_bisector = radius * 0.25
        mark_length = radius * 0.05
        
        # Draw mark for first angle (AOE)
        mark_x1 = center_coords[0] + arc_radius_bisector * np.cos(mid_angle_1_rad)
        mark_y1 = center_coords[1] + arc_radius_bisector * np.sin(mid_angle_1_rad)
        ax.plot([mark_x1 - mark_length * np.sin(mid_angle_1_rad), mark_x1 + mark_length * np.sin(mid_angle_1_rad)],
                [mark_y1 + mark_length * np.cos(mid_angle_1_rad), mark_y1 - mark_length * np.cos(mid_angle_1_rad)],
                'k-', linewidth=1)
        
        # Draw mark for second angle (EOC)
        mark_x2 = center_coords[0] + arc_radius_bisector * np.cos(mid_angle_2_rad)
        mark_y2 = center_coords[1] + arc_radius_bisector * np.sin(mid_angle_2_rad)
        ax.plot([mark_x2 - mark_length * np.sin(mid_angle_2_rad), mark_x2 + mark_length * np.sin(mid_angle_2_rad)],
                [mark_y2 + mark_length * np.cos(mid_angle_2_rad), mark_y2 - mark_length * np.cos(mid_angle_2_rad)],
                'k-', linewidth=1)

    return _get_base64_image(fig)


# --- Check function (CRITICAL CODING STANDARDS: Verification & Stability) ---

    # 1. 輸入清洗 (Input Sanitization)
    # 移除 LaTeX 符號, 變數前綴, 單位, 所有空白字元
    cleaned_user_answer = user_answer.lower()
    cleaned_user_answer = re.sub(r'[\\$}{x=y=k=ans:答案:°\s]', '', cleaned_user_answer)
    
    # 2. 分割多個答案 (如果存在)
    user_parts = [part.strip() for part in cleaned_user_answer.split(',') if part.strip()]
    correct_parts = [part.strip() for part in str(correct_answer).split(',') if part.strip()]

    # 3. 數值序列比對
    if len(user_parts) != len(correct_parts):
        return False

    for u_val_str, c_val_str in zip(user_parts, correct_parts):
        try:
            u_val = float(u_val_str)
            c_val = float(c_val_str)
            # 允許浮點數比較存在小誤差
            if abs(u_val - c_val) > 1e-6:
                return False
        except ValueError:
            # 如果轉換失敗，說明輸入不是純數字，直接判斷為錯
            return False
            
    return True


# --- generate function ---
def generate(level=1):
    problem_type = random.choice([1, 2, 3, 4, 5])
    question_text = ""
    correct_answer = ""
    display_answer = ""
    image_base64 = ""

    # Radius for drawing diagrams
    radius = 1.0

    if problem_type == 1:
        # Problem Type 1 (Maps to Example 1, 2): 互餘角與互補角
        relation_type = random.choice(["complementary", "supplementary"])
        problem_form = random.choice(["direct_calc", "algebraic_relation"])

        if relation_type == "complementary": # 互餘角
            if problem_form == "direct_calc":
                angle_val = random.randint(10, 80)
                correct_ans = 90 - angle_val
                question_text = "一個角的度數是 ${val}^{\circ}$，求其互餘角的度數。".replace("{val}", str(angle_val))
            else: # algebraic_relation
                diff_options = [d for d in range(5, 31) if (90 + d) % 2 == 0 or (90 - d) % 2 == 0]
                diff = random.choice(diff_options)
                op = random.choice(["more", "less"])
                if op == "more":
                    correct_ans = (90 + diff) / 2
                    question_text = "一個角比它的互餘角多 ${diff}^{\circ}$，求這個角的度數。".replace("{diff}", str(diff))
                else: # op == "less"
                    correct_ans = (90 - diff) / 2
                    question_text = "一個角比它的互餘角少 ${diff}^{\circ}$，求這個角的度數。".replace("{diff}", str(diff))
                correct_ans = int(correct_ans) # Ensure it's an integer

            correct_answer = str(correct_ans)
            display_answer = r"$x = {a}^{\circ}$".replace("{a}", str(correct_ans))

        else: # relation_type == "supplementary" # 互補角
            if problem_form == "direct_calc":
                angle_val = random.randint(10, 170)
                correct_ans = 180 - angle_val
                question_text = "一個角的度數是 ${val}^{\circ}$，求其互補角的度數。".replace("{val}", str(angle_val))
            else: # algebraic_relation
                diff_options = [d for d in range(5, 51) if (180 + d) % 2 == 0 or (180 - d) % 2 == 0]
                diff = random.choice(diff_options)
                op = random.choice(["more", "less"])
                if op == "more":
                    correct_ans = (180 + diff) / 2
                    question_text = "一個角比它的互補角多 ${diff}^{\circ}$，求這個角的度數。".replace("{diff}", str(diff))
                else: # op == "less"
                    correct_ans = (180 - diff) / 2
                    question_text = "一個角比它的互補角少 ${diff}^{\circ}$，求這個角的度數。".replace("{diff}", str(diff))
                correct_ans = int(correct_ans) # Ensure it's an integer

            correct_answer = str(correct_ans)
            display_answer = r"$x = {a}^{\circ}$".replace("{a}", str(correct_ans))

    elif problem_type == 2:
        # Problem Type 2 (Maps to Example 3, 4): 平角上的角度計算
        num_rays = random.choice([1, 2])
        points_coords = {'O': (0, 0), 'A': (-radius, 0), 'B': (radius, 0)}
        angles_to_label = []
        
        if num_rays == 1:
            angle_AOC_val = random.randint(20, 160)
            angle_BOC_val = 180 - angle_AOC_val
            
            if random.choice([True, False]): # AOC is known, BOC is x
                known_angle = angle_AOC_val
                correct_ans = angle_BOC_val
                points_coords['C'] = (radius * np.cos(np.radians(180 - known_angle)), radius * np.sin(np.radians(180 - known_angle)))
                angles_to_label.append({'center': 'O', 'p1': 'A', 'p2': 'C', 'label': str(known_angle), 'type': 'value'})
                angles_to_label.append({'center': 'O', 'p1': 'C', 'p2': 'B', 'label': 'x', 'type': 'variable'})
                question_text = "如右圖，A、O、B 三點共線，若 $\\angle AOC = {val}^{\circ}$，則 $\\angle BOC = ? $".replace("{val}", str(known_angle))
            else: # BOC is known, AOC is x
                known_angle = angle_BOC_val
                correct_ans = angle_AOC_val
                points_coords['C'] = (radius * np.cos(np.radians(known_angle)), radius * np.sin(np.radians(known_angle)))
                angles_to_label.append({'center': 'O', 'p1': 'C', 'p2': 'B', 'label': str(known_angle), 'type': 'value'})
                angles_to_label.append({'center': 'O', 'p1': 'A', 'p2': 'C', 'label': 'x', 'type': 'variable'})
                question_text = "如右圖，A、O、B 三點共線，若 $\\angle BOC = {val}^{\circ}$，則 $\\angle AOC = ? $".replace("{val}", str(known_angle))

            correct_answer = str(correct_ans)
            display_answer = r"$x = {a}^{\circ}$".replace("{a}", str(correct_ans))
            image_base64 = _draw_angle_diagram(points_coords, angles_to_label, radius=radius)

        else: # num_rays == 2 (rays OC, OD)
            angle_aoc = random.randint(20, 60)
            angle_cod = random.randint(20, 60)
            angle_dob = 180 - angle_aoc - angle_cod
            while angle_dob < 20: # Ensure all angles are at least 20
                angle_aoc = random.randint(20, 60)
                angle_cod = random.randint(20, 60)
                angle_dob = 180 - angle_aoc - angle_cod

            angles_in_sequence = [angle_dob, angle_cod, angle_aoc] # DOB -> COD -> AOC
            point_names_in_sequence = ['B', 'D', 'C', 'A'] # B-O-D-O-C-O-A

            x_idx = random.randint(0, 2)
            correct_ans = angles_in_sequence[x_idx]
            
            current_cumulative_angle = 0 # Starting from B (0 degrees)
            points_coords['B'] = (radius, 0)
            angles_to_label = []

            for i in range(3):
                angle_val = angles_in_sequence[i]
                
                p1_name = point_names_in_sequence[i]
                p2_name = point_names_in_sequence[i+1]

                current_cumulative_angle += angle_val
                p2_x = radius * np.cos(np.radians(current_cumulative_angle))
                p2_y = radius * np.sin(np.radians(current_cumulative_angle))
                points_coords[p2_name] = (p2_x, p2_y)

                if i == x_idx:
                    angles_to_label.append({'center': 'O', 'p1': p1_name, 'p2': p2_name, 'label': 'x', 'type': 'variable'})
                else:
                    angles_to_label.append({'center': 'O', 'p1': p1_name, 'p2': p2_name, 'label': str(angle_val), 'type': 'value'})
            
            question_text = "如右圖，A、O、B 三點共線，求 $\\angle x$ 的度數。"
            correct_answer = str(correct_ans)
            display_answer = r"$x = {a}^{\circ}$".replace("{a}", str(correct_ans))
            image_base64 = _draw_angle_diagram(points_coords, angles_to_label, radius=radius)

    elif problem_type == 3:
        # Problem Type 3 (Maps to Example 5, 6): 對頂角與鄰角
        
        angle_BOC_val = random.randint(20, 160)
        angle_COA_val = 180 - angle_BOC_val
        angle_AOD_val = angle_BOC_val # Vertically opposite
        angle_BOD_val = angle_COA_val # Vertically opposite

        # Set up points for intersecting lines
        # B at 0 deg, A at 180 deg
        # C at angle_BOC_val from B (counter-clockwise)
        # D at angle_BOC_val + 180 from B (counter-clockwise)
        points_coords = {
            'O': (0, 0),
            'B': (radius, 0),
            'A': (-radius, 0),
            'C': (radius * np.cos(np.radians(angle_BOC_val)), radius * np.sin(np.radians(angle_BOC_val))),
            'D': (radius * np.cos(np.radians(angle_BOC_val + 180)), radius * np.sin(np.radians(angle_BOC_val + 180)))
        }

        angles_data = [
            {'p1': 'B', 'p2': 'C', 'val': angle_BOC_val, 'name_str': 'BOC'},
            {'p1': 'C', 'p2': 'A', 'val': angle_COA_val, 'name_str': 'COA'},
            {'p1': 'A', 'p2': 'D', 'val': angle_AOD_val, 'name_str': 'AOD'},
            {'p1': 'D', 'p2': 'B', 'val': angle_BOD_val, 'name_str': 'BOD'}
        ]
        
        # Randomly select one angle to be known, and one to be 'x'
        known_angle_idx = random.randint(0, 3)
        x_angle_idx = random.randint(0, 3)
        while x_angle_idx == known_angle_idx:
            x_angle_idx = random.randint(0, 3)

        known_angle_info = angles_data[known_angle_idx]
        x_angle_info = angles_data[x_angle_idx]

        question_text = "如右圖，直線 AB 與 CD 相交於 O 點。"
        question_text += "若 $\\angle {known_name} = {val}^{\circ}$，".replace("{known_name}", known_angle_info['name_str']).replace("{val}", str(known_angle_info['val']))
        question_text += "則 $\\angle {x_name} = ? $".replace("{x_name}", x_angle_info['name_str'])

        angles_to_label = []
        angles_to_label.append({'center': 'O', 'p1': known_angle_info['p1'], 'p2': known_angle_info['p2'], 'label': str(known_angle_info['val']), 'type': 'value'})
        angles_to_label.append({'center': 'O', 'p1': x_angle_info['p1'], 'p2': x_angle_info['p2'], 'label': 'x', 'type': 'variable'})
        
        correct_ans = x_angle_info['val']
        correct_answer = str(correct_ans)
        display_answer = r"$x = {a}^{\circ}$".replace("{a}", str(correct_ans))
        image_base64 = _draw_angle_diagram(points_coords, angles_to_label, radius=radius)

    elif problem_type == 4:
        # Problem Type 4 (Maps to Example 7, 8): 周角上的角度計算
        num_known_angles = random.choice([2, 3]) # Total rays will be num_known_angles + 1
        
        known_angles_vals = []
        sum_known = 0
        
        for _ in range(num_known_angles):
            angle = random.randint(50, 100)
            known_angles_vals.append(angle)
            sum_known += angle
        
        unknown_angle_val = 360 - sum_known
        # Ensure unknown angle is also reasonable (e.g., between 40 and 120)
        while unknown_angle_val < 40 or unknown_angle_val > 120:
            known_angles_vals = []
            sum_known = 0
            for _ in range(num_known_angles):
                angle = random.randint(50, 100)
                known_angles_vals.append(angle)
                sum_known += angle
            unknown_angle_val = 360 - sum_known

        correct_ans = unknown_angle_val
        
        all_angles_for_plot = known_angles_vals + [correct_ans]
        random.shuffle(all_angles_for_plot) # Randomize which angle is 'x'
        
        points_coords = {'O': (0, 0)}
        angles_to_label = []
        
        current_cumulative_angle = 0 # Start from 0 degrees (positive x-axis)
        point_names = ['A', 'B', 'C', 'D', 'E'] # Max 5 points for 4 rays + 1 starting point
        
        points_coords[point_names[0]] = (radius, 0) # First point A at (radius, 0)
        
        for i in range(len(all_angles_for_plot)):
            angle_val = all_angles_for_plot[i]
            
            p1_name = point_names[i]
            p2_name = point_names[(i + 1) % len(all_angles_for_plot)] # Wrap around for last angle

            current_cumulative_angle += angle_val
            
            p2_x = radius * np.cos(np.radians(current_cumulative_angle))
            p2_y = radius * np.sin(np.radians(current_cumulative_angle))
            points_coords[p2_name] = (p2_x, p2_y)

            if angle_val == correct_ans and 'x' not in [a['label'] for a in angles_to_label]: # Only one 'x'
                angles_to_label.append({'center': 'O', 'p1': p1_name, 'p2': p2_name, 'label': 'x', 'type': 'variable'})
            else:
                angles_to_label.append({'center': 'O', 'p1': p1_name, 'p2': p2_name, 'label': str(angle_val), 'type': 'value'})
        
        question_text = "如右圖，O 為中心點，求 $\\angle x$ 的度數。"
        correct_answer = str(correct_ans)
        display_answer = r"$x = {a}^{\circ}$".replace("{a}", str(correct_ans))
        image_base64 = _draw_angle_diagram(points_coords, angles_to_label, radius=radius)


    elif problem_type == 5:
        # Problem Type 5 (Maps to Example 9, 10): 綜合應用題
        scenario = random.choice(["perpendicular_ray", "angle_bisector_intersecting_lines"])
        
        if scenario == "perpendicular_ray":
            # 直線 AOB, OC 垂直 AB (∠AOC = 90°), OD 位於 ∠COB 內部
            points_coords = {
                'O': (0, 0),
                'A': (-radius, 0),
                'B': (radius, 0),
                'C': (0, radius), # OC is perpendicular (90 deg from OB or OA)
            }
            
            angle_COD_val = random.randint(10, 70)
            angle_DOB_val = 90 - angle_COD_val
            
            d_x = radius * np.cos(np.radians(angle_DOB_val))
            d_y = radius * np.sin(np.radians(angle_DOB_val))
            points_coords['D'] = (d_x, d_y)

            angles_to_label = []
            right_angle_at = ('O', 'C', 'B') # For angle COB

            if random.choice([True, False]): # Known COD, find DOB (x)
                angles_to_label.append({'center': 'O', 'p1': 'C', 'p2': 'D', 'label': str(angle_COD_val), 'type': 'value'})
                angles_to_label.append({'center': 'O', 'p1': 'D', 'p2': 'B', 'label': 'x', 'type': 'variable'})
                correct_ans = angle_DOB_val
                question_text = "如右圖，直線 AB，OC $\\bot$ AB，若 $\\angle COD = {val}^{\circ}$，求 $\\angle DOB$ 的度數。".replace("{val}", str(angle_COD_val))
            else: # Known DOB, find COD (x)
                angles_to_label.append({'center': 'O', 'p1': 'D', 'p2': 'B', 'label': str(angle_DOB_val), 'type': 'value'})
                angles_to_label.append({'center': 'O', 'p1': 'C', 'p2': 'D', 'label': 'x', 'type': 'variable'})
                correct_ans = angle_COD_val
                question_text = "如右圖，直線 AB，OC $\\bot$ AB，若 $\\angle DOB = {val}^{\circ}$，求 $\\angle COD$ 的度數。".replace("{val}", str(angle_DOB_val))
            
            correct_answer = str(correct_ans)
            display_answer = r"$x = {a}^{\circ}$".replace("{a}", str(correct_ans))
            image_base64 = _draw_angle_diagram(points_coords, angles_to_label, right_angle_at=right_angle_at, radius=radius)

        else: # angle_bisector_intersecting_lines
            # 直線 AB 與 CD 相交於 O, OE 平分 ∠AOC
            
            # Use B as 0 deg, A as 180 deg.
            # Angle BOC will be the base angle for C's position.
            angle_BOC_base = random.choice([x for x in range(40, 161) if x % 2 == 0])
            angle_AOC_actual = 180 - angle_BOC_base # This is the angle OE bisects
            angle_AOE_actual = angle_AOC_actual // 2
            
            points_coords = {
                'O': (0, 0),
                'B': (radius, 0),
                'A': (-radius, 0),
                'C': (radius * np.cos(np.radians(angle_BOC_base)), radius * np.sin(np.radians(angle_BOC_base))),
                'D': (radius * np.cos(np.radians(angle_BOC_base + 180)), radius * np.sin(np.radians(angle_BOC_base + 180))),
            }
            
            # Position E such that OE bisects AOC.
            # Angle from OA (180 deg) to OE is angle_AOE_actual (clockwise from OA, or counter-clockwise from OC).
            # Angle from positive x-axis to OE: 180 - angle_AOE_actual.
            e_angle_from_x_axis = 180 - angle_AOE_actual
            e_x = radius * np.cos(np.radians(e_angle_from_x_axis))
            e_y = radius * np.sin(np.radians(e_angle_from_x_axis))
            points_coords['E'] = (e_x, e_y)

            angles_to_label = []
            
            # Always label the angle that is bisected
            angles_to_label.append({'center': 'O', 'p1': 'A', 'p2': 'C', 'label': str(angle_AOC_actual), 'type': 'value'})
            
            # Choose angle to find (x)
            choice_angle = random.choice(['EOD', 'BOE'])
            
            if choice_angle == 'EOD':
                # EOD = EOC + COD
                # EOC = angle_AOE_actual
                # COD = angle_AOD_actual = angle_BOC_base
                correct_ans = angle_AOE_actual + angle_BOC_base
                
                angles_to_label.append({'center': 'O', 'p1': 'E', 'p2': 'D', 'label': 'x', 'type': 'variable'})
                question_text = "如右圖，直線 AB 與 CD 相交於 O 點，OE 平分 $\\angle AOC$。若 $\\angle AOC = {val}^{\circ}$，求 $\\angle EOD$ 的度數。".replace("{val}", str(angle_AOC_actual))
            else: # BOE
                # BOE = BOC + COE
                # BOC = angle_BOC_base
                # COE = angle_AOE_actual
                correct_ans = angle_BOC_base + angle_AOE_actual
                
                angles_to_label.append({'center': 'O', 'p1': 'B', 'p2': 'E', 'label': 'x', 'type': 'variable'})
                question_text = "如右圖，直線 AB 與 CD 相交於 O 點，OE 平分 $\\angle AOC$。若 $\\angle AOC = {val}^{\circ}$，求 $\\angle BOE$ 的度數。".replace("{val}", str(angle_AOC_actual))
            
            bisector_marks = ('O', 'A', 'E', 'C') # For AOE and EOC
            correct_answer = str(correct_ans)
            display_answer = r"$x = {a}^{\circ}$".replace("{a}", str(correct_ans))
            image_base64 = _draw_angle_diagram(points_coords, angles_to_label, bisector_marks=bisector_marks, radius=radius)


    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": display_answer,
        "image_base64": image_base64,
        "created_at": datetime.datetime.now().isoformat(),
        "version": "1.0"
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
