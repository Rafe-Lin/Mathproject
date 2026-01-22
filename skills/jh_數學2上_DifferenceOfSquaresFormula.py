# ==============================================================================
# ID: jh_數學2上_DifferenceOfSquaresFormula
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 26.19s | RAG: 2 examples
# Created At: 2026-01-18 13:50:32
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


# 輔助函式：用於生成代數項的字串表示
def _get_term_str(coeff, var=None, power=1):
    """
    根據係數、變數和冪次生成代數項的字串表示。
    例如：(1, 'x', 1) -> 'x', (3, 'x', 1) -> '3x', (1, 'y', 2) -> 'y^2', (4, 'y', 2) -> '4y^2', (5) -> '5'
    """
    if var is None:
        return str(coeff) # For constant terms

    if coeff == 1 and power == 1:
        return var
    elif coeff == 1 and power > 1:
        return f"{var}^{power}"
    elif power == 1:
        return f"{coeff}{var}"
    elif power > 1:
        return f"{coeff}{var}^{power}"
    return str(coeff) # Fallback for constant (should be covered by var is None)


def generate(level=1):
    """
    根據隨機選擇的題型，生成平方差公式相關的題目。
    """
    problem_type = random.choice([1, 2, 3])
    question_text = ""
    correct_answer = ""
    image_base64 = None # 不涉及圖形，設為 None

    if problem_type == 1:
        # Type 1 (Maps to RAG Example 1): 基礎代數式展開 (ax+by)(ax-by)
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        
        # 避免變數與係數名稱衝突，並確保變數不同
        vars_pool = ['x', 'y', 'p', 'q', 'm', 'n', 'u', 'v'] 
        var1 = random.choice(vars_pool)
        
        temp_vars_pool = [v for v in vars_pool if v != var1]
        var2 = random.choice(temp_vars_pool)
        
        # 構建 LaTeX 格式的題目項
        term1_latex = f"{a}{var1}"
        term2_latex = f"{b}{var2}"

        # 題目文字使用 LaTeX 模板
        question_text_template = r"展開 $( {term1} + {term2} ) ( {term1} - {term2} )$"
        question_text = question_text_template.replace("{term1}", term1_latex).replace("{term2}", term2_latex)
        
        # 計算並格式化正確答案 (純文字，無 LaTeX)
        ans_term1 = _get_term_str(a * a, var1, 2)
        ans_term2 = _get_term_str(b * b, var2, 2)
        correct_answer = f"{ans_term1}-{ans_term2}"

    elif problem_type == 2:
        # Type 2 (Maps to RAG Example 2): 代數式與常數展開 (ax+b)(ax-b) 或 (a+bx)(a-bx)
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        var = random.choice(['x', 'y', 'z', 'p', 'q'])
        
        is_var_first_term = random.choice([True, False]) # 決定變數在第一項還是第二項

        if is_var_first_term:
            # 題型: (ax+b)(ax-b)
            term1_latex = f"{a}{var}"
            term2_latex = str(b)
            
            # 計算並格式化正確答案
            ans_term1 = _get_term_str(a * a, var, 2)
            ans_term2 = _get_term_str(b * b) # Constant term
            correct_answer = f"{ans_term1}-{ans_term2}"
        else:
            # 題型: (a+bx)(a-bx)
            term1_latex = str(a)
            term2_latex = f"{b}{var}"
            
            # 計算並格式化正確答案
            ans_term1 = _get_term_str(a * a) # Constant term
            ans_term2 = _get_term_str(b * b, var, 2)
            correct_answer = f"{ans_term1}-{ans_term2}"
            
        # 題目文字使用 LaTeX 模板 (Type 1 和 Type 2 模板相同)
        question_text_template = r"展開 $( {term1} + {term2} ) ( {term1} - {term2} )$"
        question_text = question_text_template.replace("{term1}", term1_latex).replace("{term2}", term2_latex)

    else: # problem_type == 3
        # Type 3 (Maps to RAG Example 3): 數值計算應用 (N-k)(N+k)
        base_N = random.randint(10, 100)
        # 確保 offset_k 不會導致 num1 為負或零
        offset_k = random.randint(1, min(base_N - 1, 9)) 
        
        num1 = base_N - offset_k
        num2 = base_N + offset_k

        # 題目文字使用 LaTeX 模板
        question_text_template = r"利用平方差公式計算 $ {num1} \times {num2} $"
        question_text = question_text_template.replace("{num1}", str(num1)).replace("{num2}", str(num2))
        
        # 計算並格式化正確答案 (純數字字串)
        correct_answer = str(base_N * base_N - offset_k * offset_k)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer, # 為了顯示目的 (若需要)，但 `check` 函式是關鍵
        "image_base64": image_base64,
        "created_at": datetime.datetime.now().isoformat(),
        "version": "1.0"
    }



    """
    根據「系統底層鐵律」中的通用 Check 函式模板，比對使用者答案與正確答案。
    具備強韌的閱卷邏輯，處理輸入清洗、數值比對和字串比對。
    """
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        # 移除 x=, y=, k=, ans: (大小寫不敏感)
        s = re.sub(r'(?i)(x=|y=|k=|ans:)', '', s) 
        # 移除 LaTeX 符號
        s = re.sub(r'[\$\\\{\}]', '', s)
        
        # 處理一些常見的代數表示法，使其更規範化
        s = s.replace('^1', '') # x^1 -> x
        s = s.replace('+-', '-') # a+-b -> a-b
        
        # 簡單處理前導加號，如果存在
        if s.startswith('+'):
            s = s[1:]
        
        # 對於代數式，我們需要更智能的規範化來處理項的順序
        # 但在 K12階段，通常期望特定規範形式。
        # 此處的 clean 函數會盡力將用戶輸入轉換為與正確答案相同的規範形式。
        # 例如，'9x^2-4y^2' 和 '-4y^2+9x^2' 經過此 clean 函數後仍可能不同
        # 除非進行更複雜的代數解析 (e.g., 轉換為字典或 AST)。
        # 依照規範，correct_answer 已是規範形式，故我們期望用戶輸入經清洗後能直接匹配。
        
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
        
        # 只有當清洗後的字串看起來像數字時才嘗試數值比對
        if re.fullmatch(r"[-+]?\d+(\.\d+)?(/[+-]?\d+)?", u) and \
           re.fullmatch(r"[-+]?\d+(\.\d+)?(/[+-]?\d+)?", c):
            if math.isclose(parse_val(u), parse_val(c), rel_tol=1e-5):
                return {"correct": True, "result": "正確！"}
    except ValueError:
        # 如果解析失敗，說明不是純數字，降級到字串比對
        pass
        
    # 3. 降級為字串比對 (這是代數表達式和非嚴格數值匹配的主要方式)
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
