# ==============================================================================
# ID: jh_數學2上_BasicPropertiesOfRadicalOperations
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 113.66s | RAG: 5 examples
# Created At: 2026-01-18 20:51:52
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

# --- 輔助函式定義區 (Coder MUST implement these helper functions below) ---

def _find_largest_perfect_square_factor(n: int) -> int:
    """
    用途: 找出一個整數 `n` 的最大完全平方因數。
    輸入: n (int)
    輸出: 最大完全平方因數 (int)。例：_find_largest_perfect_square_factor(48) 應回傳 16。
    """
    if n < 1:
        return 1
    for i in range(int(math.sqrt(n)), 0, -1):
        if n % (i * i) == 0:
            return i * i
    return 1

def _simplify_radical(n: int) -> tuple[int, int]:
    """
    用途: 將 \sqrt{n} 簡化為 a\sqrt{b} 的形式。
    輸入: n (int)
    輸出: (a, b) (tuple of int)。例：_simplify_radical(48) 應回傳 (4, 3)。_simplify_radical(7) 應回傳 (1, 7)。
    防洩漏原則: 此函式僅接收題目已知數據 n。
    """
    if n < 0:
        raise ValueError("Radicand cannot be negative for real numbers.")
    if n == 0:
        return (0, 1) # sqrt(0) = 0
    
    perfect_square_factor = _find_largest_perfect_square_factor(n)
    coeff = int(math.sqrt(perfect_square_factor))
    radicand = n // perfect_square_factor
    return (coeff, radicand)

def _format_radical_expression(coeff_num: int, coeff_den: int, radicand: int) -> str:
    """
    用途: 將 (coeff_num/coeff_den, radicand) 格式化為 LaTeX 字符串，表示為 (coeff)\sqrt{radicand}。
    輸入: coeff_num (int), coeff_den (int), radicand (int)
    輸出: LaTeX 格式的根式字串 (str)。
    排版與 LaTeX 安全: 嚴格使用 .replace()。
    """
    if coeff_num == 0 or radicand == 0:
        return "0"
    
    # 簡化分數係數 coeff_num/coeff_den
    common_divisor = math.gcd(abs(coeff_num), abs(coeff_den))
    coeff_num //= common_divisor
    coeff_den //= common_divisor

    sign_str = ""
    if coeff_num < 0:
        sign_str = "-"
        coeff_num = abs(coeff_num) # 處理絕對值進行數字部分格式化
    
    # 處理 radicand == 1 的情況 (即結果為純數字)
    if radicand == 1:
        if coeff_den == 1:
            return sign_str + str(coeff_num)
        else:
            return sign_str + r"\frac{{{cn}}}{{{cd}}}".replace("{cn}", str(coeff_num)).replace("{cd}", str(coeff_den))
    
    # 處理根號部分的係數
    coeff_prefix = ""
    if coeff_num == 1:
        if coeff_den == 1:
            coeff_prefix = "" # 例如 \sqrt{R}
        else:
            coeff_prefix = r"\frac{1}{{{cd}}}".replace("{cd}", str(coeff_den)) # 例如 \frac{1}{2}\sqrt{R}
    else:
        if coeff_den == 1:
            coeff_prefix = str(coeff_num) # 例如 2\sqrt{R}
        else:
            coeff_prefix = r"\frac{{{cn}}}{{{cd}}}".replace("{cn}", str(coeff_num)).replace("{cd}", str(coeff_den)) # 例如 \frac{2}{3}\sqrt{R}
    
    if coeff_prefix == "": # 係數為 1/1 的情況
        return sign_str + r"\sqrt{{{r}}}".replace("{r}", str(radicand))
    else:
        return sign_str + coeff_prefix + r"\sqrt{{{r}}}".replace("{r}", str(radicand))

def _parse_number(num_str: str) -> float:
    """
    用途: 將數字字串（可為整數、小數、分數如 "1/2"）解析為浮點數。
    輸入: num_str (str)
    輸出: float。
    """
    if '/' in num_str:
        try:
            numerator, denominator = map(float, num_str.split('/'))
            if denominator == 0: raise ValueError("Denominator cannot be zero.")
            return numerator / denominator
        except ValueError:
            raise ValueError(f"Invalid fraction format: {num_str}")
    try:
        return float(num_str)
    except ValueError:
        raise ValueError(f"Invalid number format: {num_str}")

def _parse_radical_expression(expression_str: str) -> tuple:
    """
    用途: 將簡化後的根式表達式字串（如 "4,3" 或 "2/3,5" 或 "70"）解析為內部可比對的 tuple 結構。
    輸入: expression_str (str)
    輸出: (coeff, radicand) 或 (value)
    CRITICAL: 此函式專為 check 內部使用，處理 correct_answer 和解析後的 user_answer。
    """
    parts = expression_str.split(',')
    if len(parts) == 1:
        # Scalar number (e.g., "70", "1/3")
        return (_parse_number(parts[0]),)
    elif len(parts) == 2:
        # a,b for a*sqrt(b) (e.g., "4,3" for 4\sqrt{3}, "2/3,5" for (2/3)\sqrt{5})
        coeff = _parse_number(parts[0])
        radicand = _parse_number(parts[1]) # Radicand should be an integer, but parse as float for consistency
        if radicand < 0: raise ValueError("Radicand cannot be negative.")
        if radicand != int(radicand): raise ValueError("Radicand must be an integer.")
        return (coeff, int(radicand)) # Store radicand as int
    else:
        raise ValueError(f"Invalid radical expression format: {expression_str}")

def _compare_radical_expressions(user_parsed: tuple, correct_parsed: tuple) -> bool:
    """
    用途: 比較兩個解析後的根式 tuple 是否等價。
    輸入: user_parsed, correct_parsed (tuples)
    輸出: True 或 False。
    CRITICAL: 需處理不同形式的等價性。
    """
    if len(user_parsed) != len(correct_parsed):
        return False
    
    tolerance = 1e-9 # For floating point comparisons

    if len(user_parsed) == 1: # Scalar comparison
        return abs(user_parsed[0] - correct_parsed[0]) < tolerance
    elif len(user_parsed) == 2: # a*sqrt(b) comparison
        # Compare (coeff, radicand)
        # Handle cases like "1,1" (for 1) vs "1"
        if correct_parsed[1] == 1 and len(correct_parsed) == 2: # Correct is e.g., "5,1" which means 5
            return abs(user_parsed[0] * math.sqrt(user_parsed[1]) - correct_parsed[0]) < tolerance
        if user_parsed[1] == 1 and len(user_parsed) == 2: # User is e.g., "5,1" which means 5
            return abs(user_parsed[0] - correct_parsed[0] * math.sqrt(correct_parsed[1])) < tolerance

        return (abs(user_parsed[0] - correct_parsed[0]) < tolerance and
                abs(user_parsed[1] - correct_parsed[1]) < tolerance)
    return False


def generate(level: int = 1) -> dict:
    """
    根據難度等級生成 K12 國中二年級上學期「根式運算的基本性質」題目。
    """
    # 嚴格遵循 MANDATORY MIRRORING RULES: STRICT MAPPING to RAG Ex 1-5
    problem_type_choices = [
        "rag_ex1_2_coeff_radical_mult", # 數學模型對應 RAG Ex 1 & 2
        "rag_ex3_4_radical_radical_mult", # 數學模型對應 RAG Ex 3 & 4
        "rag_ex5_radical_division", # 數學模型對應 RAG Ex 5
    ]
    problem_type = random.choice(problem_type_choices)

    question_text = ""
    correct_answer = ""
    solution_text = ""
    image_base64 = None # 此技能不涉及圖形

    if problem_type == "rag_ex1_2_coeff_radical_mult":
        # 數學模型: (A * sqrt(R)) * B 或 A * (B * sqrt(R))
        # 其中 A, B 可以是整數或分數。R 是非完全平方數。
        
        radicand_val = random.choice([2, 3, 5, 7, 10, 11, 13, 14, 15, 17, 19])
        
        # 第一項: (coeff_rad_num / coeff_rad_den) * sqrt(radicand_val)
        coeff_rad_num = random.randint(1, 10) * random.choice([-1, 1])
        coeff_rad_den = random.choice([1, 2, 3, 4, 5])
        
        # 第二項: (coeff_other_num / coeff_other_den)
        coeff_other_num = random.randint(1, 10) * random.choice([-1, 1])
        coeff_other_den = random.choice([1, 2, 3, 4, 5])
        
        # 確保題目不至於過於簡單或無意義
        while (coeff_rad_num == 1 and coeff_rad_den == 1 and coeff_other_num == 1 and coeff_other_den == 1) or \
              (coeff_rad_num == 0 or coeff_other_num == 0):
            radicand_val = random.choice([2, 3, 5, 7, 10, 11, 13, 14, 15, 17, 19])
            coeff_rad_num = random.randint(1, 10) * random.choice([-1, 1])
            coeff_rad_den = random.choice([1, 2, 3, 4, 5])
            coeff_other_num = random.randint(1, 10) * random.choice([-1, 1])
            coeff_other_den = random.choice([1, 2, 3, 4, 5])

        # 計算最終係數 (分子/分母)
        final_coeff_num = coeff_rad_num * coeff_other_num
        final_coeff_den = coeff_rad_den * coeff_other_den

        # 簡化最終分數係數
        gcd_final = math.gcd(abs(final_coeff_num), abs(final_coeff_den))
        final_coeff_num //= gcd_final
        final_coeff_den //= gcd_final

        # 生成題目字串
        radical_term_str = _format_radical_expression(coeff_rad_num, coeff_rad_den, radicand_val)
        other_term_str = _format_radical_expression(coeff_other_num, coeff_other_den, 1) # 純係數，radicand為1
        
        # 隨機排列兩項
        if random.choice([True, False]):
            question_text = r"計算並化簡 $({other}) \times ({radical})$。" \
                            .replace("{other}", other_term_str).replace("{radical}", radical_term_str)
        else:
            question_text = r"計算並化簡 $({radical}) \times ({other})$。" \
                            .replace("{radical}", radical_term_str).replace("{other}", other_term_str)

        # 整理正確答案格式 (例如: "4,3" 或 "2/3,5")
        if final_coeff_den == 1:
            correct_answer = f"{final_coeff_num},{radicand_val}"
        else:
            correct_answer = f"{final_coeff_num}/{final_coeff_den},{radicand_val}"

        # 整理詳解字串
        solution_text = r"原式 = {q_text}".replace("{q_text}", question_text[question_text.find('$')+1:question_text.rfind('$')])
        solution_text += r" = $({cn1}/{cd1}) \times ({cn2}/{cd2})\sqrt{{{r}}}$".replace("{cn1}", str(coeff_rad_num)).replace("{cd1}", str(coeff_rad_den)).replace("{cn2}", str(coeff_other_num)).replace("{cd2}", str(coeff_other_den)).replace("{r}", str(radicand_val))
        solution_text += r" = $({fn_raw}/{fd_raw})\sqrt{{{r}}}$".replace("{fn_raw}", str(coeff_rad_num * coeff_other_num)).replace("{fd_raw}", str(coeff_rad_den * coeff_other_den)).replace("{r}", str(radicand_val))
        
        if gcd_final > 1:
            solution_text += r" = ${ans_latex}$".replace("{ans_latex}", _format_radical_expression(final_coeff_num, final_coeff_den, radicand_val))
        else:
            solution_text += r" = ${ans_latex}$".replace("{ans_latex}", _format_radical_expression(final_coeff_num, final_coeff_den, radicand_val))


    elif problem_type == "rag_ex3_4_radical_radical_mult":
        # 數學模型: (C1 * sqrt(R1)) * (C2 * sqrt(R2))
        # 其中 C1, C2 可以是整數或分數。R1, R2 是非完全平方數。
        
        radicand1 = random.choice([2, 3, 5, 7, 10, 11, 13])
        radicand2 = random.choice([2, 3, 5, 7, 10, 11, 13])
        
        coeff1_num = random.randint(1, 5) * random.choice([-1, 1])
        coeff1_den = random.choice([1, 2, 3])
        coeff2_num = random.randint(1, 5) * random.choice([-1, 1])
        coeff2_den = random.choice([1, 2, 3])

        # 確保題目有足夠的複雜度，避免過於簡單的結果
        while (coeff1_num == 1 and coeff1_den == 1 and coeff2_num == 1 and coeff2_den == 1) or \
              (coeff1_num == 0 or coeff2_num == 0) or \
              (_simplify_radical(radicand1 * radicand2)[0] == 1 and radicand1 * radicand2 < 20) or \
              (radicand1 == radicand2 and (coeff1_num * coeff2_num * radicand1) < 10): # 避免整數答案過小
            radicand1 = random.choice([2, 3, 5, 7, 10, 11, 13])
            radicand2 = random.choice([2, 3, 5, 7, 10, 11, 13])
            coeff1_num = random.randint(1, 5) * random.choice([-1, 1])
            coeff1_den = random.choice([1, 2, 3])
            coeff2_num = random.randint(1, 5) * random.choice([-1, 1])
            coeff2_den = random.choice([1, 2, 3])

        # 計算係數與根號部分的原始乘積
        product_coeff_num_raw = coeff1_num * coeff2_num
        product_coeff_den_raw = coeff1_den * coeff2_den
        product_radicand_raw = radicand1 * radicand2

        # 簡化根號部分
        simplified_rad_coeff, simplified_rad_val = _simplify_radical(product_radicand_raw)

        # 結合所有係數
        final_coeff_num = product_coeff_num_raw * simplified_rad_coeff
        final_coeff_den = product_coeff_den_raw
        
        # 簡化最終分數係數
        gcd_final = math.gcd(abs(final_coeff_num), abs(final_coeff_den))
        final_coeff_num //= gcd_final
        final_coeff_den //= gcd_final

        # 生成題目字串
        term1_str = _format_radical_expression(coeff1_num, coeff1_den, radicand1)
        term2_str = _format_radical_expression(coeff2_num, coeff2_den, radicand2)
        question_text = r"計算並化簡 $({t1}) \times ({t2})$。".replace("{t1}", term1_str).replace("{t2}", term2_str)

        # 整理正確答案格式
        if simplified_rad_val == 1: # 結果為純數字 (整數或分數)
            if final_coeff_den == 1:
                correct_answer = str(final_coeff_num)
            else:
                correct_answer = f"{final_coeff_num}/{final_coeff_den}"
        else: # 結果為根式
            if final_coeff_den == 1:
                correct_answer = f"{final_coeff_num},{simplified_rad_val}"
            else:
                correct_answer = f"{final_coeff_num}/{final_coeff_den},{simplified_rad_val}"

        # 整理詳解字串
        solution_text = r"原式 = {q_text}".replace("{q_text}", question_text[question_text.find('$')+1:question_text.rfind('$')])
        solution_text += r" = $({cn1}/{cd1} \times {cn2}/{cd2})\sqrt{{{r1} \times {r2}}}$".replace("{cn1}", str(coeff1_num)).replace("{cd1}", str(coeff1_den)).replace("{cn2}", str(coeff2_num)).replace("{cd2}", str(coeff2_den)).replace("{r1}", str(radicand1)).replace("{r2}", str(radicand2))
        solution_text += r" = $({pcn_raw}/{pcd_raw})\sqrt{{{pr_raw}}}$".replace("{pcn_raw}", str(product_coeff_num_raw)).replace("{pcd_raw}", str(product_coeff_den_raw)).replace("{pr_raw}", str(product_radicand_raw))
        
        if simplified_rad_coeff > 1:
            solution_text += r" = $({pcn_raw}/{pcd_raw}) \times {src}\sqrt{{{srv}}}$".replace("{pcn_raw}", str(product_coeff_num_raw)).replace("{pcd_raw}", str(product_coeff_den_raw)).replace("{src}", str(simplified_rad_coeff)).replace("{srv}", str(simplified_rad_val))
            solution_text += r" = $({fcn_raw_step}/{fcd_raw_step})\sqrt{{{srv}}}$".replace("{fcn_raw_step}", str(product_coeff_num_raw * simplified_rad_coeff)).replace("{fcd_raw_step}", str(product_coeff_den_raw)).replace("{srv}", str(simplified_rad_val))

        final_ans_str_solution = _format_radical_expression(final_coeff_num, final_coeff_den, simplified_rad_val)
        solution_text += r" = ${ans}$".replace("{ans}", final_ans_str_solution)


    elif problem_type == "rag_ex5_radical_division":
        # 數學模型: (C1 * sqrt(R1)) / (C2 * sqrt(R2)) 或 A / (B * sqrt(R))
        # 包含根號除法以及分母有理化。

        division_subtype = random.choice(["div_simple_radicands", "div_rationalize_denominator"])

        if division_subtype == "div_simple_radicands":
            # 模型: (C1 * sqrt(R1)) / (C2 * sqrt(R2))，其中 R1 % R2 == 0
            radicand2 = random.choice([2, 3, 5, 7, 10, 11, 13])
            radicand1_multiplier = random.choice([2, 3, 5, 7])
            radicand1 = radicand2 * radicand1_multiplier
            
            coeff1_num = random.randint(1, 10) * random.choice([-1, 1])
            coeff1_den = random.choice([1, 2, 3, 4])
            coeff2_num = random.randint(1, 10) * random.choice([-1, 1])
            coeff2_den = random.choice([1, 2, 3, 4])

            while coeff2_num == 0: # 除數係數不能為零
                coeff2_num = random.randint(1, 10) * random.choice([-1, 1])
            
            # 確保題目不至於過於簡單或無意義
            while (coeff1_num == coeff2_num and coeff1_den == coeff2_den and radicand1_multiplier == 1) or \
                  (coeff1_num == 0) or \
                  (radicand1_multiplier == 1 and (coeff1_num * coeff2_den) % (coeff1_den * coeff2_num) == 0 and (coeff1_num * coeff2_den) / (coeff1_den * coeff2_num) == 1):
                radicand2 = random.choice([2, 3, 5, 7, 10, 11, 13])
                radicand1_multiplier = random.choice([2, 3, 5, 7])
                radicand1 = radicand2 * radicand1_multiplier
                coeff1_num = random.randint(1, 10) * random.choice([-1, 1])
                coeff1_den = random.choice([1, 2, 3, 4])
                coeff2_num = random.randint(1, 10) * random.choice([-1, 1])
                coeff2_den = random.choice([1, 2, 3, 4])
                while coeff2_num == 0:
                    coeff2_num = random.randint(1, 10) * random.choice([-1, 1])

            # 計算原始商的係數與根號部分
            # (coeff1_num/coeff1_den) / (coeff2_num/coeff2_den) = (coeff1_num*coeff2_den) / (coeff1_den*coeff2_num)
            final_coeff_num_raw = coeff1_num * coeff2_den
            final_coeff_den_raw = coeff1_den * coeff2_num
            final_radicand_raw = radicand1 // radicand2

            # 簡化根號部分
            simplified_rad_coeff, simplified_rad_val = _simplify_radical(final_radicand_raw)

            # 結合所有係數
            final_coeff_num = final_coeff_num_raw * simplified_rad_coeff
            final_coeff_den = final_coeff_den_raw
            
            # 簡化最終分數係數
            gcd_final = math.gcd(abs(final_coeff_num), abs(final_coeff_den))
            final_coeff_num //= gcd_final
            final_coeff_den //= gcd_final

            # 生成題目字串
            term1_str = _format_radical_expression(coeff1_num, coeff1_den, radicand1)
            term2_str = _format_radical_expression(coeff2_num, coeff2_den, radicand2)
            question_text = r"計算並化簡 $({t1}) \div ({t2})$。".replace("{t1}", term1_str).replace("{t2}", term2_str)

            # 整理正確答案格式
            if simplified_rad_val == 1:
                if final_coeff_den == 1:
                    correct_answer = str(final_coeff_num)
                else:
                    correct_answer = f"{final_coeff_num}/{final_coeff_den}"
            else:
                if final_coeff_den == 1:
                    correct_answer = f"{final_coeff_num},{simplified_rad_val}"
                else:
                    correct_answer = f"{final_coeff_num}/{final_coeff_den},{simplified_rad_val}"

            # 整理詳解字串
            solution_text = r"原式 = {q_text}".replace("{q_text}", question_text[question_text.find('$')+1:question_text.rfind('$')])
            solution_text += r" = $({cn1}/{cd1} \div {cn2}/{cd2})\sqrt{{{r1} \div {r2}}}$".replace("{cn1}", str(coeff1_num)).replace("{cd1}", str(coeff1_den)).replace("{cn2}", str(coeff2_num)).replace("{cd2}", str(coeff2_den)).replace("{r1}", str(radicand1)).replace("{r2}", str(radicand2))
            solution_text += r" = $({cn1}/{cd1} \times {cd2}/{cn2})\sqrt{{{r1_div_r2}}}$".replace("{cn1}", str(coeff1_num)).replace("{cd1}", str(coeff1_den)).replace("{cn2}", str(coeff2_num)).replace("{cd2}", str(coeff2_den)).replace("{r1_div_r2}", str(radicand1 // radicand2))
            solution_text += r" = $({pcn_raw}/{pcd_raw})\sqrt{{{pr_raw}}}$".replace("{pcn_raw}", str(final_coeff_num_raw)).replace("{pcd_raw}", str(final_coeff_den_raw)).replace("{pr_raw}", str(final_radicand_raw))

            if simplified_rad_coeff > 1:
                solution_text += r" = $({pcn_raw}/{pcd_raw}) \times {src}\sqrt{{{srv}}}$".replace("{pcn_raw}", str(final_coeff_num_raw)).replace("{pcd_raw}", str(final_coeff_den_raw)).replace("{src}", str(simplified_rad_coeff)).replace("{srv}", str(simplified_rad_val))
                solution_text += r" = $({fcn_raw_step}/{fcd_raw_step})\sqrt{{{srv}}}$".replace("{fcn_raw_step}", str(final_coeff_num_raw * simplified_rad_coeff)).replace("{fcd_raw_step}", str(final_coeff_den_raw)).replace("{srv}", str(simplified_rad_val))

            final_ans_str_solution = _format_radical_expression(final_coeff_num, final_coeff_den, simplified_rad_val)
            solution_text += r" = ${ans}$".replace("{ans}", final_ans_str_solution)

        elif division_subtype == "div_rationalize_denominator":
            # 模型: A / (B * sqrt(R))，需要分母有理化
            numerator_val = random.randint(1, 15) * random.choice([-1, 1])
            denominator_coeff = random.randint(1, 5) * random.choice([-1, 1])
            denominator_radicand = random.choice([2, 3, 5, 7, 10, 11, 13])

            # 確保題目不至於過於簡單或無意義
            while (numerator_val == 0) or \
                  (denominator_coeff == 0) or \
                  (numerator_val % denominator_coeff == 0 and numerator_val / denominator_coeff == denominator_radicand) or \
                  (numerator_val % (denominator_coeff * denominator_radicand) == 0): # 避免結果是純整數
                numerator_val = random.randint(1, 15) * random.choice([-1, 1])
                denominator_coeff = random.randint(1, 5) * random.choice([-1, 1])
                denominator_radicand = random.choice([2, 3, 5, 7, 10, 11, 13])

            question_text = r"計算並化簡 $\frac{{{num}}}{{{den_coeff}}\sqrt{{{den_rad}}}}$。".replace("{num}", str(numerator_val)).replace("{den_coeff}", str(denominator_coeff)).replace("{den_rad}", str(denominator_radicand))

            # 有理化過程: 分子分母同乘以 sqrt(den_rad)
            # 分子變成: numerator_val * sqrt(den_rad)
            # 分母變成: denominator_coeff * den_rad
            
            final_num_coeff = numerator_val
            final_num_radicand = denominator_radicand
            final_den = denominator_coeff * denominator_radicand

            # 簡化最終係數 (final_num_coeff / final_den)
            gcd_final = math.gcd(abs(final_num_coeff), abs(final_den))
            final_coeff_num = final_num_coeff // gcd_final
            final_coeff_den = final_den // gcd_final

            # 整理正確答案格式
            if final_coeff_den == 1:
                correct_answer = f"{final_coeff_num},{final_num_radicand}"
            else:
                correct_answer = f"{final_coeff_num}/{final_coeff_den},{final_num_radicand}"

            # 整理詳解字串
            solution_text = r"原式 = $\frac{{{num_orig}}}{{{den_coeff_orig}}\sqrt{{{den_rad_orig}}}}$".replace("{num_orig}", str(numerator_val)).replace("{den_coeff_orig}", str(denominator_coeff)).replace("{den_rad_orig}", str(denominator_radicand))
            solution_text += r" = $\frac{{{num_orig}}\sqrt{{{den_rad_orig}}}}{{{den_coeff_orig}}\sqrt{{{den_rad_orig}}} \times \sqrt{{{den_rad_orig}}}}$".replace("{num_orig}", str(numerator_val)).replace("{den_coeff_orig}", str(denominator_coeff)).replace("{den_rad_orig}", str(denominator_radicand))
            solution_text += r" = $\frac{{{num_orig}}\sqrt{{{den_rad_orig}}}}{{{den_coeff_orig} \times {den_rad_orig}}}$".replace("{num_orig}", str(numerator_val)).replace("{den_coeff_orig}", str(denominator_coeff)).replace("{den_rad_orig}", str(denominator_radicand))
            solution_text += r" = $\frac{{{num_final_coeff}}\sqrt{{{num_final_radicand}}}}{{{den_final}}}$".replace("{num_final_coeff}", str(final_num_coeff)).replace("{num_final_radicand}", str(final_num_radicand)).replace("{den_final}", str(final_den))
            
            final_ans_str_solution = _format_radical_expression(final_coeff_num, final_coeff_den, final_num_radicand)
            solution_text += r" = ${ans}$".replace("{ans}", final_ans_str_solution)


    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "solution_text": solution_text,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

def check(user_answer: str, correct_answer: str) -> bool:
    """
    檢查使用者答案的正確性，支援多種格式和等價性。
    CRITICAL RULE: Robust Check Logic (強韌閱卷邏輯)
    1. Input Sanitization (輸入清洗):
       移除 LaTeX 符號 ($ \ { } ), 變數前綴 (x=, y=, k=, Ans:), 所有空白字元。
    2. Equivalence Checking (等價性檢查):
       根據 correct_answer 的格式判斷比較邏輯。
    """
    # 1. 輸入清洗 (Input Sanitization)
    cleaned_user_answer = re.sub(r'[\$\\\{\}xXyYkK=aAnNsS:]|\s+', '', user_answer).strip()
    cleaned_correct_answer = re.sub(r'[\$\\\{\}xXyYkK=aAnNsS:]|\s+', '', correct_answer).strip()

    # 2. 等價性檢查 (Equivalence Checking)
    try:
        if cleaned_correct_answer in [">", "<", "="]: # 比較符號類型 (此技能暫不生成此類，但保留檢查兼容性)
            return cleaned_user_answer == cleaned_correct_answer
        elif ',' in cleaned_correct_answer: # 根式表達式 (a,b 或 a/b,c)
            user_parsed = _parse_radical_expression(cleaned_user_answer)
            correct_parsed = _parse_radical_expression(cleaned_correct_answer)
            return _compare_radical_expressions(user_parsed, correct_parsed)
        else: # 純數字 (整數、小數、分數)
            user_num = _parse_number(cleaned_user_answer)
            correct_num = _parse_number(cleaned_correct_answer)
            return abs(user_num - correct_num) < 1e-9 # 浮點數比較容忍度
    except ValueError:
        return False # 解析失敗視為錯誤答案
    except Exception as e:
        # Log unexpected errors for debugging
        print(f"An unexpected error occurred during check: {e}")
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
