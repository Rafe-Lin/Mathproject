# ==============================================================================
# ID: jh_數學2上_SquareOfDifferenceFormula
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 61.39s | RAG: 2 examples
# Created At: 2026-01-18 13:49:00
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
 # For robust float comparison in check function

# --- 輔助函式 (Coder MUST implement and ensure robustness) ---

def _generate_coeffs():
    """
    生成用於 Type 1 (代數式展開) 的係數 a 和 b。
    - 確保 'a' 不為 0 以保留 x^2 項。
    - 係數應為 K12 學生可處理的小整數。
    """
    a = random.randint(2, 6) # x 的係數
    b = random.randint(1, 10) # 常數項
    return a, b

def _generate_numerical_base():
    """
    生成用於 Type 3 (數值計算) 的數字，並提供其公式顯示形式。
    回傳值: (實際數值, 公式顯示字串)。
    範例: (98, "100 - 2") 或 (19.9, "20 - 0.1")
    """
    choice = random.choice(['integer_near_hundred', 'decimal_near_integer'])
    if choice == 'integer_near_hundred':
        base = random.choice([100, 200, 300])
        adjustment = random.randint(1, 9)
        num = base - adjustment
        return num, f"{base} - {adjustment}"
    else: # decimal_near_integer
        base_int = random.randint(5, 20)
        # 確保 adjustment_dec 使 num_to_square 成為浮點數
        adjustment_dec = random.choice([0.1, 0.2, 0.3, 0.4, 0.5])
        num = base_int - adjustment_dec
        return num, f"{base_int} - {adjustment_dec}"


def _canonicalize_polynomial(expr_str):
    """
    此函式接收一個代數表達式字串 (例如: "9 - 6x + x^2", "x^2 - 6x + 9")，
    並回傳一個標準化的字串表示形式 (例如: "x^2-6x+9")。

    實作細節:
    1.  **輸入清洗**: 移除所有空白字元、LaTeX 符號 ($, \, {, }) 等，僅保留數學運算相關字符。
    2.  **解析項**: 將表達式解析為其組成項 (x^2 項、x 項、常數項)。
        *   範例: "x^2-6x+9" 應被解析為係數字典 {'x^2': 1, 'x': -6, 'const': 9}。
        *   處理隱式係數 (例如: 'x^2' 表示 1x^2, '-x' 表示 -1x)。
        *   正確處理正負號。
    3.  **標準化輸出**: 回傳一個一致的、標準化的字串表示形式。
        *   標準形式應為降冪排列 (例如: "Ax^2 + Bx + C")。
        *   為了內部比對的嚴格性，字串中不應包含多餘的空格 (例如: "x^2-6x+9")。
        *   即使係數為 0，也應考慮其在標準化過程中的處理，最終輸出只包含非零項。
        *   如果所有係數都為零，應回傳 "0"。
        *   範例:
            *   輸入: "x^2 - 6x + 9" -> 輸出: "x^2-6x+9"
            *   輸入: "9 + x^2 - 6x" -> 輸出: "x^2-6x+9"
            *   輸入: "4x^2 - 12x + 9" -> 輸出: "4x^2-12x+9"
    """
    coeffs = {'x^2': 0, 'x': 0, 'const': 0}
    
    # 1. 輸入清洗
    clean_expr = re.sub(r'[\s\$\{\}\\]', '', expr_str.lower())
    
    if not clean_expr:
        return "0"

    # Add a '+' at the beginning if the expression doesn't start with '+' or '-'
    if not clean_expr.startswith(('-', '+')):
        clean_expr = '+' + clean_expr

    # 2. 解析項
    # Use re.findall to get all terms with their signs
    terms = re.findall(r'([+-]?[^+-]+)', clean_expr)

    for term in terms:
        match_x2 = re.match(r'([+-]?\d*)x\^2', term)
        if match_x2:
            coeff_str = match_x2.group(1)
            if coeff_str == '+' or coeff_str == '':
                coeffs['x^2'] += 1
            elif coeff_str == '-':
                coeffs['x^2'] -= 1
            else:
                coeffs['x^2'] += int(coeff_str)
            continue

        match_x = re.match(r'([+-]?\d*)x', term)
        if match_x:
            coeff_str = match_x.group(1)
            if coeff_str == '+' or coeff_str == '':
                coeffs['x'] += 1
            elif coeff_str == '-':
                coeffs['x'] -= 1
            else:
                coeffs['x'] += int(coeff_str)
            continue

        match_const = re.match(r'([+-]?\d+)$', term)
        if match_const:
            coeffs['const'] += int(match_const.group(1))
            continue
    
    # 3. 標準化輸出
    canonical_parts = []
    
    # x^2 term
    if coeffs['x^2'] != 0:
        if coeffs['x^2'] == 1:
            canonical_parts.append("x^2")
        elif coeffs['x^2'] == -1:
            canonical_parts.append("-x^2")
        else:
            canonical_parts.append(f"{coeffs['x^2']}x^2")
            
    # x term
    if coeffs['x'] != 0:
        if coeffs['x'] > 0:
            if coeffs['x'] == 1:
                canonical_parts.append("+x")
            else:
                canonical_parts.append(f"+{coeffs['x']}x")
        else: # coeffs['x'] < 0
            if coeffs['x'] == -1:
                canonical_parts.append("-x")
            else:
                canonical_parts.append(f"{coeffs['x']}x")
                
    # Constant term
    if coeffs['const'] != 0:
        if coeffs['const'] > 0:
            canonical_parts.append(f"+{coeffs['const']}")
        else: # coeffs['const'] < 0
            canonical_parts.append(f"{coeffs['const']}")

    canonical_str = "".join(canonical_parts)
    
    # Remove leading '+' if it's the first character (e.g., "+x^2-6x+9" -> "x^2-6x+9")
    if canonical_str.startswith('+'):
        canonical_str = canonical_str[1:]
    
    # If all coefficients were zero
    if not canonical_str:
        return "0"
        
    return canonical_str.strip()


# 3. 頂層函式 `generate` 規範

def generate(level=1):
    problem_type = random.choice(['expand_algebraic', 'find_missing_term', 'numerical_calculation'])

    question_text = ""
    correct_answer = ""
    solution_text = ""
    image_base64 = "" # 無圖形題，設為空字串

    if problem_type == 'expand_algebraic':
        # Type 1 (Maps to RAG Example 1, 2, but based on Architect's description for algebraic expansion): 代數式展開
        a, b = _generate_coeffs()
        term_with_x_first = random.choice([True, False]) # (ax-b)^2 vs (b-ax)^2
        
        if term_with_x_first:
            # (ax - b)^2
            question_text_template = r"請展開 $({a}x - {b})^2$。"
            a_sq = a*a
            two_ab = 2*a*b
            b_sq = b*b
            
            correct_answer_raw = f"{a_sq}x^2 - {two_ab}x + {b_sq}"
            
            solution_text_template = r"根據差的平方公式 $(A-B)^2 = A^2 - 2AB + B^2$，" \
                                     r"原式為 $({a}x)^2 - 2({a}x)({b}) + ({b})^2 = {a_sq}x^2 - {two_ab}x + {b_sq}$。"
        else:
            # (b - ax)^2
            question_text_template = r"請展開 $({b} - {a}x)^2$。"
            b_sq = b*b
            two_ab = 2*a*b
            a_sq = a*a
            
            correct_answer_raw = f"{a_sq}x^2 - {two_ab}x + {b_sq}" 
            
            solution_text_template = r"根據差的平方公式 $(A-B)^2 = A^2 - 2AB + B^2$，" \
                                     r"原式為 $({b})^2 - 2({b})({a}x) + ({a}x)^2 = {b_sq} - {two_ab}x + {a_sq}x^2$。"
        
        question_text = question_text_template.replace("{a}", str(a)).replace("{b}", str(b))
        correct_answer = _canonicalize_polynomial(correct_answer_raw) # 確保 correct_answer 標準化
        solution_text = solution_text_template.replace("{a}", str(a)).replace("{b}", str(b))\
                                              .replace("{a_sq}", str(a_sq))\
                                              .replace("{two_ab}", str(two_ab))\
                                              .replace("{b_sq}", str(b_sq))

    elif problem_type == 'find_missing_term':
        # Type 2 (Maps to RAG Example 3, but based on Architect's description for missing term): 填補完全平方數中的缺失項
        sub_type = random.choice(['missing_constant', 'missing_middle_coeff'])

        if sub_type == 'missing_constant':
            # 給定 x^2 - Bx + ___，找出常數項
            b_val = random.randint(2, 10) * 2 # 確保 B 為偶數
            k = b_val // 2 # (x-k)^2 中的 k
            missing_term = k*k
            
            question_text_template = r"使 $x^2 - {b_val}x + \text{___}$ 成為完全平方數，空格中應填入何值？"
            correct_answer = str(missing_term) # 純數字
            solution_text_template = r"要使 $x^2 - {b_val}x + \text{___}$ 成為完全平方數，需要符合 $(x-k)^2 = x^2 - 2kx + k^2$ 的形式。" \
                                     r"因此，${b_val} = 2k$，所以 $k = {k}$。" \
                                     r"空格中應填入 $k^2 = {k}^2 = {missing_term}$。"
            
            question_text = question_text_template.replace("{b_val}", str(b_val))
            solution_text = solution_text_template.replace("{b_val}", str(b_val))\
                                                  .replace("{k}", str(k))\
                                                  .replace("{missing_term}", str(missing_term))
        else: # missing_middle_coeff
            # 給定 A^2x^2 - ___x + C^2，找出中間項係數
            a_val = random.randint(2, 5) # (Ax-C)^2 中的 A
            c_val = random.randint(1, 8) # (Ax-C)^2 中的 C
            
            a_sq = a_val * a_val
            c_sq = c_val * c_val
            missing_middle_term_coeff = 2 * a_val * c_val
            
            question_text_template = r"使 ${a_sq}x^2 - \text{___}x + {c_sq}$ 成為完全平方數，空格中應填入何值？"
            correct_answer = str(missing_middle_term_coeff) # 純數字
            solution_text_template = r"要使 ${a_sq}x^2 - \text{___}x + {c_sq}$ 成為完全平方數，需要符合 $(Ax-C)^2 = A^2x^2 - 2ACx + C^2$ 的形式。" \
                                     r"因此，${a_sq}x^2 = ({a_val}x)^2$，所以 $A = {a_val}$。" \
                                     r"${c_sq} = ({c_val})^2$，所以 $C = {c_val}$。" \
                                     r"空格中應填入 $2AC = 2 \times {a_val} \times {c_val} = {missing_middle_term_coeff}$。"

            question_text = question_text_template.replace("{a_sq}", str(a_sq))\
                                                  .replace("{c_sq}", str(c_sq))
            solution_text = solution_text_template.replace("{a_sq}", str(a_sq))\
                                                  .replace("{a_val}", str(a_val))\
                                                  .replace("{c_sq}", str(c_sq))\
                                                  .replace("{c_val}", str(c_val))\
                                                  .replace("{missing_middle_term_coeff}", str(missing_middle_term_coeff))

    else: # numerical_calculation
        # Type 3 (Maps to RAG Example 1, 2, 4, 5): 數值計算
        num_to_square, display_formula = _generate_numerical_base()
        
        actual_result = num_to_square * num_to_square
        
        question_text_template = r"請利用差的平方公式計算 $({num_display})^2$ 的值。"
        
        # 解析 display_formula 以用於 solution_text
        parts = display_formula.split(' - ')
        base_val_str = parts[0]
        adj_val_str = parts[1]
        
        try:
            base_val = int(base_val_str)
            adj_val = int(adj_val_str)
            is_int_calculation = True
        except ValueError:
            base_val = float(base_val_str)
            adj_val = float(adj_val_str)
            is_int_calculation = False

        base_val_sq = base_val * base_val
        two_ab = 2 * base_val * adj_val
        adj_val_sq = adj_val * adj_val
        
        if is_int_calculation:
            solution_text_template = r"根據差的平方公式 $(A-B)^2 = A^2 - 2AB + B^2$，" \
                                     r"原式為 $({base_val_str} - {adj_val_str})^2 = {base_val_str}^2 - 2 \times {base_val_str} \times {adj_val_str} + {adj_val_str}^2$" \
                                     r"$ = {base_val_sq} - {two_ab} + {adj_val_sq} = {actual_result}$。"
            solution_text = solution_text_template.replace("{base_val_str}", base_val_str)\
                                                  .replace("{adj_val_str}", adj_val_str)\
                                                  .replace("{base_val_sq}", str(int(base_val_sq)))\
                                                  .replace("{two_ab}", str(int(two_ab)))\
                                                  .replace("{adj_val_sq}", str(int(adj_val_sq)))\
                                                  .replace("{actual_result}", str(int(actual_result)))
            correct_answer = str(int(actual_result)) # 純數據，整數
        else:
            # 浮點數結果的格式化，確保精度
            def count_decimal_places(number):
                s = str(number)
                if '.' in s:
                    return len(s.split('.')[-1].rstrip('0')) # Remove trailing zeros for counting
                return 0

            # Find max decimal places among all numbers involved to ensure consistent formatting
            dec_places = [
                count_decimal_places(base_val),
                count_decimal_places(adj_val),
                count_decimal_places(base_val_sq),
                count_decimal_places(two_ab),
                count_decimal_places(adj_val_sq),
                count_decimal_places(actual_result)
            ]
            max_dec = max(dec_places + [2]) # Ensure at least 2 decimal places for results like 0.1 * 0.1 = 0.01
            
            solution_text_template = r"根據差的平方公式 $(A-B)^2 = A^2 - 2AB + B^2$，" \
                                     r"原式為 $({base_val_str} - {adj_val_str})^2 = {base_val_str}^2 - 2 \times {base_val_str} \times {adj_val_str} + {adj_val_str}^2$" \
                                     r"$ = {base_val_sq_fmt} - {two_ab_fmt} + {adj_val_sq_fmt} = {actual_result_fmt}$。"
            
            solution_text = solution_text_template.replace("{base_val_str}", base_val_str)\
                                                  .replace("{adj_val_str}", adj_val_str)\
                                                  .replace("{base_val_sq_fmt}", f"{base_val_sq:.{max_dec}f}")\
                                                  .replace("{two_ab_fmt}", f"{two_ab:.{max_dec}f}")\
                                                  .replace("{adj_val_sq_fmt}", f"{adj_val_sq:.{max_dec}f}")\
                                                  .replace("{actual_result_fmt}", f"{actual_result:.{max_dec}f}")
            correct_answer = f"{actual_result:.{max_dec}f}" # 純數據，格式化浮點數

        question_text = question_text_template.replace("{num_display}", display_formula)
        
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": solution_text, # `answer` 欄位用於顯示詳解
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.1" 
    }


# 4. 頂層函式 `check` 規範 (強韌閱卷邏輯)
# Adapting the "通用 Check 函式模板" from "系統底層鐵律" to be more robust for algebraic expressions.

    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean_input(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=, Ans: 等前綴
        s = s.replace("$", "").replace("\\", "").replace("{", "").replace("}", "")
        return s
    
    u = clean_input(user_answer)
    c = clean_input(correct_answer)
    
    # 判斷答案類型 (數值或代數式)
    # `correct_answer` 來自 `generate` 函式，已經過標準化。
    is_algebraic_correct = 'x' in c or '^' in c

    if is_algebraic_correct:
        # 代數式比對: 將用戶輸入標準化後與已標準化的正確答案比對
        try:
            canonical_u = _canonicalize_polynomial(u)
            # `correct_answer` 已經是 `_canonicalize_polynomial` 的結果
            return {"correct": canonical_u == c, "result": "正確！"}
        except Exception:
            # 解析或標準化失敗，則視為不正確的代數表達式。
            return {"correct": False, "result": "答案格式錯誤或代數表達式不正確。"}
    else:
        # 數值比對:
        # 支援浮點數等價性，使用容忍度進行比對。
        try:
            def parse_val(val_str):
                # 處理分數 (雖然本技能目前不產生分數答案，但通用性考慮)
                if "/" in val_str:
                    n, d = map(float, val_str.split("/"))
                    if d == 0: raise ValueError("Division by zero")
                    return n/d
                return float(val_str)
            
            user_num = parse_val(u)
            correct_num = parse_val(c)
            
            # 使用 math.isclose 進行浮點數比較，提供相對和絕對容忍度
            if math.isclose(user_num, correct_num, rel_tol=1e-5, abs_tol=1e-9):
                return {"correct": True, "result": "正確！"}
        except ValueError:
            # 無法轉換為數字，則視為不正確的數值輸入。
            pass
        
        # 降級為字串比對 (作為最終的保障，例如用戶輸入的數字格式非常特殊但字串完全匹配)
        if u == c: 
            return {"correct": True, "result": "正確！"}

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
