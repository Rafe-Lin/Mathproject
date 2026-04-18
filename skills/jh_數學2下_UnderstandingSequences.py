# ==============================================================================
# ID: jh_數學2下_UnderstandingSequences
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 47.61s | RAG: 2 examples
# Created At: 2026-01-19 14:53:08
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


# --- Core Helper Functions (輔助函式) ---

def _generate_arithmetic_sequence(a1, d, count):
    """
    接收 a1 (首項), d (公差), count (項數)。
    回傳一個包含 count 項的算術數列列表。
    """
    return [a1 + (i * d) for i in range(count)]

def _generate_geometric_sequence(a1, r, count):
    """
    接收 a1 (首項), r (公比), count (項數)。
    回傳一個包含 count 項的幾何數列列表。
    """
    return [a1 * (r**i) for i in range(count)]

def _generate_pattern_sequence(pattern_type, count, c=0, a_coeff=0, b_coeff=0):
    """
    接收 pattern_type (字串, 如 "n_squared", "2n_plus_c", "alternating_n"), 
    count (項數), c (常數), a_coeff, b_coeff。
    根據 pattern_type 生成指定項數的數列。
    """
    if pattern_type == "n_squared":
        return [n**2 for n in range(1, count + 1)]
    elif pattern_type == "n_squared_plus_c":
        return [n**2 + c for n in range(1, count + 1)]
    elif pattern_type == "linear_an_plus_b":
        return [a_coeff*n + b_coeff for n in range(1, count + 1)]
    elif pattern_type == "alternating_n":
        return [(-1)**(n+1) * n for n in range(1, count + 1)]
    elif pattern_type == "alternating_n_squared":
        return [(-1)**(n+1) * (n**2) for n in range(1, count + 1)]
    else:
        raise ValueError(f"Unknown pattern_type: {pattern_type}")

# --- generate 函式 (Generate Function) ---

def generate(level=1):
    """
    Generates a K12 math problem for the '認識數列' skill.
    Problems cover arithmetic, geometric, and other patterned sequences.
    """
    problem_types = [
        "Type 1",  # 算術數列 - 找下一項/公差 (Mirror RAG Ex 1 & 2 arithmetic model)
        "Type 2",  # 算術數列 - 找第 n 項 (Mirror RAG Ex 2 arithmetic model)
        "Type 3",  # 幾何數列 - 找下一項/公比 (Mirror RAG Ex 1 geometric model)
        "Type 4",  # 幾何數列 - 找第 n 項 (Mirror RAG Ex 1 geometric model)
        "Type 5"   # 其他模式數列 - 找下一項 (Mirror RAG Ex 1 alternating, RAG Ex 2 squared)
    ]
    
    selected_problem_type = random.choice(problem_types)

    question_text = ""
    correct_answer = ""
    image_base64 = None # As per Architect's Spec, image_base64 is None for this skill.

    if selected_problem_type == "Type 1":
        # MANDATORY MIRRORING: Uses the exact mathematical model of arithmetic sequences from RAG Ex 1 (e.g., 1, 3, 5, 7) and RAG Ex 2 (e.g., 5, 10, 15).
        # Type 1: 算術數列 - 找下一項/公差
        a1 = random.randint(-15, 15)
        d = random.choice([i for i in range(-7, 8) if i != 0]) # Ensure common difference is not zero
        num_terms_display = random.randint(3, 5) # Display 3 to 5 terms
        sequence = _generate_arithmetic_sequence(a1, d, num_terms_display + 1)
        displayed_sequence = sequence[:-1]
        next_term = sequence[-1]
        
        problem_type_subtype = random.choice(["next_term", "common_difference"])

        if problem_type_subtype == "next_term":
            question_text = r"觀察數列 $" + ", ".join(map(str, displayed_sequence)) + r", \ldots$，找出下一個數字。"
            correct_answer = str(next_term)
        elif problem_type_subtype == "common_difference":
            question_text = r"數列 $" + ", ".join(map(str, displayed_sequence)) + r", \ldots$ 是一個算術數列，找出其公差。"
            correct_answer = str(d)

    elif selected_problem_type == "Type 2":
        # MANDATORY MIRRORING: Uses the exact mathematical model of arithmetic sequences from RAG Ex 2 (e.g., 5, 10, 15).
        # Type 2: 算術數列 - 找第 n 項
        a1 = random.randint(-15, 15)
        d = random.choice([i for i in range(-7, 8) if i != 0]) # Ensure common difference is not zero
        n_term_to_find = random.randint(6, 12) # Find a term further in the sequence
        sequence = _generate_arithmetic_sequence(a1, d, n_term_to_find)
        target_term = sequence[-1]
        display_first_few = sequence[:3] # Display first 3 terms
        
        question_text = r"一個算術數列的首三項為 $" + ", ".join(map(str, display_first_few)) + r", \ldots$。求此數列的第 {n} 項。".replace("{n}", str(n_term_to_find))
        correct_answer = str(target_term)

    elif selected_problem_type == "Type 3":
        # MANDATORY MIRRORING: Uses the exact mathematical model of geometric sequences from RAG Ex 1 (e.g., 3, 9, 27).
        # Type 3: 幾何數列 - 找下一項/公比
        a1 = random.randint(1, 10) # a1 must not be zero for geometric sequence
        r = random.choice([-2, -3, 2, 3]) # Ensure common ratio is not 0, 1, or -1 for non-trivial sequences
        num_terms_display = random.randint(3, 4) # Geometric sequences grow quickly, so fewer terms displayed
        sequence = _generate_geometric_sequence(a1, r, num_terms_display + 1)
        displayed_sequence = sequence[:-1]
        next_term = sequence[-1]
        
        problem_type_subtype = random.choice(["next_term", "common_ratio"])

        if problem_type_subtype == "next_term":
            question_text = r"觀察數列 $" + ", ".join(map(str, displayed_sequence)) + r", \ldots$，找出下一個數字。"
            correct_answer = str(next_term)
        elif problem_type_subtype == "common_ratio":
            question_text = r"數列 $" + ", ".join(map(str, displayed_sequence)) + r", \ldots$ 是一個幾何數列，找出其公比。"
            correct_answer = str(r)

    elif selected_problem_type == "Type 4":
        # MANDATORY MIRRORING: Uses the exact mathematical model of geometric sequences from RAG Ex 1 (e.g., 3, 9, 27).
        # Type 4: 幾何數列 - 找第 n 項
        a1 = random.randint(1, 8)
        r = random.choice([-2, 2, 3]) # Avoid r=1 or r=-1 for more challenging sequences
        n_term_to_find = random.randint(4, 7) # Limit term number to prevent excessively large values
        sequence = _generate_geometric_sequence(a1, r, n_term_to_find)
        target_term = sequence[-1]
        display_first_few = sequence[:3]
        
        question_text = r"一個幾何數列的首三項為 $" + ", ".join(map(str, display_first_few)) + r", \ldots$。求此數列的第 {n} 項。".replace("{n}", str(n_term_to_find))
        correct_answer = str(target_term)

    elif selected_problem_type == "Type 5":
        # MANDATORY MIRRORING: Uses mathematical models like alternating sequence from RAG Ex 1 (e.g., 1, -2, 3) and squared numbers from RAG Ex 2 (e.g., 1, 4, 9).
        # Type 5: 其他模式數列 - 找下一項
        pattern_choices = ["n_squared", "n_squared_plus_c", "linear_an_plus_b", "alternating_n", "alternating_n_squared"]
        selected_pattern = random.choice(pattern_choices)
        num_terms_display = random.randint(4, 6) # Display 4 to 6 terms

        # Parameters for specific patterns
        c = 0
        a_coeff = 0
        b_coeff = 0
        
        if selected_pattern == "n_squared_plus_c":
            c = random.randint(-5, 5)
        elif selected_pattern == "linear_an_plus_b":
            a_coeff = random.randint(2, 5) # Coefficient 'a' should not be zero
            b_coeff = random.randint(-5, 5)
        
        sequence_full = _generate_pattern_sequence(selected_pattern, num_terms_display + 1, c, a_coeff, b_coeff)
        
        displayed_sequence = sequence_full[:-1]
        next_term = sequence_full[-1]
        
        question_text = r"觀察數列 $" + ", ".join(map(str, displayed_sequence)) + r", \ldots$，找出下一個數字。"
        correct_answer = str(next_term)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": None, # As per V11.8 Mirroring Enhancement, this should be image_base64. If no image, then None.
        "image_base64": image_base64, # This problem type does not include images.
        "created_at": datetime.datetime.now().isoformat(),
        "version": "1.0.0"
    }

# --- check 函式 (Check Function) ---


    """
    Robust check logic based on the Universal Check Template from System Guardrails.
    It cleans inputs, attempts numerical comparison, and falls back to string comparison.
    """
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=, ans= 等前綴
        s = s.replace("$", "").replace("\\", "") # 移除 LaTeX 符號
        return s
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 嘗試數值比對 (支援分數與小數)
    try:
        def parse_val(val_str):
            if "/" in val_str:
                n, d = map(float, val_str.split("/"))
                return n/d
            return float(val_str)
        
        # 使用 math.isclose 進行浮點數比較，以提高容錯性
        if math.isclose(parse_val(u), parse_val(c), rel_tol=1e-5):
            return {"correct": True, "result": "正確！"}
    except ValueError:
        # 如果無法轉換為數字，則跳過數值比對，直接進入字串比對
        pass
        
    # 3. 降級為字串比對
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
