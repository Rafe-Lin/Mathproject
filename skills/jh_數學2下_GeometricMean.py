# ==============================================================================
# ID: jh_數學2下_GeometricMean
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 84.82s | RAG: 5 examples
# Created At: 2026-01-19 21:36:40
# Fix Status: [Repaired]
# Fixes: Regex=4, Logic=0
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
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# 輔助函式：檢查是否為完全平方數
def _is_perfect_square(n):
    if n < 0:
        return False
    if n == 0:
        return True
    sqrt_n = int(math.sqrt(n))
    return sqrt_n * sqrt_n == n

# 輔助函式：繪製座標平面上的點和線 (用於 Type 3)
def _draw_right_triangle_altitude(points_data, labels, line_segments, x_range, y_range):
    fig, ax = plt.subplots(figsize=(8, 8))

    # 繪製座標軸
    ax.axhline(0, color='black', linewidth=1, clip_on=False)
    ax.axvline(0, color='black', linewidth=1, clip_on=False)

    # 繪製箭頭 (V13.6 API Hardened Spec)
    # 確保箭頭繪製在軸線的末端
    ax.plot(x_range[1], 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False) # X 軸箭頭
    ax.plot(0, y_range[1], "^k", transform=ax.get_xaxis_transform(), clip_on=False) # Y 軸箭頭

    # 設定座標軸範圍
    ax.set_xlim(x_range[0], x_range[1])
    ax.set_ylim(y_range[0], y_range[1])

    # 確保網格為正方形 (V10.2 Pure Style)
    ax.set_aspect('equal', adjustable='box')

    # 標示 X 軸與 Y 軸的主要整數刻度 (CRITICAL RULE: Visual Solvability, Mandatory Axis Ticks)
    # 使用 numpy.arange 確保即使範圍邊界為浮點數也能生成正確的整數刻度
    ax.set_xticks(np.arange(int(x_range[0]), int(x_range[1]) + 1))
    ax.set_yticks(np.arange(int(y_range[0]), int(y_range[1]) + 1))
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.tick_params(axis='both', which='major', labelsize=12) # 提高刻度標籤可讀性

    # 標示原點 '0' (V10.2 Pure Style)
    ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold', 
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))

    # 繪製點和標籤
    for i, (x, y) in enumerate(points_data):
        ax.plot(x, y, 'o', color='blue', markersize=6)
        # V13.0 標註權限隔離, V13.1 標籤純淨化, V13.5 標籤隔離: ax.text 只能是點的名稱
        ax.text(x + 0.2, y + 0.2, labels[i], color='red', fontsize=12, ha='left', va='bottom',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2')) # V10.2 Pure Style

    # 繪製線段
    for (p1_idx, p2_idx) in line_segments:
        x1, y1 = points_data[p1_idx]
        x2, y2 = points_data[p2_idx]
        ax.plot([x1, x2], [y1, y2], color='blue', linewidth=1.5)

    # 將圖形轉換為 base64 編碼
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, dpi=300) # ULTRA VISUAL STANDARDS: dpi=300
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# 輔助函式：生成直角三角形及相關邊長數據
def _get_geometric_mean_triplet_data():
    while True:
        target_type = random.choice(['AD', 'AB', 'AC'])

        if target_type == 'AD':
            ad_ans_sq = random.randint(16, 100) # AD^2, 確保其值不會太小，且有足夠的因數
            divisors = [d for d in range(2, int(math.sqrt(ad_ans_sq)) + 1) if ad_ans_sq % d == 0 and d >= 2 and ad_ans_sq // d >= 2]
            if not divisors:
                continue # 如果沒有合適的因數，重新生成 ad_ans_sq

            bd_val = random.choice(divisors)
            cd_val = ad_ans_sq // bd_val
            
            if bd_val == cd_val: # 避免 BD=CD=AD 的平凡情況
                continue

            ad_val = int(math.sqrt(ad_ans_sq)) # AD 是 AD^2 的平方根

            bc_val = bd_val + cd_val
            
            # 檢查 AB 和 AC 是否能為整數
            # AB^2 = BD * BC, AC^2 = CD * BC
            if not _is_perfect_square(bd_val * bc_val) or not _is_perfect_square(cd_val * bc_val):
                continue

            ab_val = int(math.sqrt(bd_val * bc_val))
            ac_val = int(math.sqrt(cd_val * bc_val))
            
            # 確保所有值在合理的範圍內以便繪圖
            if max(ad_val, bd_val, cd_val, ab_val, ac_val, bc_val) > 15: # 座標最大值限制在 15
                continue

            return (ad_val, bd_val, cd_val, ab_val, ac_val, bc_val, target_type)

        elif target_type == 'AB':
            ab_ans_sq = random.randint(16, 100) # AB^2
            divisors = [d for d in range(2, int(math.sqrt(ab_ans_sq)) + 1) if ab_ans_sq % d == 0 and d >= 2 and ab_ans_sq // d > d]
            if not divisors:
                continue

            bd_val = random.choice(divisors)
            bc_val = ab_ans_sq // bd_val
            cd_val = bc_val - bd_val
            
            if cd_val <= 0: # 確保 CD 是正數
                continue

            # 檢查 AD 和 AC 是否能為整數
            # AD^2 = BD * CD, AC^2 = CD * BC
            if not _is_perfect_square(bd_val * cd_val) or not _is_perfect_square(cd_val * bc_val):
                continue
            
            ad_val = int(math.sqrt(bd_val * cd_val))
            ac_val = int(math.sqrt(cd_val * bc_val))
            ab_val = int(math.sqrt(ab_ans_sq)) # AB 是 AB^2 的平方根

            # 確保所有值在合理的範圍內以便繪圖
            if max(ad_val, bd_val, cd_val, ab_val, ac_val, bc_val) > 15:
                continue

            return (ad_val, bd_val, cd_val, ab_val, ac_val, bc_val, target_type)

        elif target_type == 'AC': # 與 AB 對稱
            ac_ans_sq = random.randint(16, 100) # AC^2
            divisors = [d for d in range(2, int(math.sqrt(ac_ans_sq)) + 1) if ac_ans_sq % d == 0 and d >= 2 and ac_ans_sq // d > d]
            if not divisors:
                continue

            cd_val = random.choice(divisors)
            bc_val = ac_ans_sq // cd_val
            bd_val = bc_val - cd_val
            
            if bd_val <= 0: # 確保 BD 是正數
                continue

            # 檢查 AD 和 AB 是否能為整數
            # AD^2 = BD * CD, AB^2 = BD * BC
            if not _is_perfect_square(bd_val * cd_val) or not _is_perfect_square(bd_val * bc_val):
                continue

            ad_val = int(math.sqrt(bd_val * cd_val))
            ab_val = int(math.sqrt(bd_val * bc_val))
            ac_val = int(math.sqrt(ac_ans_sq)) # AC 是 AC^2 的平方根

            # 確保所有值在合理的範圍內以便繪圖
            if max(ad_val, bd_val, cd_val, ab_val, ac_val, bc_val) > 15:
                continue
                
            return (ad_val, bd_val, cd_val, ab_val, ac_val, bc_val, target_type)


def generate(level=1):
    # 根據 RAG 範例和架構師規範選擇問題類別
    question_category = random.choice(["GM_Basic", "GP_Product_Middle", "GP_Product_Ends", "GM_RightTriangle"])
    
    question_text = ""
    correct_answer = "" # 將是浮點數或浮點數列表 (用於 +/- 情況)
    image_base64 = None

    if question_category == "GM_Basic":
        # 映射至 RAG Ex 1, 4, 5: 求等比數列 A, k, B 中的 k 值。
        # k = +/- sqrt(A*B)
        
        # 確保 A 和 B 具有相同的符號以得到實數等比中項
        sign = random.choice([-1, 1])
        
        # 生成 gm_base (等比中項的整數部分或平方根的底數)
        gm_base = random.randint(2, 12)
        
        # 生成 num1 和 num2 的因數 d
        divisors = [i for i in range(1, gm_base + 1) if gm_base % i == 0]
        d = random.choice(divisors)
        
        num1_abs = gm_base * d
        num2_abs = gm_base // d

        # 確保值不會太大且不同
        while num1_abs > 30 or num2_abs > 30 or num1_abs == num2_abs:
            gm_base = random.randint(2, 12)
            divisors = [i for i in range(1, gm_base + 1) if gm_base % i == 0]
            d = random.choice(divisors)
            num1_abs = gm_base * d
            num2_abs = gm_base // d

        num1 = num1_abs * sign
        num2 = num2_abs * sign
        
        product = num1 * num2 # 始終為正數
        sqrt_product = math.sqrt(product)

        # 格式化問題文本
        question_text = f"已知 ${num1}$、$k$、${num2}$ 成等比數列，求 $k$ 的值為何？"

        # 根據 CRITICAL RULE: Answer Data Purity，correct_answer 僅包含純數據 (浮點數列表)
        # 不使用格式化字符串如 "±4\sqrt{2}"
        if _is_perfect_square(product):
            int_sqrt = int(sqrt_product)
            correct_answer = [float(int_sqrt), float(-int_sqrt)]
        else:
            correct_answer = [sqrt_product, -sqrt_product]

    elif question_category == "GP_Product_Middle":
        # 映射至 RAG Ex 2: 給定三項等比數列的第 2 項，求此三項的乘積。
        # a, X, b => 乘積 = a*X*b。由於 X^2 = a*b，所以乘積 = X*X^2 = X^3。
        
        middle_term = random.randint(-10, 10)
        while middle_term == 0: # 避免中間項為 0
            middle_term = random.randint(-10, 10)

        question_text = f"有三數成等比數列，已知數列的第 2 項為 ${middle_term}$，則此三數的乘積為何？"
        correct_answer = float(middle_term ** 3)

    elif question_category == "GP_Product_Ends":
        # 映射至 RAG Ex 3: 給定奇數項等比數列的某中間項，求首項與末項的乘積。
        # a1, a2, a3, ..., an (n 為奇數)。a1 * an = (a_middle)^2
        
        num_terms = random.choice([3, 5, 7]) # 項數必須為奇數
        middle_index = (num_terms + 1) // 2
        
        middle_term = random.randint(-10, 10)
        while middle_term == 0: # 避免中間項為 0
            middle_term = random.randint(-10, 10)

        question_text = f"若一等比數列共有 {num_terms} 項，已知數列的第 {middle_index} 項為 ${middle_term}$，則此數列首項與末項的乘積為何？"
        correct_answer = float(middle_term ** 2)

    elif question_category == "GM_RightTriangle":
        # 映射至架構師規範: 直角三角形的射影定理 (等比中項應用)
        ad_val, bd_val, cd_val, ab_val, ac_val, bc_val, target_type = _get_geometric_mean_triplet_data()

        # 定義座標 (為簡化，D 點設為原點)
        # A = (0, AD_val)
        # B = (-BD_val, 0)
        # C = (CD_val, 0)
        # D = (0,0)
        points_coords = [(0, ad_val), (-bd_val, 0), (cd_val, 0), (0, 0)]
        point_labels = ['A', 'B', 'C', 'D']
        line_segments = [(0, 1), (0, 2), (1, 2), (0, 3)] # AB, AC, BC, AD

        # 根據座標數據確定繪圖範圍
        all_x = [p[0] for p in points_coords]
        all_y = [p[1] for p in points_coords]
        
        x_min_data = min(all_x)
        x_max_data = max(all_x)
        y_min_data = min(all_y)
        y_max_data = max(all_y)

        # V13.0 格線對齊：座標軸範圍必須是對稱整數，且 xticks 間隔必須固定為 1。
        # V13.5 座標範圍：確保點與標籤不會被邊框切掉。
        # 為標籤和整體美觀增加填充，並確保對稱的整數範圍
        max_abs_coord = max(abs(x_min_data), abs(x_max_data), abs(y_min_data), abs(y_max_data))
        plot_padding = 2 # 標籤及美觀填充
        plot_range_val = int(math.ceil(max_abs_coord)) + plot_padding 
        
        x_range = (-plot_range_val, plot_range_val)
        y_range = (-plot_range_val, plot_range_val)

        image_base64 = _draw_right_triangle_altitude(points_coords, point_labels, line_segments, x_range, y_range)

        if target_type == 'AD':
            question_text = f"在直角三角形 $ABC$ 中，$\\angle BAC = 90^\\circ$，$\\overline{AD} \\perp \\overline{BC}$。若 $\\overline{BD} = {bd_val}$，$\\overline{CD} = {cd_val}$，則 $\\overline{AD}$ 的長度為何？"
            correct_answer = float(ad_val)
        elif target_type == 'AB':
            question_text = f"在直角三角形 $ABC$ 中，$\\angle BAC = 90^\\circ$，$\\overline{AD} \\perp \\overline{BC}$。若 $\\overline{BD} = {bd_val}$，$\\overline{BC} = {bc_val}$，則 $\\overline{AB}$ 的長度為何？"
            correct_answer = float(ab_val)
        elif target_type == 'AC':
            question_text = f"在直角三角形 $ABC$ 中，$\\angle BAC = 90^\\circ$，$\\overline{AD} \\perp \\overline{BC}$。若 $\\overline{CD} = {cd_val}$，$\\overline{BC} = {bc_val}$，則 $\\overline{AC}$ 的長度為何？"
            correct_answer = float(ac_val)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer, # 內部使用，生產環境可移除
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    # [強韌閱卷邏輯 (Robust Check Logic)]
    # 1. 輸入清洗 (Input Sanitization)
    # 必須使用 Regex 自動移除使用者輸入中的 LaTeX 符號、變數前綴、所有空白字元。
    import re, math

    def clean_and_parse(s_raw):
        s = str(s_raw).strip().replace(" ", "").lower()
        # 移除變數前綴 (k=, x=, y=, ans=)
        s = re.sub(r'^[a-z]+=', '', s) 
        # 移除 LaTeX 格式符號如 $, \, { }
        s = s.replace("$", "").replace("\\", "").replace("{", "").replace("}", "")
        # 移除 LaTeX 的正負號符號
        s = s.replace("\pm", "") 

        # 嘗試解析為浮點數、分數或平方根表達式
        try:
            # 處理開頭的負號 (如果存在)
            is_negative_overall = False
            if s.startswith('-'):
                is_negative_overall = True
                s = s[1:] # 移除開頭的 '-' 進行內部解析，稍後再應用

            # 移除潛在的乘號 '*'
            s = s.replace("*", "")
            
            # 匹配 XsqrtY 或 sqrtY (例如 '4sqrt2', 'sqrt2')
            match_sqrt = re.match(r'(\d*)sqrt(\d+)$', s) 
            # 匹配 sqrt(Y) 或 sqrtY (例如 'sqrt(2)', 'sqrt2')
            match_sqrt_paren = re.match(r'sqrt\(?(\d+)\)?$', s) 

            if match_sqrt:
                coeff_str = match_sqrt.group(1)
                coeff = 1.0
                if coeff_str != '': coeff = float(coeff_str)
                
                radicand = float(match_sqrt.group(2))
                val = coeff * math.sqrt(radicand)
                return -val if is_negative_overall else val
            elif match_sqrt_paren:
                radicand = float(match_sqrt_paren.group(1))
                val = math.sqrt(radicand)
                return -val if is_negative_overall else val

            # 處理分數
            if "/" in s:
                n_str, d_str = s.split("/")
                val = float(n_str) / float(d_str)
                return -val if is_negative_overall else val
            
            # 處理標準浮點數/整數
            val = float(s)
            # 如果原始數字是正數但有前導負號，則應用負號
            # 例如，user_answer="-5" => s="5", is_negative_overall=True => return -5
            # 例如，user_answer="5" => s="5", is_negative_overall=False => return 5
            # 避免雙重負號導致錯誤 (例如 "- -5")
            return -val if is_negative_overall and val >= 0 else val
        except ValueError:
            return None # 表示解析失敗

    user_parsed = clean_and_parse(user_answer)
    
    if user_parsed is None:
        return False # 使用者輸入無法解析為數字

    # correct_answer 可以是單個浮點數或浮點數列表 (用於 +/- 情況)
    # 根據通用檢查模板，使用相對容差 (1e-5) 和絕對容差 (1e-9) 進行浮點數比較
    if isinstance(correct_answer, list):
        for c_val in correct_answer:
            if math.isclose(user_parsed, float(c_val), rel_tol=1e-5, abs_tol=1e-9):
                return True
        return False
    else: # 單個浮點數/整數
        return math.isclose(user_parsed, float(correct_answer), rel_tol=1e-5, abs_tol=1e-9)


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
