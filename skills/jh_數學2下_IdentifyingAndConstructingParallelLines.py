# ==============================================================================
# ID: jh_數學2下_IdentifyingAndConstructingParallelLines
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 49.55s | RAG: 4 examples
# Created At: 2026-01-24 12:57:05
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


import base64
from io import BytesIO
import matplotlib.pyplot as plt
import re
from datetime import datetime
 # Used for numerical comparison in check function
import numpy as np # Imported for potential future use as per spec, not strictly for this skill.

# Helper function for drawing angles in parallel lines context
def _draw_parallel_lines_angles(line1_angle=None, line2_angle=None, angle_type="corresponding", is_parallel=True, label_x=False, known_angle_val=None, unknown_angle_label='x'):
    """
    繪製兩條直線被一截線所截的示意圖，並標示角度。
    
    Args:
        line1_angle (int, optional): L1 上角度的數值。用於 Type 1。
        line2_angle (int, optional): L2 上角度的數值。用於 Type 1。
        angle_type (str): 角度類型 ("corresponding", "alternate_interior", "consecutive_interior")。
        is_parallel (bool): 指示圖中兩條線是否平行。主要用於 Type 1 的視覺判斷。
        label_x (bool): 是否將 L2 上的角度標記為 'x'。用於 Type 2。
        known_angle_val (int, optional): 已知角度的數值。用於 Type 2。
        unknown_angle_label (str): 未知角的標籤，預設為 'x'。
        
    Returns:
        str: PNG 格式的 base64 編碼字串。
    """
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300) # ULTRA VISUAL STANDARDS: dpi=300
    ax.set_aspect('equal') # V10.2 Pure Style: Ensure square grid if present, though this is schematic.

    line_color = 'black'
    transversal_color = 'gray'
    text_color = 'blue'
    
    x_min, x_max = -5, 5
    y_min, y_max = -4, 4 # Adjusted y_max/min to give more space

    # Line L1 (horizontal)
    ax.plot([x_min, x_max], [1.5, 1.5], color=line_color, linewidth=2)
    ax.text(x_max - 0.5, 1.8, 'L1', fontsize=12, color=line_color, ha='center', va='center')

    # Line L2 (horizontal)
    ax.plot([x_min, x_max], [-1.5, -1.5], color=line_color, linewidth=2)
    ax.text(x_max - 0.5, -1.2, 'L2', fontsize=12, color=line_color, ha='center', va='center')

    # Transversal line (slanted)
    # Define intersection points for visual consistency and easier angle placement
    int_x_L1 = -1.5 # x-coordinate where transversal intersects L1
    int_y_L1 = 1.5   # y-coordinate of L1
    int_x_L2 = 1.5  # x-coordinate where transversal intersects L2
    int_y_L2 = -1.5  # y-coordinate of L2

    # Draw transversal line passing through (int_x_L1, int_y_L1) and (int_x_L2, int_y_L2)
    # Extend it beyond the parallel lines for a clear visual.
    # Slope m = (int_y_L2 - int_y_L1) / (int_x_L2 - int_x_L1) = (-1.5 - 1.5) / (1.5 - (-1.5)) = -3 / 3 = -1
    # y - int_y_L1 = m * (x - int_x_L1) => y - 1.5 = -1 * (x - (-1.5)) => y = -x - 1.5 + 1.5 => y = -x
    
    # Calculate start and end points for the transversal based on y=-x, extending to y_min/y_max
    trans_start_x = -y_max
    trans_start_y = y_max
    trans_end_x = -y_min
    trans_end_y = y_min
    
    ax.plot([trans_start_x, trans_end_x], [trans_start_y, trans_end_y], color=transversal_color, linestyle='--', linewidth=1.5)
    ax.text(trans_end_x + 0.2, trans_end_y - 0.2, 'M', fontsize=12, color=transversal_color) # Label M at the end of transversal

    # Draw and label angles based on type
    # [CRITICAL RULE: Visual Solvability]: Angles must be explicitly labeled.
    # [V13.5 標籤隔離]: ax.text 只能標註點名稱或角度值，不能包含座標。
    bbox_props = dict(boxstyle="round,pad=0.1", fc='white', ec='none', alpha=0.7)

    # Angle text offsets (adjust for better visual placement relative to intersection point)
    offset_x_upper_left = -0.7
    offset_y_upper_left = 0.5
    offset_x_lower_left = -0.7
    offset_y_lower_left = -0.5
    offset_x_lower_right = 0.7
    offset_y_lower_right = -0.5

    # Determine angle values to display for L1 and L2
    # For Type 1, line1_angle and line2_angle are provided.
    # For Type 2, known_angle_val and label_x are provided.
    val_to_display_L1 = f"${known_angle_val}°$" if known_angle_val is not None else f"${line1_angle}°$"
    val_to_display_L2 = f"${unknown_angle_label}$" if label_x else (f"${line2_angle}°$" if line2_angle is not None else "")

    if angle_type == "corresponding":
        # L1: upper-left angle (e.g., ∠1 in standard diagrams)
        ax.text(int_x_L1 + offset_x_upper_left, int_y_L1 + offset_y_upper_left, val_to_display_L1, fontsize=12, color=text_color, ha='center', va='center', bbox=bbox_props)
        # L2: upper-left angle (e.g., ∠5 in standard diagrams)
        ax.text(int_x_L2 + offset_x_upper_left, int_y_L2 + offset_y_upper_left, val_to_display_L2, fontsize=12, color=text_color, ha='center', va='center', bbox=bbox_props)
        
    elif angle_type == "alternate_interior":
        # L1: lower-right angle (e.g., ∠4 in standard diagrams)
        ax.text(int_x_L1 + offset_x_lower_right, int_y_L1 + offset_y_lower_right, val_to_display_L1, fontsize=12, color=text_color, ha='center', va='center', bbox=bbox_props)
        # L2: upper-left angle (e.g., ∠5 in standard diagrams)
        ax.text(int_x_L2 + offset_x_upper_left, int_y_L2 + offset_y_upper_left, val_to_display_L2, fontsize=12, color=text_color, ha='center', va='center', bbox=bbox_props)

    elif angle_type == "consecutive_interior":
        # L1: lower-right angle (e.g., ∠4 in standard diagrams)
        ax.text(int_x_L1 + offset_x_lower_right, int_y_L1 + offset_y_lower_right, val_to_display_L1, fontsize=12, color=text_color, ha='center', va='center', bbox=bbox_props)
        # L2: lower-left angle (e.g., ∠6 in standard diagrams)
        ax.text(int_x_L2 + offset_x_lower_left, int_y_L2 + offset_y_lower_left, val_to_display_L2, fontsize=12, color=text_color, ha='center', va='center', bbox=bbox_props)
            
    # Remove axes and ticks for schematic diagram
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.axis('off')

    # Convert plot to base64
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# Helper function for generic construction image
def _draw_construction_template():
    """
    繪製一個通用作圖題模板，包含一條直線 L 和一個點 P。
    
    Returns:
        str: PNG 格式的 base64 編碼字串。
    """
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300) # ULTRA VISUAL STANDARDS: dpi=300
    ax.set_aspect('equal') # V10.2 Pure Style
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.axis('off') # Hide axes for a clean template

    # Draw a generic line L
    ax.plot([-4, 4], [0, 0], 'k-', linewidth=2)
    ax.text(3.5, 0.3, 'L', fontsize=12, color='black')

    # Draw a generic point P not on L
    ax.plot([0], [2], 'ro', markersize=8)
    ax.text(0.2, 2.2, 'P', fontsize=12, color='red')

    ax.text(0, -3, "此為作圖題，請依照題意作圖。", fontsize=14, color='gray', ha='center')

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def generate(level=1):
    """
    根據指定的難度等級生成一道關於平行線判別或作圖的題目。
    
    Args:
        level (int): 難度等級 (目前僅支援 level=1)。
        
    Returns:
        dict: 包含題目資訊的字典。
    """
    # [題型鏡射 (Problem Mirroring)]: Use random.choice to select problem type.
    problem_type = random.choice([1, 2, 3]) # Type 1: Determine parallel, Type 2: Calculate angle, Type 3: Construction
    
    question_text = ""
    correct_answer = ""
    image_base64 = ""
    
    if problem_type == 1: # Type 1 (Maps to RAG Example 1, 2): Determine if lines are parallel
        # [數據禁絕常數 (Data Prohibition)]: Generate random angles.
        angle_val_a = random.randint(30, 150)
        is_parallel_condition = random.choice([True, False])
        
        # [CRITICAL RULE: Grade & Semantic Alignment]: Use Grade 8 concepts.
        angle_type = random.choice(["corresponding", "alternate_interior", "consecutive_interior"])
        
        if is_parallel_condition:
            if angle_type in ["corresponding", "alternate_interior"]:
                angle_val_b = angle_val_a # Lines are parallel, angles are equal
            elif angle_type == "consecutive_interior":
                angle_val_b = 180 - angle_val_a # Lines are parallel, consecutive interior angles are supplementary
            correct_answer = "是"
        else:
            # Lines are not parallel, make angle_val_b different.
            deviation = random.choice([-5, 5]) # Ensure deviation is non-zero
            if angle_type in ["corresponding", "alternate_interior"]:
                angle_val_b = angle_val_a + deviation
            elif angle_type == "consecutive_interior":
                angle_val_b = 180 - angle_val_a + deviation
            correct_answer = "否"
            
        # [排版與 LaTeX 安全 (Elite Guardrails)]: Use .replace() for LaTeX strings.
        angle_type_text_map = {
            "corresponding": "同位角",
            "alternate_interior": "內錯角",
            "consecutive_interior": "同側內角"
        }
        angle_type_display = angle_type_text_map[angle_type]

        q_text_template = r"如圖，直線 $L_1$ 和 $L_2$ 被直線 $M$ 所截。若${angle_type_text}$分別為 ${angle_a}°$ 和 ${angle_b}°$，請問 $L_1$ 和 $L_2$ 是否平行？"
        question_text = q_text_template.replace("{angle_type_text}", angle_type_display).replace("{angle_a}", str(angle_val_a)).replace("{angle_b}", str(angle_val_b))
        
        # [CRITICAL RULE: Visual Solvability]: Ensure angles are labeled.
        image_base64 = _draw_parallel_lines_angles(line1_angle=angle_val_a, line2_angle=angle_val_b, angle_type=angle_type, is_parallel=is_parallel_condition)
        
    elif problem_type == 2: # Type 2 (Maps to RAG Example 3, 4): Calculate unknown angle with parallel lines
        # [數據禁絕常數 (Data Prohibition)]: Generate random angles.
        given_angle = random.randint(30, 150)
        angle_type = random.choice(["corresponding", "alternate_interior", "consecutive_interior"])
        
        if angle_type in ["corresponding", "alternate_interior"]:
            correct_answer = str(given_angle)
        elif angle_type == "consecutive_interior":
            correct_answer = str(180 - given_angle)
        
        # [排版與 LaTeX 安全 (Elite Guardrails)]: Use .replace() for LaTeX strings.
        angle_type_text_map = {
            "corresponding": "同位角",
            "alternate_interior": "內錯角",
            "consecutive_interior": "同側內角"
        }
        angle_type_display = angle_type_text_map[angle_type]

        q_text_template = r"如圖，直線 $L_1 \parallel L_2$，且直線 $M$ 為截線。若其中一個${angle_type_text}$為 ${given_angle}°$，則 $x$ 為多少度？"
        question_text = q_text_template.replace("{angle_type_text}", angle_type_display).replace("{given_angle}", str(given_angle))
        
        # [CRITICAL RULE: Visual Solvability]: Ensure angles are labeled.
        image_base64 = _draw_parallel_lines_angles(known_angle_val=given_angle, angle_type=angle_type, is_parallel=True, label_x=True)

    elif problem_type == 3: # Type 3 (Maps to RAG Example 5): Construction
        question_text = r"請在平面上畫出通過點 $P$ 且與直線 $L$ 平行的直線。此為作圖題，請依照題意作圖。"
        correct_answer = "" # [幾何/圖形題的特殊規範]: No auto-grading for construction.
        image_base64 = _draw_construction_template() # Generic template for construction.

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "", # This field is typically for system's internal answer, not for display.
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

def check(user_answer, correct_answer):
    """
    [V18.13 Hybrid Check] 支援：
    1. 中文是非題 (是/否, Yes/No, 1/0 互通)
    2. 集合比對 (L1, L2 == L2, L1)
    3. 數值比對 (容許誤差)
    """
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    import re, math

    # 0. 若正確答案為空 (如作圖題)，直接視為正確或忽略
    if not str(correct_answer).strip():
        return {"correct": True, "result": "作圖題請自行核對。"}

    # 1. 預處理
    def normalize(s):
        s = str(s).strip().upper()
        s = re.sub(r'[\$\\ \(\)\{\}]', '', s) # 移除 LaTeX 與括號
        return s.replace("，", ",").replace("、", ",")

    u_str = normalize(user_answer)
    c_str = normalize(correct_answer)

    # 2. 是非題特化處理 (Keyword Mapping)
    yes_keywords = ["是", "YES", "TRUE", "T", "O", "1", "平行"]
    no_keywords = ["否", "NO", "FALSE", "F", "X", "0", "不平行"]
    
    if c_str in yes_keywords:
        if u_str in yes_keywords: return {"correct": True, "result": "正確！"}
        return {"correct": False, "result": "答案錯誤。"}
    
    if c_str in no_keywords:
        if u_str in no_keywords: return {"correct": True, "result": "正確！"}
        return {"correct": False, "result": "答案錯誤。"}

    # 3. 集合比對 (針對 "L1, L2" 類型的多選)
    u_set = set(u_str.split(','))
    c_set = set(c_str.split(','))
    if u_set == c_set:
        return {"correct": True, "result": "正確！"}

    # 4. 數值比對 (針對角度計算)
    try:
        # 取出第一個數值進行比對
        u_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", u_str)[0])
        c_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", c_str)[0])
        if math.isclose(u_val, c_val, rel_tol=1e-5):
            return {"correct": True, "result": "正確！"}
    except:
        pass

    return {"correct": False, "result": f"答案錯誤。正確答案為：{correct_answer}"}

# [Auto-Injected Patch v11.0]
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤'}
        if isinstance(res, dict):
            # [Fix] 確保顯示正確
            if 'question_text' in res and isinstance(res['question_text'], str):
                res['question_text'] = res['question_text'].replace(r"\\n", "\n")
            if 'answer' not in res and 'correct_answer' in res:
                res['answer'] = res['correct_answer']
        return res
    return wrapper

import sys
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith('generate') or _name == 'check'):
        globals()[_name] = _patch_all_returns(_func)
