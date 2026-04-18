# ==============================================================================
# ID: jh_數學2上_FactorizationByMultiplicationFormulas
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 88.50s | RAG: 4 examples
# Created At: 2026-01-19 10:40:43
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
 # Included for adherence to the universal check template's imports, though not directly used in this specific check logic.

# --- Helper functions for check() ---
def _parse_single_factor_to_tuple(factor_str: str) -> tuple[int, int]:
    """
    將單個因式字串解析為規範化的 (x項係數, 常數項) 元組。
    處理 'x', '-x', '3x', 'x+3', '3+x', '-x+3', '4' 等格式。
    """
    factor_str = factor_str.replace(' ', '').strip()
    coeff_x = 0
    const_term = 0

    if not factor_str:
        return (0, 0)

    # 嘗試將其解析為一個簡單的整數常數（例如 '4'）
    try:
        const_term = int(factor_str)
        return (0, const_term)
    except ValueError:
        pass # 如果不是簡單的常數，則繼續解析包含 'x' 的項

    # 處理包含 'x' 的項
    # 匹配係數，包括正負號和省略的 '1'
    x_match = re.search(r'([+-]?\d*)x', factor_str)
    if x_match:
        coeff_str = x_match.group(1)
        if coeff_str == '': # 匹配 'x'，係數為 1
            coeff_x = 1
        elif coeff_str == '-': # 匹配 '-x'，係數為 -1
            coeff_x = -1
        else: # 匹配 '2x', '-3x'
            try:
                coeff_x = int(coeff_str)
            except ValueError:
                # 如果正則表達式匹配錯誤，這不應該發生
                pass 
        
        # 移除 x 項後，尋找剩餘的常數項
        remaining_str = re.sub(r'([+-]?\d*)x', '', factor_str)
        if remaining_str:
            try:
                const_term = int(remaining_str)
            except ValueError:
                # 常數部分格式錯誤
                pass
    # 如果沒有匹配到 'x' 項，且之前也不是簡單的整數，則可能是格式錯誤的因式，或其係數和常數都為 0 (已初始化)

    return (coeff_x, const_term)

def _parse_factors_for_comparison(input_str: str) -> list[tuple[int, int]]:
    """
    將完整的答案字串（可能包含多個因式）解析為排序過的規範化因式元組列表。
    處理 'x+3, x-3', '(x+3)(x-3)', '2(x+3)(x+3)', '(x+3)^2' 等格式。
    """
    input_str = input_str.strip()
    
    # 將 (X)^2 展開為 (X)(X) 以處理完全平方項
    input_str = re.sub(r'\(([^)]+)\)\^2', r'(\1)(\1)', input_str)

    # 將 ')(' 或 ') (' 替換為 ',' 以便分割因式
    cleaned_str = re.sub(r'\)\s*\(', ',', input_str)
    cleaned_str = re.sub(r'\)\(', ',', cleaned_str) # 處理沒有空格的情況

    # 移除可能存在的外部括號 (例如 "(A,B,C)" -> "A,B,C")
    cleaned_str = re.sub(r'^\(|\)$', '', cleaned_str)
    
    # 使用逗號 ',' 分割字串，得到單個因式字串列表
    raw_factors = [f.strip() for f in cleaned_str.split(',') if f.strip()]
    
    canonical_tuples = []
    for factor_str in raw_factors:
        # 檢查是否有前導常數因式，例如 '2(x+3)'
        match_leading_const = re.match(r'(\d+)\((.+)\)', factor_str)
        if match_leading_const:
            const_val = int(match_leading_const.group(1))
            inner_factor_str = match_leading_const.group(2)
            # 將常數作為一個獨立的因式加入
            canonical_tuples.append(_parse_single_factor_to_tuple(str(const_val)))
            # 解析括號內的因式
            canonical_tuples.append(_parse_single_factor_to_tuple(inner_factor_str))
        else:
            canonical_tuples.append(_parse_single_factor_to_tuple(factor_str))
    
    # 對規範化後的元組列表進行排序，以確保因式順序不影響比對結果
    # 排序優先依據 x 項係數，其次是常數項
    canonical_tuples.sort() 
    return canonical_tuples

# --- Top-level functions ---

def generate(level: int) -> dict:
    # 題型名稱依照「ARCHITECT'S SPECIFICATION」定義，
    # 但其中 Type 1-4 的具體數學模型實作，嚴格遵循「MANDATORY MIRRORING RULES」
    # 對 RAG Ex 1-4 的要求，覆蓋了 Spec 中可能存在的衝突描述。
    problem_type = random.choice([
        "difference_of_squares", # 邏輯實作 RAG Ex 1 模型: (ax)^2 - b^2
        "perfect_square_trinomial_plus", # 邏輯實作 RAG Ex 2 模型: (Ax+B)^2 - C^2
        "perfect_square_trinomial_minus", # 邏輯實作 RAG Ex 3 模型: x^2 + 2bx + b^2
        "difference_of_squares_with_coefficient", # 邏輯實作 RAG Ex 4 模型: x^2 - 2bx + b^2
        
        # 剩餘的 Architect's Spec 題型 (Type 5-9)，其描述與實作一致
        "perfect_square_trinomial_plus_with_coefficient",
        "perfect_square_trinomial_minus_with_coefficient",
        "common_factor_then_difference_of_squares",
        "common_factor_then_perfect_square_trinomial_plus",
        "common_factor_then_perfect_square_trinomial_minus",
    ])

    question_text = ""
    correct_answer = ""
    image_base64 = None # 本技能不涉及圖形繪製

    # [CRITICAL RULE: Data Prohibition] - 所有數字均由 random.randint 生成
    # [CRITICAL RULE: Grade & Semantic Alignment] - 嚴格遵循國中二年級上學期利用乘法公式進行因式分解的題型

    if problem_type == "difference_of_squares":
        # Architect's Spec Type 1 (描述: x^2 - b^2)
        # MANDATORY MIRRORING: 必須使用 RAG Ex 1 的數學模型: (ax)^2 - b^2 (例如: 9x^2 - 16)
        a_val = random.randint(2, 5) # x 的係數
        b_val = random.randint(2, 7) # 常數項
        a_squared = a_val * a_val
        b_squared = b_val * b_val
        expr_template = r"因式分解 ${a_squared}x^2 - {b_squared}$。"
        question_text = expr_template.replace("{a_squared}", str(a_squared)).replace("{b_squared}", str(b_squared))
        correct_answer = f"{a_val}x+{b_val}, {a_val}x-{b_val}"

    elif problem_type == "perfect_square_trinomial_plus":
        # Architect's Spec Type 2 (描述: x^2 + 2bx + b^2)
        # MANDATORY MIRRORING: 必須使用 RAG Ex 2 的數學模型: (Ax+B)^2 - C^2 (例如: (2x+1)^2 - 36)
        A_val = random.randint(2, 4) # 二項式內部 x 的係數
        B_val = random.randint(1, 5) # 二項式內部的常數項
        C_val = random.randint(2, 7) # 被減去的平方項的常數
        
        # 題目格式: (Ax+B)^2 - C^2
        expr_template = r"因式分解 $({A_val}x+{B_val})^2 - {C_squared}$。"
        question_text = expr_template.replace("{A_val}", str(A_val)).replace("{B_val}", str(B_val)).replace("{C_squared}", str(C_val * C_val))
        
        # 因式: (Ax+B+C)(Ax+B-C)
        factor1_const = B_val + C_val
        factor2_const = B_val - C_val
        correct_answer = f"{A_val}x+{factor1_const}, {A_val}x+{factor2_const}"

    elif problem_type == "perfect_square_trinomial_minus":
        # Architect's Spec Type 3 (描述: x^2 - 2bx + b^2)
        # MANDATORY MIRRORING: 必須使用 RAG Ex 3 的數學模型: x^2 + 2bx + b^2 (例如: x^2 + 6x + 9)
        b_val = random.randint(2, 7)
        b_squared = b_val * b_val
        two_b = 2 * b_val
        expr_template = r"因式分解 $x^2 + {two_b}x + {b_squared}$。"
        question_text = expr_template.replace("{two_b}", str(two_b)).replace("{b_squared}", str(b_squared))
        correct_answer = f"x+{b_val}, x+{b_val}"

    elif problem_type == "difference_of_squares_with_coefficient":
        # Architect's Spec Type 4 (描述: (ax)^2 - b^2)
        # MANDATORY MIRRORING: 必須使用 RAG Ex 4 的數學模型: x^2 - 2bx + b^2 (例如: x^2 - 12x + 36)
        b_val = random.randint(2, 7)
        b_squared = b_val * b_val
        two_b = 2 * b_val
        expr_template = r"因式分解 $x^2 - {two_b}x + {b_squared}$。"
        question_text = expr_template.replace("{two_b}", str(two_b)).replace("{b_squared}", str(b_squared))
        correct_answer = f"x-{b_val}, x-{b_val}"

    elif problem_type == "perfect_square_trinomial_plus_with_coefficient":
        # Architect's Spec Type 5: (ax)^2 + 2(ax)(b) + b^2
        a_val = random.randint(2, 4)
        b_val = random.randint(2, 6)
        a_squared = a_val * a_val
        b_squared = b_val * b_val
        two_ab = 2 * a_val * b_val
        expr_template = r"因式分解 ${a_squared}x^2 + {two_ab}x + {b_squared}$。"
        question_text = expr_template.replace("{a_squared}", str(a_squared)).replace("{two_ab}", str(two_ab)).replace("{b_squared}", str(b_squared))
        correct_answer = f"{a_val}x+{b_val}, {a_val}x+{b_val}"

    elif problem_type == "perfect_square_trinomial_minus_with_coefficient":
        # Architect's Spec Type 6: (ax)^2 - 2(ax)(b) + b^2
        a_val = random.randint(2, 4)
        b_val = random.randint(2, 6)
        a_squared = a_val * a_val
        b_squared = b_val * b_val
        two_ab = 2 * a_val * b_val
        expr_template = r"因式分解 ${a_squared}x^2 - {two_ab}x + {b_squared}$。"
        question_text = expr_template.replace("{a_squared}", str(a_squared)).replace("{two_ab}", str(two_ab)).replace("{b_squared}", str(b_squared))
        correct_answer = f"{a_val}x-{b_val}, {a_val}x-{b_val}"

    elif problem_type == "common_factor_then_difference_of_squares":
        # Architect's Spec Type 7: k(x^2 - b^2)
        k_val = random.randint(2, 5)
        b_val = random.randint(2, 5)
        b_squared = b_val * b_val
        expr_x_squared_coeff = k_val
        expr_b_squared_term = k_val * b_squared
        expr_template = r"因式分解 ${expr_x_squared_coeff}x^2 - {expr_b_squared_term}$。"
        question_text = expr_template.replace("{expr_x_squared_coeff}", str(expr_x_squared_coeff)).replace("{expr_b_squared_term}", str(expr_b_squared_term))
        correct_answer = f"{k_val}, x+{b_val}, x-{b_val}"

    elif problem_type == "common_factor_then_perfect_square_trinomial_plus":
        # Architect's Spec Type 8: k(x^2 + 2bx + b^2)
        k_val = random.randint(2, 5)
        b_val = random.randint(2, 5)
        b_squared = b_val * b_val
        two_b = 2 * b_val
        term_x_squared = k_val
        term_x = k_val * two_b
        term_const = k_val * b_squared
        expr_template = r"因式分解 ${term_x_squared}x^2 + {term_x}x + {term_const}$。"
        question_text = expr_template.replace("{term_x_squared}", str(term_x_squared)).replace("{term_x}", str(term_x)).replace("{term_const}", str(term_const))
        correct_answer = f"{k_val}, x+{b_val}, x+{b_val}"

    elif problem_type == "common_factor_then_perfect_square_trinomial_minus":
        # Architect's Spec Type 9: k(x^2 - 2bx + b^2)
        k_val = random.randint(2, 5)
        b_val = random.randint(2, 5)
        b_squared = b_val * b_val
        two_b = 2 * b_val
        term_x_squared = k_val
        term_x = k_val * two_b
        term_const = k_val * b_squared
        expr_template = r"因式分解 ${term_x_squared}x^2 - {term_x}x + {term_const}$。"
        question_text = expr_template.replace("{term_x_squared}", str(term_x_squared)).replace("{term_x}", str(term_x)).replace("{term_const}", str(term_const))
        correct_answer = f"{k_val}, x-{b_val}, x-{b_val}"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer, # 依據規範，此欄位與 correct_answer 相同
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

def check(user_answer: str, correct_answer: str) -> dict:
    # [強韌閱卷邏輯 (Robust Check Logic)]
    # 1. 輸入清洗 (Input Sanitization):
    #    使用 Regex 自動移除使用者輸入中的 LaTeX 符號、變數前綴和所有空白字元。
    sanitized_user_answer = re.sub(r'[$\\\{\}]', '', user_answer) # 移除 LaTeX 符號
    sanitized_user_answer = re.sub(r'(x|y|k|Ans):', '', sanitized_user_answer, flags=re.IGNORECASE) # 移除變數前綴
    sanitized_user_answer = re.sub(r'\s+', '', sanitized_user_answer) # 移除所有空白字元

    # 2. 規範化因式列表 (Canonicalize Factors):
    #    呼叫 _parse_factors_for_comparison 輔助函式，將正確答案和使用者答案都轉換為
    #    排序過的規範化 (x項係數, 常數項) 元組列表。這能確保因式順序和內部項順序不影響比對。
    expected_factors_canonical = _parse_factors_for_comparison(correct_answer)
    user_factors_canonical = _parse_factors_for_comparison(sanitized_user_answer)
    
    # 3. 比對規範化列表:
    #    直接比對兩個規範化後的列表是否完全一致。
    is_correct = (expected_factors_canonical == user_factors_canonical)
    
    # 依據「系統底層鐵律 (不可違背)」中的通用 Check 函式模板，返回字典格式
    if is_correct:
        return {"correct": True, "result": "正確！"}
    else:
        return {"correct": False, "result": "答案錯誤。"}


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
