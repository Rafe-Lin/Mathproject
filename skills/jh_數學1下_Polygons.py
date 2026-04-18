# ==============================================================================
# ID: jh_數學1下_Polygons
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 49.52s | RAG: 3 examples
# Created At: 2026-01-17 23:27:07
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

import re
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# --- Helper Functions (遵循 V10.2, V13.0, V13.1, V13.5, V13.6 規範) ---

def _generate_coordinate_value(is_fraction=False, integer_range=(-8, 8)):
    """
    目的: 統一生成座標數值，可以是整數或帶分數。
    V10.2 A 規範: 必須回傳固定格式 (float_val, (int_part, num, den, is_neg))。
    V13.0 規範: integer_range, int_part 若為 0 則重新生成。
    V13.1 規範 (禁絕假分數): num < den, den > 1, 建議 num (1,3), den (num+1, 5)。
    """
    is_neg = False
    float_val = 0
    int_part = 0
    num = 0
    den = 0

    # 1. 隨機決定是否生成分數 (例如 70% 機率為整數，30% 機率為分數)
    # V13.0: 生成整數時，直接使用 random.randint
    if not is_fraction or random.random() < 0.7:  
        int_part = random.randint(integer_range[0], integer_range[1])
        float_val = float(int_part)
        is_neg = int_part < 0
        return float_val, (int_part, 0, 0, is_neg)
    else:
        # V13.0: 生成分數時，先生成 int_part (若為 0 則重新生成以避免混淆)
        int_part = random.randint(integer_range[0], integer_range[1])
        while int_part == 0:
            int_part = random.randint(integer_range[0], integer_range[1])
        
        # V13.1 規範 (禁絕假分數)
        numerator = random.randint(1, 3) 
        denominator = random.randint(numerator + 1, 5) # 確保 numerator < denominator 且 denominator > 1
        
        is_neg = int_part < 0
        
        # 根據 int_part 和分數部分計算 float_val
        float_val = abs(int_part) + numerator / denominator
        if is_neg:
            float_val = -float_val
        
        return float_val, (int_part, numerator, denominator, is_neg)

def _format_coordinate_display(val_data):
    """
    目的: 將 _generate_coordinate_value 回傳的數據格式化為 LaTeX 字串。
    V10.2 A 規範: 嚴格解包 data[1]。
    V10.2 C 規範 (LaTeX 模板規範): 嚴禁 f"{{...}}", 必須用 .replace()。
    V13.0 規範 (格式精確要求): 整數輸出如 "5" 而非 "5.0"。
    """
    float_val, data_parts = val_data
    # V10.2 A 規範
    int_part, num, den, is_neg = data_parts
    
    # V13.0 規範
    if num == 0: # It's an integer
        return str(int(float_val))
    else:
        sign_str = "-" if is_neg and int_part == 0 else "" # 處理純分數的負號
        if int_part == 0: # Pure fraction (e.g., 1/2 or -1/2)
            # V10.2 C 規範
            return r"{}\frac{{{num}}}{{{den}}}".replace("{}", sign_str).replace("{num}", str(num)).replace("{den}", str(den))
        else: # Mixed fraction (e.g., 1 and 1/2 or -1 and 1/2)
            # V10.2 C 規範
            return r"{}{int_part}\frac{{{num}}}{{{den}}}".replace("{}", sign_str).replace("{int_part}", str(abs(int_part))).replace("{num}", str(num)).replace("{den}", str(den))

def draw_coordinate_plane(points_with_labels, x_range=(-8, 8), y_range=(-8, 8), plot_points=True):
    """
    目的: 繪製座標平面，並可選擇性地標示點。
    遵循 V13.6, V13.5, V13.1, V13.0, V10.2 規範及 ULTRA VISUAL STANDARDS, SYSTEM GUARDRAILS。
    """
    fig, ax = plt.subplots(figsize=(6, 6), dpi=300) # V11.6 Resolution

    ax.set_aspect('equal') # V10.2 D, V11.6 Aspect Ratio

    ax.set_xlim(x_range[0], x_range[1])
    ax.set_ylim(y_range[0], y_range[1])

    # V13.0, CRITICAL RULE: Visual Solvability, System Guardrail 6 (強制顯示刻度)
    ax.set_xticks(np.arange(x_range[0], x_range[1] + 1, 1))
    ax.set_yticks(np.arange(y_range[0], y_range[1] + 1, 1))
    ax.grid(True, linestyle='--', alpha=0.6) # V10.2 D, System Guardrail 8 (網格線輔助)

    # V13.6 API Hardened Spec (Arrow Ban) - 使用 plot 繪製箭頭
    ax.plot(x_range[1], 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False, markersize=8) # X軸右箭頭
    ax.plot(x_range[0], 0, "<k", transform=ax.get_yaxis_transform(), clip_on=False, markersize=8) # X軸左箭頭
    ax.plot(0, y_range[1], "^k", transform=ax.get_xaxis_transform(), clip_on=False, markersize=8) # Y軸上箭頭
    ax.plot(0, y_range[0], "vk", transform=ax.get_xaxis_transform(), clip_on=False, markersize=8) # Y軸下箭頭

    # V10.2 D: 原點 '0' (18號加粗, 白色光暈)
    ax.text(0, 0, '0', color='black', ha='center', va='center', fontsize=18, fontweight='bold',
            bbox=dict(facecolor='white', edgecolor='none', pad=1))

    ax.set_xlabel('X', loc='right', fontsize=12)
    ax.set_ylabel('Y', loc='top', fontsize=12, rotation=0)

    # System Guardrail 7 (座標軸優化)
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.tick_params(axis='both', which='major', labelsize=10)

    # V13.6 Strict Labeling: 定義 label_whitelist
    label_whitelist = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    if plot_points: # V10.2 B 標點題防洩漏協定
        for x, y, label in points_with_labels:
            if label not in label_whitelist:
                raise ValueError(f"Label '{label}' not in whitelist for coordinate points.")
            ax.plot(x, y, 'o', color='red', markersize=8, zorder=5) # 繪製點
            # V13.5 最終硬化規約 (標籤隔離), V13.1 教學正確性補正 (標籤純淨化)
            # V11.6 Label Halo
            ax.text(x, y, label, fontsize=12, ha='right', va='bottom',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300) # V11.6 Resolution
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64

# --- 頂層函式規範 ---

def generate(level=1):
    """
    目的: 根據隨機選取的題型生成題目、答案和圖形。
    程式結構: 嚴禁使用 class 封裝，直接定義於模組最外層。
    題型鏡射 (Problem Mirroring): 內部使用 random.choice 對應 RAG 例題。
    數據禁絕常數: 所有數據動態化。
    """
    problem_type = random.choice([1, 2, 3, 4]) # 隨機選擇四種題型之一

    question_text = ""
    correct_answer = ""
    image_base64 = ""
    
    # 座標範圍與點標籤
    x_range_draw = (-8, 8)
    y_range_draw = (-8, 8)
    point_labels = ['A', 'B', 'C'] # For triangle, use 'A', 'B', 'C'

    if problem_type == 1:
        # Type 1 (Maps to RAG Example 1): 根據邊數判斷多邊形名稱
        num_sides = random.randint(3, 10) # 數據動態化
        
        polygon_names = {
            3: "三角形", 4: "四邊形", 5: "五邊形", 6: "六邊形",
            7: "七邊形", 8: "八邊形", 9: "九邊形", 10: "十邊形"
        }
        
        # question_text 結構, LaTeX 單層大括號
        question_text = r"一個多邊形有 {n} 條邊，它是什麼多邊形？".replace("{n}", str(num_sides))
        correct_answer = polygon_names[num_sides] # V12.6 邏輯驗證硬化規約 (禁絕映射)
        
    elif problem_type == 2:
        # Type 2 (Maps to RAG Example 2): 計算多邊形內角和
        num_sides = random.randint(3, 12) # 數據動態化
        
        sum_angles = (num_sides - 2) * 180 # 數據動態化
        
        # question_text 結構, LaTeX 單層大括號
        question_text = r"一個 {n} 邊形的內角和是多少度？".replace("{n}", str(num_sides))
        correct_answer = str(sum_angles) # 純數字字串
        
    elif problem_type == 3:
        # Type 3 (Maps to RAG Example 3): 計算正多邊形的單一內角或外角
        sub_type = random.choice(['interior', 'exterior'])
        num_sides = random.randint(3, 12) # 數據動態化
        
        if sub_type == 'interior':
            interior_angle = ((num_sides - 2) * 180) / num_sides # 數據動態化
            # question_text 結構, LaTeX 單層大括號
            question_text = r"一個正 {n} 邊形的每個內角是多少度？".replace("{n}", str(num_sides))
            correct_answer = str(round(interior_angle, 2)) # 四捨五入到小數點後 2 位
        else: # exterior
            exterior_angle = 360 / num_sides # 數據動態化
            # question_text 結構, LaTeX 單層大括號
            question_text = r"一個正 {n} 邊形的每個外角是多少度？".replace("{n}", str(num_sides))
            correct_answer = str(round(exterior_angle, 2)) # 四捨五入到小數點後 2 位

    elif problem_type == 4:
        # Type 4 (Maps to Custom RAG Example for Coordinate Geometry): 根據座標判斷三角形類型
        num_vertices = 3 
        
        coords = []
        coord_display_texts = []
        
        # 避免生成共線或重疊點
        generated_points_set = set()

        while len(coords) < num_vertices:
            # V13.0 座標選取控制, V13.5 座標範圍
            x_val_data = _generate_coordinate_value(is_fraction=random.random()<0.2, integer_range=(-5, 5))
            y_val_data = _generate_coordinate_value(is_fraction=random.random()<0.2, integer_range=(-5, 5))
            
            x_float, y_float = x_val_data[0], y_val_data[0]

            # Check for overlapping points
            if (x_float, y_float) in generated_points_set:
                continue

            # Add point to list and set
            coords.append((x_float, y_float))
            generated_points_set.add((x_float, y_float))

            x_display = _format_coordinate_display(x_val_data)
            y_display = _format_coordinate_display(y_val_data)
            
            # LaTeX 單層大括號
            point_text_template = r"{label}({x_val}, {y_val})"
            point_text = point_text_template.replace("{label}", point_labels[len(coords)-1]).replace("{x_val}", x_display).replace("{y_val}", y_display)
            coord_display_texts.append(point_text)

        # 幾何公式計算: 三邊長度平方
        def dist_sq(p1, p2):
            return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

        d_ab_sq = dist_sq(coords[0], coords[1])
        d_bc_sq = dist_sq(coords[1], coords[2])
        d_ca_sq = dist_sq(coords[2], coords[0])

        sides_sq = sorted([d_ab_sq, d_bc_sq, d_ca_sq])
        
        # 判斷共線 (非三角形)
        # Area = 0.5 * |x1(y2-y3) + x2(y3-y1) + x3(y1-y2)|
        area = 0.5 * abs(coords[0][0]*(coords[1][1] - coords[2][1]) +
                         coords[1][0]*(coords[2][1] - coords[0][1]) +
                         coords[2][0]*(coords[0][1] - coords[1][1]))
        
        # V13.5 禁絕複雜比對: 答案判斷基於計算結果，而非字串解析
        if area < 1e-9: # 面積接近零，視為共線
            triangle_type = "非三角形 (共線)"
        elif math.isclose(sides_sq[0], sides_sq[1]) and math.isclose(sides_sq[1], sides_sq[2]):
            triangle_type = "正三角形"
        elif math.isclose(sides_sq[0], sides_sq[1]) or math.isclose(sides_sq[1], sides_sq[2]):
            triangle_type = "等腰三角形"
        else:
            triangle_type = "不等邊三角形"
        
        # question_text 結構, LaTeX 單層大括號
        question_text = r"在座標平面上標出點 {p1}, {p2}, {p3}，並判斷此多邊形為何種三角形。".replace(
            "{p1}", coord_display_texts[0]).replace(
            "{p2}", coord_display_texts[1]).replace(
            "{p3}", coord_display_texts[2])
        
        correct_answer = triangle_type # 純數據字串
        
        # image_base64 規範: 呼叫 draw_coordinate_plane, plot_points=True
        points_to_draw = [(c[0], c[1], point_labels[i]) for i, c in enumerate(coords)]
        image_base64 = draw_coordinate_plane(points_to_draw, x_range=x_range_draw, y_range=y_range_draw, plot_points=True)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "", 
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

# V4. 強韌閱卷邏輯 (Robust Check Logic), V13.6 Exact Check Logic
# System Guardrail 1: 閱卷決定論 (Deterministic Grading)
# System Guardrail 7: 閱卷與反饋 (check 僅限回傳 True/False)

    # V4. 輸入清洗 (Input Sanitization)
    # V13.6 Exact Check Logic: 必須逐字複製以下 4-line 檢查邏輯，不得自行發揮。
    cleaned_user_answer = re.sub(r'[$\\x=y=k=Ans:\{\}\s]', '', str(user_answer), flags=re.IGNORECASE)
    cleaned_correct_answer = re.sub(r'[$\\x=y=k=Ans:\{\}\s]', '', str(correct_answer), flags=re.IGNORECASE)

    try:
        # V4. 支援多種數學格式的等價性 (例如：1/2 = 0.5)
        # V12.6 結構鎖死: 嘗試將答案轉換為浮點數進行數值比對 (適用於 Type 2, Type 3)
        user_num = float(cleaned_user_answer)
        correct_num = float(cleaned_correct_answer)
        # 使用 math.isclose 處理浮點數精度問題
        return math.isclose(user_num, correct_num, rel_tol=1e-5)
    except ValueError:
        # V12.6 結構鎖死: 如果無法轉換為數字，則進行字串比對 (適用於 Type 1, Type 4)
        # V13.5 禁絕複雜比對: 直接比對清洗後的字串
        return cleaned_user_answer.lower() == cleaned_correct_answer.lower()

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
