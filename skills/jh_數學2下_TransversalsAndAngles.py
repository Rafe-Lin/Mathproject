# ==============================================================================
# ID: jh_數學2下_TransversalsAndAngles
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 89.26s | RAG: 5 examples
# Created At: 2026-01-23 15:16:08
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
from io import BytesIO
import matplotlib.pyplot as plt
import re
import numpy as np

# 輔助繪圖函式 (Helper Drawing Function)
# [防洩漏原則]: 視覺化函式僅能接收「題目已知數據」。嚴禁將「答案數據」傳入繪圖函式。
# [標籤隔離]: ax.text 只能標註點名稱或表達式，不能包含座標值。
def _draw_parallel_lines_with_transversal(angle_labels: dict, line_parallel_symbol: bool = True) -> str:
    """
    繪製兩條平行線被一條截線所截的示意圖。

    Args:
        angle_labels (dict): 字典，鍵為角度位置 ('angle1' 到 'angle8')，值為要顯示的標籤字串 (例如 '60', 'x', '2x+10')。
                             標籤字串會自動以 LaTeX 數學模式顯示。
        line_parallel_symbol (bool): 是否繪製平行線標示箭頭。

    Returns:
        str: Base64 編碼的 PNG 圖片字串。
    """
    fig, ax = plt.subplots(figsize=(6, 6), dpi=300) # V11.6: Resolution dpi=300
    ax.set_aspect('equal') # V10.2 Pure Style
    ax.axis('off') # 隱藏坐標軸，僅顯示幾何圖形

    # 定義平行線的 y 座標和 x 範圍
    y1, y2 = 1.5, -1.5 
    x_range_lines = [-4, 4]

    # 定義截線：隨機生成一個介於 40 到 70 度之間的銳角與 x 軸正向的夾角
    theta_draw_deg = random.randint(40, 70) 
    theta_draw_rad = math.radians(theta_draw_deg)
    m_trans = math.tan(theta_draw_rad)
    c_trans = random.uniform(-0.5, 0.5) # 隨機 y 截距

    # 繪製平行線
    ax.plot(x_range_lines, [y1, y1], 'k-') # 上方平行線
    ax.plot(x_range_lines, [y2, y2], 'k-') # 下方平行線

    # 計算截線與平行線的交點
    # y = mx + c  => x = (y - c) / m
    x_top_intersect = (y1 - c_trans) / m_trans
    x_bottom_intersect = (y2 - c_trans) / m_trans

    # 繪製截線，確保其延伸超出平行線的範圍
    x_trans_start = min(x_top_intersect, x_bottom_intersect) - 1.5
    x_trans_end = max(x_top_intersect, x_bottom_intersect) + 1.5
    y_trans_start = m_trans * x_trans_start + c_trans
    y_trans_end = m_trans * x_trans_end + c_trans
    ax.plot([x_trans_start, x_trans_end], [y_trans_start, y_trans_end], 'k-') 

    # 繪製平行線標示箭頭 (V13.6 API Hardened Spec: 嚴禁使用 arrowprops)
    if line_parallel_symbol:
        arrow_len = 0.5 # 箭頭長度
        # 上方線右側箭頭
        ax.plot([x_range_lines[1] - arrow_len, x_range_lines[1]], [y1, y1], 'k>', clip_on=False, markersize=8)
        # 上方線左側箭頭
        ax.plot([x_range_lines[0] + arrow_len, x_range_lines[0]], [y1, y1], 'k<', clip_on=False, markersize=8)
        # 下方線右側箭頭
        ax.plot([x_range_lines[1] - arrow_len, x_range_lines[1]], [y2, y2], 'k>', clip_on=False, markersize=8)
        # 下方線左側箭頭
        ax.plot([x_range_lines[0] + arrow_len, x_range_lines[0]], [y2, y2], 'k<', clip_on=False, markersize=8)

    # 角度標籤位置的相對偏移量 (從交點出發)
    # These offsets are designed to place labels within their respective angle sectors
    label_offsets_map = {
        'angle1': (-0.7, 0.7), # Left-up-exterior
        'angle2': (0.7, 0.7),  # Right-up-exterior
        'angle3': (-0.7, -0.7), # Left-up-interior
        'angle4': (0.7, -0.7),  # Right-up-interior
        'angle5': (-0.7, 0.7), # Left-down-exterior (relative to bottom intersection)
        'angle6': (0.7, 0.7),  # Right-down-exterior (relative to bottom intersection)
        'angle7': (-0.7, -0.7), # Left-down-interior (relative to bottom intersection)
        'angle8': (0.7, -0.7)  # Right-down-interior (relative to bottom intersection)
    }

    # 放置角度標籤
    for pos_name, label_text in angle_labels.items():
        if pos_name in ['angle1', 'angle2', 'angle3', 'angle4']:
            ix, iy = x_top_intersect, y1
        else: # 'angle5' to 'angle8'
            ix, iy = x_bottom_intersect, y2
        
        offset_x, offset_y = label_offsets_map[pos_name]
        
        # V10.2: 點標籤須加白色光暈 (bbox)
        # 標籤文字一律以 LaTeX 數學模式顯示
        ax.text(ix + offset_x, iy + offset_y, f"${label_text}$", 
                fontsize=14, weight='bold', ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8))

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 問題類型 1: 基本角度計算 ---
def _generate_type1_problem():
    # 隨機生成一個初始角度，避免 90 度
    initial_angle_val = random.randint(30, 150)
    while initial_angle_val == 90:
        initial_angle_val = random.randint(30, 150)

    # 定義 8 個標準角度位置
    angle_positions = [f"angle{i}" for i in range(1, 9)]
    
    # 隨機選擇已知角度和目標角度的位置
    known_pos_idx = random.randint(0, 7)
    target_pos_idx = random.randint(0, 7)
    while target_pos_idx == known_pos_idx: # 確保已知與目標角度位置不同
        target_pos_idx = random.randint(0, 7)
    
    known_angle_pos_str = angle_positions[known_pos_idx]
    target_angle_pos_str = angle_positions[target_pos_idx]

    # 建立角度類型映射 (判斷角度是銳角還是鈍角)
    # This mapping assumes a standard configuration where the transversal has a positive slope.
    angle_type_map = {
        'angle1': 'obtuse', 'angle2': 'acute', 'angle3': 'acute', 'angle4': 'obtuse',
        'angle5': 'obtuse', 'angle6': 'acute', 'angle7': 'acute', 'angle8': 'obtuse'
    }

    # 根據已知角度的位置和數值，推導出圖中銳角和鈍角的實際值
    # This logic correctly determines the true acute and obtuse angles from the given initial_angle_val,
    # regardless of whether the initial_angle_val itself is acute or obtuse.
    actual_acute_val = 0
    actual_obtuse_val = 0

    if angle_type_map[known_angle_pos_str] == 'obtuse':
        if initial_angle_val > 90: 
            actual_obtuse_val = initial_angle_val
            actual_acute_val = 180 - initial_angle_val
        else: # initial_angle_val is acute, so it must be 180 - actual_obtuse_val
            actual_acute_val = initial_angle_val
            actual_obtuse_val = 180 - initial_angle_val
    else: # 'acute'
        if initial_angle_val <= 90: 
            actual_acute_val = initial_angle_val
            actual_obtuse_val = 180 - initial_angle_val
        else: # initial_angle_val is obtuse, so it must be 180 - actual_acute_val
            actual_obtuse_val = initial_angle_val
            actual_acute_val = 180 - initial_angle_val
    
    # 根據目標角度的類型，確定正確答案
    if angle_type_map[target_angle_pos_str] == 'obtuse':
        correct_answer = actual_obtuse_val
    else: # 'acute'
        correct_answer = actual_acute_val

    # 1. 定義可讀標籤 (對應 1~8)
    readable_labels = {f"angle{i}": str(i) for i in range(1, 9)}

    # 2. 鎖定繪圖標籤 (Drawing Labels MUST be Indices)
    # 嚴禁在這裡填入 str(degree) 或 "x"
    angle_labels_for_drawing = {
        known_angle_pos_str: readable_labels[known_angle_pos_str],   # 顯示 "2"
        target_angle_pos_str: readable_labels[target_angle_pos_str]  # 顯示 "7"
    }

    # 3. 題目文字 (Text uses Values)
    question_template = random.choice([
        r"如圖所示，直線 $L_1 // L_2$ 被直線 $M$ 所截。若 $\angle {known} = {val}^\circ$，則 $\angle {target} = ?$",
        r"已知 $L_1 // L_2$，若 $\angle {known} = {val}^\circ$，求 $\angle {target}$。",
    ])
    
    question_text = question_template.replace("{known}", readable_labels[known_angle_pos_str]) \
                                     .replace("{val}", str(initial_angle_val)) \
                                     .replace("{target}", readable_labels[target_angle_pos_str])
    
    # 產生 Base64 圖片
    image_base64 = _draw_parallel_lines_with_transversal(angle_labels=angle_labels_for_drawing)

    return {
        "question_text": question_text,
        "correct_answer": str(correct_answer),
        "image_base64": image_base64
    }

# --- 問題類型 2: 代數角度計算 ---
def _generate_type2_problem():
    # 隨機選擇一個關係類型，用於建立方程式
    relationship_types = [
        'corresponding_equal',       # 同位角相等
        'alternate_interior_equal',  # 內錯角相等
        'consecutive_interior_supplementary', # 同側內角互補
        'vertical_opposite_equal',   # 對頂角相等
        'straight_line_supplementary' # 直線上的角互補
    ]
    chosen_relationship = random.choice(relationship_types)

    # 隨機生成一個 x 的合理整數解
    x_solution = random.randint(5, 25) 

    # 定義 8 個標準角度位置
    angle_positions = [f"angle{i}" for i in range(1, 9)]
    
    # 建立角度類型映射
    angle_type_map = {
        'angle1': 'obtuse', 'angle2': 'acute', 'angle3': 'acute', 'angle4': 'obtuse',
        'angle5': 'obtuse', 'angle6': 'acute', 'angle7': 'acute', 'angle8': 'obtuse'
    }

    # Helper to check if two angles have a specific relationship
    def check_relationship(p1_str, p2_str, rel_type):
        # Angle groups for top intersection (1,2,3,4) and bottom intersection (5,6,7,8)
        top_angles_set = {'angle1', 'angle2', 'angle3', 'angle4'}
        bottom_angles_set = {'angle5', 'angle6', 'angle7', 'angle8'}

        # Vertical opposite angles (always equal)
        vertical_pairs = [('angle1', 'angle4'), ('angle2', 'angle3'), 
                          ('angle5', 'angle8'), ('angle6', 'angle7')]
        
        # Angles on a straight line (supplementary) - explicit pairs
        straight_line_pairs_explicit = [
            ('angle1', 'angle2'), ('angle2', 'angle1'), 
            ('angle3', 'angle4'), ('angle4', 'angle3'), 
            ('angle1', 'angle3'), ('angle3', 'angle1'), 
            ('angle2', 'angle4'), ('angle4', 'angle2'), 
            ('angle5', 'angle6'), ('angle6', 'angle5'), 
            ('angle7', 'angle8'), ('angle8', 'angle7'), 
            ('angle5', 'angle7'), ('angle7', 'angle5'), 
            ('angle6', 'angle8'), ('angle8', 'angle6')  
        ]
        
        # Corresponding angles (L1 // L2, equal)
        corresponding_pairs = [('angle1', 'angle5'), ('angle2', 'angle6'), ('angle3', 'angle7'), ('angle4', 'angle8')]
        # Alternate interior angles (L1 // L2, equal)
        alternate_interior_pairs = [('angle3', 'angle6'), ('angle4', 'angle5')]
        # Consecutive interior angles (L1 // L2, supplementary)
        consecutive_interior_pairs = [('angle3', 'angle5'), ('angle4', 'angle6')]

        if rel_type == 'vertical_opposite_equal':
            return (p1_str, p2_str) in vertical_pairs or (p2_str, p1_str) in vertical_pairs
        elif rel_type == 'straight_line_supplementary':
            return (p1_str, p2_str) in straight_line_pairs_explicit
        elif rel_type == 'corresponding_equal':
            return (p1_str, p2_str) in corresponding_pairs or (p2_str, p1_str) in corresponding_pairs
        elif rel_type == 'alternate_interior_equal':
            return (p1_str, p2_str) in alternate_interior_pairs or (p2_str, p1_str) in alternate_interior_pairs
        elif rel_type == 'consecutive_interior_supplementary':
            return (p1_str, p2_str) in consecutive_interior_pairs or (p2_str, p1_str) in consecutive_interior_pairs
        return False

    # Find valid angle positions for the chosen relationship
    valid_pairs = []
    for i in range(8):
        for j in range(8):
            if i == j: continue
            if check_relationship(angle_positions[i], angle_positions[j], chosen_relationship):
                valid_pairs.append((angle_positions[i], angle_positions[j]))
    
    # If no specific valid pair is found (should not happen with comprehensive lists),
    # fall back to choosing two distinct angles for a general problem.
    if not valid_pairs:
        while True:
            pos1_idx = random.randint(0, 7)
            pos2_idx = random.randint(0, 7)
            if pos1_idx != pos2_idx:
                valid_pairs.append((angle_positions[pos1_idx], angle_positions[pos2_idx]))
                break
    
    angle_pos1_str, angle_pos2_str = random.choice(valid_pairs)

    # Determine base angle values (acute/obtuse)
    # Pick a random acute angle between 30 and 80 degrees
    base_acute_angle = random.randint(30, 80)
    base_obtuse_angle = 180 - base_acute_angle

    # Assign angle values based on their type
    angle_val_pos1 = base_acute_angle if angle_type_map[angle_pos1_str] == 'acute' else base_obtuse_angle
    
    # Determine angle_val_pos2 based on relationship
    if chosen_relationship in ['corresponding_equal', 'alternate_interior_equal', 'vertical_opposite_equal']:
        angle_val_pos2 = angle_val_pos1
    elif chosen_relationship in ['consecutive_interior_supplementary', 'straight_line_supplementary']:
        angle_val_pos2 = 180 - angle_val_pos1
    else: # Fallback to general case (e.g., if valid_pairs was chosen randomly)
        if angle_type_map[angle_pos1_str] == angle_type_map[angle_pos2_str]:
            angle_val_pos2 = angle_val_pos1
        else:
            angle_val_pos2 = 180 - angle_val_pos1

    # Generate first expression (ax + b)
    a = random.randint(1, 5)
    b = angle_val_pos1 - a * x_solution
    # Ensure a, b lead to reasonable values and a positive angle (1 to 180 degrees)
    while not (1 <= a <= 5 and -50 <= b <= 50 and (a * x_solution + b) > 0 and (a * x_solution + b) <= 180):
        a = random.randint(1, 5)
        b = angle_val_pos1 - a * x_solution

    # Format LaTeX string for drawing (e.g., "2x+10" or "3x-5")
    expr1_str_latex = f"{a}x" + (f" + {b}" if b > 0 else f" {b}" if b < 0 else "")
    # Format string for question text (e.g., "(2x + 10)^\circ" or "(3x - 5)^\circ")
    expr1_str_question = r"({a}x {op} {b})^\circ".replace("{a}", str(a)).replace("{op}", "+" if b>=0 else "-").replace("{b}", str(abs(b)))

    # Generate second expression (cx + d) or constant
    is_second_expr_algebraic = random.choice([True, False])
    expr2_str_latex = ""
    expr2_str_question = ""
    
    angle_labels_for_drawing = {}

    if is_second_expr_algebraic:
        c = random.randint(1, 5)
        # Avoid trivial cases like (ax+b) = (ax+d) if angles are equal
        if angle_val_pos1 == angle_val_pos2:
            while c == a:
                c = random.randint(1, 5)
        d = angle_val_pos2 - c * x_solution
        while not (1 <= c <= 5 and -50 <= d <= 50 and (c * x_solution + d) > 0 and (c * x_solution + d) <= 180):
            c = random.randint(1, 5)
            if angle_val_pos1 == angle_val_pos2:
                while c == a:
                    c = random.randint(1, 5)
            d = angle_val_pos2 - c * x_solution
            
        expr2_str_latex = f"{c}x" + (f" + {d}" if d > 0 else f" {d}" if d < 0 else "")
        expr2_str_question = r"({c}x {op} {d})^\circ".replace("{c}", str(c)).replace("{op}", "+" if d>=0 else "-").replace("{d}", str(abs(d)))
        
        angle_labels_for_drawing = {
            angle_pos1_str: expr1_str_latex,
            angle_pos2_str: expr2_str_latex
        }
    else: # Second angle is a constant value
        expr2_str_latex = str(angle_val_pos2) + r"^\circ" # For drawing, include degree symbol
        expr2_str_question = r"{val}^\circ".replace("{val}", str(angle_val_pos2)) # For question text
        
        angle_labels_for_drawing = {
            angle_pos1_str: expr1_str_latex,
            angle_pos2_str: str(angle_val_pos2) + r"^\circ" # Must be latex string for drawing
        }

    # 產生問題文字
    question_template = random.choice([
        r"如圖所示，$L_1 // L_2$，求 $x$ 的值。圖中標示的兩個角分別為 ${expr1}$ 和 ${expr2}$。",
        r"已知 $L_1 // L_2$，且圖中 $\angle {label1} = {expr1}$ 和 $\angle {label2} = {expr2}$，求 $x$ 的值。",
        r"下圖中，$L_1$ 平行於 $L_2$，請根據圖中標示的 ${expr1}$ 和 ${expr2}$，計算 $x$ 的值。"
    ])
    readable_labels = {f"angle{i}": str(i) for i in range(1, 9)}
    
    question_text = question_template.replace("{expr1}", expr1_str_question).replace("{expr2}", expr2_str_question)
    question_text = question_text.replace("{label1}", readable_labels[angle_pos1_str]).replace("{label2}", readable_labels[angle_pos2_str])

    # 產生 Base64 圖片
    image_base64 = _draw_parallel_lines_with_transversal(angle_labels=angle_labels_for_drawing)

    return {
        "question_text": question_text,
        "correct_answer": str(x_solution),
        "image_base64": image_base64
    }

# --- 頂層生成函式 ---
def generate(level: int = 1) -> dict:
    """
    根據指定難度等級生成截線與截角相關的數學問題。

    Args:
        level (int): 難度等級，目前僅支持 level=1。

    Returns:
        dict: 包含問題文本、正確答案、圖片 Base64 編碼的字典。
    """
    problem_type = random.choice([1, 2]) # 隨機選擇問題類型
    
    if problem_type == 1:
        problem_data = _generate_type1_problem()
    elif problem_type == 2:
        problem_data = _generate_type2_problem()
    else:
        raise ValueError("Invalid problem type selected.")

    return {
        "question_text": problem_data["question_text"],
        "correct_answer": problem_data["correct_answer"],
        "answer": "", # 預留給使用者輸入
        "image_base64": problem_data["image_base64"],
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

# --- 頂層批改函式 ---
# [CRITICAL CODING STANDARDS: Verification & Stability]
# 2. 通用 Check 函式模板 (Universal Check Template)

    """
    批改使用者答案。

    Args:
        user_answer (str): 使用者輸入的答案。
        correct_answer (str): 系統生成的正確答案。

    Returns:
        dict: 包含 'correct' (bool) 和 'result' (str) 的字典。
    """
    import re, math
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=
        s = s.replace("$", "").replace("\\", "")
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
        
        if math.isclose(parse_val(u), parse_val(c), rel_tol=1e-5):
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
