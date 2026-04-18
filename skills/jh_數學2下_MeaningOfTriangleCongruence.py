# ==============================================================================
# ID: jh_數學2下_MeaningOfTriangleCongruence
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 75.89s | RAG: 2 examples
# Created At: 2026-01-22 20:45:23
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
import matplotlib.pyplot as plt
from datetime import datetime
import re

def _generate_coordinate_value(min_val=-7, max_val=7, allow_fraction=False):
    """
    [V10.2 A. 資料結構鎖死] [V13.0 座標選取控制]
    生成一個座標值 (整數或半整數) 及其格式化的組成部分。
    回傳: (float_val, (int_part, num, den, is_neg))
    """
    if allow_fraction and random.random() < 0.5: # 約 50% 機率生成半整數
        val = random.randint(min_val, max_val) + 0.5
        is_neg = val < 0
        abs_val = abs(val)
        int_part = int(abs_val)
        num = 1 if abs_val - int_part == 0.5 else 0
        den = 2 if num == 1 else 0
        return val, (int_part, num, den, is_neg)
    else: # 整數
        val = random.randint(min_val, max_val)
        is_neg = val < 0
        int_part = abs(val)
        num = 0
        den = 0
        return float(val), (int_part, num, den, is_neg)

def _format_coordinate_for_display(val_data):
    """
    [V13.0 格式精確要求] [V13.5 整數優先]
    格式化座標值以供顯示，確保整數顯示為整數形式。
    """
    val_float, _ = val_data # 忽略後面的數據元組，僅使用浮點值
    if val_float.is_integer():
        return str(int(val_float))
    else:
        # [V13.1 禁絕假分數]: 半整數顯示為小數形式，避免複雜分數處理。
        return str(val_float)

def _calculate_distance(p1, p2):
    """
    計算兩點 (x1, y1) 和 (x2, y2) 之間的歐幾里得距離。
    """
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

# 2. 繪圖函式定義 (Drawing Function, V10.2, V13.0, V13.1, V13.5, V13.6, V17.0)
def draw_coordinate_plane(points_with_labels, x_range=(-10, 10), y_range=(-10, 10)):
    """
    [座標鎖死] [V10.2 D. 視覺一致性] [V13.0 格線對齊] [V13.6 API Hardened Spec]
    [V17.0 圖表必須可解]
    繪製座標平面，標註點和軸。
    `points_with_labels` 格式為 `[((x, y), 'Label'), ...]`。
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # [V10.2 D. 視覺一致性] 確保網格為正方形
    ax.set_aspect('equal')
    
    # 網格與軸線限制 [V13.0 格線對齊]
    ax.set_xlim(x_range)
    ax.set_ylim(y_range)
    
    # [V17.0 座標與數線規範] 主要刻度每 1 單位，並顯示標籤
    ax.set_xticks(range(x_range[0], x_range[1] + 1))
    ax.set_yticks(range(y_range[0], y_range[1] + 1))
    
    # 顯示所有整數刻度標籤 [V17.0 圖表必須可解]
    ax.set_xticklabels([str(int(t)) for t in ax.get_xticks()])
    ax.set_yticklabels([str(int(t)) for t in ax.get_yticks()])

    # 次要刻度與網格
    ax.minorticks_on()
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    
    # 繪製座標軸 [V13.6 API Hardened Spec]
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axvline(0, color='black', linewidth=1.5)
    
    # 座標軸箭頭 [V13.6 API Hardened Spec]
    ax.plot(x_range[1], 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False, markersize=8)
    ax.plot(0, y_range[1], "^k", transform=ax.get_xaxis_transform(), clip_on=False, markersize=8)

    # 標註原點 '0' [V10.2 D. 視覺一致性]
    ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))
    
    # 繪製點和標籤
    point_labels_whitelist = ['A', 'B', 'C', 'D', 'E', 'F', 'P', 'Q', 'R'] # [V13.6 Strict Labeling]
    for (x, y), label in points_with_labels:
        if label not in point_labels_whitelist:
            continue # Skip labels not in whitelist
        ax.plot(x, y, 'o', color='red', markersize=6)
        # [V13.0 標註權限隔離] [V13.1 標籤純淨化] [V13.5 標籤隔離]
        # ax.text 只能包含點的名稱，嚴禁包含座標值
        ax.text(x + 0.3, y + 0.3, label, color='blue', fontsize=12, 
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))

    # 將繪圖轉換為 base64 字串 [ULTRA VISUAL STANDARDS: dpi=300]
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300) 
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


# 3. `generate()` 主函式 (Top-level Function, V3.0, V4.0, V5.0, V7.0, V9.0, V10.0, V11.0)
def generate(level=1):
    """
    [禁絕原創] [隨機分流] [座標鎖死] [數據禁絕常數]
    生成關於三角形全等意義的題目。
    根據 MANDATORY MIRRORING RULES，重新映射問題類型：
    - Type 1 (maps to RAG Ex 1): 尋找對應角度 (△ABC ~ △DEF)
    - Type 2 (maps to RAG Ex 2): 尋找對應邊長 (△ABC ~ △PQR)
    """
    problem_type = random.choice([1, 2]) # 隨機選擇問題類型 (1: 角度, 2: 邊長)

    # 座標生成範圍 [V13.0 座標選取控制] [V13.5 座標範圍]
    coord_min, coord_max = -7, 7 
    # 繪圖範圍，確保點和標籤不會被截斷 [V13.0 格線對齊] [V13.5 座標範圍]
    x_range_plot, y_range_plot = (-10, 10), (-10, 10) 

    # 生成三角形 ABC 的座標
    # [數據禁絕常數]: 座標隨機生成
    while True:
        ax_val, ax_data = _generate_coordinate_value(coord_min, coord_max, allow_fraction=True)
        ay_val, ay_data = _generate_coordinate_value(coord_min, coord_max, allow_fraction=True)
        bx_val, bx_data = _generate_coordinate_value(coord_min, coord_max, allow_fraction=True)
        by_val, by_data = _generate_coordinate_value(coord_min, coord_max, allow_fraction=True)
        cx_val, cx_data = _generate_coordinate_value(coord_min, coord_max, allow_fraction=True)
        cy_val, cy_data = _generate_coordinate_value(coord_min, coord_max, allow_fraction=True)

        A = (ax_val, ay_val)
        B = (bx_val, by_val)
        C = (cx_val, cy_val)

        # 檢查是否為非退化三角形 (面積大於一個小數點精度)
        area = 0.5 * abs(A[0]*(B[1]-C[1]) + B[0]*(C[1]-A[1]) + C[0]*(A[1]-B[1]))
        if area > 0.1 and A!=B and B!=C and A!=C: # 確保點不重合且面積非零
            break

    # 格式化座標以用於題目文字顯示 (V13.0, V13.5)
    A_formatted = (_format_coordinate_for_display((ax_val, ax_data)), _format_coordinate_for_display((ay_val, ay_data)))
    B_formatted = (_format_coordinate_for_display((bx_val, bx_data)), _format_coordinate_for_display((by_val, by_data)))
    C_formatted = (_format_coordinate_for_display((cx_val, cx_data)), _format_coordinate_for_display((cy_val, cy_data)))
    
    question_text = ""
    correct_answer = ""
    points_for_plot = [] # Will be populated based on problem_type

    # Type 1: 尋找對應角度 (Maps to RAG Ex 1: △ABC ~ △DEF, find angles)
    if problem_type == 1:
        # 應用剛體變換 (平移、旋轉、反射) 創建與 ABC 全等的三角形 DEF
        # [數據禁絕常數]: 變換方式隨機生成
        transform_type = random.choice(['translate', 'rotate90', 'rotate180', 'rotate270', 'reflect_x', 'reflect_y'])

        if transform_type == 'translate':
            tx = random.randint(-5, 5) # 平移量
            ty = random.randint(-5, 5)
            D = (A[0] + tx, A[1] + ty)
            E = (B[0] + tx, B[1] + ty)
            F = (C[0] + tx, C[1] + ty)
        elif transform_type == 'rotate90': # 繞原點逆時針旋轉 90 度 (x,y) -> (-y,x)
            D = (-A[1], A[0])
            E = (-B[1], B[0])
            F = (-C[1], C[0])
        elif transform_type == 'rotate180': # 繞原點旋轉 180 度 (x,y) -> (-x,-y)
            D = (-A[0], -A[1])
            E = (-B[0], -B[1])
            F = (-C[0], -C[1])
        elif transform_type == 'rotate270': # 繞原點逆時針旋轉 270 度 (x,y) -> (y,-x)
            D = (A[1], -A[0])
            E = (B[1], -B[0])
            F = (C[1], -C[0])
        elif transform_type == 'reflect_x': # 沿 x 軸反射 (x,y) -> (x,-y)
            D = (A[0], -A[1])
            E = (B[0], -B[1])
            F = (C[0], -C[1])
        elif transform_type == 'reflect_y': # 沿 y 軸反射 (x,y) -> (-x,y)
            D = (-A[0], A[1])
            E = (-B[0], B[1])
            F = (-C[0], C[1])

        D_formatted = (_format_coordinate_for_display((D[0], (0,0,0,False))), _format_coordinate_for_display((D[1], (0,0,0,False))))
        E_formatted = (_format_coordinate_for_display((E[0], (0,0,0,False))), _format_coordinate_for_display((E[1], (0,0,0,False))))
        F_formatted = (_format_coordinate_for_display((F[0], (0,0,0,False))), _format_coordinate_for_display((F[1], (0,0,0,False))))

        # 隨機生成三角形內角，確保和為 180 度且各角非零
        # [數據禁絕常數]: 角度隨機生成
        angle_A_val = random.randint(20, 80)
        angle_B_val = random.randint(20, 180 - angle_A_val - 20) 
        angle_C_val = 180 - angle_A_val - angle_B_val
        
        # 根據 RAG Ex 1: A 和 D、B 和 E、C 和 F 為對應點。
        angle_map = {
            "A": angle_A_val, "B": angle_B_val, "C": angle_C_val,
            "D": angle_A_val, "E": angle_B_val, "F": angle_C_val
        }
        
        # 隨機選擇一個角 (從 ABC 或 DEF) 作為已知，並詢問其對應角
        chosen_angle_key_src = random.choice(["A", "B", "C", "D", "E", "F"])
        
        if chosen_angle_key_src in ["A", "B", "C"]: # If given angle is from ABC
            given_angle_name = f"$\\angle {chosen_angle_key_src}$"
            given_deg = angle_map[chosen_angle_key_src]
            asked_angle_key_target = { "A": "D", "B": "E", "C": "F" }[chosen_angle_key_src]
            asked_angle_name = f"$\\angle {asked_angle_key_target}$"
            correct_deg_val = angle_map[asked_angle_key_target]
        else: # If given angle is from DEF
            given_angle_name = f"$\\angle {chosen_angle_key_src}$"
            given_deg = angle_map[chosen_angle_key_src]
            asked_angle_key_target = { "D": "A", "E": "B", "F": "C" }[chosen_angle_key_src]
            asked_angle_name = f"$\\angle {asked_angle_key_target}$"
            correct_deg_val = angle_map[asked_angle_key_target]

        # [排版與 LaTeX 安全] 使用 .replace() 避免 f-string 與 LaTeX 衝突
        question_text_template = r"如圖所示，已知 $\triangle ABC \cong \triangle DEF$，其中 $A$ 和 $D$、$B$ 和 $E$、$C$ 和 $F$ 為對應點。" \
                                 r"已知 $A({ax},{ay})$, $B({bx},{by})$, $C({cx},{cy})$，" \
                                 r"且 $D({dx},{dy})$, $E({ex},{ey})$, $F({fx},{fy})$。" \
                                 r"若 {angle1} 的度數為 {deg1}°，則 {angle2} 的度數為何？"
        
        question_text = question_text_template.replace("{ax}", A_formatted[0]).replace("{ay}", A_formatted[1]) \
                                              .replace("{bx}", B_formatted[0]).replace("{by}", B_formatted[1]) \
                                              .replace("{cx}", C_formatted[0]).replace("{cy}", C_formatted[1]) \
                                              .replace("{dx}", D_formatted[0]).replace("{dy}", D_formatted[1]) \
                                              .replace("{ex}", E_formatted[0]).replace("{ey}", E_formatted[1]) \
                                              .replace("{fx}", F_formatted[0]).replace("{fy}", F_formatted[1]) \
                                              .replace("{angle1}", given_angle_name) \
                                              .replace("{deg1}", str(given_deg)) \
                                              .replace("{angle2}", asked_angle_name)
        
        # [CRITICAL RULE: Answer Data Purity] correct_answer 必須是純數據
        correct_answer = str(correct_deg_val)

        points_for_plot = [
            (A, 'A'), (B, 'B'), (C, 'C'),
            (D, 'D'), (E, 'E'), (F, 'F')
        ]

    # Type 2: 尋找對應邊長 (Maps to RAG Ex 2: △ABC ~ △PQR, find side lengths)
    else: # problem_type == 2
        # 應用剛體變換 (平移、旋轉、反射) 創建與 ABC 全等的三角形 PQR
        # [數據禁絕常數]: 變換方式隨機生成
        transform_type = random.choice(['translate', 'rotate90', 'rotate180', 'rotate270', 'reflect_x', 'reflect_y'])

        if transform_type == 'translate':
            tx = random.randint(-5, 5) # 平移量
            ty = random.randint(-5, 5)
            P = (A[0] + tx, A[1] + ty)
            Q = (B[0] + tx, B[1] + ty)
            R = (C[0] + tx, C[1] + ty)
        elif transform_type == 'rotate90': # 繞原點逆時針旋轉 90 度 (x,y) -> (-y,x)
            P = (-A[1], A[0])
            Q = (-B[1], B[0])
            R = (-C[1], C[0])
        elif transform_type == 'rotate180': # 繞原點旋轉 180 度 (x,y) -> (-x,-y)
            P = (-A[0], -A[1])
            Q = (-B[0], -B[1])
            R = (-C[0], -C[1])
        elif transform_type == 'rotate270': # 繞原點逆時針旋轉 270 度 (x,y) -> (y,-x)
            P = (A[1], -A[0])
            Q = (B[1], -B[0])
            R = (C[1], -C[0])
        elif transform_type == 'reflect_x': # 沿 x 軸反射 (x,y) -> (x,-y)
            P = (A[0], -A[1])
            Q = (B[0], -B[1])
            R = (C[0], -C[1])
        elif transform_type == 'reflect_y': # 沿 y 軸反射 (x,y) -> (-x,y)
            P = (-A[0], A[1])
            Q = (-B[0], B[1])
            R = (-C[0], C[1])
        
        P_formatted = (_format_coordinate_for_display((P[0], (0,0,0,False))), _format_coordinate_for_display((P[1], (0,0,0,False))))
        Q_formatted = (_format_coordinate_for_display((Q[0], (0,0,0,False))), _format_coordinate_for_display((Q[1], (0,0,0,False))))
        R_formatted = (_format_coordinate_for_display((R[0], (0,0,0,False))), _format_coordinate_for_display((R[1], (0,0,0,False))))

        # 計算邊長
        len_AB = _calculate_distance(A, B)
        len_BC = _calculate_distance(B, C)
        len_CA = _calculate_distance(C, A)
        len_PQ = _calculate_distance(P, Q)
        len_QR = _calculate_distance(Q, R)
        len_RP = _calculate_distance(R, P)

        # 根據 RAG Ex 2: AB＝PQ, BC＝QR, CA＝PR
        side_map_abc = {"AB": len_AB, "BC": len_BC, "CA": len_CA}
        side_map_pqr = {"PQ": len_PQ, "QR": len_QR, "RP": len_RP}

        # 隨機選擇一個邊 (從 ABC 或 PQR) 作為已知，並詢問其對應邊
        chosen_side_key_src = random.choice(list(side_map_abc.keys()) + list(side_map_pqr.keys()))
        
        if chosen_side_key_src in side_map_abc: # If given side is from ABC
            given_side_name = chosen_side_key_src
            given_len = round(side_map_abc[given_side_name], 2)
            asked_side_key_target = { "AB": "PQ", "BC": "QR", "CA": "RP" }[chosen_side_key_src]
            asked_side_name = asked_side_key_target
            correct_len_val = round(side_map_pqr[asked_side_name], 2)
        else: # If given side is from PQR
            given_side_name = chosen_side_key_src
            given_len = round(side_map_pqr[given_side_name], 2)
            asked_side_key_target = { "PQ": "AB", "QR": "BC", "RP": "CA" }[chosen_side_key_src]
            asked_side_name = asked_side_key_target
            correct_len_val = round(side_map_abc[asked_side_name], 2)

        # [排版與 LaTeX 安全] 使用 .replace() 避免 f-string 與 LaTeX 衝突
        question_text_template = r"如圖所示，已知 $\triangle ABC \cong \triangle PQR$，其中 $\angle A$ 和 $\angle P$、$\angle B$ 和 $\angle Q$、$\angle C$ 和 $\angle R$ 為對應角。" \
                                 r"已知 $A({ax},{ay})$, $B({bx},{by})$, $C({cx},{cy})$，" \
                                 r"且 $P({px},{py})$, $Q({qx},{qy})$, $R({rx},{ry})$。" \
                                 r"若邊 {side1} 的長度為 {len1}，則邊 {side2} 的長度為何？ (答案請四捨五入至小數點後兩位)"
        
        question_text = question_text_template.replace("{ax}", A_formatted[0]).replace("{ay}", A_formatted[1]) \
                                              .replace("{bx}", B_formatted[0]).replace("{by}", B_formatted[1]) \
                                              .replace("{cx}", C_formatted[0]).replace("{cy}", C_formatted[1]) \
                                              .replace("{px}", P_formatted[0]).replace("{py}", P_formatted[1]) \
                                              .replace("{qx}", Q_formatted[0]).replace("{qy}", Q_formatted[1]) \
                                              .replace("{rx}", R_formatted[0]).replace("{ry}", R_formatted[1]) \
                                              .replace("{side1}", given_side_name) \
                                              .replace("{len1}", str(given_len)) \
                                              .replace("{side2}", asked_side_name)
        
        # [CRITICAL RULE: Answer Data Purity] correct_answer 必須是純數據
        correct_answer = str(correct_len_val)

        points_for_plot = [
            (A, 'A'), (B, 'B'), (C, 'C'),
            (P, 'P'), (Q, 'Q'), (R, 'R')
        ]

    # 繪製座標平面圖 [視覺化與輔助函式通用規範] [幾何/圖形題的特殊規範]
    image_base64 = draw_coordinate_plane(points_for_plot, x_range=x_range_plot, y_range=y_range_plot)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer, # [CRITICAL RULE: Answer Data Purity]
        "answer": correct_answer, # 提供給前端顯示詳解，但 `check` 不會使用此欄位
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


#### `check()` 函式設計 (Top-level Function, V3.0, V12.6, V13.5, V13.6)

def check(user_answer, correct_answer):
    """
    [CRITICAL RULE: Answer Data Purity] [定義「強韌閱卷邏輯 (Robust Check Logic)」]
    [V12.6 邏輯驗證硬化規約] [V13.5 禁絕複雜比對] [V13.6 Exact Check Logic]
    對使用者答案進行輸入清洗和等價性檢查。
    """
    import re, math

    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y= 等潛在前綴
        s = s.replace("$", "").replace("\\", "") # 移除 LaTeX 符號
        # 僅保留數字、小數點、分數斜線、負號
        s = re.sub(r'[^0-9./-]+', '', s) 
        return s
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 嘗試數值比對 (支援分數與小數)
    try:
        def parse_val(val_str):
            if not val_str: # 處理清洗後為空字串的情況
                return float('nan') 
            if "/" in val_str: # 處理分數
                n, d = map(float, val_str.split("/"))
                if d == 0: raise ValueError("Division by zero")
                return n/d
            return float(val_str) # 處理小數或整數
        
        user_float = parse_val(u)
        correct_float = parse_val(c)
        
        # 考慮浮點數精度問題，使用 math.isclose 進行比較
        # rel_tol=1e-3 (千分之一) 適合答案四捨五入至小數點後兩位 (0.01) 的情況
        # abs_tol=1e-6 處理接近零的數值比較
        if math.isclose(user_float, correct_float, rel_tol=1e-3, abs_tol=1e-6):
            return True
    except (ValueError, ZeroDivisionError):
        pass # 如果轉換或計算失敗，則不進行數值比對，直接進入字串比對

    # 3. 降級為字串比對 (作為最終的備用檢查，例如對於整數的精確比對)
    if u == c: 
        return True
        
    return False


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
