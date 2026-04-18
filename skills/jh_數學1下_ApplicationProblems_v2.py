# ==============================================================================
# ID: jh_數學1下_ApplicationProblems_v2
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 71.29s | RAG: 3 examples
# Created At: 2026-01-16 14:49:10
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


import base64
from io import BytesIO
from datetime import datetime


# Assuming matplotlib is available for drawing
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Helper function for coordinate generation (V10.2 A)
def _generate_coordinate_value(min_val=-8, max_val=8, allow_fraction=False):
    """
    Generates a coordinate value, either integer or mixed fraction.
    Returns (float_val, (int_part, num, den, is_neg)).
    V10.2 A, V13.0, V13.1, V13.5
    """
    is_neg = random.choice([True, False])
    # V13.0 【座標選取控制】
    base_val = random.randint(0, max_val) 
    
    num, den = 0, 0
    float_val = float(base_val)

    if allow_fraction and random.random() < 0.5: # 50% chance to be a fraction if allowed
        # V13.1 【禁絕假分數】: numerator < denominator and denominator > 1
        den = random.randint(2, 5) # Denominators like 2, 3, 4, 5
        num = random.randint(1, den - 1) # Numerator smaller than denominator
        
        if num == 0: # Ensure numerator is not zero if it's a fraction
            num = 1
        
        float_val = base_val + num / den
    
    if is_neg:
        float_val = -float_val

    # V13.5 【整數優先】
    if float_val.is_integer():
        float_val = int(float_val)
        num, den = 0, 0 # Reset fraction parts if it's an integer
        int_part = abs(int(float_val))
    else:
        int_part = abs(base_val) # For mixed fraction display, int_part is absolute

    return (float_val, (int_part, num, den, is_neg))

# Helper function to format coordinate value as LaTeX string (V10.2 C, V13.5)
def _format_coordinate_latex(float_val, data_tuple):
    int_part, num, den, is_neg = data_tuple
    
    # V13.5 【整數優先】
    if isinstance(float_val, int):
        return str(float_val)

    # V10.2 C: LaTeX template using single layer braces
    sign = "-" if is_neg and float_val != 0 else ""
    if num == 0: # It's an integer or 0
        return str(int(float_val))
    else: # It's a fraction
        if int_part == 0: # Pure fraction (e.g., -1/2)
            return r"{sign}\frac{{{num}}}{{{den}}}".replace("{sign}", sign).replace("{num}", str(num)).replace("{den}", str(den))
        else: # Mixed fraction (e.g., -1 1/2)
            return r"{sign}{int_part}\frac{{{num}}}{{{den}}}".replace("{sign}", sign).replace("{int_part}", str(int_part)).replace("{num}", str(num)).replace("{den}", str(den))

# Helper function for drawing coordinates (if needed)
def _draw_coordinate_plane(points, x_range=(-8, 8), y_range=(-8, 8), point_labels=None):
    """
    Draws a coordinate plane with optional points.
    V10.2 B, D; V13.0; V13.1; V13.5; V13.6
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # V10.2 D: ax.set_aspect('equal')
    ax.set_aspect('equal')

    # V13.0 【格線對齊】: Symmetric range, xticks interval 1
    ax.set_xlim(x_range[0], x_range[1])
    ax.set_ylim(y_range[0], y_range[1])
    ax.set_xticks(range(x_range[0], x_range[1] + 1))
    ax.set_yticks(range(y_range[0], y_range[1] + 1))
    
    ax.grid(True, linestyle='--', alpha=0.6)

    # Draw axes with arrows (V13.6 【Arrow Ban】)
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axvline(0, color='black', linewidth=1.5)
    
    # Arrows for x-axis (V13.6)
    ax.plot(x_range[1], 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(x_range[0], 0, "<k", transform=ax.get_yaxis_transform(), clip_on=False) # Left arrow
    # Arrows for y-axis (V13.6)
    ax.plot(0, y_range[1], "^k", transform=ax.get_xaxis_transform(), clip_on=False)
    ax.plot(0, y_range[0], "vk", transform=ax.get_xaxis_transform(), clip_on=False) # Down arrow


    # V10.2 D: Label origin '0' (18号加粗)
    ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold')

    # V13.6 【Strict Labeling】: Whitelist for point names
    valid_labels = ['A', 'B', 'C', 'D', 'P', 'Q', 'R', 'S', 'O', 'M', 'N', 'X', 'Y', 'Z']

    if point_labels is None:
        point_labels = [f"P{i+1}" for i in range(len(points))]

    for i, (x, y) in enumerate(points):
        label = point_labels[i] if i < len(point_labels) and point_labels[i] in valid_labels else f"P{i+1}"
        ax.plot(x, y, 'o', color='red', markersize=8)
        # V13.0 【標註權限隔離】 & V13.1 【標籤純淨化】 & V13.5 【標籤隔離】
        # ax.text only for point name, not coordinate values
        ax.text(x, y, label, 
                fontsize=12, ha='right', va='bottom', 
                bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='none', alpha=0.7)) # V10.2 D: white glow

    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title('')

    # Convert plot to base64 image
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# Helper function for drawing simple shapes (e.g., rectangle for area/perimeter)
def _draw_rectangle(width, height):
    """
    Draws a simple rectangle with width and height labels.
    """
    fig, ax = plt.subplots(figsize=(5, 5))
    rect = patches.Rectangle((0, 0), width, height, linewidth=2, edgecolor='blue', facecolor='lightblue', alpha=0.7)
    ax.add_patch(rect)

    ax.set_xlim(-width*0.1, width*1.1)
    ax.set_ylim(-height*0.1, height*1.1)
    ax.set_aspect('equal')
    ax.axis('off') # Hide axes for simple shape

    # Add labels for width and height
    ax.text(width/2, -height*0.05, f"{width}", ha='center', va='top', fontsize=12)
    ax.text(-width*0.05, height/2, f"{height}", ha='right', va='center', fontsize=12)

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def generate(level=1):
    # Problem type chosen based on MANDATORY MIRRORING RULES (RAG Ex 1, 2, 3)
    problem_type = random.choice([1, 2, 3]) 

    question_text = ""
    correct_answer = ""
    answer_display = ""
    image_base64 = None

    if problem_type == 1:
        # Type 1 (Maps to RAG Ex 1): Ratio Relationship and Allocation
        # RAG Ex 1: 已知小翊零用錢的 2 倍和小靖零用錢的 3 倍一樣多，則：
        # ⑴ 小翊的零用錢：小靖的零用錢=？
        # ⑵ 承⑴，若小翊和小靖的零用錢共有 500 元，那麼小翊和小靖的零用錢各有多少元？
        
        coeff1 = random.randint(2, 5) # Multiplier for person1 (e.g., 2 for 小翊)
        coeff2 = random.randint(2, 5) # Multiplier for person2 (e.g., 3 for 小靖)
        while coeff1 == coeff2:
            coeff2 = random.randint(2, 5)

        person1_name = random.choice(["小翊", "巴奈", "ACEF"]) # Context retention
        person2_name = random.choice(["小靖", "BDF", "小華"]) # Context retention
        while person1_name == person2_name:
            person2_name = random.choice(["小靖", "BDF", "小華"])

        # From coeff1 * P1 = coeff2 * P2, we get P1 : P2 = coeff2 : coeff1
        ratio_p1 = coeff2
        ratio_p2 = coeff1
        
        base_unit = random.randint(50, 150)
        # Ensure total_money is a multiple of (ratio_p1 + ratio_p2) for integer results
        total_money = (ratio_p1 + ratio_p2) * base_unit

        p1_actual_money = ratio_p1 * base_unit
        p2_actual_money = ratio_p2 * base_unit

        question_text_part1 = r"已知{person1_name}零用錢的{coeff1}倍和{person2_name}零用錢的{coeff2}倍一樣多，則：⑴ {person1_name}的零用錢：{person2_name}的零用錢=？".replace("{person1_name}", person1_name).replace("{coeff1}", str(coeff1)).replace("{person2_name}", person2_name).replace("{coeff2}", str(coeff2))
        question_text_part2 = r"⑵ 承⑴，若{person1_name}和{person2_name}的零用錢共有{total_money}元，那麼{person1_name}和{person2_name}的零用錢各有多少元？".replace("{person1_name}", person1_name).replace("{person2_name}", person2_name).replace("{total_money}", str(total_money))
        
        question_text = question_text_part1 + question_text_part2

        # For correct_answer, only include the numerical values for comparison
        # The check function handles list parsing. Order reflects person1 then person2.
        correct_answer_list = [p1_actual_money, p2_actual_money]
        correct_answer = str(correct_answer_list) 
        
        # Answer display includes the full text answer as in RAG example
        answer_display = r"⑴ {ratio_p1}：{ratio_p2}⑵ {person1_name} {p1_actual_money} 元，{person2_name} {p2_actual_money} 元".replace("{ratio_p1}", str(ratio_p1)).replace("{ratio_p2}", str(ratio_p2)).replace("{person1_name}", person1_name).replace("{p1_actual_money}", str(p1_actual_money)).replace("{person2_name}", person2_name).replace("{p2_actual_money}", str(p2_actual_money))

    elif problem_type == 2:
        # Type 2 (Maps to RAG Ex 2): Changing Ratio Problem (simultaneous equations)
        # RAG Ex 2: 亞駿和雅婷都喜愛跑馬拉松，已知兩人原本跑的公里數比是 6：5，後來兩人分別又跑了 5 公里和 3 公里，結果總里程數的比變為 5：4，則兩人原本各跑了多少公里？
        
        person1_name = random.choice(["亞駿", "小明", "大華"]) # Context retention
        person2_name = random.choice(["雅婷", "小紅", "小美"]) # Context retention
        while person1_name == person2_name:
            person2_name = random.choice(["雅婷", "小紅", "小美"])

        # Generate initial values and changes that lead to integer solutions
        k_val = random.randint(3, 10) # Common multiplier for initial ratio
        initial_ratio_a = random.randint(4, 8)
        initial_ratio_b = random.randint(4, 8)
        while initial_ratio_a == initial_ratio_b: # Ensure distinct initial ratios for more variety
            initial_ratio_b = random.randint(4, 8)

        original_p1_km = initial_ratio_a * k_val
        original_p2_km = initial_ratio_b * k_val

        added_p1_km = random.randint(2, 7)
        added_p2_km = random.randint(2, 7)
        
        # Calculate final ratios based on adjusted distances
        new_p1_km = original_p1_km + added_p1_km
        new_p2_km = original_p2_km + added_p2_km

        common_divisor = math.gcd(new_p1_km, new_p2_km)
        final_ratio_a = new_p1_km // common_divisor
        final_ratio_b = new_p2_km // common_divisor
        
        question_text = r"{person1_name}和{person2_name}都喜愛跑馬拉松，已知兩人原本跑的公里數比是 {initial_ratio_a}：{initial_ratio_b}，後來兩人分別又跑了 {added_p1_km} 公里和 {added_p2_km} 公里，結果總里程數的比變為 {final_ratio_a}：{final_ratio_b}，則兩人原本各跑了多少公里？".replace("{person1_name}", person1_name).replace("{person2_name}", person2_name).replace("{initial_ratio_a}", str(initial_ratio_a)).replace("{initial_ratio_b}", str(initial_ratio_b)).replace("{added_p1_km}", str(added_p1_km)).replace("{added_p2_km}", str(added_p2_km)).replace("{final_ratio_a}", str(final_ratio_a)).replace("{final_ratio_b}", str(final_ratio_b))
        
        # For correct_answer, only include the numerical values
        correct_answer_list = [original_p1_km, original_p2_km]
        correct_answer = str(correct_answer_list)

        answer_display = r"{person1_name} {original_p1_km} 公里，{person2_name} {original_p2_km} 公里".replace("{person1_name}", person1_name).replace("{original_p1_km}", str(original_p1_km)).replace("{person2_name}", person2_name).replace("{original_p2_km}", str(original_p2_km))

    elif problem_type == 3:
        # Type 3 (Maps to RAG Ex 3): Scale/Proportion Problem
        # RAG Ex 3: 右圖是臺灣鐵道路線圖，小妍用尺量得花蓮站到臺東站的距離約為 3 公分，比例尺為 2cm 對應 100km，則這兩站的實際距離約為多少公里？
        
        loc1_name = random.choice(["花蓮站", "臺北站", "高雄站"]) # Context retention
        loc2_name = random.choice(["臺東站", "臺中站", "墾丁站"]) # Context retention
        while loc1_name == loc2_name:
            loc2_name = random.choice(["臺東站", "臺中站", "墾丁站"])
        
        # Ensure '小妍' is mentioned as in the RAG example
        person_measuring = "小妍"

        # Dynamize scale and measured distance to ensure clean actual distance
        scale_map_cm = random.choice([1, 2]) # e.g., 1cm or 2cm
        scale_actual_km = random.choice([50, 100, 150, 200]) # e.g., 50km, 100km
        
        # Measured distance should be a multiple of 0.5 if scale_map_cm is 2, or any for 1
        if scale_map_cm == 1:
            measured_cm = random.choice([2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
        else: # scale_map_cm == 2
            measured_cm = random.choice([2.0, 3.0, 4.0, 5.0, 2.5, 3.5, 4.5]) # Include half cm to match RAG example 3cm/2cm=1.5
        
        actual_distance_km = (measured_cm / scale_map_cm) * scale_actual_km
        
        # Ensure actual_distance_km is an integer or has one decimal place for K12 context
        if not actual_distance_km.is_integer():
            actual_distance_km = round(actual_distance_km, 1)
        else:
            actual_distance_km = int(actual_distance_km) # Convert to int if it's whole

        # The RAG example says "右圖是臺灣鐵道路線圖", implying an image.
        # However, no specific drawing helper function is provided for this type of image.
        # As per "視覺化函式僅能接收「題目已知數據」。嚴禁將「答案數據」傳入繪圖函式。"
        # and "視覺絕對淨化 (Zero-Graph Protocol)" for coordinate plane,
        # and given no specific image generation for a "railway map" in the helper functions,
        # image_base64 will remain None.

        question_text = r"右圖是臺灣鐵道路線圖，{person_measuring}用尺量得{loc1_name}到{loc2_name}的距離約為 {measured_cm} 公分，比例尺為 {scale_map_cm}cm 對應 {scale_actual_km}km，則這兩站的實際距離約為多少公里？".replace("{person_measuring}", person_measuring).replace("{loc1_name}", loc1_name).replace("{loc2_name}", loc2_name).replace("{measured_cm}", str(measured_cm)).replace("{scale_map_cm}", str(scale_map_cm)).replace("{scale_actual_km}", str(scale_actual_km))
        
        correct_answer = str(actual_distance_km)
        answer_display = r"約 {actual_distance_km} 公里".replace("{actual_distance_km}", str(actual_distance_km))

    # Final structure and return (V7.0)
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display, # This is the display format for the answer
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    # V12.6 【結構鎖死】 & V13.5 【禁絕複雜比對】: Numeric sequence comparison
    # V13.6 【Exact Check Logic】: Coder 必須逐字複製
    try:
        # Attempt to parse user_answer as a comma-separated list of numbers
        user_nums = [float(s.strip()) for s in user_answer.replace('(', '').replace(')', '').split(',')]
    except ValueError:
        return False # If user_answer is not a valid number or comma-separated list

    try:
        # correct_answer could be a string representing a single number or a list
        if '[' in correct_answer and ']' in correct_answer:
            # It's a stringified list, e.g., "[10, 20]"
            correct_nums_str = correct_answer.strip('[]').split(',')
            correct_nums = [float(s.strip()) for s in correct_nums_str]
        else:
            # It's a single number string
            correct_nums = [float(correct_answer)]
    except ValueError:
        return False # Should not happen if generate produces valid correct_answer

    if len(user_nums) != len(correct_nums):
        return False
    
    # Convert to int if they are effectively integers for robust comparison (V13.5 【整數優先】)
    user_int_nums = [int(n) if n.is_integer() else n for n in user_nums]
    correct_int_nums = [int(n) if n.is_integer() else n for n in correct_nums]

    # Compare directly for strict order (V12.6)
    return user_int_nums == correct_int_nums

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
