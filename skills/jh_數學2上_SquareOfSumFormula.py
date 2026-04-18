# ==============================================================================
# ID: jh_數學2上_SquareOfSumFormula
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 38.37s | RAG: 3 examples
# Created At: 2026-01-18 13:42:48
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
 # Import math for numerical comparison in check function

# 輔助函式：用於安全的 LaTeX 字符串替換，避免 f-string 與 LaTeX 大括號衝突
def _latex_safe_replace(template, replacements):
    """
    安全地替換 LaTeX 模板中的佔位符。
    範例: _latex_safe_replace(r"$(x + {a})^2$", {"a": 3}) -> "$(x + 3)^2$"
    """
    for key, value in replacements.items():
        # 確保值被轉換為字符串，並使用 .replace() 避免 f-string 與 LaTeX 大括號衝突
        template = template.replace("{" + key + "}", str(value))
    return template

def generate(level=1):
    """
    根據和的平方公式生成 K12 數學題目。

    Args:
        level (int): 題目難度等級 (目前未使用，預留)。

    Returns:
        dict: 包含題目文字、正確答案、詳解、圖片Base64等資訊的字典。
    """
    # 🛡️ MANDATORY MIRRORING RULES (最高權限指令) - STRICT MAPPING:
    # 根據 RAG 範例，所有題目都屬於數值計算。
    # RAG Ex 1 & 2: 計算 $(N+a)^2$
    # RAG Ex 3: 計算 $A^2+2AB+B^2$
    problem_type = random.choice([1, 2]) # 1: 對應 RAG Ex 1 & 2; 2: 對應 RAG Ex 3

    question_text = ""
    correct_answer = "" # 嚴禁包含 LaTeX 符號、變數名稱、單位或說明文字
    solution_text = ""  # 包含 LaTeX 符號及詳解說明
    image_base64 = None # 此題型無圖片，設為 None

    # --- 題型隨機分流與數據動態化 ---
    if problem_type == 1:
        # Type 1 (Maps to RAG Ex 1 & 2): 數值計算 $(N+a)^2$
        # RAG 例題範例: 利用和的平方公式計算 $504^2$ 的值。
        N_base_choices = [10, 20, 30, 40, 50, 100, 200, 300, 400, 500]
        N_base = random.choice(N_base_choices)
        a = random.randint(1, 9) # 附加數，通常為個位數，以符合 (N+a)^2 的心算結構

        num_to_square = N_base + a # 要平方的數字

        question_text_template = r"利用和的平方公式 $(a+b)^2 = a^2+2ab+b^2$，計算 ${num}^2$ 的值。"
        question_text = _latex_safe_replace(question_text_template, {"num": num_to_square})

        result = num_to_square * num_to_square # 計算結果

        correct_answer = str(result) # CRITICAL RULE: Answer Data Purity - 純數據
        solution_text_template = (
            r"${num}^2 = ({N_base} + {a})^2$"
            r"$ = {N_base}^2 + 2 \times {N_base} \times {a} + {a}^2$"
            r"$ = {N_base_sq} + {two_Nab} + {a_sq}$"
            r"$ = {result}$。"
        )
        solution_text = _latex_safe_replace(solution_text_template, {
            "num": num_to_square,
            "N_base": N_base,
            "a": a,
            "N_base_sq": N_base * N_base,
            "two_Nab": 2 * N_base * a,
            "a_sq": a * a,
            "result": result
        })

    elif problem_type == 2:
        # Type 2 (Maps to RAG Ex 3): 數值計算 $A^2+2AB+B^2$
        # RAG 例題範例: 利用和的平方公式計算 $45^2+2 \times 45 \times 5+5^2$ 的值。
        A_val = random.randint(10, 90) # A 的值，通常為十位數或以上
        B_val = random.randint(1, 10) # B 的值，通常為個位數

        # 確保 A 和 B 數值合理，避免過於簡單或複雜的組合
        if A_val % 10 == 0 and B_val == 0: # 避免 (X0 + 0)^2 這種情況
             B_val = random.randint(1, 10)
        
        # 確保 A, B 範圍在合理區間，即使 random.randint 已經提供了保障
        if A_val < 10: A_val = 10
        if B_val < 1: B_val = 1

        question_text_template = (
            r"利用和的平方公式 $a^2+2ab+b^2 = (a+b)^2$，計算 ${A_val}^2+2 \times {A_val} \times {B_val}+{B_val}^2$ 的值。"
        )
        question_text = _latex_safe_replace(question_text_template, {
            "A_val": A_val,
            "B_val": B_val
        })

        result = (A_val + B_val) * (A_val + B_val) # 計算結果

        correct_answer = str(result) # CRITICAL RULE: Answer Data Purity - 純數據
        solution_text_template = (
            r"${A_val}^2+2 \times {A_val} \times {B_val}+{B_val}^2$"
            r"$ = ({A_val}+{B_val})^2$"
            r"$ = ({sum_AB})^2$"
            r"$ = {result}$。"
        )
        solution_text = _latex_safe_replace(solution_text_template, {
            "A_val": A_val,
            "B_val": B_val,
            "sum_AB": A_val + B_val,
            "result": result
        })

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "solution_text": solution_text,
        "image_base64": image_base64,
        "created_at": datetime.datetime.now().isoformat(),
        "version": "V11.8"
    }


    """
    檢查使用者答案是否正確。

    Args:
        user_answer (str): 使用者輸入的答案。
        correct_answer (str): `generate` 函式產生的純數據正確答案。

    Returns:
        bool: 如果答案正確則為 True，否則為 False。
    """
    # ⛔ 系統底層鐵律 (不可違背):
    # 遵循「閱卷決定論」和「通用 Check 函式模板」的邏輯，
    # 但根據 `generate` 函式簽名和「閱卷與反饋」規則，返回 `bool` 類型。

    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y= 等前綴
        s = s.replace("$", "").replace("\\", "") # 移除 LaTeX 符號
        s = s.replace(",", "") # 移除逗號，因為答案是單一數值
        return s
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 嘗試數值比對 (支援分數與小數)
    try:
        def parse_val(val_str):
            # 題目答案為整數，但使用者可能輸入小數或分數
            if "/" in val_str:
                n, d = map(float, val_str.split("/"))
                return n/d
            return float(val_str)
        
        # 使用 math.isclose 進行浮點數比較，考慮精度問題
        if math.isclose(parse_val(u), parse_val(c), rel_tol=1e-5):
            return True
    except ValueError:
        # 如果解析為浮點數失敗，則該輸入不是有效數字，無法進行數值比對
        pass
        
    # 3. 降級為字串比對 (作為最終的後備方案)
    if u == c: 
        return True
    
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
