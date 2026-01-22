# ==============================================================================
# ID: jh_數學2上_TheQuadraticFormula
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 90.52s | RAG: 5 examples
# Created At: 2026-01-19 12:13:44
# Fix Status: [Repaired]
# Fixes: Regex=8, Logic=0
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
    # 隱藏刻度,僅保留 0
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
        # 雙向清理:剝除 LaTeX 符號與空格
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

# --- 輔助函式定義 (Helper Functions) ---
def _simplify_sqrt(n):
    """
    簡化平方根,例如 sqrt(12) -> 2sqrt(3)
    回傳 (係數, 根號內的值)
    """
    if n < 0:
        raise ValueError("Cannot simplify sqrt of negative number for real roots.")
    if n == 0:
        return 0, 1 # 0 * sqrt(1)

    factor = 1
    # 從 2 開始找平方因子
    i = 2
    while i * i <= n:
        if n % (i * i) == 0:
            factor *= i # 乘上找到的因子
            n //= (i * i) # 更新 n 為簡化後的根號內值
            i = 2 # 從頭開始檢查新的 n
        else:
            i += 1
    
    return factor, n # 例如 sqrt(12) -> (2, 3), sqrt(5) -> (1, 5)

def _simplify_fraction(numerator, denominator):
    """
    簡化分數
    回傳 (簡化後的分子, 簡化後的分母)
    """
    if denominator == 0:
        raise ZeroDivisionError("Denominator cannot be zero.")
    if numerator == 0:
        return 0, 1 # 0/X 簡化為 0/1
    
    gcd_val = math.gcd(abs(numerator), abs(denominator))
    simplified_num = numerator // gcd_val
    simplified_den = denominator // gcd_val
    
    # 確保分母為正數
    if simplified_den < 0:
        simplified_num *= -1
        simplified_den *= -1
        
    return simplified_num, simplified_den

def _format_fraction_display(numerator, denominator):
    """
    將分數格式化為顯示字串 (例如 "1/2" 或 "3")
    """
    s_num, s_den = _simplify_fraction(numerator, denominator)
    if s_den == 1:
        return str(s_num)
    else:
        return r"\frac{{{}}}{{{}}}".replace("{}", str(s_num)).replace("{}", str(s_den))

def _generate_quadratic_coefficients(discriminant_type="any", max_val_a=5, max_val_b=10, max_val_c=10):
    """
    [數據禁絕常數] 隨機生成 ax^2 + bx + c = 0 的係數 a, b, c
    根據判別式類型生成係數
    discriminant_type: "positive_rational" (D > 0, D為完全平方數),
                       "positive_irrational" (D > 0, D非完全平方數),
                       "zero" (D = 0),
                       "negative" (D < 0)
    """
    if discriminant_type == "zero":
        # 對於 D=0 的情況,從根反推係數以確保整數係數
        root_int = random.randint(-8, 8)
        a_prime = random.randint(-max_val_a, max_val_a)
        while a_prime == 0: a_prime = random.randint(-max_val_a, max_val_a)
        b_prime = -2 * a_prime * root_int
        c_prime = a_prime * root_int * root_int
        return a_prime, b_prime, c_prime
    
    while True:
        a = random.randint(-max_val_a, max_val_a)
        while a == 0:  # a 不能為 0
            a = random.randint(-max_val_a, max_val_a)

        b = random.randint(-max_val_b, max_val_b)
        c = random.randint(-max_val_c, max_val_c)

        discriminant = b*b - 4*a*c

        if discriminant_type == "positive_rational":
            if discriminant > 0: # 確保 D > 0 且為完全平方數
                sqrt_d = int(math.sqrt(discriminant))
                if sqrt_d * sqrt_d == discriminant:
                    return a, b, c
        elif discriminant_type == "positive_irrational":
            # 確保 D > 0 且 D 不是完全平方數 (D=1 是完全平方數,避免之)
            if discriminant > 0:
                sqrt_d = int(math.sqrt(discriminant))
                if sqrt_d * sqrt_d != discriminant:
                    return a, b, c
        elif discriminant_type == "negative":
            if discriminant < 0:
                return a, b, c

# --- 頂層函式定義 ---
# [程式結構] 嚴禁使用 class 封裝。必須直接定義 generate() 與 check() 於模組最外層
# [自動重載] 確保代碼不依賴全域狀態

def generate(level=1):
    """
    [題型鏡射] 根據 RAG 例題 (概念性對應) 隨機生成一元二次方程式公式解題目
    問題類型嚴格映射至 RAG 範例的數學模型
    - Type 1: RAG Ex 1 (b²-4ac＞0, 有理根)
    - Type 2: RAG Ex 4 (b²-4ac＞0, 無理根, 二次項係數可為負)
    - Type 3: RAG Ex 3 ⑴ (b²-4ac=0, 重根)
    - Type 4: RAG Ex 3 ⑵ (b²-4ac＜0, 無解)
    - Type 5: RAG Ex 5 (已知重根,求參數 m 及解)
    """
    problem_type = random.choice([1, 2, 3, 4, 5]) # 隨機分流至不同題型
    
    question_text = ""
    correct_answer = ""
    solution_text = ""
    
    # [CRITICAL RULE: Grade & Semantic Alignment]
    # 確保題目符合國二 (jh_數學2上) 程度,專注於公式解的應用
    # 嚴禁降級到國一內容

    if problem_type == 1:
        # Type 1 (Maps to RAG Ex 1): 直接應用公式解,結果為有理相異根
        a, b, c = _generate_quadratic_coefficients(discriminant_type="positive_rational", max_val_a=5, max_val_b=10, max_val_c=10)
        
        discriminant = b*b - 4*a*c
        sqrt_d = int(math.sqrt(discriminant))

        x1_num = -b + sqrt_d
        x1_den = 2 * a
        x2_num = -b - sqrt_d
        x2_den = 2 * a
        
        root1_display = _format_fraction_display(x1_num, x1_den)
        root2_display = _format_fraction_display(x2_num, x2_den)
        
        # 將根轉換為浮點數以便排序,確保 correct_answer 順序一致性
        roots_list = sorted([float(eval(root1_display.replace(r'\frac{','(').replace('}{','/').replace('}',''))),
                             float(eval(root2_display.replace(r'\frac{','(').replace('}{','/').replace('}','')))])
        
        # [CRITICAL RULE: Answer Data Purity]
        # correct_answer 必須是純數據,嚴禁 LaTeX、變數名稱、單位或說明文字
        correct_answer = f"{roots_list[0]}, {roots_list[1]}"
        
        # [排版與 LaTeX 安全] 嚴禁 f-string 結合 LaTeX,必須使用 .replace()
        question_text_template = r"請使用公式解法，解一元二次方程式 $A_val x^2 + B_val x + C_val = 0$。"
        question_text = question_text_template.replace("A_val", str(a)).replace("B_val", str(b)).replace("C_val", str(c))

        solution_text = f"方程式為 ${a}x^2 + {b}x + {c} = 0$\n"
        solution_text += f"套用公式解 $x = \\frac{{-b \\pm \\sqrt{{b^2 - 4ac}}}}{{2a}}$\n"
        solution_text += f"$x = \\frac{{-({b}) \\pm \\sqrt{{({b})^2 - 4({a})({c})}}}}{{2({a})}}$\n"
        solution_text += f"$x = \\frac{{{-b} \\pm \\sqrt{{{discriminant}}}}}{{{2*a}}}$\n"
        solution_text += f"$x = \\frac{{{-b} \\pm {sqrt_d}}}{{{2*a}}}$\n"
        solution_text += f"$x_1 = {root1_display}$, $x_2 = {root2_display}$"

    elif problem_type == 2:
        # Type 2 (Maps to RAG Ex 4): 直接應用公式解,結果為無理相異根。係數 a 可為負數
        a, b, c = _generate_quadratic_coefficients(discriminant_type="positive_irrational", max_val_a=5, max_val_b=10, max_val_c=10)

        discriminant = b*b - 4*a*c
        
        # 簡化 sqrt(discriminant),例如 sqrt(12) -> 2sqrt(3)
        sqrt_factor, sqrt_radicand = _simplify_sqrt(discriminant)

        common_den = 2 * a
        num_b = -b
        
        # correct_answer 格式: 數學表達式字串，例如 "(-3+2*sqrt(5))/4, (-3-2*sqrt(5))/4"
        # 允許 'sqrt' 作為函數名，Check 函式將負責解析
        root1_pure_data = f"({num_b}+{sqrt_factor}*sqrt({sqrt_radicand}))/{common_den}"
        root2_pure_data = f"({num_b}-{sqrt_factor}*sqrt({sqrt_radicand}))/{common_den}"
        
        # 為了確保 check 函式能夠正確比對,我們將其以逗號分隔
        correct_answer = f"{root1_pure_data},{root2_pure_data}"

        # 顯示用的 LaTeX 格式
        sqrt_term_display = ""
        if sqrt_factor == 1:
            sqrt_term_display = r"\sqrt{{{}}}".replace("{}", str(sqrt_radicand))
        else:
            sqrt_term_display = r"{}\sqrt{{{}}}".replace("{}", str(sqrt_factor)).replace("{}", str(sqrt_radicand))
        
        root1_display = r"\frac{{{num_b} + {sqrt_term}}}{{{common_den}}}".replace("{num_b}", str(num_b)).replace("{sqrt_term}", sqrt_term_display).replace("{common_den}", str(common_den))
        root2_display = r"\frac{{{num_b} - {sqrt_term}}}{{{common_den}}}".replace("{num_b}", str(num_b)).replace("{sqrt_term}", sqrt_term_display).replace("{common_den}", str(common_den))
        
        question_text_template = r"請使用公式解法，解一元二次方程式 $A_val x^2 + B_val x + C_val = 0$。"
        question_text = question_text_template.replace("A_val", str(a)).replace("B_val", str(b)).replace("C_val", str(c))

        solution_text = f"方程式為 ${a}x^2 + {b}x + {c} = 0$\n"
        solution_text += f"套用公式解 $x = \\frac{{-b \\pm \\sqrt{{b^2 - 4ac}}}}{{2a}}$\n"
        solution_text += f"$x = \\frac{{-({b}) \\pm \\sqrt{{({b})^2 - 4({a})({c})}}}}{{2({a})}}$\n"
        solution_text += f"$x = \\frac{{{-b} \\pm \\sqrt{{{discriminant}}}}}{{{2*a}}}$\n"
        solution_text += f"$x = \\frac{{{-b} \\pm {sqrt_term_display}}}{{{2*a}}}$\n"
        solution_text += f"$x_1 = {root1_display}$, $x_2 = {root2_display}$"

    elif problem_type == 3:
        # Type 3 (Maps to RAG Ex 3 ⑴): 重根 (判別式 D = 0)
        a, b, c = _generate_quadratic_coefficients(discriminant_type="zero", max_val_a=5, max_val_b=10, max_val_c=10)
        
        discriminant = b*b - 4*a*c # 應為 0
        
        single_root_num = -b
        single_root_den = 2 * a
        
        root_display = _format_fraction_display(single_root_num, single_root_den)
        correct_answer = f"{{float(eval(root_display.replace(r'\frac{{','(').replace('}}{{','/').replace('}}','')))}}" # 單一重根
        
        question_text_template = r"請使用公式解法，解一元二次方程式 $A_val x^2 + B_val x + C_val = 0$。"
        question_text = question_text_template.replace("A_val", str(a)).replace("B_val", str(b)).replace("C_val", str(c))

        solution_text = f"方程式為 ${a}x^2 + {b}x + {c} = 0$\n"
        solution_text += f"套用公式解 $x = \\frac{{-b \\pm \\sqrt{{b^2 - 4ac}}}}{{2a}}$\n"
        solution_text += f"$x = \\frac{{-({b}) \\pm \\sqrt{{({b})^2 - 4({a})({c})}}}}{{2({a})}}$\n"
        solution_text += f"$x = \\frac{{{-b} \\pm \\sqrt{{{discriminant}}}}}{{{2*a}}}$\n"
        solution_text += f"$x = \\frac{{{-b}}}{{{2*a}}} = {root_display}$ (重根)"

    elif problem_type == 4:
        # Type 4 (Maps to RAG Ex 3 ⑵): 無解 (判別式 D < 0)
        a, b, c = _generate_quadratic_coefficients(discriminant_type="negative", max_val_a=5, max_val_b=10, max_val_c=10)
        
        discriminant = b*b - 4*a*c
        
        correct_answer = "無解" # 依 RAG 例題 3 ⑵
        
        question_text_template = r"請使用公式解法，解一元二次方程式 $A_val x^2 + B_val x + C_val = 0$。"
        question_text = question_text_template.replace("A_val", str(a)).replace("B_val", str(b)).replace("C_val", str(c))

        solution_text = f"方程式為 ${a}x^2 + {b}x + {c} = 0$\n"
        solution_text += f"套用公式解 $x = \\frac{{-b \\pm \\sqrt{{b^2 - 4ac}}}}{{2a}}$\n"
        solution_text += f"$x = \\frac{{-({b}) \\pm \\sqrt{{({b})^2 - 4({a})({c})}}}}{{2({a})}}$\n"
        solution_text += f"$x = \\frac{{{-b} \\pm \\sqrt{{{discriminant}}}}}{{{2*a}}}$\n"
        solution_text += f"由於判別式 $b^2 - 4ac = {discriminant} < 0$，方程式沒有實數解，故為無解。"

    elif problem_type == 5:
        # Type 5 (Maps to RAG Ex 5): 已知方程式有重根,求參數 m 的值及此方程式的解
        # 遵循 RAG Ex 5 結構,設定 a=1
        a_val = 1
        
        # 隨機生成一個整數重根
        root_val = random.randint(-8, 8)
        
        # 根據 a=1 和重根計算 b 和目標 c
        b_coeff = -2 * a_val * root_val
        c_coeff_target = a_val * root_val * root_val # 這是使 D=0 的 c 值
        
        # 將參數 m 嵌入 c 中,例如 c = Km + C_fixed
        k_m = random.choice([2, 3, 4, 5]) # m 的係數
        
        # 確保 m 的答案為整數
        m_ans = random.randint(-5, 5)
        while m_ans == 0: # 避免 m=0
            m_ans = random.randint(-5, 5)
            
        c_fixed = c_coeff_target - (k_m * m_ans) # 計算常數項
        
        # 格式化方程式中的 b 項
        b_display = ""
        if b_coeff == 1: b_display = "x"
        elif b_coeff == -1: b_display = "-x"
        elif b_coeff != 0: b_display = f"{b_coeff}x"

        # 格式化方程式中的 c 項 (含 m)
        c_term_m_part = f"{k_m}m"
        c_term_fixed_part = ""
        if c_fixed != 0:
            if c_fixed > 0: c_term_fixed_part = f"+{c_fixed}"
            else: c_term_fixed_part = str(c_fixed)
        
        question_text_template = r"已知 x 的一元二次方程式 $x^2 {b_term} + ({c_m_part} {c_fixed_part})=0$ 有重根，求 $m$ 的值及此方程式的解。"
        question_text = question_text_template.replace("{b_term}", b_display).replace("{c_m_part}", c_term_m_part).replace("{c_fixed_part}", c_term_fixed_part)
        
        correct_answer = f"m={m_ans}, x={root_val}" # 依 RAG Ex 5 格式
        
        solution_text = f"方程式為 $x^2 {b_display} + ({k_m}m {c_fixed_part})=0$\n"
        solution_text += f"當方程式有重根時，判別式 $b^2 - 4ac = 0$\n"
        solution_text += f"在此方程式中， $a=1$, $b={b_coeff}$, $c=({k_m}m {c_fixed_part})$\n"
        
        c_display_for_calc = f"{k_m}m"
        if c_fixed > 0: c_display_for_calc += f"+{c_fixed}"
        elif c_fixed < 0: c_display_for_calc += f"{c_fixed}"

        solution_text += f"$({b_coeff})^2 - 4(1)({c_display_for_calc}) = 0$\n"
        solution_text += f"${b_coeff**2} - 4({c_display_for_calc}) = 0$\n"
        
        # 展開並簡化 m 的方程式
        expanded_term_m = 4 * k_m
        expanded_const_from_c = 4 * c_fixed # 這是 -4c 展開後,c 的常數部分
        
        solution_text += f"${b_coeff**2} - {expanded_term_m}m "
        if expanded_const_from_c > 0:
            solution_text += f"-{expanded_const_from_c} = 0$\n"
        elif expanded_const_from_c < 0:
            solution_text += f"+{abs(expanded_const_from_c)} = 0$\n"
        else:
            solution_text += f"= 0$\n"

        final_const_on_lhs = b_coeff**2 - expanded_const_from_c
        
        solution_text += f"${final_const_on_lhs} - {expanded_term_m}m = 0$\n"
        solution_text += f"${expanded_term_m}m = {final_const_on_lhs}$\n"
        solution_text += f"$m = \\frac{{final_const_on_lhs}}{{expanded_term_m}} = {m_ans}$\n"
        solution_text += f"將 $m={m_ans}$ 代回原方程式，得 $x^2 {b_display} + ({k_m}*{m_ans} {c_fixed_part})=0$\n"
        solution_text += f"$x^2 {b_display} + ({c_coeff_target})=0$\n"
        solution_text += f"解此方程式，得 $x = \\frac{{-({b_coeff})}}{{2(1)}} = {root_val}$ (重根)\n"
        solution_text += f"所以 $m={m_ans}$, $x={root_val}$ (重根)"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "solution_text": solution_text,
        "image_base64": None, # [幾何/圖形題的特殊規範] 此題型無需圖片
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    """
    [強韌閱卷邏輯 (Robust Check Logic)]
    對使用者輸入進行清洗,並支援多種數學格式的等價性判斷
    特別處理帶有 'sqrt' 的無理數表達式、無解、以及參數 m 和解 x 的情況
    """
    # [V13.6 API Hardened Spec] 逐字複製 4-line check logic
    # 1. 輸入清洗 (Input Sanitization): 移除 LaTeX 符號、變數前綴、所有空白字元
    user_answer_sanitized = str(user_answer).strip()
    user_answer_sanitized = re.sub(r'x\s*=|y\s*=|k\s*=|Ans:\s*', '', user_answer_sanitized, flags=re.IGNORECASE)
    user_answer_sanitized = user_answer_sanitized.replace('$', '').replace('\\', '').replace('{', '').replace('}', '').replace(' ', '')
    user_answer_sanitized = user_answer_sanitized.replace('重根', '') # 移除 "重根" 標記，不影響答案判斷
    
    correct_answer_sanitized = str(correct_answer).strip().replace(' ', '') # correct_answer 已是純數據格式，僅移除空白

    # 2. 特殊情況處理: "無解"
    if correct_answer_sanitized == "無解":
        return user_answer_sanitized.lower() == "無解" or user_answer_sanitized.lower() == "nosolution"

    # 3. 特殊情況處理: 參數 m 及解 x (如 RAG Ex 5)
    if correct_answer_sanitized.startswith("m="):
        # 預期格式: "m=val_m,x=val_x" (清洗後)
        # 使用者可能輸入 "m=val_m, x=val_x" 或 "x=val_x, m=val_m"
        user_parts = [p.strip() for p in user_answer_sanitized.split(',') if p.strip()]
        correct_parts = [p.strip() for p in correct_answer_sanitized.split(',') if p.strip()]

        user_m_str = next((p for p in user_parts if p.startswith('m=')), None)
        user_x_str = next((p for p in user_parts if p.startswith('x=')), None)
        correct_m_str = next((p for p in correct_parts if p.startswith('m=')), None)
        correct_x_str = next((p for p in correct_parts if p.startswith('x=')), None)

        if not (user_m_str and user_x_str and correct_m_str and correct_x_str):
            return False # 缺少必要部分

        try:
            user_m = float(user_m_str.split('=')[1])
            user_x = float(user_x_str.split('=')[1])
            correct_m = float(correct_m_str.split('=')[1])
            correct_x = float(correct_x_str.split('=')[1])

            tolerance = 1e-9
            return abs(user_m - correct_m) < tolerance and abs(user_x - correct_x) < tolerance
        except (ValueError, IndexError):
            return False

    # 4. 解析並評估數學表達式 (支援 sqrt)
    def evaluate_expression_robust(expr_str):
        """
        安全地評估數學表達式字串，支援 'sqrt' 函數
        """
        # 將 'sqrt' 替換為 'math.sqrt'
        expr_str = re.sub(r'sqrt\((.*?)\)', r'math.sqrt(\1)', expr_str, flags=re.IGNORECASE)
        
        try:
            # 使用 eval 搭配有限的命名空間,以提高安全性
            return eval(expr_str, {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
        except (SyntaxError, NameError, TypeError, ValueError):
            return None # 表示解析或評估失敗

    user_roots_str = [r.strip() for r in user_answer_sanitized.split(',') if r.strip()]
    correct_roots_str = [r.strip() for r in correct_answer_sanitized.split(',') if r.strip()]

    # 如果預期只有一個重根,但使用者提供了兩個相同的值,則視為正確
    if len(correct_roots_str) == 1 and len(user_roots_str) == 2:
        val1 = evaluate_expression_robust(user_roots_str[0])
        val2 = evaluate_expression_robust(user_roots_str[1])
        if val1 is not None and val2 is not None and abs(val1 - val2) < 1e-9:
            user_roots_str = [user_roots_str[0]] # 處理為單一根

    if len(user_roots_str) != len(correct_roots_str):
        return False
    
    # [V13.5 最終硬化規約]: 統一要求使用數字序列比對
    # 將所有根轉換為浮點數,以便進行數值比較
    user_evaluated_roots = []
    for root_str in user_roots_str:
        val = evaluate_expression_robust(root_str)
        if val is None:
            return False # 使用者輸入無法解析或評估
        user_evaluated_roots.append(val)
    
    correct_evaluated_roots = []
    for root_str in correct_roots_str:
        val = evaluate_expression_robust(root_str)
        if val is None:
            # correct_answer 應始終可解析,若失敗表示 generate() 有問題
            return False 
        correct_evaluated_roots.append(val)

    # 排序兩組根,以處理答案順序無關性
    user_evaluated_roots.sort()
    correct_evaluated_roots.sort()

    # 5. 數值比對 (考慮浮點數精度)
    tolerance = 1e-9 # 標準浮點數比較容許誤差
    
    if len(user_evaluated_roots) != len(correct_evaluated_roots):
        return False

    for u_root, c_root in zip(user_evaluated_roots, correct_evaluated_roots):
        if abs(u_root - c_root) > tolerance:
            return False
            
    return True

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
                # 僅針對「文字反斜線+n」進行物理換行替換,不進行全局編碼轉換
                import re
                # 解決 r-string 導致的 \n 問題
                res['question_text'] = re.sub(r'\n', '\n', res['question_text'])
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則:若答案包含複雜運算符號,強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            # [V13.1 修復] 移除 '(' 與 ','，允許座標與數列使用純文字輸入
            triggers = ['^', '/', '|', '[', '{', '\\']
            
            # [V11.1 Refined] 僅在題目尚未包含提示時注入,避免重複堆疊
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
