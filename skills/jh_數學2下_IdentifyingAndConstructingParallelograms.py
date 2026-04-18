# ==============================================================================
# ID: jh_數學2下_IdentifyingAndConstructingParallelograms
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 126.88s | RAG: 5 examples
# Created At: 2026-01-28 23:51:57
# Fix Status: [Repaired]
# Fixes: Regex=3, Logic=0
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
    import math, random, re
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
import numpy as np
from datetime import datetime
import re # For check function

# --- 輔助函式設計規範 ---

def _generate_coordinate_value(min_val=-7, max_val=7):
    """
    功能: 生成一個隨機的座標值，可以是整數或帶分數 (僅限 .5)。
    參數: min_val (int), max_val (int)。
    回傳: (float_val, (int_part, num, den, is_neg))。
          float_val: 實際的浮點數值。
          int_part: 整數部分 (若為純分數則為 0)。
          num: 分子 (若為整數則為 0，若為 .5 則為 1)。
          den: 分母 (若為整數則為 0，若為 .5 則為 2)。
          is_neg: 布林值，表示是否為負數。
    CRITICAL: 座標值僅限整數或 0.5。
    """
    is_half_fraction = random.choice([True, False]) # 隨機決定是否為帶 0.5 的分數

    if not is_half_fraction:
        val = random.randint(min_val, max_val)
        return float(val), (val, 0, 0, val < 0)
    else:
        # 確保 int_part + 0.5 不會超出 max_val，且 int_part - 0.5 不會低於 min_val
        # 為了避免複雜的邊界判斷，直接將 int_part 範圍縮小，並在之後檢查 float_val
        int_part = random.randint(min_val, max_val)
        
        # 確保分數部分是 0.5
        numerator = 1
        denominator = 2
        
        float_val = abs(int_part) + 0.5
        is_neg = (int_part < 0)
        if is_neg:
            float_val *= -1
        
        # 特殊處理純分數 (例如 0.5 或 -0.5) 當 int_part 為 0 時
        if int_part == 0:
            if random.choice([True, False]): # 50% 機率為 -0.5
                float_val = -0.5
                is_neg = True
            else:
                float_val = 0.5
                is_neg = False
            return float_val, (0, numerator, denominator, is_neg)
        
        # 確保最終的 float_val 在 min_val 和 max_val 之間
        if not (min_val <= float_val <= max_val):
            # 如果超出範圍，則重新生成 int_part，直到符合為止
            # 簡化處理：如果超出範圍，則退回生成一個整數
            val = random.randint(min_val, max_val)
            return float(val), (val, 0, 0, val < 0)

        return float_val, (int_part, numerator, denominator, is_neg)


def _format_coordinate_latex(coord_tuple):
    """
    功能: 將座標浮點數格式化為 LaTeX 字串 (如 (3, 5) 或 (-$\frac{1}{2}$, 2$\frac{1}{2}$))。
    參數: coord_tuple (tuple of floats)。
    回傳: str。
    V10.2 LaTeX 模板規範: 使用 .replace() 避免雙大括號問題。
    V13.0 格式精確要求: str(int(val)) 處理整數。
    CRITICAL: 座標值僅限整數或 0.5。
    """
    x_val, y_val = coord_tuple
    
    def format_single_value(val):
        if val.is_integer():
            return str(int(val))
        else:
            # 由於 _generate_coordinate_value 只產生 .5 的分數，我們可以硬編碼此邏輯
            abs_val = abs(val)
            int_part = int(abs_val)
            
            if int_part == 0:
                frac_str = r"\frac{1}{2}"
            else:
                # 確保 int_part 不為 0 時，顯示為帶分數形式
                frac_str = r"{int_part}\frac{1}{2}".replace("{int_part}", str(int_part))
            
            if val < 0:
                return r"-"+frac_str
            else:
                return frac_str
                
    x_str = format_single_value(x_val)
    y_str = format_single_value(y_val)

    return r"({x_str}, {y_str})".replace("{x_str}", x_str).replace("{y_str}", y_str)

def _format_raw_coordinate_value(val):
    """
    Helper for raw data conversion (V13.1, V13.5).
    Converts a float coordinate value to a string for the correct_answer.
    If integer, return int string. Otherwise, return float string.
    """
    if val.is_integer():
        return str(int(val))
    # 對於 0.5 的分數，直接回傳浮點數的字串表示即可，例如 "1.5"
    return str(val)


def _draw_coordinate_plane(points, x_min_limit, x_max_limit, y_min_limit, y_max_limit):
    """
    功能: 繪製座標平面圖，並標示點。
    參數:
        points (dict): 鍵為點的標籤 (e.g., 'A', 'P1')，值為座標 tuple (x, y)。
        x_min_limit, x_max_limit, y_min_limit, y_max_limit: 座標軸範圍。
    回傳: str (Base64 編碼的圖片)。
    V10.2 視覺一致性: ax.set_aspect('equal')，原點 '0' (18號加粗)，點標籤加白色光暈。
    V13.0 標註權限隔離: ax.text 只能是點的名稱，嚴禁座標值。
    V13.0 格線對齊: 座標軸範圍對稱，xticks 間隔為 1。
    V13.5 標籤隔離: 強制 ax.text 只能標註點名稱。
    V13.6 API Hardened: 箭頭使用 ax.plot(limit, 0, ">k", clip_on=False)。
    V17.1 Visual Solvability: 必須標示 X 軸與 Y 軸的主要整數刻度。
    ULTRA VISUAL STANDARDS (V11.6): Aspect Ratio, Resolution, Label Halo.
    """
    fig, ax = plt.subplots(figsize=(8, 8), dpi=300) # ULTRA VISUAL STANDARDS: Resolution

    # 設置座標軸範圍
    ax.set_xlim(x_min_limit, x_max_limit)
    ax.set_ylim(y_min_limit, y_max_limit)

    # 繪製座標軸 (更粗的線)
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axvline(0, color='black', linewidth=1.5)

    # 繪製網格線
    ax.grid(True, linestyle='--', alpha=0.6)

    # 設置刻度 V17.1 CRITICAL RULE: Visual Solvability
    ax.set_xticks(range(x_min_limit, x_max_limit + 1))
    ax.set_yticks(range(y_min_limit, y_max_limit + 1))
    
    # 設置刻度標籤
    ax.tick_params(axis='x', labelsize=10)
    ax.tick_params(axis='y', labelsize=10)

    # 標示原點 '0' (V10.2)
    ax.text(0, 0, '0', color='black', ha='right', va='top', fontsize=18, fontweight='bold')

    # 繪製箭頭 (V13.6 API Hardened)
    # 使用 ax.get_xlim() 和 ax.get_ylim() 確保箭頭位於繪圖區域的邊緣
    current_xlim = ax.get_xlim()
    current_ylim = ax.get_ylim()
    ax.plot(current_xlim[1], 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False, markersize=8)
    ax.plot(0, current_ylim[1], "^k", transform=ax.get_xaxis_transform(), clip_on=False, markersize=8)

    # 標示點 V13.5 標籤隔離
    for label, (x, y) in points.items():
        ax.plot(x, y, 'o', color='red', markersize=8) # 繪製點
        # ax.text 只能標註點名稱，嚴禁座標值 (V13.0, V13.5)
        ax.text(x + 0.3, y + 0.3, label, fontsize=12, color='blue',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2')) # V10.2 白色光暈

    # 確保網格為正方形 (V10.2)
    ax.set_aspect('equal', adjustable='box')

    # 隱藏座標軸標籤，只顯示刻度數字
    ax.set_xlabel('')
    ax.set_ylabel('')

    # 將圖形轉換為 base64 編碼
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64


# --- `generate()` 函數設計規範 ---

def generate(level=1):
    problem_type = random.choice([
        'property_application',
        'condition_check',
        'coordinate_missing_vertex',
        'coordinate_identify_plot'
    ])

    question_text = ""
    correct_answer = ""
    answer_display = ""
    image_base64 = None

    if problem_type == 'property_application':
        # Type 1: 平行四邊形性質應用
        # Grade Alignment: 國二下，應用平行四邊形的對邊相等、對角相等、對角線互相平分等性質。
        # 對應 RAG Ex 3 (代數角度) 和 RAG Ex 4 (邊長性質應用)。
        
        sub_type = random.choice(['side', 'angle', 'diagonal'])

        if sub_type == 'side':
            side_ab = random.randint(5, 12)
            side_bc = random.randint(4, 10)
            question_text_template = r"已知四邊形 ABCD 為平行四邊形，若 $\overline{AB} = {ab_val}$ 公分，$\overline{BC} = {bc_val}$ 公分，則 $\overline{CD}$ 與 $\overline{AD}$ 的長度各為多少公分？請依序以半形逗號分隔填寫答案。"
            question_text = question_text_template.replace("{ab_val}", str(side_ab)).replace("{bc_val}", str(side_bc))
            correct_answer = f"{side_ab},{side_bc}"
            answer_display = f"$\overline{CD} = {side_ab}$ 公分, $\overline{AD} = {side_bc}$ 公分"
        elif sub_type == 'angle':
            # 鏡射 RAG Ex 3 第一部分 (代數角度)
            angle_a_val = random.randint(60, 120) # 實際的 ∠A 值
            angle_c_val = angle_a_val # 對角相等

            # 為 ∠A 生成代數表達式
            coeff_x = random.randint(1, 3)
            const_x = random.randint(0, 30) * random.choice([-1, 1]) # 常數可以是負數
            
            # 確保 x 是整數，且計算出的角度為正數
            while (angle_a_val - const_x) % coeff_x != 0 or (angle_a_val - const_x) / coeff_x <= 0:
                angle_a_val = random.randint(60, 120)
                angle_c_val = angle_a_val
                coeff_x = random.randint(1, 3)
                const_x = random.randint(0, 30) * random.choice([-1, 1])
            
            x_val = (angle_a_val - const_x) // coeff_x
            
            question_text_template = r"已知四邊形 ABCD 為平行四邊形，若 $\angle A = ({coeff}x + {const})^\circ$，且 $\angle C = {angle_c_val}^\circ$，則 $x$ 的值為何？"
            question_text = question_text_template.replace("{coeff}", str(coeff_x)).replace("{const}", str(const_x)).replace("{angle_c_val}", str(angle_c_val))
            correct_answer = str(x_val)
            answer_display = f"$x = {x_val}$"
        elif sub_type == 'diagonal':
            diag_half_ac = random.randint(3, 8)
            # diag_half_bd = random.randint(4, 9) # BD長度在此題型中不使用
            
            # 確保表達式能得出整數值
            diag_ac_expr_coeff = random.randint(1, 2)
            diag_ac_expr_const = random.randint(0, 3) * random.choice([-1, 1]) # 常數可以是負數
            
            # 確保 x_diag_val 是正整數
            while (diag_half_ac * 2 - diag_ac_expr_const) % diag_ac_expr_coeff != 0 or (diag_half_ac * 2 - diag_ac_expr_const) / diag_ac_expr_coeff <= 0:
                diag_half_ac = random.randint(3, 8)
                diag_ac_expr_coeff = random.randint(1, 2)
                diag_ac_expr_const = random.randint(0, 3) * random.choice([-1, 1])
            
            x_diag_val = (diag_half_ac * 2 - diag_ac_expr_const) // diag_ac_expr_coeff

            question_text_template = r"已知四邊形 ABCD 為平行四邊形，對角線 $\overline{AC}$ 與 $\overline{BD}$ 交於 $O$ 點。若 $\overline{AO} = {ao_val}$ 公分，$\overline{AC} = ({coeff}x + {const})$ 公分，則 $x$ 的值為何？"
            question_text = question_text_template.replace("{ao_val}", str(diag_half_ac)).replace("{coeff}", str(diag_ac_expr_coeff)).replace("{const}", str(diag_ac_expr_const))
            correct_answer = str(x_diag_val)
            answer_display = f"$x = {x_diag_val}$"


    elif problem_type == 'condition_check':
        # Type 2: 平行四邊形判別條件 (True/False)
        # Grade Alignment: 國二下，判斷四邊形是否為平行四邊形的五大條件。
        # 對應 RAG Ex 1, 2, 4, 5。生成單一的是非題。
        
        # 構成平行四邊形的條件 (答案為「是」)
        true_conditions = [
            (r"一個四邊形，兩雙對邊互相平行，請問它是否為平行四邊形？", "是"),
            (r"一個四邊形，兩雙對角相等，請問它是否為平行四邊形？", "是"), # 鏡射 RAG Ex 1
            (r"一個四邊形，對角線互相平分，請問它是否為平行四邊形？", "是"),
            (r"一個四邊形，一雙對邊平行且相等，請問它是否為平行四邊形？", "是"),
            (r"一個四邊形，四邊都相等，請問它是否為平行四邊形？", "是"), # 菱形是平行四邊形
            (r"一個四邊形，四個角都是直角，請問它是否為平行四邊形？", "是"), # 矩形是平行四邊形
            (r"一個四邊形，相鄰兩角互補，請問它是否為平行四邊形？", "是"),
            (r"一個四邊形，對角線互相垂直平分，請問它是否為平行四邊形？", "是"), # 菱形是平行四邊形
            # 特定角度/邊長案例 (鏡射 RAG Ex 2 & 5 的判斷邏輯，但以是非題形式呈現)
            (r"一個四邊形 ABCD，若 $\angle A = 70^\circ, \angle B = 110^\circ, \angle C = 70^\circ, \angle D = 110^\circ$，請問它是否為平行四邊形？", "是"), # 鏡射 RAG Ex 2乙 的判斷邏輯
            (r"一個四邊形 ABCD，若 $\angle A = 90^\circ, \angle B = 90^\circ, \angle C = 90^\circ, \angle D = 90^\circ$，請問它是否為平行四邊形？", "是"), # 鏡射 RAG Ex 2丁 的判斷邏輯
            (r"一個四邊形 ABCD，若 $\overline{AB} = 4$ 公分, $\overline{BC} = 4$ 公分, $\overline{CD} = 4$ 公分, $\overline{DA} = 4$ 公分，請問它是否為平行四邊形？", "是"), # 鏡射 RAG Ex 5甲 的判斷邏輯
            (r"一個四邊形 ABCD，若 $\overline{AB} = 2$ 公分, $\overline{BC} = 3$ 公分, $\overline{CD} = 2$ 公分, $\overline{DA} = 3$ 公分，請問它是否為平行四邊形？", "是"), # 鏡射 RAG Ex 5丁 的判斷邏輯
            (r"一個四邊形，兩雙對邊分別相等，請問它是否為平行四邊形？", "是"), # 鏡射 RAG Ex 4
        ]
        
        # 不構成平行四邊形的條件 (答案為「否」)
        false_conditions = [
            (r"一個四邊形，一雙對邊平行，另一雙對邊相等，請問它是否為平行四邊形？", "否"), # 可能是等腰梯形
            (r"一個四邊形，一雙對邊平行，且對角線相等，請問它是否為平行四邊形？", "否"), # 可能是等腰梯形
            (r"一個四邊形 ABCD，若 $\angle A = 120^\circ, \angle B = 60^\circ, \angle C = 60^\circ, \angle D = 120^\circ$，請問它是否為平行四邊形？", "否"), # 鏡射 RAG Ex 2甲 的判斷邏輯 (∠A != ∠C)
            (r"一個四邊形 ABCD，若 $\angle A = 89^\circ, \angle B = 89^\circ, \angle C = 91^\circ, \angle D = 91^\circ$，請問它是否為平行四邊形？", "否"), # 鏡射 RAG Ex 2丙 的判斷邏輯 (∠A != ∠C, ∠B != ∠D)
            (r"一個四邊形 ABCD，若 $\overline{AB} = 1$ 公分, $\overline{BC} = 2$ 公分, $\overline{CD} = 3$ 公分, $\overline{DA} = 4$ 公分，請問它是否為平行四邊形？", "否"), # 鏡射 RAG Ex 5乙 的判斷邏輯
            (r"一個四邊形 ABCD，若 $\overline{AB} = 2$ 公分, $\overline{BC} = 2$ 公分, $\overline{CD} = 3$ 公分, $\overline{DA} = 3$ 公分，請問它是否為平行四邊形？", "否"), # 鏡射 RAG Ex 5丙 的判斷邏輯
            (r"一個四邊形，只有一組對邊平行，請問它是否為平行四邊形？", "否"), # 梯形
            (r"一個四邊形，只有一組對邊相等，請問它是否為平行四邊形？", "否"),
        ]

        # 隨機選擇一個條件 (是或否)
        if random.choice([True, False]):
            question_text_template, correct_answer = random.choice(true_conditions)
        else:
            question_text_template, correct_answer = random.choice(false_conditions)
        
        question_text = question_text_template
        answer_display = correct_answer
        
    elif problem_type == 'coordinate_missing_vertex':
        # Type 3: 座標平面上平行四邊形缺失頂點
        # Grade Alignment: 國二下，結合座標幾何與平行四邊形向量性質 (對邊向量相等)。
        
        # 隨機生成三個頂點 A, B, C
        # 確保點不共線，且能構成一個平行四邊形
        # 座標範圍 -8 到 8
        A = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
        B = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
        C = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])

        # 確保 A, B, C 是不同的點且不共線
        def are_collinear(p1, p2, p3):
            # 檢查 (y2-y1)(x3-x2) == (y3-y2)(x2-x1)
            return abs((p2[1] - p1[1]) * (p3[0] - p2[0]) - (p3[1] - p2[1]) * (p2[0] - p1[0])) < 1e-9

        while len(set([A, B, C])) < 3 or are_collinear(A, B, C):
            A = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
            B = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
            C = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])

        # 計算第四個點 D 的座標，使 ABCD 形成平行四邊形
        # D = A + (C - B) => Dx = Ax + Cx - Bx, Dy = Ay + Cy - By
        dx_val = A[0] + C[0] - B[0]
        dy_val = A[1] + C[1] - B[1]
        
        # 確保 D 點座標在合理範圍內 (-8 到 8)，且不與 A, B, C 重合
        max_coord_val = 8
        min_coord_val = -8
        D_candidate = (dx_val, dy_val)
        
        # 如果 D 超出範圍或重合，則重新生成所有點
        while not (min_coord_val <= D_candidate[0] <= max_coord_val and min_coord_val <= D_candidate[1] <= max_coord_val) or \
              D_candidate in [A, B, C]:
            A = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
            B = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
            C = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
            while len(set([A, B, C])) < 3 or are_collinear(A, B, C): # 確保 A,B,C 仍滿足條件
                A = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
                B = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
                C = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
            dx_val = A[0] + C[0] - B[0]
            dy_val = A[1] + C[1] - B[1]
            D_candidate = (dx_val, dy_val)

        D = D_candidate

        # 格式化座標為顯示字串
        A_str = _format_coordinate_latex(A)
        B_str = _format_coordinate_latex(B)
        C_str = _format_coordinate_latex(C)
        D_str_display = _format_coordinate_latex(D) # 用於 answer_display

        question_text_template = r"在座標平面上，已知平行四邊形 ABCD 的三個頂點為 $A{A_coord}$、$B{B_coord}$、$C{C_coord}$，則 $D$ 點的座標為何？請以 (x,y) 格式填寫答案。"
        question_text = question_text_template.replace("{A_coord}", A_str).replace("{B_coord}", B_str).replace("{C_coord}", C_str)
        
        # correct_answer 必須是純數據 (x,y)
        correct_answer = f"{_format_raw_coordinate_value(D[0])},{_format_raw_coordinate_value(D[1])}"
        answer_display = f"$D{D_str_display}$"

        # 繪製座標平面圖 (不顯示 D 點，讓學生計算)
        points_to_plot = {'A': A, 'B': B, 'C': C} 
        image_base64 = _draw_coordinate_plane(points_to_plot, -10, 10, -10, 10)

    elif problem_type == 'coordinate_identify_plot':
        # Type 4: 座標平面上判別平行四邊形
        # Grade Alignment: 國二下，結合座標幾何，透過斜率、距離或中點公式判斷平行四邊形。

        # 生成四個點 P1, P2, P3, P4
        P1 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
        P2 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
        P3 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
        P4 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])

        # 確保初始點是不同的
        initial_points = [P1, P2, P3, P4]
        while len(set(initial_points)) < 4:
            P1 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
            P2 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
            P3 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
            P4 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
            initial_points = [P1, P2, P3, P4]

        # 隨機決定是否為平行四邊形
        is_parallelogram_actual = random.choice([True, False])

        if is_parallelogram_actual:
            # 確保 P1P2P3P4 是平行四邊形
            # P4 = P1 + (P3 - P2) => P4x = P1x + P3x - P2x, P4y = P1y + P3y - P2y
            P4_new_x = P1[0] + P3[0] - P2[0]
            P4_new_y = P1[1] + P3[1] - P2[1]
            P4_candidate = (P4_new_x, P4_new_y)
            
            # 確保新的 P4 點在合理範圍內 (-8 到 8) 且不與 P1, P2, P3 重合
            max_coord_val = 8
            min_coord_val = -8
            while not (min_coord_val <= P4_candidate[0] <= max_coord_val and min_coord_val <= P4_candidate[1] <= max_coord_val) or \
                  P4_candidate in [P1, P2, P3]:
                P1 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
                P2 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
                P3 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
                while len(set([P1, P2, P3])) < 3: # 確保 P1,P2,P3 是不同的點
                    P1 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
                    P2 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
                    P3 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
                P4_new_x = P1[0] + P3[0] - P2[0]
                P4_new_y = P1[1] + P3[1] - P2[1]
                P4_candidate = (P4_new_x, P4_new_y)
            
            P4 = P4_candidate
            points = {'P1': P1, 'P2': P2, 'P3': P3, 'P4': P4}
            correct_answer = "是"
            answer_display = "是 (因為 $\overline{P1P2} \parallel \overline{P4P3}$ 且 $\overline{P2P3} \parallel \overline{P1P4}$)"
            
        else:
            # 確保 P1P2P3P4 不是平行四邊形
            # P1, P2, P3 隨機生成。P4 必須不構成平行四邊形。
            # 利用對角線中點不重合的特性來判斷。
            
            # 重新生成 P1, P2, P3, P4 確保它們是不同的點
            P1 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
            P2 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
            P3 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
            P4 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])

            while len(set([P1, P2, P3, P4])) < 4:
                P1 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
                P2 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
                P3 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
                P4 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
            
            mid_p1p3_x = (P1[0] + P3[0]) / 2
            mid_p1p3_y = (P1[1] + P3[1]) / 2
            mid_p2p4_x = (P2[0] + P4[0]) / 2
            mid_p2p4_y = (P2[1] + P4[1]) / 2

            # 如果中點重合 (或非常接近)，則 P1P2P3P4 是平行四邊形。重新生成 P4。
            # 使用一個小的容差值來比較浮點數
            while math.isclose(mid_p1p3_x, mid_p2p4_x, rel_tol=1e-6) and math.isclose(mid_p1p3_y, mid_p2p4_y, rel_tol=1e-6):
                P4 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
                # 確保新的 P4 點與 P1, P2, P3 不同
                while P4 in [P1, P2, P3]:
                    P4 = (_generate_coordinate_value(min_val=-7, max_val=7)[0], _generate_coordinate_value(min_val=-7, max_val=7)[0])
                mid_p2p4_x = (P2[0] + P4[0]) / 2
                mid_p2p4_y = (P2[1] + P4[1]) / 2
            
            points = {'P1': P1, 'P2': P2, 'P3': P3, 'P4': P4}
            correct_answer = "否"
            answer_display = "否 (因為對角線不互相平分)"

        P1_str = _format_coordinate_latex(P1)
        P2_str = _format_coordinate_latex(P2)
        P3_str = _format_coordinate_latex(P3)
        P4_str = _format_coordinate_latex(P4)

        question_text_template = r"在座標平面上，有四個點 $P_1{P1_coord}$、$P_2{P2_coord}$、$P_3{P3_coord}$、$P_4{P4_coord}$。請問這四個點依序連接後是否形成一個平行四邊形？"
        question_text = question_text_template.replace("{P1_coord}", P1_str).replace("{P2_coord}", P2_str).replace("{P3_coord}", P3_str).replace("{P4_coord}", P4_str)
        
        image_base64 = _draw_coordinate_plane(points, -10, 10, -10, 10)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display, # 用於前端顯示，包含單位/上下文
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1"
    }


# --- `check()` 函數設計規範 (通用 Check 函式模板) ---


    import re, math
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        # 保留數字、小數點、負號、逗號、斜線 (用於分數)
        return re.sub(r'[^\d,\.\-/%]', '', s) 

    # [V18.13 Update] 支援中英文是非題互通
    u_str = str(user_answer).strip()
    c_str = str(correct_answer).strip()
    
    # [V18.14 Expanded Vocabulary - Case Robust]
    yes_group = ["是", "yes", "true", "1", "o", "right", "正確", "對", "correct", "Yes", "TRUE", "True", "O", "Right"]
    # Note: "不一定" implies the statement "It is a parallelogram" is False logic-wise.
    no_group = ["否", "no", "false", "0", "x", "wrong", "錯誤", "錯", "不正確", "不一定", "No", "FALSE", "False", "X", "Wrong"]
    
    if c_str in yes_group:
        return {"correct": u_str in yes_group, "result": "正確！" if u_str in yes_group else "答案錯誤"}
    if c_str in no_group:
        return {"correct": u_str in no_group, "result": "正確！" if u_str in no_group else "答案錯誤"}

    # 3. 數值與字串比對
    try:
        # 解析分數與浮點數
        def parse(v):
           if "/" in v: 
               parts = v.split("/")
               if len(parts) == 2:
                   return float(parts[0]) / float(parts[1])
           return float(v)
        
        # 處理逗號分隔的數值 (例如座標 "1,2" 或 "3.5,-0.5")
        user_parts = [parse(p) for p in clean(u_str).split(',') if p.strip()]
        correct_parts = [parse(p) for p in clean(c_str).split(',') if p.strip()]

        if len(user_parts) != len(correct_parts):
            return {"correct": False, "result": "答案數量不符。"}
        
        all_match = True
        for u_val, c_val in zip(user_parts, correct_parts):
            if not math.isclose(u_val, c_val, rel_tol=1e-5): # 浮點數比較容錯
                all_match = False
                break
        
        if all_match:
            return {"correct": True, "result": "正確！"}
    except Exception as e:
        # 捕獲解析錯誤，以便執行字串比對
        pass
        
    # 最後的字串完全比對
    if u_str == c_str: return {"correct": True, "result": "正確！"}
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
