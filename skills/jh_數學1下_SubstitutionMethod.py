# ==============================================================================
# ID: jh_數學1下_SubstitutionMethod
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 41.64s | RAG: 3 examples
# Created At: 2026-01-15 13:12:30
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


import datetime

import base64

# --- Helper Functions ---
# All helper functions must return a value.
# If used in question_text, return value must be string.
# Visualisation functions (N/A here) must only receive known data, not answers.

def _format_equation(coeff_x, coeff_y, constant, var1='x', var2='y'):
    """
    Helper function to format a linear equation (Ax + By = C) into a LaTeX-safe string.
    Ensures adherence to LaTeX safety rules by using .replace() method only.
    e.g., 2x - 3y = 5
    """
    parts = []

    # Handle x term
    if coeff_x == 1:
        parts.append(var1)
    elif coeff_x == -1:
        parts.append(r"-{v}".replace("{v}", var1))
    elif coeff_x != 0:
        parts.append(r"{cx}{v}".replace("{cx}", str(coeff_x)).replace("{v}", var1))

    # Handle y term
    if coeff_y != 0:
        if coeff_y == 1:
            if parts:
                parts.append(r"+ {v}".replace("{v}", var2))
            else:
                parts.append(var2)
        elif coeff_y == -1:
            parts.append(r"- {v}".replace("{v}", var2))
        else:
            if coeff_y > 0:
                if parts:
                    parts.append(r"+ {cy}{v}".replace("{cy}", str(coeff_y)).replace("{v}", var2))
                else:
                    parts.append(r"{cy}{v}".replace("{cy}", str(coeff_y)).replace("{v}", var2))
            else: # coeff_y < 0
                parts.append(r"- {abs_cy}{v}".replace("{abs_cy}", str(abs(coeff_y))).replace("{v}", var2))

    # If both coefficients are zero, this is an invalid equation for this context for a system with a unique solution
    if not parts:
        return r"0 = {c}".replace("{c}", str(constant))

    equation_str = " ".join(parts)
    equation_str = r"{eq_str} = {c}".replace("{eq_str}", equation_str).replace("{c}", str(constant))
    return equation_str

def _format_isolated_equation(coeff_other_var, const_term, var_isolated='y', var_other='x'):
    """
    Helper function to format an equation where one variable is isolated (e.g., y = Ax + B or x = Ay + B).
    Ensures adherence to LaTeX safety rules by using .replace() method only.
    """
    rhs_parts = []

    # Handle term with 'var_other'
    if coeff_other_var == 1:
        rhs_parts.append(var_other)
    elif coeff_other_var == -1:
        rhs_parts.append(r"-{v}".replace("{v}", var_other))
    elif coeff_other_var != 0:
        rhs_parts.append(r"{cx}{v}".replace("{cx}", str(coeff_other_var)).replace("{v}", var_other))

    # Handle constant term
    if const_term != 0:
        if const_term > 0:
            if rhs_parts:
                rhs_parts.append(r"+ {abs_c}".replace("{abs_c}", str(const_term)))
            else:
                rhs_parts.append(str(const_term))
        else: # const_term < 0
            rhs_parts.append(r"- {abs_c}".replace("{abs_c}", str(abs(const_term))))
    
    # If both are zero, just return 0
    if not rhs_parts:
        rhs_str = "0"
    else:
        rhs_str = " ".join(rhs_parts)

    equation_str = r"{v_iso} = {rhs_s}".replace("{v_iso}", var_isolated).replace("{rhs_s}", rhs_str)
    return equation_str


# --- Top-level Functions ---

def generate(level=1):
    """
    【任務說明】
    生成一個 K12 數學「代入消去法」的聯立方程式題目。
    題目數據嚴格遵循隨機生成與反向計算原則，確保整數解。

    【題型鏡射 (Problem Mirroring)】
    - 隨機分流: 根據 random.choice 選擇兩種主要題型。
    - 範例: 所有係數、常數和解均為動態生成，而非硬編碼。
    - 不設計新題目，僅隨機化 RAG 中的現有題型。

    【數據禁絕常數 (Data Prohibition)】
    - 隨機生成: 所有係數和常數均使用 random.randint 生成。
    - 公式計算: 先生成整數解 (x_sol, y_sol)，然後反向構建方程式，確保解的正確性。

    【排版與 LaTeX 安全 (Elite Guardrails)】
    - 語法零修復 (Regex=0): 所有包含 LaTeX 指令的字串均嚴格使用 .replace() 方法。
    - 嚴禁使用 f-string 或 % 格式化於 LaTeX 字串中。
    - 數學式一律使用 $...$。
    - 嚴禁使用 \par 或 \[...\].

    Args:
        level (int): 難度等級 (目前未實作差異化，所有題目均為中等難度，確保整數解)。

    Returns:
        dict: 包含 question_text, correct_answer, answer, image_base64 等標準欄位。
    """
    
    # 隨機選擇題型
    # Type 1 (Maps to RAG Ex 1 & Ex 2): 一個變數已明確被表示出來 (e.g., x=2y or y=3-9x)
    # Type 2 (Maps to RAG Ex 3): 某個變數的係數是 1 或 -1，易於代入消去 (e.g., x+4y=-1 or 5x-y=16)
    problem_type = random.choice([1, 2])
    
    # 1. 數據禁絕常數：隨機生成整數解
    x_sol = random.randint(-5, 5)
    y_sol = random.randint(-5, 5)

    # 避免過於瑣碎的解 (例如 x=0, y=0)
    # 確保至少一個非零，或兩個都非零
    while x_sol == 0 and y_sol == 0:
        x_sol = random.randint(-5, 5)
        y_sol = random.randint(-5, 5)

    question_text = ""
    correct_answer = {'x': x_sol, 'y': y_sol}
    
    # 係數和常數的隨機範圍
    coeff_min = -5
    coeff_max = 5

    if problem_type == 1:
        # Type 1 (Maps to RAG Ex 1 & Ex 2): 一個變數已明確被表示出來 (e.g., x=2y or y=3-9x)
        # 方程式 1: isolated_var = a * other_var + b
        # 方程式 2: c*x + d*y = e

        isolated_var_name = random.choice(['x', 'y'])
        other_var_name = 'y' if isolated_var_name == 'x' else 'x'

        while True:
            # 1.1 生成方程式 1: isolated_var = a * other_var + b
            a = random.randint(coeff_min, coeff_max)
            # 避免 isolated_var = b (過於簡單，例如 y=5)
            if a == 0: 
                continue 
            
            # 公式計算: 確保 (x_sol, y_sol) 滿足方程式 1
            if isolated_var_name == 'y':
                b = y_sol - a * x_sol
            else: # isolated_var_name == 'x'
                b = x_sol - a * y_sol

            # 1.2 生成方程式 2: cx + dy = e
            c = random.randint(coeff_min, coeff_max)
            d = random.randint(coeff_min, coeff_max)
            
            # 避免方程式 2 係數皆為零 (0 = e)
            if c == 0 and d == 0: 
                continue

            # 公式計算: 確保 (x_sol, y_sol) 滿足方程式 2
            e = c * x_sol + d * y_sol

            # 檢查是否有唯一解 (行列式不為零)
            # 系統可寫為:
            # 若 isolated_var_name == 'y': -ax + 1y = b, cx + dy = e => 行列式 = (-a)*d - (1)*c = -ad - c
            # 若 isolated_var_name == 'x': 1x - ay = b, cx + dy = e => 行列式 = (1)*d - (-a)*c = d + ac
            
            determinant = 0
            if isolated_var_name == 'y':
                determinant = (-a * d - c)
            else: # isolated_var_name == 'x'
                determinant = (d + a * c)

            if determinant != 0:
                # 避免係數過於簡單 (例如全部都是 1 或 -1，且常數也小)
                # 這是一個啟發式檢查，旨在增加題目多樣性，非數學必要條件
                if not (abs(a) <= 1 and abs(b) <=1 and abs(c) <= 1 and abs(d) <= 1 and abs(e) <=1):
                    break
            
        eq1_str = _format_isolated_equation(a, b, isolated_var_name, other_var_name)
        eq2_str = _format_equation(c, d, e, 'x', 'y')

        question_text = r"請使用代入消去法解下列聯立方程式：$\begin{cases} " + \
                        eq1_str.replace("=", "&=") + r" \\ " + \
                        eq2_str.replace("=", "&=") + r" \end{cases}$"

    elif problem_type == 2:
        # Type 2 (Maps to RAG Ex 3): 某個變數的係數是 1 或 -1，易於代入消去
        # 方程式 1: ax + by = c (其中 a 或 b 為 1 或 -1)
        # 方程式 2: dx + ey = f

        while True:
            # 2.1 生成方程式 1: 確保某個變數係數為 1 或 -1
            a, b = 0, 0
            choice_coeff_eq1 = random.choice(['x_coeff", "y_coeff'])
            coeff_val_for_easy_isolation = random.choice([1, -1])

            if choice_coeff_eq1 == 'x_coeff':
                a = coeff_val_for_easy_isolation
                b = random.randint(coeff_min, coeff_max)
                # 避免 ax = c (過於簡單，例如 x=5)
                if b == 0: continue 
            else: # choice_coeff_eq1 == 'y_coeff'
                a = random.randint(coeff_min, coeff_max)
                # 避免 by = c (過於簡單，例如 y=5)
                if a == 0: continue 
                b = coeff_val_for_easy_isolation
            
            # 增加複雜度：如果 Eq1 的兩個係數都為 1 或 -1 (例如 x+y=C)，隨機增大其中一個
            if abs(a) == 1 and abs(b) == 1:
                if random.random() < 0.5: # 增大 'a'
                    a = random.randint(2, coeff_max) * random.choice([1, -1])
                else: # 增大 'b'
                    b = random.randint(2, coeff_max) * random.choice([1, -1])
                # 重新檢查是否變為過於簡單 (例如增大後變成 0)
                if a == 0 or b == 0: continue

            # 公式計算: 確保 (x_sol, y_sol) 滿足方程式 1
            c = a * x_sol + b * y_sol

            # 2.2 生成方程式 2: dx + ey = f
            d = random.randint(coeff_min, coeff_max)
            e = random.randint(coeff_min, coeff_max)
            
            # 避免方程式 2 係數皆為零 (0 = f)
            if d == 0 and e == 0: 
                continue

            # 公式計算: 確保 (x_sol, y_sol) 滿足方程式 2
            f = d * x_sol + e * y_sol

            # 檢查是否有唯一解 (行列式不為零)
            # 行列式 = ae - bd
            determinant = (a * e - b * d)
            
            if determinant != 0:
                # 避免係數過於簡單 (例如全部都是 1 或 -1，且常數也小)
                # 這是一個啟發式檢查，旨在增加題目多樣性，非數學必要條件
                if not (abs(a) <= 1 and abs(b) <= 1 and abs(c) <= 1 and abs(d) <= 1 and abs(e) <= 1 and abs(f) <= 1):
                    break
            
        eq1_str = _format_equation(a, b, c, 'x', 'y')
        eq2_str = _format_equation(d, e, f, 'x', 'y')

        question_text = r"請使用代入消去法解下列聯立方程式：$\begin{cases} " + \
                        eq1_str.replace("=", "&=") + r" \\ " + \
                        eq2_str.replace("=", "&=") + r" \end{cases}$"

    else:
        # 如果 problem_type 不在預期範圍內，拋出錯誤
        raise ValueError("Selected problem type is not implemented.")

    # 7. 數據與欄位 (Standard Fields)
    # 欄位鎖死: 必須且僅能包含 question_text, correct_answer, answer, image_base64
    # 時間戳記: 更新時必須將 created_at 設為 datetime.now() 並遞增 version。
    output = {
        "question_text": question_text,
        "correct_answer": correct_answer, # dict {'x': val, 'y': val} for internal comparison
        "answer": f"x={x_sol}, y={y_sol}", # string for display (f-string allowed here as it's not LaTeX)
        "image_base64": "", # 無圖形，因此為空字串
        "created_at": datetime.datetime.now().isoformat(),
        "version": "1.0"
    }
    return output


    """
    【任務說明】
    檢查用戶答案的正確性。

    Args:
        user_answer (str): 用戶提交的答案，例如 "x=3, y=2" 或 "x=3\ny=2"。
        correct_answer (dict): 正確答案，例如 {'x': 3, 'y': 2}。

    Returns:
        bool: 如果用戶答案正確則為 True，否則為 False。
    """
    try:
        # 標準化用戶答案字串：轉小寫、去除空格、將換行符替換為逗號以利解析
        user_answer_normalized = user_answer.lower().replace(" ", "").replace("\n", ",")
        
        parsed_user_ans = {}
        parts = user_answer_normalized.split(',')
        for part in parts:
            if '=' in part:
                var, val_str = part.split('=')
                parsed_user_ans[var.strip()] = int(val_str.strip())
            
        # 比較解析後的用戶答案與正確答案
        # 確保 'x' 和 'y' 都存在且值匹配
        is_correct = (parsed_user_ans.get('x') == correct_answer.get('x') and
                      parsed_user_ans.get('y') == correct_answer.get('y'))
        
        return is_correct
    except (ValueError, KeyError, IndexError):
        # 處理用戶答案格式不正確的情況
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
            triggers = ['^', '/', ',', '|', '(', '[', '{', '\\']
            
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
