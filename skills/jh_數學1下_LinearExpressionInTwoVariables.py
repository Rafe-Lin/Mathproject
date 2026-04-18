# ==============================================================================
# ID: jh_數學1下_LinearExpressionInTwoVariables
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 76.30s | RAG: 5 examples
# Created At: 2026-01-15 09:42:17
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

# [頂層函式] 嚴禁使用 class 封裝。必須直接定義 generate 與 check 於模組最外層。
# [自動重載] 確保代碼不依賴全域狀態。

def generate(level=1):
    """
    根據指定的難度等級生成一個二元一次式問題。
    [隨機分流] 內部使用 random.choice 或 if/elif 邏輯，明確對應到 RAG 中的例題。
    [數據禁絕常數] 嚴禁硬編碼答案或座標。所有目標答案與圖形座標必須根據隨機生成的數據，透過公式計算得出。
    """
    
    question_text = ""
    correct_answer = None
    answer_value = None
    
    # Helper for expression string formatting (Handles coefficients 1, -1, positive, negative, and constant)
    def format_expression(a_coeff, b_coeff, constant):
        parts = []
        if a_coeff != 0:
            if a_coeff == 1:
                parts.append(r"x")
            elif a_coeff == -1:
                parts.append(r"-x")
            else:
                parts.append(str(a_coeff) + r"x")

        if b_coeff != 0:
            if b_coeff == 1:
                parts.append(r"y")
            elif b_coeff == -1:
                parts.append(r"-y")
            else:
                parts.append(str(b_coeff) + r"y")
        
        if constant != 0:
            parts.append(str(constant))

        if not parts:
            return "0" # Fallback, though ideally 'a' or 'b' will be non-zero

        # Join parts with appropriate signs for LaTeX display
        formatted_expr = parts[0]
        for i in range(1, len(parts)):
            part = parts[i]
            if part.startswith('-'): # If term starts with '-', append ' - ' and the absolute value
                formatted_expr += r" - " + part[1:]
            else: # Otherwise, append ' + '
                formatted_expr += r" + " + part
        return formatted_expr

    # Determine problem type based on level, balancing complexity and RAG mapping.
    # Note: Due to the fixed `check` function (numerical comparison), all problems
    # generated here must ultimately result in a numerical answer. This means RAG Ex 2-5,
    # which are simplification problems resulting in expressions, are adapted to be
    # evaluated numerically after their "mathematical model" structure is applied.
    if level == 1:
        problem_type = random.choice([1, 2]) # Simpler evaluation and word problem
    else: # level >= 2
        problem_type = random.choice([1, 2, 3]) # Include more complex evaluation (Type 3) and wider ranges

    if problem_type == 1:
        # Type 1: Maps to the concept of an expression with x, y, constants (like RAG Ex 1),
        # but asks for numerical evaluation given specific x, y values.
        # Description: Given a linear expression in two variables, find its value for given x and y.
        a = random.randint(2, 10)
        b = random.randint(2, 10)
        c = random.randint(1, 15)
        x_val = random.randint(1, 5)
        y_val = random.randint(1, 5)

        if level >= 2: # Wider ranges, allow negatives for higher levels
            a = random.randint(-10, 10)
            b = random.randint(-10, 10)
            c = random.randint(-15, 15)
            x_val = random.randint(-5, 5)
            y_val = random.randint(-5, 5)

        # Ensure coefficients for x and y are non-zero to maintain the "two variables" nature.
        while a == 0: a = random.randint(-10, 10) if level >= 2 else random.randint(2, 10)
        while b == 0: b = random.randint(-10, 10) if level >= 2 else random.randint(2, 10)
        
        # [公式計算] Calculate the correct numerical answer
        answer_value = a * x_val + b * y_val + c
        expression_str = format_expression(a, b, c)
        
        question_text_template = r"已知一個二元一次式為 ${expr}$，當 $x = {x_val}$ 且 $y = {y_val}$ 時，此式的值為何？"
        question_text = question_text_template.replace("{expr}", expression_str)\
                                                .replace("{x_val}", str(x_val))\
                                                .replace("{y_val}", str(y_val))

    elif problem_type == 2:
        # Type 2: Maps to RAG Ex 1's word problem structure (initial amount and spending),
        # asking for the numerical remainder. Retains the name '小靖'.
        # Description: A word problem involving initial money and two types of expenses,
        # requiring calculation of the remaining amount.
        initial_money = random.randint(200, 1000)
        item1_price = random.randint(5, 20)
        item2_price = random.randint(10, 30)
        num_item1_spent = random.randint(2, 8)
        num_item2_spent = random.randint(2, 8)

        if level >= 2: # Wider ranges for higher levels
            initial_money = random.randint(500, 2000)
            item1_price = random.randint(10, 50)
            item2_price = random.randint(20, 80)
            num_item1_spent = random.randint(5, 15)
            num_item2_spent = random.randint(5, 15)

        # Ensure total spent is less than initial money to have a positive remainder
        while (item1_price * num_item1_spent + item2_price * num_item2_spent) >= initial_money:
            initial_money = random.randint(200, 1000) if level == 1 else random.randint(500, 2000)
            item1_price = random.randint(5, 20) if level == 1 else random.randint(10, 50)
            item2_price = random.randint(10, 30) if level == 1 else random.randint(20, 80)
            num_item1_spent = random.randint(2, 8) if level == 1 else random.randint(5, 15)
            num_item2_spent = random.randint(2, 8) if level == 1 else random.randint(5, 15)

        item1_name = random.choice(["鉛筆", "原子筆", "橡皮擦", "筆記本"])
        item2_name = random.choice(["尺", "立可帶", "螢光筆", "彩色筆"])
        while item1_name == item2_name: # Ensure item names are distinct
            item2_name = random.choice(["尺", "立可帶", "螢光筆", "彩色筆"])

        # [公式計算] Calculate the correct numerical answer
        answer_value = initial_money - (item1_price * num_item1_spent) - (item2_price * num_item2_spent)
        
        question_text_template = r"小靖身上原有 {initial_money} 元。吃午餐用了 {num_item1_spent} 個 {item1_price} 元的{item1_name}，" \
                                 r"買文具花掉 {num_item2_spent} 個 {item2_price} 元的{item2_name}。" \
                                 r"那麼小靖身上還有多少錢？"
        
        question_text = question_text_template.replace("{initial_money}", str(initial_money))\
                                                .replace("{num_item1_spent}", str(num_item1_spent))\
                                                .replace("{item1_price}", str(item1_price))\
                                                .replace("{item1_name}", item1_name)\
                                                .replace("{num_item2_spent}", str(num_item2_spent))\
                                                .replace("{item2_price}", str(item2_price))\
                                                .replace("{item2_name}", item2_name)

    elif problem_type == 3:
        # Type 3: Maps to the mathematical model of RAG Ex 3 (combining two expressions),
        # but asks for numerical evaluation after substitution. This represents a more complex algebraic task.
        # Description: Evaluate the sum or difference of two linear expressions in two variables
        # for given x and y values, potentially involving negative coefficients and larger numbers.
        a1 = random.randint(-15, 15)
        b1 = random.randint(-15, 15)
        c1 = random.randint(-20, 20)
        
        a2 = random.randint(-15, 15)
        b2 = random.randint(-15, 15)
        c2 = random.randint(-20, 20)

        op = random.choice(['+', '-']) # Operation between the two expressions

        x_val = random.randint(-10, 10)
        y_val = random.randint(-10, 10)

        # Ensure the combined expression (after simplification) still has at least one variable term.
        while (a1 + a2 if op == '+' else a1 - a2) == 0 and \
              (b1 + b2 if op == '+' else b1 - b2) == 0:
            a1 = random.randint(-15, 15)
            b1 = random.randint(-15, 15)
            a2 = random.randint(-15, 15)
            b2 = random.randint(-15, 15)

        expr1_str = format_expression(a1, b1, c1)
        expr2_str = format_expression(a2, b2, c2)

        # [公式計算] Calculate the correct numerical answer by evaluating each part then combining
        val1 = a1 * x_val + b1 * y_val + c1
        val2 = a2 * x_val + b2 * y_val + c2
        
        if op == '+':
            answer_value = val1 + val2
            question_text_template = r"計算 $( {expr1} ) + ( {expr2} )$ 的值，當 $x = {x_val}$ 且 $y = {y_val}$ 時。"
        else: # op == '-'
            answer_value = val1 - val2
            question_text_template = r"計算 $( {expr1} ) - ( {expr2} )$ 的值，當 $x = {x_val}$ 且 $y = {y_val}$ 時。"
        
        question_text = question_text_template.replace("{expr1}", expr1_str)\
                                                .replace("{expr2}", expr2_str)\
                                                .replace("{x_val}", str(x_val))\
                                                .replace("{y_val}", str(y_val))
    
    # [數據與欄位] 返回字典必須且僅能包含 question_text, correct_answer, answer, image_base64。
    # [時間戳記] 更新時必須將 created_at 設為 datetime.now() 並遞增 version。
    return {
        "question_text": question_text,
        "correct_answer": str(answer_value), # correct_answer 必須為字串
        "answer": str(answer_value), # answer 欄位也保存相同值
        "image_base64": "", # 此技能不涉及圖形，故為空字串。
        "created_at": datetime.now().isoformat(),
        "version": "1.0.0"
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
