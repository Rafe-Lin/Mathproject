# ==============================================================================
# ID: jh_數學1下_LinearEquationInTwoVariables
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 106.22s | RAG: 4 examples
# Created At: 2026-01-15 09:49:19
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

# --- 4. Answer Checker (V10.6 Hardcoded Golden Standard) ---
def check(user_answer, correct_answer):
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    # [V11.0] 暴力清理 LaTeX 冗餘符號 ($, \) 與空格
    u = str(user_answer).strip().replace(" ", "").replace("，", ",").replace("$", "").replace("\\", "")
    
    # 強制還原字典格式 (針對商餘題)
    c_raw = correct_answer
    if isinstance(c_raw, str) and c_raw.startswith("{") and "quotient" in c_raw:
        try: import ast; c_raw = ast.literal_eval(c_raw)
        except: pass

    if isinstance(c_raw, dict) and "quotient" in c_raw:
        q, r = str(c_raw.get("quotient", "")), str(c_raw.get("remainder", ""))
        ans_display = r"{q},{r}".replace("{q}", q).replace("{r}", r)
        try:
            u_parts = u.replace("商", "").replace("餘", ",").split(",")
            if int(u_parts[0]) == int(q) and int(u_parts[1]) == int(r):
                return {"correct": True, "result": "正確！"}
        except: pass
    else:
        ans_display = str(c_raw).strip()

    if u == ans_display.replace(" ", ""): return {"correct": True, "result": "正確！"}
    try:
        import math
        if math.isclose(float(u), float(ans_display), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
    except: pass
    
    # [V11.1] 科學記號自動比對 (1.23*10^4 vs 1.23e4)
    # 支援 *10^, x10^, e 格式
    if "*" in str(ans_display) or "^" in str(ans_display) or "e" in str(ans_display):
        try:
            # 正規化：將常見乘號與次方符號轉為 E-notation
            norm_ans = str(ans_display).lower().replace("*10^", "e").replace("x10^", "e").replace("×10^", "e").replace("^", "")
            norm_user = str(u).lower().replace("*10^", "e").replace("x10^", "e").replace("×10^", "e").replace("^", "")
            if math.isclose(float(norm_ans), float(norm_user), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
        except: pass

    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", ans_display)}


from datetime import datetime
import base64
import re


# --- 輔助函式 (Helper Functions) ---
# 遵守規範 6: 必須回傳, 類型一致, 防洩漏原則
# 遵守規範 10: 數據禁絕常數, 隨機生成, 公式計算

def _generate_linear_equation_params():
    """
    [CRITICAL] 隨機生成二元一次方程式 Ax + By = C 的係數 A, B, C。
    確保 A 和 B 不會同時為零，以構成有效的二元一次方程式。
    回傳: tuple (A, B, C)
    """
    A = random.randint(-5, 5)
    B = random.randint(-5, 5)
    
    # 確保 A 和 B 不會同時為零，否則不是一個有效的「二元一次方程式」
    # (如果 A=0, B=0, 則為 0=C, 這不是方程式)
    while A == 0 and B == 0:
        A = random.randint(-5, 5)
        B = random.randint(-5, 5)

    C = random.randint(-10, 10)
    return A, B, C

def _render_equation_text(A, B, C, include_eq_sign=True):
    """
    [ELITE GUARDRAILS] 將係數 A, B, C 轉換為 LaTeX 格式的方程式字串 Ax + By = C。
    處理係數為 1 或 -1 及正負號，並嚴格使用 .replace 格式化。
    遵守規範 5: 排版與 LaTeX 安全 (嚴禁 f-string, 必須使用 .replace, 數學式 $...$)
    回傳: str
    """
    parts = []
    
    # Handle Ax part
    if A != 0:
        if A == 1:
            parts.append("x")
        elif A == -1:
            parts.append("-x")
        else:
            parts.append(str(A) + "x")

    # Handle By part
    if B != 0:
        if B > 0 and parts: # 如果前面有項，且 B 為正，則加 '+'
            parts.append("+")
        if B == 1:
            parts.append("y")
        elif B == -1:
            parts.append("-y")
        else:
            parts.append(str(B) + "y")
    
    # 根據 _generate_linear_equation_params 的邏輯，parts 不會為空。
    equation_lhs = "".join(parts)
    
    if include_eq_sign:
        # 嚴格使用 .replace 格式化 LaTeX 字串
        equation_str = r"${LHS} = {C}$".replace("{LHS}", equation_lhs).replace("{C}", str(C))
    else:
        # 如果不需要等號，通常用於表達式或方程式的左側部分
        equation_str = r"${LHS}$".replace("{LHS}", equation_lhs)
    
    return equation_str

def _generate_image_base64():
    """
    [GENERIC HELPER RULES] 視覺化函式佔位符。
    對於二元一次方程式，通常不需要複雜的幾何圖形。
    遵守規範 6: 必須回傳 (回傳空字串表示無圖形)
    回傳: str (Base64 編碼的圖片字串，如果沒有則為空字串)
    """
    # 對於此技能，假設不需要複雜的視覺化圖形。
    # 回傳空字串。
    return ""

# --- 題型實作 (Problem Type Implementations) ---
# 遵守規範 4: 題型鏡射 (隨機分流, 範例動態化)
# 遵守規範 9: 題目對應 (明確指出對應的 RAG 例題編號)

# Type 1 (Maps to Example 1): 從文字敘述列出二元一次方程式
def _generate_type1_problem():
    """
    [PROBLEM MIRRORING] 動態化 RAG 例題 1。
    生成一個文字問題，要求從中列出一個二元一次方程式。
    """
    item1_name = random.choice(["鋁罐", "寶特瓶", "彈珠糖", "牛奶糖", "蘋果", "橘子"])
    item2_name = random.choice(["寶特瓶", "鋁罐", "牛奶糖", "彈珠糖", "橘子", "蘋果"])
    while item1_name == item2_name: # 確保兩個物品不同
        item2_name = random.choice(["寶特瓶", "鋁罐", "牛奶糖", "彈珠糖", "橘子", "蘋果"])

    person_name = random.choice(["小盈", "巴奈", "小明", "阿華"])
    store_name = random.choice(["康康柑仔店", "幸福雜貨店", "大華超市"])

    # Scenario 1: Total quantity/weight
    total_qty = random.randint(5, 20)
    qty_unit = random.choice(["公斤", "個", "顆", "斤"])
    
    # Scenario 2: Total value/cost
    price1 = random.randint(1, 50)
    price2 = random.randint(1, 50)
    while price1 == price2: # 確保價格不同
        price2 = random.randint(1, 50)
    total_value = random.randint(50, 300)
    currency_unit = "元"

    # Define variables as per RAG Ex 1
    var_x = "x"
    var_y = "y"

    # Randomly choose which type of equation to ask for
    question_choice = random.choice(["quantity", "value"])

    # Base sentence structure with variables
    question_text_base = r"已知 {ITEM1} 每{QTY_UNIT_SINGLE} {PRICE1}{CURRENCY}，{ITEM2} 每{QTY_UNIT_SINGLE} {PRICE2}{CURRENCY}。若 {PERSON} 購買了 {ITEM1} {VAR_X}{QTY_UNIT}、{ITEM2} {VAR_Y}{QTY_UNIT}，則依題意列出二元一次方程式：" \
                         .replace("{ITEM1}", item1_name) \
                         .replace("{ITEM2}", item2_name) \
                         .replace("{QTY_UNIT_SINGLE}", qty_unit.replace("公斤", "公斤").replace("個", "個").replace("顆", "顆").replace("斤", "斤")) \
                         .replace("{PRICE1}", str(price1)) \
                         .replace("{PRICE2}", str(price2)) \
                         .replace("{CURRENCY}", currency_unit) \
                         .replace("{PERSON}", person_name) \
                         .replace("{VAR_X}", var_x) \
                         .replace("{VAR_Y}", var_y) \
                         .replace("{QTY_UNIT}", qty_unit)

    if question_choice == "quantity":
        # Ask for the total quantity equation
        question_text_condition = r" {ITEM1} 與 {ITEM2} 的總量共 {TOTAL_QTY}{QTY_UNIT}。"\
                                  .replace("{ITEM1}", item1_name) \
                                  .replace("{ITEM2}", item2_name) \
                                  .replace("{TOTAL_QTY}", str(total_qty)) \
                                  .replace("{QTY_UNIT}", qty_unit)
        
        A, B, C = 1, 1, total_qty
        correct_answer = _render_equation_text(A, B, C)

    else: # question_choice == "value"
        # Ask for the total value equation
        question_text_condition = r" {PERSON} 共消費了 {TOTAL_VALUE}{CURRENCY}。"\
                                  .replace("{PERSON}", person_name) \
                                  .replace("{TOTAL_VALUE}", str(total_value)) \
                                  .replace("{CURRENCY}", currency_unit)
        
        A, B, C = price1, price2, total_value
        correct_answer = _render_equation_text(A, B, C)
    
    question_text = question_text_base + question_text_condition

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer, # 顯示給使用者的答案與正確答案相同
        "image_base64": _generate_image_base64(),
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

# Type 2 (Maps to Example 2): 判斷給定的點是否為方程式的解
def _generate_type2_problem():
    """
    [PROBLEM MIRRORING] 動態化 RAG 例題 2。
    生成判斷給定 (x, y) 點是否為方程式解的問題。
    """
    A, B, C = _generate_linear_equation_params()
    
    # 隨機生成一個潛在的解 (x_val, y_val)
    x_val = random.randint(-5, 5)
    y_val = random.randint(-5, 5)
    
    # 計算 Ax + By 在 (x_val, y_val) 處的值
    test_C = A * x_val + B * y_val
    
    # 隨機決定該點是否為解
    is_solution = random.choice([True, False])
    
    if is_solution:
        # 如果是解，則方程式右側等於 test_C
        final_C = test_C
        correct_answer = "是"
    else:
        # 如果不是解，則方程式右側 C 必須不等於 test_C
        final_C = random.randint(-10, 10)
        while final_C == test_C: # 確保 C 與 test_C 不同
            final_C = random.randint(-10, 10)
        correct_answer = "否"
            
    equation_str = _render_equation_text(A, B, final_C)
    
    x_val_str = str(x_val)
    y_val_str = str(y_val)
    
    # 嚴格使用 .replace 格式化 LaTeX 字串
    question_text = r"判斷點 $({X}, {Y})$ 是否為二元一次方程式 ".replace("{X}", x_val_str).replace("{Y}", y_val_str) + equation_str + r" 的解？"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer,
        "image_base64": _generate_image_base64(),
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

# Type 3 (Maps to Example 3): 給定一個變數的值，求另一個變數的值
def _generate_type3_problem():
    """
    [PROBLEM MIRRORING] 動態化 RAG 例題 3 (找出二元一次方程式的解的子問題)。
    生成給定一個變數 (x 或 y) 的值，求解另一個變數的問題。
    """
    A, B, C = _generate_linear_equation_params()
    
    # 決定給定 x 求 y 還是給定 y 求 x
    # 確保不會導致除以零
    if A == 0: # 只有 By = C，必須解 y
        given_x = False
    elif B == 0: # 只有 Ax = C，必須解 x
        given_x = True
    else: # A, B 都不為零，隨機選擇
        given_x = random.choice([True, False])

    answer_val = None
    find_var = ""
    given_val_str = ""

    # This loop ensures we always get a solvable problem without division by zero for the target variable.
    # It might regenerate coefficients if the initial choice leads to an unsolvable case.
    attempts = 0
    while answer_val is None and attempts < 10:
        if given_x: # 給定 x，求 y。方程式為 Ax + By = C => By = C - Ax => y = (C - Ax) / B
            x_given = random.randint(-5, 5)
            if B == 0: # 如果 B 為零，則無法解 y。重新生成或切換。
                A, B, C = _generate_linear_equation_params() # 重新生成
                if B == 0: # 如果 B 仍然為 0，且 A 不為 0，則切換為給定 y 求 x
                    given_x = False
                    continue # 重新開始迴圈，走 'else' 分支
                elif A == 0: # 如果 A, B 都為 0 (不該發生)，重新生成
                    A, B, C = _generate_linear_equation_params()
                    continue
            
            if B != 0: # 確保 B 係數非零
                answer_val = Fraction(C - A * x_given, B)
                given_val_str = r"$x = {X}$".replace("{X}", str(x_given))
                find_var = "y"
            else: # Fallback if B somehow remains 0 and cannot switch.
                A, B, C = _generate_linear_equation_params()
                given_x = random.choice([True, False]) # Reset decision
                answer_val = None # Reset answer_val to retry
                
        else: # 給定 y，求 x。方程式為 Ax + By = C => Ax = C - By => x = (C - By) / A
            y_given = random.randint(-5, 5)
            if A == 0: # 如果 A 為零，則無法解 x。重新生成或切換。
                A, B, C = _generate_linear_equation_params() # 重新生成
                if A == 0: # 如果 A 仍然為 0，且 B 不為 0，則切換為給定 x 求 y
                    given_x = True
                    continue # 重新開始迴圈，走 'if' 分支
                elif B == 0: # 如果 A, B 都為 0 (不該發生)，重新生成
                    A, B, C = _generate_linear_equation_params()
                    continue

            if A != 0: # 確保 A 係數非零
                answer_val = Fraction(C - B * y_given, A)
                given_val_str = r"$y = {Y}$".replace("{Y}", str(y_given))
                find_var = "x"
            else: # Fallback if A somehow remains 0 and cannot switch.
                A, B, C = _generate_linear_equation_params()
                given_x = random.choice([True, False]) # Reset decision
                answer_val = None # Reset answer_val to retry
        attempts += 1
    
    # Fallback if after many attempts, still no valid problem (should be rare)
    if answer_val is None:
        # Provide a default valid problem
        A, B, C = 2, 1, 7
        x_given = 1
        answer_val = Fraction(7 - 2 * x_given, 1)
        given_val_str = r"$x = {X}$".replace("{X}", str(x_given))
        find_var = "y"

    equation_str = _render_equation_text(A, B, C)
    
    # 將答案格式化為整數或分數的 LaTeX 字串
    if answer_val.denominator == 1:
        answer_val_str = str(answer_val.numerator)
    else:
        # 嚴格使用 .replace 格式化 LaTeX 字串
        answer_val_str = r"\frac{{{NUM}}}{{{DEN}}}".replace("{NUM}", str(answer_val.numerator)).replace("{DEN}", str(answer_val.denominator))
            
    # 嚴格使用 .replace 格式化 LaTeX 字串
    correct_answer_text = r"${VAR} = {VAL}$".replace("{VAR}", find_var).replace("{VAL}", answer_val_str)

    question_text = r"若方程式為 " + equation_str + r"，且 " + given_val_str + r"，則 $" + find_var + r"$ 的值為何？"
    
    return {
        "question_text": question_text,
        "correct_answer": correct_answer_text,
        "answer": correct_answer_text,
        "image_base64": _generate_image_base64(),
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

# Type 4 (Maps to Example 4): 數數可能的買法 (非負整數解的數量)
def _generate_type4_problem():
    """
    [PROBLEM MIRRORING] 動態化 RAG 例題 4。
    生成一個文字問題，要求計算二元一次方程式的非負整數解的數量。
    """
    item1_name = random.choice(["彈珠糖", "鉛筆", "橡皮擦", "蘋果"])
    item2_name = random.choice(["牛奶糖", "原子筆", "立可白", "橘子"])
    while item1_name == item2_name:
        item2_name = random.choice(["牛奶糖", "原子筆", "立可白", "橘子"])

    person_name = random.choice(["小盈", "巴奈", "小華", "美玲"])
    store_name = random.choice(["康康柑仔店", "文具店", "水果攤"])

    # Coefficients (prices) must be positive integers
    # To ensure a reasonable number of solutions (not too many, not zero too often)
    A = random.randint(2, 10)
    B = random.randint(2, 10)
    
    # Total cost (C) must be large enough to have some solutions
    num_solutions = 0
    attempts = 0
    while num_solutions == 0 and attempts < 20: # Limit attempts to avoid infinite loop
        # Generate C such that it's likely to have solutions
        C = random.randint(max(A, B), max(A, B) * random.randint(5, 15))
        
        num_solutions = 0
        # Iterate x from 0 up to C/A (inclusive)
        for x_val in range(C // A + 1):
            remaining_C = C - A * x_val
            if remaining_C >= 0 and remaining_C % B == 0:
                # y_val = remaining_C // B  (this is a valid non-negative integer solution)
                num_solutions += 1
        attempts += 1
    
    # Fallback if after many attempts, still no valid problem (should be rare)
    if num_solutions == 0:
        A, B, C = 5, 3, 30 # RAG Ex 4 parameters
        num_solutions = 3 # Known answer
        item1_name, item2_name = "彈珠糖", "牛奶糖"
        person_name, store_name = "小盈", "康康柑仔店"


    question_text = r"{PERSON} 到 {STORE} 想買 {ITEM1} 及 {ITEM2} 兩種零食，已知 {ITEM1} 1 顆 {PRICE1} 元、{ITEM2} 1 顆 {PRICE2} 元，若他到此店共消費了 {TOTAL_COST} 元，且零食可只買一種，則他有幾種可能的買法？"\
                    .replace("{PERSON}", person_name)\
                    .replace("{STORE}", store_name)\
                    .replace("{ITEM1}", item1_name)\
                    .replace("{ITEM2}", item2_name)\
                    .replace("{PRICE1}", str(A))\
                    .replace("{PRICE2}", str(B))\
                    .replace("{TOTAL_COST}", str(C))

    correct_answer = str(num_solutions) + " 種" # Example: "3 種"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer,
        "image_base64": _generate_image_base64(),
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


# --- 頂層函式 (Top-level Functions) ---
# 遵守規範 3: 程式結構 (頂層函式, 自動重載)
# 遵守規範 7: 數據與欄位 (欄位鎖死, 時間戳記)

def generate(level=1):
    """
    [頂層函式] 生成二元一次方程式的 K12 數學題目。
    根據隨機選擇動態化 RAG 例題。
    Args:
        level (int): 題目難度等級 (目前未用於分流，但可於未來擴展)。
    回傳:
        dict: 包含題目細節的字典。
    """
    # [隨機分流] 使用 random.choice 選擇題型，明確對應 RAG 例題
    problem_type_selector = random.choice([
        "type1", # 對應 RAG 例題 1 (列出方程式)
        "type2", # 對應 RAG 例題 2 (判斷解)
        "type3", # 對應 RAG 例題 3 (求特定解)
        "type4"  # 對應 RAG 例題 4 (數非負整數解)
    ])

    if problem_type_selector == "type1":
        problem_data = _generate_type1_problem()
    elif problem_type_selector == "type2":
        problem_data = _generate_type2_problem()
    elif problem_type_selector == "type3":
        problem_data = _generate_type3_problem()
    elif problem_type_selector == "type4":
        problem_data = _generate_type4_problem()
    else:
        # 預設或錯誤處理，回退到一個基本題型
        problem_data = _generate_type2_problem()

    # [時間戳記] 更新時間戳記與版本
    problem_data["created_at"] = datetime.now().isoformat()
    problem_data["version"] = "1.0"

    # [欄位鎖死] 確保返回的字典只包含指定欄位
    return {
        "question_text": problem_data["question_text"],
        "correct_answer": problem_data["correct_answer"],
        "answer": problem_data["answer"],
        "image_base64": problem_data["image_base64"],
        "created_at": problem_data["created_at"],
        "version": problem_data["version"]
    }



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
