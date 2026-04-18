# ==============================================================================
# ID: jh_數學2下_NSidedPolygonInteriorAndExteriorAngles
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 95.58s | RAG: 4 examples
# Created At: 2026-01-21 18:02:15
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
from datetime import datetime
import base64
import io
import matplotlib.pyplot as plt
import numpy as np

# 輔助函式定義 (Helper Functions Definitions)
def _generate_polygon_data(min_sides=3, max_sides=12):
    """
    功能: 隨機生成多邊形的邊數 n。
    防洩漏原則: 此函式僅生成 n，不涉及任何答案數據。
    輸入: min_sides (int), max_sides (int)
    輸出: n (int)
    """
    n = random.randint(min_sides, max_sides)
    return n

def _draw_polygon(n, angle_labels=None, angle_label_indices=None, side_length=5):
    """
    功能: 繪製一個正多邊形或帶有指定角度標籤的多邊形。
    防洩漏原則: 此函式嚴禁接收或繪製 correct_answer 相關的數值。
                angle_labels 用於顯示題目已知的角度或變數表達式，而非答案。
    視覺可解性: 若有角度標註，必須清晰。
    輸入: n (int), angle_labels (list of str, optional), angle_label_indices (list of int, optional)
    輸出: base64 encoded PNG 圖片字串
    """
    fig, ax = plt.subplots(figsize=(6, 6), dpi=300) # ULTRA VISUAL STANDARDS: dpi=300
    ax.set_aspect('equal') # V10.2 Pure Style

    # 計算頂點
    vertices = []
    center_x, center_y = 0, 0
    # 計算半徑，使邊長約為 side_length
    radius = side_length / (2 * math.sin(math.pi / n))
    
    for i in range(n):
        # 從頂部開始繪製，使多邊形更均衡
        angle_rad = 2 * math.pi * i / n + math.pi/n 
        x = center_x + radius * math.cos(angle_rad)
        y = center_y + radius * math.sin(angle_rad)
        vertices.append((x, y))

    # 繪製多邊形
    for i in range(n):
        start_point = vertices[i]
        end_point = vertices[(i + 1) % n]
        ax.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], 'k-')

    # 標註角度 (如果提供)
    if angle_labels and angle_label_indices:
        for idx, label_text in zip(angle_label_indices, angle_labels):
            if 0 <= idx < n:
                p_vertex = vertices[idx]
                
                # 計算位置稍微往多邊形內部移動
                vec_x = p_vertex[0] - center_x
                vec_y = p_vertex[1] - center_y
                
                norm = math.sqrt(vec_x**2 + vec_y**2)
                if norm > 0:
                    vec_x /= norm
                    vec_y /= norm
                
                # 角度文本位置，稍微往內移動，避免與線段重疊
                text_x = p_vertex[0] - vec_x * radius * 0.45
                text_y = p_vertex[1] - vec_y * radius * 0.45
                
                ax.text(text_x, text_y, 
                        f"${label_text}^\circ$", # LaTeX 數學模式和度數符號
                        bbox=dict(boxstyle="round,pad=0.2", fc="yellow", ec="red", lw=1, alpha=0.8),
                        ha='center', va='center', fontsize=12, color='red')
                     
    ax.set_xlim(center_x - radius * 1.2, center_x + radius * 1.2)
    ax.set_ylim(center_y - radius * 1.2, center_y + radius * 1.2)
    ax.axis('off') # 關閉座標軸，因此無需設置刻度、spines或網格

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def generate(level=1):
    problem_type = random.choice([1, 2, 3, 4, 5, 6]) # 隨機選擇題型

    question_text = ""
    correct_answer = ""
    image_base64 = None
    
    # 根據 level 調整邊數範圍
    if level == 1: # 基礎題
        n_min, n_max = 3, 7
    elif level == 2: # 中等題
        n_min, n_max = 5, 10
    else: # 困難題
        n_min, n_max = 7, 12
    
    # 基礎邊數生成，特定題型可能會覆蓋
    n = _generate_polygon_data(min_sides=max(3, n_min), max_sides=n_max)

    if problem_type == 1: # Type 1: 計算多邊形內角和 (基於 RAG Ex 1 的數學模型 (n-2)*180 的正向應用)
        question_text_template = r"一個 {n} 邊形的內角和是多少度？"
        correct_angle_sum = (n - 2) * 180
        question_text = question_text_template.replace("{n}", str(n))
        correct_answer = str(correct_angle_sum)
        image_base64 = _draw_polygon(n) # 僅作參考圖形

    elif problem_type == 2: # Type 2: 計算正多邊形單一內角 (嚴格對應 RAG Ex 2: 正十二邊形...每一個內角為多少度？)
        question_text_template = r"一個正 {n} 邊形的每一個內角是多少度？"
        one_interior_angle = ((n - 2) * 180) / n
        
        if one_interior_angle != int(one_interior_angle):
            one_interior_angle = round(one_interior_angle, 2)
            question_text_template += r"(請四捨五入到小數點後兩位)"
        else:
            one_interior_angle = int(one_interior_angle)

        question_text = question_text_template.replace("{n}", str(n))
        correct_answer = str(one_interior_angle)
        image_base64 = _draw_polygon(n) # 僅作參考圖形

    elif problem_type == 3: # Type 3: 計算正多邊形單一外角 (基於內外角關係 360/n 的正向應用)
        question_text_template = r"一個正 {n} 邊形的每一個外角是多少度？"
        one_exterior_angle = 360 / n

        if one_exterior_angle != int(one_exterior_angle):
            one_exterior_angle = round(one_exterior_angle, 2)
            question_text_template += r"(請四捨五入到小數點後兩位)"
        else:
            one_exterior_angle = int(one_exterior_angle)
        
        question_text = question_text_template.replace("{n}", str(n))
        correct_answer = str(one_exterior_angle)
        image_base64 = _draw_polygon(n) # 僅作參考圖形

    elif problem_type == 4: # Type 4: 已知角度求邊數 (對應 RAG Ex 1 (內角和求 n), RAG Ex 3 (內角求 n), 外角求 n)
        sub_type = random.choice(['sum_int', 'one_int', 'one_ext'])
        
        # 為了確保答案 n 為整數，且角度為整數，選擇 n 時會考慮 360 的因數
        valid_ns_for_angles = [x for x in range(max(3, n_min), n_max + 3) if 360 % x == 0]
        if not valid_ns_for_angles: 
            valid_ns_for_angles = [random.randint(max(3, n_min), n_max + 3)] # 後備方案
        
        correct_n = random.choice(valid_ns_for_angles)

        if sub_type == 'sum_int': # 對應 RAG Ex 1 (內角和為 1800°，則 m＝？)
            sum_angles = (correct_n - 2) * 180
            question_text_template = r"一個多邊形的內角和是 ${sum_angles}^\circ$，請問這個多邊形是幾邊形？"
            question_text = question_text_template.replace("{sum_angles}", str(sum_angles))
            correct_answer = str(correct_n)
        
        elif sub_type == 'one_int': # 對應 RAG Ex 3 (每一個內角為 156°，則 n 是多少？)
            one_int_angle = ((correct_n - 2) * 180) / correct_n
            question_text_template = r"一個正多邊形的每一個內角是 ${int_angle}^\circ$，請問這個多邊形是幾邊形？"
            question_text = question_text_template.replace("{int_angle}", str(int(one_int_angle)))
            correct_answer = str(correct_n)
        
        elif sub_type == 'one_ext': # 外角求邊數 (RAG Ex 4 內外角關係的組成部分)
            one_ext_angle = 360 / correct_n
            question_text_template = r"一個正多邊形的每一個外角是 ${ext_angle}^\circ$，請問這個多邊形是幾邊形？"
            question_text = question_text_template.replace("{ext_angle}", str(int(one_ext_angle)))
            correct_answer = str(correct_n)
        
        image_base64 = None

    elif problem_type == 5: # Type 5: 綜合應用題 - 變數與方程式 (基於 (n-2)*180 模型應用代數)
        n = random.randint(max(4, n_min), min(7, n_max)) # 邊數範圍 4 到 7
        sum_interior_angles = (n - 2) * 180
        
        angle_labels_for_drawing = []
        angle_label_indices_for_drawing = []
        
        # 設定變數角度 (Ax+B) 的目標值，確保其為合理角度 (60-170 度)
        target_variable_angle_value = random.randint(60, 170) 
        
        # 計算其他 n-1 個固定角度的總和
        sum_of_fixed_angles = sum_interior_angles - target_variable_angle_value
        
        num_fixed_angles = n - 1
        fixed_angles = []

        # 循環生成 n-1 個固定角度，確保每個角度都在合理範圍內 (50-170 度)
        while True:
            current_fixed_angles_attempt = []
            remaining_sum_for_distribution = sum_of_fixed_angles
            is_valid_set = True

            for i in range(num_fixed_angles - 1): # 生成 n-2 個角度
                # 確保當前角度取值後，剩餘角度仍能滿足條件
                min_val = max(50, remaining_sum_for_distribution - (num_fixed_angles - 1 - i) * 170)
                max_val = min(170, remaining_sum_for_distribution - (num_fixed_angles - 1 - i) * 50)
                
                if min_val > max_val: # 如果範圍無效，則重新生成
                    is_valid_set = False
                    break
                
                angle = random.randint(min_val, max_val)
                current_fixed_angles_attempt.append(angle)
                remaining_sum_for_distribution -= angle
            
            if not is_valid_set:
                continue # 重新嘗試生成

            # 最後一個固定角度
            last_fixed_angle = remaining_sum_for_distribution
            if 50 <= last_fixed_angle <= 170: # 檢查最後一個角度是否有效
                current_fixed_angles_attempt.append(last_fixed_angle)
                fixed_angles = current_fixed_angles_attempt
                break # 找到有效角度集，退出循環
            else:
                continue # 最後一個角度無效，重新嘗試

        # 將固定角度加入繪圖標籤列表
        for i, angle in enumerate(fixed_angles):
            angle_labels_for_drawing.append(str(angle))
            angle_label_indices_for_drawing.append(i)
        
        # 設定變數角度的係數 A 和常數 B
        A = random.choice([1, 2, 3])
        
        # 確保 x 為正整數，且 Ax+B 等於 target_variable_angle_value
        # target_variable_angle_value = Ax + B
        # 先選定一個合理的正整數 x
        correct_x = random.randint(5, 40) 
        B = target_variable_angle_value - A * correct_x
        
        # 確保 B 不會過於極端 (-50 到 50)，且變數角度 (Ax+B) 是正數
        while B < -50 or B > 50:
            B = random.randint(-50, 50) # 重新選擇 B
            if (target_variable_angle_value - B) % A == 0 and (target_variable_angle_value - B) / A > 0:
                correct_x = (target_variable_angle_value - B) // A
                break # 找到有效的 B 和 x
            # 如果 x 無效，循環會繼續嘗試其他 B
        
        # 格式化變數角度字串 (CRITICAL CODING STANDARDS: 方程式生成鎖死)
        variable_angle_parts = []
        if A == 1:
            variable_angle_parts.append("x")
        else:
            variable_angle_parts.append(f"{A}x")
        
        if B > 0:
            variable_angle_parts.append(f"+{B}")
        elif B < 0:
            variable_angle_parts.append(f"-{abs(B)}")
        
        variable_angle_text = "".join(variable_angle_parts)
        
        angle_labels_for_drawing.append(variable_angle_text)
        angle_label_indices_for_drawing.append(n-1) # 最後一個角度標註變數表達式
        
        angles_str_list = [f"${s}$" for s in angle_labels_for_drawing[:-1]] # 除最後一個外，都用 $ 符號包裝
        angles_str = ", ".join(angles_str_list)
        
        question_text_template = r"一個 {n} 邊形的內角分別為 {angles_str} 和 ${variable_angle}^\circ$。請問 $x$ 的值是多少？"
        question_text = question_text_template.replace("{n}", str(n)).replace("{angles_str}", angles_str).replace("{variable_angle}", variable_angle_text)
        correct_answer = str(correct_x)
        image_base64 = _draw_polygon(n, angle_labels=angle_labels_for_drawing, angle_label_indices=angle_label_indices_for_drawing)

    elif problem_type == 6: # Type 6: 混合題 - 內外角關係 (對應 RAG Ex 4: 內外角倍數關係求 n)
        # 確保 n 能產生整數內外角，以簡化題目描述
        valid_ns = [x for x in range(max(5, n_min), min(10, n_max) + 1) if 360 % x == 0]
        if not valid_ns: 
            valid_ns = [random.randint(max(5, n_min), min(10, n_max))] # 後備方案
        
        correct_n = random.choice(valid_ns)
        
        int_angle = ((correct_n - 2) * 180) / correct_n
        ext_angle = 360 / correct_n
        
        # 確保角度為整數
        int_angle = int(int_angle) 
        ext_angle = int(ext_angle) 

        sub_type = random.choice(['diff", "ratio'])

        if sub_type == 'diff': # 內外角差值關係
            diff = int_angle - ext_angle
            question_text_template = r"一個正多邊形的每一個內角比每一個外角多 ${diff_angle}^\circ$，請問這個多邊形是幾邊形？"
            question_text = question_text_template.replace("{diff_angle}", str(diff))
            correct_answer = str(correct_n)
        elif sub_type == 'ratio': # 內外角倍數關係 (嚴格對應 RAG Ex 4: 內角度數恰好為一個外角度數的 3 倍)
            # 確保比例 k 為整數
            k_val = int_angle / ext_angle
            if k_val == int(k_val) and k_val > 1: # 確保倍數大於 1
                k = int(k_val)
                question_text_template = r"一個正多邊形的每一個內角是其每一個外角的 {k_factor} 倍，請問這個多邊形是幾邊形？"
                question_text = question_text_template.replace("{k_factor}", str(k))
                correct_answer = str(correct_n)
            else: # 如果比例不是整數或不符合條件，則退化為差值關係
                diff = int_angle - ext_angle
                question_text_template = r"一個正多邊形的每一個內角比每一個外角多 ${diff_angle}^\circ$，請問這個多邊形是幾邊形？"
                question_text = question_text_template.replace("{diff_angle}", str(diff))
                correct_answer = str(correct_n)
        
        image_base64 = None

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "", 
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    """
    功能: 檢查使用者答案是否正確。
    CRITICAL RULE: V13.6 API Hardened Spec - Exact Check Logic
    CRITICAL CODING STANDARDS: 閱卷決定論 & 通用 Check 函式模板
    閱卷與反饋: check(u, c) 僅限回傳 True/False。
    """
    # 1. 輸入清洗 (Input Sanitization)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        # 移除 LaTeX 符號、變數前綴 (k=, x=, y=, Ans: 等)、所有空白字元和度數符號
        s = re.sub(r'^[a-z]+[=:]?', '', s) 
        s = s.replace("$", "").replace("\\", "").replace("°", "")
        return s
    
    u_cleaned = clean(user_answer)
    c_cleaned = clean(correct_answer)

    # 2. 數值序列比對 (Numerical Sequence Comparison)
    # 本技能主要處理單一數值答案。
    try:
        def parse_val(val_str):
            # 支援分數轉換 (例如 "1/2" 轉為 0.5)
            if '/' in val_str:
                parts = val_str.split('/')
                if len(parts) == 2:
                    return float(parts[0]) / float(parts[1])
            return float(val_str)

        user_num = parse_val(u_cleaned)
        correct_num = parse_val(c_cleaned)
        
        # 支援多種數學格式的等價性 (例如：1/2 = 0.5) - 浮點數比較考慮精度
        tolerance = 1e-5 # 允許的浮點數誤差
        is_correct = math.isclose(user_num, correct_num, rel_tol=tolerance)
        
        # 如果正確答案是整數，也檢查是否整數相等
        if correct_num == int(correct_num):
            is_correct = is_correct and (abs(user_num - correct_num) < tolerance or int(user_num) == int(correct_num))
            
        return is_correct
            
    except ValueError:
        # 如果無法轉換為數字，則進行字串比較 (此技能答案預期為數字，此路徑應避免)
        return u_cleaned == c_cleaned


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
