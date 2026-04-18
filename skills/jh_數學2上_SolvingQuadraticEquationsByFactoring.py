# ==============================================================================
# ID: jh_數學2上_SolvingQuadraticEquationsByFactoring
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 48.23s | RAG: 5 examples
# Created At: 2026-01-19 11:28:55
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


from datetime import datetime
import re

# Coder must define _format_quadratic_term here or as a module-level private helper
def _format_quadratic_term(coeff, power, var='x', include_plus=False):
    """
    Formats a quadratic term (e.g., ax^2, bx, c), handling coefficients of 1/-1,
    positive/negative signs, and powers.

    Args:
        coeff (int): The coefficient of the term.
        power (int): The power of the variable (0 for constant, 1 for linear, 2 for quadratic).
        var (str, optional): The variable name. Defaults to 'x'.
        include_plus (bool, optional): If True and coeff is positive, prepends a '+'. Defaults to False.

    Returns:
        str: The formatted term string.
    """
    if coeff == 0:
        return ""

    sign_str = ""
    if coeff > 0 and include_plus:
        sign_str = "+"
    elif coeff < 0:
        sign_str = "-"
    
    abs_coeff = abs(coeff)
    term_str = ""
    
    if power == 0:
        term_str = str(abs_coeff)
    elif power == 1:
        term_str = var if abs_coeff == 1 else str(abs_coeff) + var
    elif power == 2:
        term_str = var + "^2" if abs_coeff == 1 else str(abs_coeff) + var + "^2"
    
    return sign_str + term_str

def generate(level=1):
    """
    Generates a quadratic equation problem that can be solved by factoring.
    The problem type is randomly selected from 5 different scenarios.
    """
    problem_type = random.choice([1, 2, 3, 4, 5]) 
    
    r1, r2 = 0, 0 # Initialize roots, will be overwritten
    question_text_val = ""
    correct_answer_val = ""

    # Type 1 (Maps to Example 1: (x-a)(x-b)=0 已因式分解型)
    if problem_type == 1:
        r1 = random.randint(-8, 8)
        r2 = random.randint(-8, 8)
        # Ensure distinct roots for variety, allowing for occasional perfect squares
        if random.random() < 0.8: # 80% chance of distinct roots
            while r1 == r2:
                r2 = random.randint(-8, 8)
        
        # Construct factor strings carefully for x or (x +/- k)
        factor1_str = "x" if r1 == 0 else (f"(x - {r1})" if r1 > 0 else f"(x + {-r1})")
        factor2_str = "x" if r2 == 0 else (f"(x - {r2})" if r2 > 0 else f"(x + {-r2})")
        
        eq_str_raw = f"{factor1_str}{factor2_str} = 0"
        question_text_val = r"試求方程式 $" + eq_str_raw + r"$ 的解。"
        correct_answer_val = f"{min(r1, r2)},{max(r1, r2)}"

    # Type 2 (Maps to Example 2: x^2 + bx + c = 0 簡單三項式型)
    elif problem_type == 2:
        r1 = random.randint(-8, 8)
        r2 = random.randint(-8, 8)
        if random.random() < 0.8: # 80% chance of distinct roots
            while r1 == r2:
                r2 = random.randint(-8, 8)
        
        b_val = -(r1 + r2)
        c_val = r1 * r2
        
        term_x2 = _format_quadratic_term(1, 2)
        term_x = _format_quadratic_term(b_val, 1, include_plus=True)
        term_c = _format_quadratic_term(c_val, 0, include_plus=True)
        
        eq_parts = [term_x2, term_x, term_c]
        eq_str_raw = "".join(p for p in eq_parts if p).lstrip('+') + " = 0"
        
        question_text_val = r"試求方程式 $" + eq_str_raw + r"$ 的解。"
        correct_answer_val = f"{min(r1, r2)},{max(r1, r2)}"

    # Type 3 (Maps to Example 3: ax^2 + bx + c = 0 首項係數不為 1 型)
    elif problem_type == 3:
        r1 = random.randint(-8, 8)
        r2 = random.randint(-8, 8)
        if random.random() < 0.8: # 80% chance of distinct roots
            while r1 == r2:
                r2 = random.randint(-8, 8)
        
        a_coeff_raw = random.choice([2, 3, 4, -2, -3, -4])
        a_coeff = abs(a_coeff_raw) # Ensure final x^2 coeff is positive for display
        
        b_val = -a_coeff * (r1 + r2)
        c_val = a_coeff * r1 * r2
        
        term_x2 = _format_quadratic_term(a_coeff, 2)
        term_x = _format_quadratic_term(b_val, 1, include_plus=True)
        term_c = _format_quadratic_term(c_val, 0, include_plus=True)
        
        eq_parts = [term_x2, term_x, term_c]
        eq_str_raw = "".join(p for p in eq_parts if p).lstrip('+') + " = 0"
        
        question_text_val = r"試求方程式 $" + eq_str_raw + r"$ 的解。"
        correct_answer_val = f"{min(r1, r2)},{max(r1, r2)}"

    # Type 4 (Maps to Example 4: ax^2 + bx = 0 或 ax^2 - c = 0 不完全二次方程式型)
    elif problem_type == 4:
        sub_type = random.choice(['ax^2+bx=0', 'ax^2-c=0'])

        if sub_type == 'ax^2+bx=0': # 子類型 4a: ax^2 + bx = 0 (提取公因數型)
            r2 = 0 # One root is always 0
            r1 = random.randint(-8, 8)
            while r1 == 0: # Ensure the other root is non-zero
                r1 = random.randint(-8, 8)
            
            a_coeff = random.randint(2, 5)
            b_val = -a_coeff * r1
            
            term_x2 = _format_quadratic_term(a_coeff, 2)
            term_x = _format_quadratic_term(b_val, 1, include_plus=True)
            
            eq_parts = [term_x2, term_x]
            eq_str_raw = "".join(p for p in eq_parts if p).lstrip('+') + " = 0"
            
            correct_answer_val = f"{min(r1, r2)},{max(r1, r2)}"

        else: # 子類型 4b: ax^2 - c = 0 (平方差型)
            k = random.randint(2, 8) # Ensure k > 1 for meaningful square roots
            r1 = k
            r2 = -k
            
            a_coeff = random.randint(1, 4)
            c_val = a_coeff * k * k # c_val is positive, so term_c will be negative for display
            
            term_x2 = _format_quadratic_term(a_coeff, 2)
            term_c = _format_quadratic_term(-c_val, 0, include_plus=True) # Note: constant term is negative
            
            eq_parts = [term_x2, term_c]
            eq_str_raw = "".join(p for p in eq_parts if p).lstrip('+') + " = 0"
            
            correct_answer_val = f"{min(r1, r2)},{max(r1, r2)}"
        
        question_text_val = r"試求方程式 $" + eq_str_raw + r"$ 的解。"

    # Type 5 (Maps to Example 5: 方程式需先整理型)
    elif problem_type == 5:
        r1 = random.randint(-8, 8)
        r2 = random.randint(-8, 8)
        if random.random() < 0.8: # 80% chance of distinct roots
            while r1 == r2:
                r2 = random.randint(-8, 8)
        
        a_coeff_raw = random.choice([1, 2, -1, -2])
        # Coefficients for the standard form ax^2+bx+c=0 (after rearrangement)
        # However, the initial equation might have a negative x^2 coefficient.
        actual_a_coeff = a_coeff_raw
        actual_b_coeff = -a_coeff_raw * (r1 + r2)
        actual_c_coeff = a_coeff_raw * r1 * r2
        
        rearrange_type = random.choice(['const_right', 'bx_right', 'all_right'])
        
        left_eq_str = ""
        right_eq_str = ""

        if rearrange_type == 'const_right':
            # Form: ax^2 + bx = -c
            left_eq_parts = [_format_quadratic_term(actual_a_coeff, 2), 
                             _format_quadratic_term(actual_b_coeff, 1, include_plus=True)]
            left_eq_str = "".join(p for p in left_eq_parts if p).lstrip('+')
            right_eq_str = _format_quadratic_term(-actual_c_coeff, 0)
        elif rearrange_type == 'bx_right':
            # Form: ax^2 + c = -bx
            left_eq_parts = [_format_quadratic_term(actual_a_coeff, 2), 
                             _format_quadratic_term(actual_c_coeff, 0, include_plus=True)]
            left_eq_str = "".join(p for p in left_eq_parts if p).lstrip('+')
            right_eq_str = _format_quadratic_term(-actual_b_coeff, 1)
        elif rearrange_type == 'all_right':
            # Form: ax^2 = -bx - c (or similar, ensuring left side has some terms)
            left_eq_str = _format_quadratic_term(actual_a_coeff, 2)
            right_eq_parts = [_format_quadratic_term(-actual_b_coeff, 1), 
                              _format_quadratic_term(-actual_c_coeff, 0, include_plus=True)]
            right_eq_str = "".join(p for p in right_eq_parts if p).lstrip('+')
            # If right_eq_str is empty (e.g., -b_std and -c_std are both 0), make it "0"
            if not right_eq_str:
                right_eq_str = "0"
            
        eq_str_raw = f"{left_eq_str} = {right_eq_str}"
        question_text_val = r"試求方程式 $" + eq_str_raw + r"$ 的解。"
        correct_answer_val = f"{min(r1, r2)},{max(r1, r2)}"

    return {
        "question_text": question_text_val,
        "correct_answer": correct_answer_val,
        "answer": "", # 留空，由前端填入
        "image_base64": None, # 本題型無圖形
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    """
    Checks if the user's answer for quadratic equation roots is correct.
    It sanitizes the input and compares sets of roots.
    """
    # 1. Input Sanitization
    # 移除常見前綴、LaTeX符號、所有空白字元、分隔符號和連接詞
    sanitized_user_answer = re.sub(r'[$\\\{\}xXkK=Ans:解或,、;and\s]+', '', user_answer)
    
    # 2. Parse user input into a set of numbers
    # 使用正則表達式尋找所有可能的整數（包括負數）
    user_roots_str = re.findall(r'-?\d+', sanitized_user_answer)
    
    try:
        user_roots = {int(root) for root in user_roots_str}
    except ValueError:
        return False # 如果用戶輸入無法轉換為數字，則為錯誤
    
    # 3. Parse correct answer into a set of numbers
    correct_roots_str = correct_answer.split(',')
    try:
        correct_roots = {int(root) for root in correct_roots_str}
    except ValueError:
        # 正確答案格式應始終正確，此處為防禦性編程
        return False 
    
    # 4. Compare the sets of roots
    return user_roots == correct_roots


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
