# ==============================================================================
# ID: jh_數學2下_TriangleAngleSideRelationships
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 43.20s | RAG: 5 examples
# Created At: 2026-01-23 14:57:40
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

import matplotlib.pyplot as plt
import numpy as np

import base64
from io import BytesIO
import re

def generate(level=1, **kwargs):
    # Given angles (Randomized)
    # 隨機生成兩個內角，確保第三角為正整數
    angle_A_given = random.randint(20, 100)
    angle_B_given = random.randint(20, 180 - angle_A_given - 10)
    
    # Calculate the third angle using the triangle angle sum theorem
    angle_C_calculated = 180 - angle_A_given - angle_B_given

    # --- Image Generation ---
    def generate_triangle_image(angle_A, angle_B, angle_C):
        fig, ax = plt.subplots(figsize=(6, 6), dpi=300)

        # Calculate coordinates for the triangle
        BC_length = 5.0
        B = np.array([0.0, 0.0])
        C = np.array([BC_length, 0.0])

        angle_B_rad = math.radians(angle_B)
        angle_C_exterior_rad = math.radians(180 - angle_C) # Angle CA makes with positive x-axis if C is at (BC_length, 0)
        
        # Calculate coordinates of vertex A
        if abs(math.cos(angle_B_rad)) < 1e-9: # Angle B is ~90 degrees
            x_A = B[0]
            y_A = BC_length / math.tan(angle_C_exterior_rad) # Using C's angle from BC
        elif abs(math.cos(angle_C_exterior_rad)) < 1e-9: # Angle C is ~90 degrees
            x_A = C[0]
            y_A = BC_length * math.tan(angle_B_rad)
        else:
            tan_B = math.tan(angle_B_rad)
            tan_C_ext = math.tan(angle_C_exterior_rad)
            # Intersection of lines y = tan_B * x and y = tan_C_ext * (x - BC_length)
            x_A = (-tan_C_ext * BC_length) / (tan_B - tan_C_ext)
            y_A = tan_B * x_A

        A = np.array([x_A, y_A])
        # Ensure positive height
        if A[1] < 0: A[1] = -A[1]

        vertices = np.array([A, B, C])

        # Plot Triangle
        triangle_points = np.vstack((vertices, vertices[0]))
        ax.plot(triangle_points[:, 0], triangle_points[:, 1], 'k-', lw=1.5)
        ax.plot(vertices[:,0], vertices[:,1], 'ko', ms=3)

        # --- helper: Centroid & Inner Position ---
        centroid = (A + B + C) / 3.0

        def get_inner_pos(vertex, center, dist=0.7):
            direction = center - vertex
            length = np.linalg.norm(direction)
            if length == 0: return vertex
            return vertex + (direction / length) * dist

        # --- helper: Angle Arcs ---
        def draw_angle_arc(ax, vertex, p1, p2, radius=0.6, color='black'):
            v_p1 = p1 - vertex
            v_p2 = p2 - vertex
            
            theta1 = np.degrees(np.arctan2(v_p1[1], v_p1[0]))
            theta2 = np.degrees(np.arctan2(v_p2[1], v_p2[0]))
            
            if theta1 < 0: theta1 += 360
            if theta2 < 0: theta2 += 360
            
            t_min, t_max = min(theta1, theta2), max(theta1, theta2)
            
            if abs(t_max - t_min) > 180:
                wedge = patches.Wedge(vertex, radius, t_max, t_min + 360, width=0.04, color=color, alpha=0.3)
            else:
                wedge = patches.Wedge(vertex, radius, t_min, t_max, width=0.04, color=color, alpha=0.3)
            
            ax.add_patch(wedge)

        # Draw Arcs
        draw_angle_arc(ax, A, B, C, radius=0.8, color='blue')
        draw_angle_arc(ax, B, A, C, radius=0.8, color='blue')
        draw_angle_arc(ax, C, A, B, radius=0.8, color='red')

        # --- Label Vertices ---
        def get_outer_pos(vertex, center, dist=0.4):
            direction = vertex - center
            length = np.linalg.norm(direction)
            return vertex + (direction / length) * dist
        
        pos_A_lbl = get_outer_pos(A, centroid, 0.4)
        pos_B_lbl = get_outer_pos(B, centroid, 0.4)
        pos_C_lbl = get_outer_pos(C, centroid, 0.4)

        ax.text(pos_A_lbl[0], pos_A_lbl[1], 'A', ha='center', va='center', fontsize=12,
               bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.2', alpha=0.8))
        ax.text(pos_B_lbl[0], pos_B_lbl[1], 'B', ha='center', va='center', fontsize=12,
               bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.2', alpha=0.8))
        ax.text(pos_C_lbl[0], pos_C_lbl[1], 'C', ha='center', va='center', fontsize=12,
               bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.2', alpha=0.8))

        # --- Label Angles ---
        pos_A_val = get_inner_pos(A, centroid, 0.9)
        pos_B_val = get_inner_pos(B, centroid, 0.9)
        pos_C_val = get_inner_pos(C, centroid, 0.9)

        ax.text(pos_A_val[0], pos_A_val[1], f"{angle_A}$\\degree$", ha='center', va='center', fontsize=10, color='blue',
               bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.1', alpha=0.8))
        ax.text(pos_B_val[0], pos_B_val[1], f"{angle_B}$\\degree$", ha='center', va='center', fontsize=10, color='blue',
               bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.1', alpha=0.8))
        # Unknown Angle (Anti-Leak)
        ax.text(pos_C_val[0], pos_C_val[1], "?", ha='center', va='center', fontsize=12, color='red', fontweight='bold',
               bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.1', alpha=0.8))

        # Set Limits
        ax.set_aspect('equal')
        # Re-calc limits
        all_x = [v[0] for v in vertices] + [pos_A_lbl[0], pos_B_lbl[0], pos_C_lbl[0]]
        all_y = [v[1] for v in vertices] + [pos_A_lbl[1], pos_B_lbl[1], pos_C_lbl[1]]
            
        pad = 0.5
        ax.set_xlim(min(all_x) - pad, max(all_x) + pad)
        ax.set_ylim(min(all_y) - pad, max(all_y) + pad)

        ax.axis('off')

        # Convert plot to base64
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
        plt.close(fig)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return image_base64

    # Generate the image
    image_base64_str = generate_triangle_image(angle_A_given, angle_B_given, angle_C_calculated)

    return {
        "question_text": f"在 $\\triangle ABC$ 中，已知 $\\angle A = {angle_A_given}^\\circ$，$\\angle B = {angle_B_given}^\\circ$。請問 $\\angle C$ 是多少度？",
        "correct_answer": str(angle_C_calculated),
        "answer": f"$\\angle C = {angle_C_calculated}^\\circ$",
        "image_base64": image_base64_str,
        "created_at": "2023-10-27T10:00:00.000000",
        "version": "1.0"
    }


    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格, 度數符號)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=
        s = s.replace("$", "").replace("\\", "").replace("circ", "").replace("°", "")
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
