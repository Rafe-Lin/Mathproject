# ==============================================================================
# ID: jh_數學2上_FactorizationByTakingCommonFactors
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 107.90s | RAG: 2 examples
# Created At: 2026-01-19 10:37:05
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
import re
from collections import defaultdict

# --- Helper Functions (輔助函式) ---

def _generate_coefficient(include_one=True, non_zero=True, max_abs_val=9):
    """
    功能: 生成隨機整數係數。
    參數:
        include_one: 布林值，若為 True 則可能生成 1 或 -1。
        non_zero: 布林值，若為 True 則不生成 0。
        max_abs_val: int，生成係數的絕對值上限。
    回傳: int 型態的係數。
    """
    val = random.randint(-max_abs_val, max_abs_val)
    if non_zero:
        while val == 0:
            val = random.randint(-max_abs_val, max_abs_val)
    if not include_one and abs(val) == 1:
        while abs(val) == 1 or val == 0:
            val = random.randint(-max_abs_val, max_abs_val)
    return val

def _format_term(coefficient, variable, exponent=1):
    """
    功能: 將係數、變數和指數組合成多項式項的字串表示，嚴格遵守 LaTeX 安全規範。
    參數:
        coefficient: int 型態的係數。
        variable: str 型態的變數名稱 (e.g., 'x', 'y')。
        exponent: int 型態的指數。
    回傳: str 型態的項 (e.g., "3x", "-x^2", "5")。
    """
    if coefficient == 0:
        return ""
    
    coeff_str = ""
    # 處理係數為 1 或 -1 的隱藏表示
    if coefficient == 1 and variable:
        coeff_str = ""
    elif coefficient == -1 and variable:
        coeff_str = "-"
    else:
        coeff_str = str(coefficient)
    
    var_str = ""
    if variable:
        if exponent == 1:
            var_str = variable
        elif exponent > 1:
            # 嚴格遵循 LaTeX 安全規範，使用 .replace 避免 f-string 與 LaTeX 大括號衝突
            template = r"{v}^{{{e}}}"
            var_str = template.replace("{v}", variable).replace("{{{e}}}", str(exponent))
    
    # 避免 f-string 進行最終組合，直接使用字串拼接
    return coeff_str + var_str

def _format_polynomial(terms):
    """
    功能: 將多項式項的列表組合成完整的 LaTeX 多項式字串。
    參數: terms: list of str (由 _format_term 生成的項)。
    回傳: str 型態的多項式字串 (e.g., "$3x^2 - 5x + 2$")。
    """
    filtered_terms = [t for t in terms if t] # 移除空字串
    if not filtered_terms:
        return "0" 
    
    result = filtered_terms[0]
    for i in range(1, len(filtered_terms)):
        term = filtered_terms[i]
        if term.startswith('-'):
            result += term
        else:
            result += "+" + term
    return result

def _assemble_multi_var_term(coeff_val, var1, exp1, var2, exp2):
    """
    輔助函式: 組合多變數的單項字串，確保變數按字母順序排列。
    例如: _assemble_multi_var_term(3, 'y', 2, 'x', 1) -> "3xy^2"
    """
    if coeff_val == 0:
        return ""

    term_parts = []
    
    # Handle coefficient
    if abs(coeff_val) != 1 or (exp1 == 0 and exp2 == 0): # If constant, or coeff is not +/-1
        term_parts.append(str(coeff_val))
    elif coeff_val == -1: # If -1 and there are variables
        term_parts.append("-")
    # If coeff_val is 1 and there are variables, no coeff_str is added.

    # Handle variables, ensuring canonical order (e.g., x before y)
    var_list = []
    if exp1 > 0: var_list.append((var1, exp1))
    if exp2 > 0: var_list.append((var2, exp2))

    # Sort variables alphabetically
    for var, exp in sorted(var_list, key=lambda p: p[0]):
        term_parts.append(var)
        if exp > 1:
            template = r"^{{{e}}}"
            term_parts.append(template.replace("{{{e}}}", str(exp)))
    
    return "".join(term_parts)


# --- generate() 函式主體 ---

def generate(level=1):
    """
    根據 level 參數生成因式分解題目。
    """
    problem_type = random.choice([1, 2, 3, 4]) # 隨機選擇題型
    
    question_text = ""
    correct_answer = ""
    
    if problem_type == 1: # Type 1: 提取單項公因式 (常數/變數/兩者) - 鏡射 RAG Ex 1 ⑴, ⑵
        subtype = random.choice([1, 2, 3])
        
        if subtype == 1: # Subtype 1.1: 僅有常數公因數 (e.g., $2x + 4y \rightarrow 2(x+2y)$)
            common_factor = _generate_coefficient(non_zero=True, include_one=False, max_abs_val=6)
            a_mult = _generate_coefficient(non_zero=True, max_abs_val=5)
            b_mult = _generate_coefficient(non_zero=True, max_abs_val=5)
            
            var1 = random.choice(['x', 'y', 'a', 'b'])
            var2 = random.choice(['x', 'y', 'a', 'b'])
            while var1 == var2: # 確保變數不同
                var2 = random.choice(['x', 'y', 'a', 'b'])
            
            term1_coeff = common_factor * a_mult
            term2_coeff = common_factor * b_mult
            
            poly_terms = [_format_term(term1_coeff, var1), _format_term(term2_coeff, var2)]
            question_text = r"請因式分解多項式：$" + _format_polynomial(poly_terms) + r"$"
            
            ans_inner_term1 = _format_term(a_mult, var1)
            ans_inner_term2 = _format_term(b_mult, var2)
            correct_answer = f"{common_factor}({ans_inner_term1}{'+' if ans_inner_term2 and not ans_inner_term2.startswith('-') else ''}{ans_inner_term2})"

        elif subtype == 2: # Subtype 1.2: 僅有變數公因數 (e.g., $x^3 - 2x \rightarrow x(x^2 - 2)$)
            common_factor_var = random.choice(['x', 'y'])
            common_factor_exp = random.choice([1, 2])
            a = _generate_coefficient(non_zero=True, max_abs_val=5)
            b = _generate_coefficient(non_zero=True, max_abs_val=5)
            
            term1_exp = common_factor_exp + random.randint(1, 2)
            
            poly_terms = [_format_term(a, common_factor_var, term1_exp), _format_term(b, common_factor_var, common_factor_exp)]
            question_text = r"請因式分解多項式：$" + _format_polynomial(poly_terms) + r"$"
            
            remaining_term1_str = _format_term(a, common_factor_var, term1_exp - common_factor_exp)
            remaining_term2_str = _format_term(b, '', 0) 
            
            common_factor_str = _format_term(1, common_factor_var, common_factor_exp)
            correct_answer = f"{common_factor_str}({remaining_term1_str}{'+' if remaining_term2_str and not remaining_term2_str.startswith('-') else ''}{remaining_term2_str})"
            
        elif subtype == 3: # Subtype 1.3: 常數與變數皆為公因數 (e.g., $6x^3 + 9x^2 \rightarrow 3x^2(2x+3)$) - 鏡射 RAG Ex 1 ⑴
            common_val = _generate_coefficient(non_zero=True, include_one=False, max_abs_val=6)
            common_factor_var = random.choice(['x', 'y'])
            common_factor_exp = random.choice([1, 2])
            a_mult = _generate_coefficient(non_zero=True, max_abs_val=5)
            b_mult = _generate_coefficient(non_zero=True, max_abs_val=5)
            
            term1_coeff = common_val * a_mult
            term2_coeff = common_val * b_mult
            
            term1_exp = common_factor_exp + random.randint(1, 2)
            
            poly_terms = [_format_term(term1_coeff, common_factor_var, term1_exp), _format_term(term2_coeff, common_factor_var, common_factor_exp)]
            question_text = r"請因式分解多項式：$" + _format_polynomial(poly_terms) + r"$"
            
            remaining_term1_str = _format_term(a_mult, common_factor_var, term1_exp - common_factor_exp)
            remaining_term2_str = _format_term(b_mult, '', 0)
            
            common_factor_str = _format_term(common_val, common_factor_var, common_factor_exp)
            correct_answer = f"{common_factor_str}({remaining_term1_str}{'+' if remaining_term2_str and not remaining_term2_str.startswith('-') else ''}{remaining_term2_str})"
            
    elif problem_type == 2: # Type 2: 提取含多變數或高次方的單項公因式
        # 此題型在 Spec 中描述，但未直接鏡射 RAG Ex 1 或 2，為單項公因式的延伸。
        common_coeff = _generate_coefficient(non_zero=True, include_one=False, max_abs_val=4)
        common_var1 = 'x'
        common_var2 = 'y'
        common_exp1 = random.choice([1, 2])
        common_exp2 = random.choice([1, 2])
        
        a_mult = _generate_coefficient(non_zero=True, max_abs_val=5)
        b_mult = _generate_coefficient(non_zero=True, max_abs_val=5)
        
        term1_x_exp = common_exp1 + random.randint(1, 2)
        term1_y_exp = common_exp2 + random.randint(1, 2)
        term2_x_exp = common_exp1 + random.randint(1, 2)
        term2_y_exp = common_exp2 + random.randint(1, 2)
        
        poly_term1_str = _assemble_multi_var_term(common_coeff * a_mult, common_var1, term1_x_exp, common_var2, term1_y_exp)
        poly_term2_str = _assemble_multi_var_term(common_coeff * b_mult, common_var1, term2_x_exp, common_var2, term2_y_exp)
        
        poly_terms_list = [poly_term1_str, poly_term2_str]
        question_text = r"請因式分解多項式：$" + _format_polynomial(poly_terms_list) + r"$"
        
        common_factor_full_str = _assemble_multi_var_term(common_coeff, common_var1, common_exp1, common_var2, common_exp2)
        
        remaining_term1_full_str = _assemble_multi_var_term(a_mult, common_var1, term1_x_exp - common_exp1, common_var2, term1_y_exp - common_exp2)
        remaining_term2_full_str = _assemble_multi_var_term(b_mult, common_var1, term2_x_exp - common_exp1, common_var2, term2_y_exp - common_exp2)
        
        correct_answer = f"{common_factor_full_str}({remaining_term1_full_str}{'+' if remaining_term2_full_str and not remaining_term2_full_str.startswith('-') else ''}{remaining_term2_full_str})"

    elif problem_type == 3: # Type 3: 提取多項式公因式 (含正負號處理) - 鏡射 RAG Ex 1 ⑶, RAG Ex 2
        subtype = random.choice([1, 2])
        
        var_x = random.choice(['x', 'y']) 
        var_y = random.choice(['a', 'b', 'c']) 
        while var_y == var_x: var_y = random.choice(['a', 'b', 'c'])

        if subtype == 1: # Subtype 3.1: 直接提取共同二項式 (e.g., $c(ax+b) + d(ax+b)$ 或 $c(ax+b)^2 + d(ax+b)$)
            choice_type_3_1 = random.choice([1, 2])
            
            a_inner = _generate_coefficient(non_zero=True, max_abs_val=5) # coeff for var_x in binomial
            b_inner = _generate_coefficient(non_zero=True, max_abs_val=5) # constant in binomial
            common_binomial_str = f"{_format_term(a_inner, var_x)}{'+' if b_inner >= 0 else ''}{_format_term(b_inner, '', 0)}"
            
            c_outer = _generate_coefficient(non_zero=True, max_abs_val=5) 
            d_outer = _generate_coefficient(non_zero=True, max_abs_val=5) 
            
            if choice_type_3_1 == 1: # $c \cdot var_y \cdot (ax+b) + d \cdot (ax+b)$
                term1_factor_str = _format_term(c_outer, var_y)
                term2_factor_str = _format_term(d_outer, '')
                
                question_text = r"請因式分解多項式：$" + term1_factor_str + r"(" + common_binomial_str + r") " 
                if d_outer >= 0 and not term2_factor_str.startswith('-'): question_text += r"+"
                question_text += term2_factor_str + r"(" + common_binomial_str + r")$"
                
                correct_answer = f"({common_binomial_str})({term1_factor_str}{'+' if term2_factor_str and not term2_factor_str.startswith('-') else ''}{term2_factor_str})"
            
            elif choice_type_3_1 == 2: # $c(ax+b)^2 + d(ax+b)$ - 鏡射 RAG Ex 1 ⑶
                # First term: c_outer * (ax+b)^2
                term1_part_str = ""
                if abs(c_outer) != 1: term1_part_str += str(c_outer)
                elif c_outer == -1: term1_part_str += "-"
                template_sq = r"({B})^{2}"
                term1_part_str += template_sq.replace("{B}", common_binomial_str)
                
                # Second term: d_outer * (ax+b)
                term2_part_str = ""
                if abs(d_outer) != 1: term2_part_str += str(d_outer)
                elif d_outer == -1: term2_part_str += "-"
                term2_part_str += r"(" + common_binomial_str + r")"
                
                question_text = r"請因式分解多項式：$" + term1_part_str
                if d_outer >= 0 and not term2_part_str.startswith('-'): question_text += r"+"
                question_text += term2_part_str + r"$"
                
                # Correct answer: (ax+b) [ c_outer*(ax+b) + d_outer ]
                inner_factor1_str = _format_term(c_outer, '') + r"(" + common_binomial_str + r")"
                inner_factor2_str = _format_term(d_outer, '')
                correct_answer = f"({common_binomial_str})({inner_factor1_str}{'+' if inner_factor2_str and not inner_factor2_str.startswith('-') else ''}{inner_factor2_str})"
                
        elif subtype == 2: # Subtype 3.2: 提取共同二項式，需處理符號轉換 (e.g., $A(x-y) + B(y-x)$) - 鏡射 RAG Ex 2
            var_m = random.choice(['x', 'a'])
            var_n = random.choice(['y', 'b'])
            while var_m == var_n: var_n = random.choice(['y', 'b'])
            
            common_binomial_pos_str = f"{_format_term(1, var_m)} - {_format_term(1, var_n)}" 
            common_binomial_neg_str = f"{_format_term(1, var_n)} - {_format_term(1, var_m)}" 
            
            factor1_coeff = _generate_coefficient(non_zero=True, max_abs_val=5)
            factor2_coeff = _generate_coefficient(non_zero=True, max_abs_val=5)
            
            # Factors outside the binomial can be variables or constants
            outer_vars = [v for v in ['k', 'p', 'q'] if v not in [var_m, var_n]]
            factor1_outer_var = random.choice(outer_vars + ['']) # Can be empty for just coefficient
            factor2_outer_var = random.choice(outer_vars + [''])
            while factor2_outer_var == factor1_outer_var and factor1_outer_var != '':
                 factor2_outer_var = random.choice(outer_vars + [''])

            factor1_str = _format_term(factor1_coeff, factor1_outer_var)
            factor2_str = _format_term(factor2_coeff, factor2_outer_var)
            
            question_text = r"請因式分解多項式：$" + factor1_str + r"(" + common_binomial_pos_str + r") " 
            if factor2_coeff >= 0 and not factor2_str.startswith('-'): question_text += r"+"
            question_text += factor2_str + r"(" + common_binomial_neg_str + r")$"
            
            inner_remaining_term1 = factor1_str
            inner_remaining_term2 = _format_term(-factor2_coeff, factor2_outer_var) 
            
            correct_answer = f"({common_binomial_pos_str})({inner_remaining_term1}{'+' if inner_remaining_term2 and not inner_remaining_term2.startswith('-') else ''}{inner_remaining_term2})"

    elif problem_type == 4: # Type 4: 提取負號作為公因式
        subtype = random.choice([1, 2])
        if subtype == 1: # Subtype 4.1: 僅提取 -1 (e.g., $-3x - 5 \rightarrow -(3x+5)$)
            a = _generate_coefficient(non_zero=True, include_one=False, max_abs_val=6)
            b = _generate_coefficient(non_zero=True, max_abs_val=6)
            var = random.choice(['x', 'y'])
            exp = random.choice([1, 2])
            
            term1_coeff = -a
            term2_coeff = -b
            
            poly_terms = [_format_term(term1_coeff, var, exp), _format_term(term2_coeff, '', 0)]
            question_text = r"請因式分解多項式：$" + _format_polynomial(poly_terms) + r"$"
            
            ans_inner_term1 = _format_term(a, var, exp)
            ans_inner_term2 = _format_term(b, '', 0)
            correct_answer = f"-({ans_inner_term1}{'+' if ans_inner_term2 and not ans_inner_term2.startswith('-') else ''}{ans_inner_term2})"
            
        elif subtype == 2: # Subtype 4.2: 提取負的常數公因式 (可能含變數) (e.g., $-6x^2 + 9 \rightarrow -3(2x^2 - 3)$)
            common_factor_val = _generate_coefficient(non_zero=True, include_one=False, max_abs_val=6)
            a_mult = _generate_coefficient(non_zero=True, max_abs_val=5)
            b_mult = _generate_coefficient(non_zero=True, max_abs_val=5)
            var = random.choice(['x', 'y'])
            exp = random.choice([1, 2])
            
            term1_coeff = -common_factor_val * a_mult
            term2_coeff = common_factor_val * b_mult 
            
            poly_terms = [_format_term(term1_coeff, var, exp), _format_term(term2_coeff, '', 0)]
            question_text = r"請因式分解多項式：$" + _format_polynomial(poly_terms) + r"$"
            
            common_factor_str = _format_term(-common_factor_val, '', 0)
            
            remaining_term1_str = _format_term(a_mult, var, exp)
            remaining_term2_str = _format_term(-b_mult, '', 0) 
            
            correct_answer = f"{common_factor_str}({remaining_term1_str}{'+' if remaining_term2_str and not remaining_term2_str.startswith('-') else ''}{remaining_term2_str})"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "", 
        "image_base64": None, 
        "created_at": datetime.datetime.now().isoformat(),
        "version": 1
    }

# --- check() 函式規格實現 ---

# 定義變數的規範化順序，用於多項式項的鍵生成
CANONICAL_VARS = ['a', 'b', 'c', 'x', 'y', 'z']

def _canonicalize_term_key(term_parts):
    """
    將 (變數, 指數) 列表規範化為字串鍵。
    範例: [('y', 1), ('x', 2)] -> 'x^2y'
    """
    if not term_parts:
        return '' # 常數項
    
    # 依 CANONICAL_VARS 順序排列變數，相同變數則指數降序 (實際上不會有相同變數，但為通用性)
    sorted_parts = sorted(term_parts, key=lambda p: (CANONICAL_VARS.index(p[0]) if p[0] in CANONICAL_VARS else len(CANONICAL_VARS), -p[1]))
    
    key_parts = []
    for var, exp in sorted_parts:
        key_parts.append(var)
        if exp > 1:
            key_parts.append(f"^{exp}") # f-string在此處用於內部鍵，非LaTeX輸出，安全
    return "".join(key_parts)

def _poly_add(poly1, poly2):
    """將兩個多項式映射相加。"""
    result = defaultdict(int, poly1)
    for term, coeff in poly2.items():
        result[term] += coeff
    return result

def _poly_subtract(poly1, poly2):
    """從 poly1 中減去 poly2。"""
    result = defaultdict(int, poly1)
    for term, coeff in poly2.items():
        result[term] -= coeff
    return result

def _poly_multiply(poly1, poly2):
    """將兩個多項式映射相乘。"""
    result = defaultdict(int)
    for term1, coeff1 in poly1.items():
        for term2, coeff2 in poly2.items():
            new_coeff = coeff1 * coeff2
            
            # 將項字串解析為 (變數, 指數) 字典
            def parse_term_string_to_dict(s):
                parts = {}
                if not s: return parts # 常數項
                
                # Regex 找出變數和指數對 (e.g., 'x^2y' -> [('x', '2'), ('y', None)])
                matches = re.findall(r'([a-zA-Z])(?:\^(\d+))?', s) # non-capturing group for exponent
                for match in matches:
                    var = match[0]
                    exp = int(match[1]) if match[1] else 1
                    parts[var] = parts.get(var, 0) + exp
                return parts
            
            term1_parts = parse_term_string_to_dict(term1)
            term2_parts = parse_term_string_to_dict(term2)
            
            combined_parts = defaultdict(int)
            for var, exp in term1_parts.items():
                combined_parts[var] += exp
            for var, exp in term2_parts.items():
                combined_parts[var] += exp
            
            new_term_key = _canonicalize_term_key(list(combined_parts.items()))
            result[new_term_key] += new_coeff
    return result

class Token:
    """表示詞彙單元 (Token)。"""
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Parser:
    """實現遞歸下降解析器，用於解析多項式表達式並展開。"""
    def __init__(self, expression):
        self.expression = expression
        self.tokens = self._tokenize(expression)
        self.pos = 0

    def _tokenize(self, expr_str):
        """
        將表達式字串分解為詞彙單元 (tokens)。
        處理隱式乘法 (例如: 2x, x(y+1), (x+1)(y+1))。
        """
        # 1. 在運算符和括號周圍添加空格，方便正則表達式匹配
        expr_str = re.sub(r'([+\-*/^()])', r' \1 ', expr_str)
        
        # 2. 處理隱式乘法
        # 數字後跟變數: 2x -> 2 * x
        expr_str = re.sub(r'(\d)([a-zA-Z])', r'\1 * \2', expr_str) 
        # 變數後跟左括號: x(y+1) -> x * (y+1)
        expr_str = re.sub(r'([a-zA-Z])(\()', r'\1 * \2', expr_str) 
        # 數字後跟左括號: 2(x+1) -> 2 * (x+1)
        expr_str = re.sub(r'(\d)(\()', r'\1 * \2', expr_str) 
        # 右括號後跟變數: (x+1)y -> (x+1) * y
        expr_str = re.sub(r'(\))([a-zA-Z])', r'\1 * \2', expr_str) 
        # 右括號後跟數字: (x+1)2 -> (x+1) * 2
        expr_str = re.sub(r'(\))(\d)', r'\1 * \2', expr_str) 
        # 右括號後跟左括號: (x+1)(y+1) -> (x+1) * (y+1)
        expr_str = re.sub(r'(\))(\()', r'\1 * \2', expr_str) 
        # 處理單元負號在數字或變數前，如 "-x"
        expr_str = re.sub(r'(^|\s)-([a-zA-Z\d(])', r'\1 - \2', expr_str)

        # 移除多餘空格
        expr_str = re.sub(r'\s+', ' ', expr_str).strip()
        
        tokens = []
        # 正則表達式匹配數字、變數、運算符、括號
        token_patterns = re.compile(r'(\d+)|([a-zA-Z])|([+\-*/^()])')
        
        for match in token_patterns.finditer(expr_str):
            if match.group(1): # 數字
                tokens.append(Token('NUMBER', int(match.group(1))))
            elif match.group(2): # 變數
                tokens.append(Token('VARIABLE', match.group(2)))
            elif match.group(3): # 運算符/括號
                op = match.group(3)
                if op in '+-*/^':
                    tokens.append(Token('OPERATOR', op))
                elif op == '(':
                    tokens.append(Token('LPAREN'))
                elif op == ')':
                    tokens.append(Token('RPAREN'))
        
        return tokens

    def _current_token(self):
        """返回當前位置的詞彙單元，若已到末尾則返回 EOF。"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token('EOF')

    def _eat(self, token_type, value=None):
        """
        消耗 (Eat) 當前詞彙單元，並移動到下一個。
        若當前詞彙單元不符合預期，則拋出 SyntaxError。
        """
        if self._current_token().type == token_type and \
           (value is None or self._current_token().value == value):
            self.pos += 1
        else:
            raise SyntaxError(f"Expected {token_type} (value: {value}), got {self._current_token()} at position {self.pos} in '{self.expression}'")

    def parse_expression(self):
        """解析加法和減法運算 (最低優先級)。"""
        result = self.parse_term()

        while self._current_token().type == 'OPERATOR' and \
              (self._current_token().value == '+' or self._current_token().value == '-'):
            op = self._current_token().value
            self._eat('OPERATOR', op)
            next_term = self.parse_term()
            if op == '+':
                result = _poly_add(result, next_term)
            else: # '-'
                result = _poly_subtract(result, next_term)
        return result

    def parse_term(self):
        """解析乘法運算 (中等優先級)。"""
        result = self.parse_factor()

        while self._current_token().type == 'OPERATOR' and \
              (self._current_token().value == '*'): 
            op = self._current_token().value
            self._eat('OPERATOR', op)
            next_factor = self.parse_factor()
            if op == '*':
                result = _poly_multiply(result, next_factor)
        return result
    
    def parse_factor(self):
        """解析指數運算和單元負號 (最高優先級)。"""
        is_negative = False
        # 處理單元負號
        if self._current_token().type == 'OPERATOR' and self._current_token().value == '-':
            is_negative = True
            self._eat('OPERATOR', '-')
        
        base_poly = self._parse_base()

        # 處理指數運算
        if self._current_token().type == 'OPERATOR' and self._current_token().value == '^':
            self._eat('OPERATOR', '^')
            exponent_token = self._current_token()
            if exponent_token.type != 'NUMBER':
                raise SyntaxError("Exponent must be an integer after '^'.")
            exponent = exponent_token.value
            self._eat('NUMBER')
            
            if exponent < 0:
                raise ValueError("Negative exponents are not supported in this K12 context.")
            if exponent == 0:
                base_poly = defaultdict(int, {'': 1}) # 任何非零項的 0 次方為 1
            else:
                original_base = base_poly
                for _ in range(exponent - 1): # 執行 (exp - 1) 次乘法
                    base_poly = _poly_multiply(base_poly, original_base)
        
        # 套用單元負號
        if is_negative:
            neg_one_poly = defaultdict(int, {'': -1})
            base_poly = _poly_multiply(neg_one_poly, base_poly)

        return base_poly

    def _parse_base(self):
        """解析基本單元: 數字、變數或括號內的表達式。"""
        token = self._current_token()
        
        if token.type == 'NUMBER':
            self._eat('NUMBER')
            return defaultdict(int, {'': token.value}) # 常數項
        
        elif token.type == 'VARIABLE':
            self._eat('VARIABLE')
            return defaultdict(int, {_canonicalize_term_key([(token.value, 1)]): 1}) # 單一變數項
        
        elif token.type == 'LPAREN':
            self._eat('LPAREN')
            poly = self.parse_expression()
            self._eat('RPAREN')
            return poly
        
        else:
            raise SyntaxError(f"Unexpected token: {token} at position {self.pos} in '{self.expression}'")

    def parse(self):
        """開始解析表達式。"""
        result = self.parse_expression()
        if self._current_token().type != 'EOF':
            raise SyntaxError(f"Unexpected tokens at end of expression: {self.tokens[self.pos:]}")
        return result

def _evaluate_polynomial_expression(expr_str):
    """
    解析多項式表達式字串 (可以是因式分解或展開形式)，
    並以標準化的展開形式 (defaultdict(int)) 返回。
    鍵為規範化的項字串 (例如 'x^2', 'xy', '')，值為整數係數。
    """
    parser = Parser(expr_str)
    return parser.parse()



    """
    驗證使用者答案的正確性，透過將多項式展開為標準形式進行代數等價比較。
    """
    # 1. 輸入清洗 (Input Sanitization)
    def clean(s):
        s = str(s).strip().lower()
        # 移除 LaTeX 符號、變數前綴、所有空白字元
        s = re.sub(r'[\$\{\}\\\=\[\]]', '', s) 
        s = re.sub(r'x=|y=|k=|Ans:', '', s) 
        s = re.sub(r'\s+', '', s) # 移除所有空白字元
        return s
    
    cleaned_user_answer = clean(user_answer)
    cleaned_correct_answer = clean(correct_answer)
    
    # 2. 強韌閱卷邏輯 (Robust Check Logic)
    try:
        user_poly_map = _evaluate_polynomial_expression(cleaned_user_answer)
        correct_poly_map = _evaluate_polynomial_expression(cleaned_correct_answer)
        
        # 移除係數為零的項，確保比較時的等價性
        user_poly_map = {k: v for k, v in user_poly_map.items() if v != 0}
        correct_poly_map = {k: v for k, v in correct_poly_map.items() if v != 0}

        # 比較標準化後的多項式表示是否完全一致
        if user_poly_map == correct_poly_map:
            return {"correct": True, "result": "正確！"}
        else:
            return {"correct": False, "result": "答案錯誤。"}
    except SyntaxError as e:
        return {"correct": False, "result": f"答案格式錯誤：{e}"}
    except ValueError as e:
        return {"correct": False, "result": f"答案數值錯誤：{e}"}
    except Exception as e:
        # 捕捉其他潛在錯誤，提供通用錯誤訊息
        return {"correct": False, "result": f"系統錯誤，請檢查答案格式或聯繫管理員。詳細錯誤: {e}"}


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
