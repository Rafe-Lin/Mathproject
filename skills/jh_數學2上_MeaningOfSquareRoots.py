# ==============================================================================
# ID: jh_數學2上_MeaningOfSquareRoots
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 61.55s | RAG: 3 examples
# Created At: 2026-01-18 15:06:32
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

# 輔助函式定義區 (Helper Functions)
# ==============================================================================

def _generate_perfect_square(min_sqrt_val, max_sqrt_val):
    """
    生成一個在指定範圍內的完全平方數。
    Args:
        min_sqrt_val (int): 平方根的最小值 (含)。
        max_sqrt_val (int): 平方根的最大值 (含)。
    Returns:
        int: 一個完全平方數。
    """
    sqrt_val = random.randint(min_sqrt_val, max_sqrt_val)
    return sqrt_val * sqrt_val

def _format_algebraic_expression(m_coeff, n_const, var_name='x'):
    """
    格式化代數表達式 Mx + N，嚴格遵守 Guardrail 4 (方程式生成鎖死)。
    Args:
        m_coeff (int): 變數的係數。
        n_const (int): 常數項。
        var_name (str): 變數名稱 (e.g., 'x', 'y')。
    Returns:
        str: 格式化後的代數表達式字串。
    """
    parts = []
    # 處理變數項 (M_coeff * var_name)
    if m_coeff == 1:
        parts.append(var_name)
    elif m_coeff == -1:
        parts.append("-" + var_name)
    else:
        parts.append(str(m_coeff) + var_name)

    # 處理常數項 (N_const)
    if n_const > 0:
        parts.append("+" + str(n_const))
    elif n_const < 0:
        parts.append("-" + str(abs(n_const)))

    expression = "".join(parts)
    return expression

def _draw_number_line(points, labels, x_range=(-10, 10), tick_interval=1, point_size=100):
    """
    繪製數線，並標示指定點。
    [CRITICAL RULE: Visual Solvability]：數線必須有明確的刻度數字。
    [防洩漏原則]：僅接收題目已知數據。
    [V13.0 格線對齊]：座標軸範圍必須是對稱整數，xticks 間隔固定為 1。
    [V13.5 座標範圍]：座標範圍必須對稱且寬裕。
    [V13.6 API Hardened Spec]：嚴禁使用 arrowprops。
    """
    fig, ax = plt.subplots(figsize=(8, 2))
    ax.set_aspect('equal') # V10.2 Pure Style

    # 繪製數線 (X軸)
    ax.axhline(0, color='black', linewidth=1)

    # 繪製箭頭 (V13.6 API Hardened Spec)
    ax.plot(x_range[1], 0, ">k", clip_on=False, markersize=5)
    ax.plot(x_range[0], 0, "<k", clip_on=False, markersize=5)

    # 設定刻度與標籤
    ax.set_xticks(np.arange(x_range[0], x_range[1] + 1, tick_interval))
    ax.set_yticks([]) # 不顯示 Y 軸刻度

    # 標示原點 (V10.2 Pure Style)
    ax.text(0, 0, '0', color='black', ha='center', va='top', fontsize=18, fontweight='bold')

    ax.set_xlim(x_range[0] - 0.5, x_range[1] + 0.5)
    ax.set_ylim(-0.5, 1) # 調整 Y 軸範圍以容納點和標籤

    # 標示點 (若有)
    for i, p in enumerate(points):
        if i < len(labels):
            ax.text(p, 0.2, labels[i], color='blue', ha='center', va='bottom',
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", lw=0, alpha=0.7)) # V10.2 Pure Style: 白色光暈

    ax.axis('off') # 隱藏所有軸線和標籤

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# ==============================================================================

def generate(level=1):
    # MANDATORY MIRRORING RULES: STRICT MAPPING to RAG Examples
    problem_types = ['type_1_find_all_square_roots', 'type_2_solve_from_negative_sqrt', 'type_3_solve_from_positive_sqrt']
    problem_type = random.choice(problem_types)

    question_text = ""
    correct_answer = ""
    image_base64 = ""
    
    # 國二上學期 (Grade 8, First Semester) 平方根的意義
    # [CRITICAL RULE: Grade & Semantic Alignment]
    # 確保題目符合國二程度，主要處理完全平方數的平方根，避免過於複雜的根號運算。

    if problem_type == 'type_1_find_all_square_roots':
        # Type 1 MUST use the EXACT mathematical model of RAG Ex 1.
        # RAG Ex 1: 寫出下列各數的平方根。⑴ 23⑵ 144⑶ 9/25⑷ 0.04 -> ⑴ $\pm\sqrt{23}$⑵ $\pm 12$⑶ $\pm 3/5$⑷ $\pm 0.2$
        # 我們將生成完全平方數，使其平方根為整數，符合 K12 國二程度。
        num_squared = _generate_perfect_square(min_sqrt_val=2, max_sqrt_val=15) # 生成 4 到 225 之間的完全平方數
        ans_val = int(math.sqrt(num_squared))

        # [CRITICAL RULE: Answer Data Purity]：純數據，不含符號、單位。
        # [V13.1 答案格式標準化]：純數字列表
        correct_answer = f"{ans_val}, -{ans_val}" # 例如: "12, -12"

        # [排版與 LaTeX 安全]：嚴禁 f-string 組合 LaTeX，使用 replace。
        question_text = r"求 $ {num_squared} $ 的平方根。".replace("{num_squared}", str(num_squared))

    elif problem_type == 'type_2_solve_from_negative_sqrt':
        # Type 2 MUST use the EXACT mathematical model of RAG Ex 2.
        # RAG Ex 2: 若-5 是 2x-1 的負平方根，求 x 的值。 -> x = 13
        
        # 1. 選擇負平方根的值 (例如 -5)
        abs_sqrt_val = random.randint(3, 10) # 3 到 10
        neg_sqrt_val = -abs_sqrt_val 
        
        # 2. 選擇 x 的解 (保證為整數，符合 K12 程度)
        x_ans = random.randint(5, 20) # 5 到 20
        
        # 3. 選擇 x 的係數 (例如 2)
        M_coeff = random.choice([2, 3]) # 2 或 3
        
        # 4. 計算常數項 N_const，使 (neg_sqrt_val)^2 = M_coeff * x_ans + N_const 成立
        # N_const = (neg_sqrt_val)^2 - M_coeff * x_ans
        N_const = neg_sqrt_val**2 - M_coeff * x_ans 

        # 5. 使用輔助函式格式化代數表達式 (嚴格遵守 Guardrail 4)
        algebraic_expr_str = _format_algebraic_expression(M_coeff, N_const, var_name='x')
        
        # [CRITICAL RULE: Answer Data Purity]
        correct_answer = str(x_ans) # 例如: "13"

        # [排版與 LaTeX 安全]
        question_text = r"若 $ {neg_sqrt_val} $ 是 $ {algebraic_expr_str} $ 的負平方根，求 x 的值。"\
                        .replace("{neg_sqrt_val}", str(neg_sqrt_val))\
                        .replace("{algebraic_expr_str}", algebraic_expr_str)

    elif problem_type == 'type_3_solve_from_positive_sqrt':
        # Type 3 MUST use the EXACT mathematical model of RAG Ex 3.
        # RAG Ex 3: 若 5 是 3x＋2 的正平方根，求 x 的值。 -> x = 23/3
        
        # 1. 選擇正平方根的值 (例如 5)
        pos_sqrt_val = random.randint(3, 10) # 3 到 10
        
        # 2. 選擇 x 的係數 (例如 3)
        M_coeff = random.choice([2, 3, 4]) # 2, 3 或 4
        
        # 3. 選擇常數項 (例如 2)
        N_const = random.randint(-10, 10) # -10 到 10
        
        # 4. 計算 x 的值：(pos_sqrt_val)^2 = M_coeff * x + N_const
        # x = ((pos_sqrt_val)^2 - N_const) / M_coeff
        x_num = pos_sqrt_val**2 - N_const 
        x_den = M_coeff 
        
        # 5. 格式化正確答案為整數或分數
        if x_num % x_den == 0:
            x_val = x_num // x_den
            correct_answer = str(x_val) # 例如: "13"
        else:
            # 簡化分數 (例如 4/2 -> 2, 6/4 -> 3/2)
            gcd_val = math.gcd(x_num, x_den)
            x_val_num = x_num // gcd_val
            x_val_den = x_den // gcd_val
            correct_answer = f"{x_val_num}/{x_val_den}" # 例如: "23/3"

        # 6. 使用輔助函式格式化代數表達式 (嚴格遵守 Guardrail 4)
        algebraic_expr_str = _format_algebraic_expression(M_coeff, N_const, var_name='x')

        # [CRITICAL RULE: Answer Data Purity]
        # [排版與 LaTeX 安全]
        question_text = r"若 $ {pos_sqrt_val} $ 是 $ {algebraic_expr_str} $ 的正平方根，求 x 的值。"\
                        .replace("{pos_sqrt_val}", str(pos_sqrt_val))\
                        .replace("{algebraic_expr_str}", algebraic_expr_str)

    # 對於此技能，通常不需要圖形，這裡預設為空。
    # image_base64 = _draw_number_line([], [], x_range=(-10, 10)) # 範例：僅繪製空白數線，不顯示點

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "", # 留空，由前端填寫
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0.0"
    }


    """
    強韌閱卷邏輯 (Robust Check Logic)
    驗證使用者答案。
    [CRITICAL RULE: Answer Data Purity]
    [CRITICAL RULE: Robust Check Logic]
    [V12.6 結構鎖死]：數值序列比對。
    [V13.5 禁絕複雜比對]：統一使用數字序列比對。
    [SYSTEM GUARDRAIL 4]: check(u, c) 僅限回傳 True/False。
    """
    # 1. 清洗雙方輸入 (Input Sanitization)
    def clean_input(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除常見的變數前綴如 'x=', 'y=', 'ans='
        s = s.replace("$", "").replace("\\", "") # 移除 LaTeX 符號
        # 處理平方根答案中常見的 "±" 符號，將其轉換為逗號，以便後續解析為多個數字
        s = s.replace('±', ',').replace('+/-', ',').replace('+/', ',')
        return s
    
    # 2. 解析數值 (支援分數與小數)
    def parse_value_or_fraction(val_str):
        val_str = val_str.strip()
        if not val_str: # 處理空字串
            return float('nan')
        if "/" in val_str: # 處理分數形式 "n/d"
            parts = val_str.split("/")
            if len(parts) == 2:
                try:
                    n = float(parts[0])
                    d = float(parts[1])
                    if d == 0: return float('nan') # 除數為零
                    return n / d
                except ValueError:
                    return float('nan') # 無效的數字部分
            return float('nan') # 格式錯誤的分數 (e.g., "1/2/3")
        try: # 處理整數或小數
            return float(val_str)
        except ValueError:
            return float('nan') # 無效的數字字串

    cleaned_user = clean_input(user_answer)
    cleaned_correct = clean_input(correct_answer)

    # 根據 correct_answer 是否包含逗號來判斷是單一答案還是多個答案
    if ',' in cleaned_correct:
        # 情況 1: 多個答案 (例如 Type 1: 求平方根的 ± 值)
        user_parts = [part.strip() for part in cleaned_user.split(',') if part.strip()]
        correct_parts = [part.strip() for part in cleaned_correct.split(',') if part.strip()]

        user_values = []
        for part in user_parts:
            val = parse_value_or_fraction(part)
            if math.isnan(val): return False # 使用者答案中包含無效數字
            user_values.append(val)
        
        correct_values = []
        for part in correct_parts:
            val = parse_value_or_fraction(part)
            if math.isnan(val): return False # 正確答案必須是有效數字
            correct_values.append(val)

        if len(user_values) != len(correct_values):
            return False

        # 排序後進行比較，以處理答案順序不一致的情況 (例如 "3, -3" vs "-3, 3")
        user_values.sort()
        correct_values.sort()

        # 逐一比較數字，考慮浮點數精度
        for u_val, c_val in zip(user_values, correct_values):
            if not math.isclose(u_val, c_val, rel_tol=1e-9, abs_tol=0.0):
                return False
        return True

    else:
        # 情況 2: 單一答案 (例如 Type 2 & 3: 求解 x 的值)
        user_val = parse_value_or_fraction(cleaned_user)
        correct_val = parse_value_or_fraction(cleaned_correct)

        if math.isnan(user_val) or math.isnan(correct_val):
            return False # 其中一個值不是有效數字
        
        # 比較兩個單一數值，考慮浮點數精度
        return math.isclose(user_val, correct_val, rel_tol=1e-9, abs_tol=0.0)


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
