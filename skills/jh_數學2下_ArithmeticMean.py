# ==============================================================================
# ID: jh_數學2下_ArithmeticMean
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 43.44s | RAG: 5 examples
# Created At: 2026-01-19 15:17:29
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
 # Added for the universal check template

# --- Helper Functions (Private) ---

def _generate_number(integer_only=False, allow_negative=True, allow_zero=True, max_abs_val=15):
    """
    [CRITICAL RULE: 數據禁絕常數]
    生成隨機數字，可控制是否為整數、是否允許負數、是否允許零，以及最大絕對值。
    為符合 K12 範圍，預設生成整數或 X.5 形式的浮點數。
    """
    # [V13.5 整數優先] 確保輸出是整數而非浮點數形式的整數
    # 確保初始值非零，之後再決定是否為零，避免生成過多重複的0
    val = random.randint(1, max_abs_val) 
    
    # 30% 機會生成 X.5 形式的浮點數，除非要求純整數
    if not integer_only and random.random() < 0.3:
        val += 0.5
    
    # 50% 機會生成負數
    if allow_negative and random.random() < 0.5:
        val *= -1
        
    # 10% 機會生成 0 (如果允許)
    if allow_zero and random.random() < 0.1:
        val = 0
        
    # 如果是浮點數但實質為整數，則轉換為整數型態
    if isinstance(val, float) and val.is_integer():
        return int(val)
    return val

def _format_number_for_display(num):
    """
    [排版與 LaTeX 安全]
    將數字格式化為適合在 LaTeX 環境中顯示的字串。
    針對 X.0 顯示為整數，X.5 顯示為小數形式。
    """
    # [V13.0 格式精確要求] 處理整數，確保回饋給學生的答案是 "(5, 4)" 而非 "(5.0, 4.0)"
    if isinstance(num, float) and num.is_integer():
        return str(int(num))
    elif isinstance(num, int):
        return str(num)
    else:
        # 對於 X.5 形式的浮點數，直接顯示為小數形式
        return str(num)

# --- Main Functions ---

def generate(level=1):
    """
    [頂層函式] 嚴禁使用 class 封裝。直接定義於模組最外層。
    [隨機分流] 內部使用 random.choice 或 if/elif 邏輯，明確對應到 RAG 中的例題。
    """
    # RAG Ex 1, 2, 3, 4 均為等差中項的直接應用。
    # Ex 1 & 3: 直接給兩數，求等差中項。
    # Ex 2 & 4: 給定等差數列三項 `a, x, b`，求 `x`。數學模型與前者相同。
    # 為了實現「rich variety of problem types」，我們增加一個代數應用題型。
    # RAG Ex 5 涉及數線上的多項等差數列，其複雜度超出單純等差中項範疇，且需要繪圖，
    # 依據 `random.choice([1, 2, 3])` 的指示，不實作此類題型。
    problem_type = random.choice([1, 2, 3]) 

    question_text = ""
    correct_answer_raw = "" # [CRITICAL RULE: Answer Data Purity] 必須是純數據 (Raw Data)
    image_base64 = None # [幾何/圖形題的特殊規範] 預設為 None，避免洩漏答案軌跡
    
    # [CRITICAL RULE: Grade & Semantic Alignment]
    # 確保題目符合國二 (jh_數學2下) 等差中項的學習範疇，涉及代數運算。

    if problem_type == 1:
        # Type 1 (Maps to RAG Ex 1 & 3): 給定兩個數，求其等差中項。
        # 數學模型: p = (a + b) / 2
        
        a = _generate_number(max_abs_val=15, allow_zero=True)
        b = _generate_number(max_abs_val=15, allow_zero=True)
        # 確保 a 和 b 不同，避免過於簡單的情況 (例如 5 和 5 的等差中項仍是 5)。
        while a == b:
            b = _generate_number(max_abs_val=15, allow_zero=True)

        mean_val = (a + b) / 2
        
        correct_answer_raw = _format_number_for_display(mean_val)

        a_str = _format_number_for_display(a)
        b_str = _format_number_for_display(b)

        # [排版與 LaTeX 安全] 嚴格使用 .replace() 模板或直接字串拼接
        # 嚴禁使用 f-string 或 % 格式化
        question_text = r"求 $" + a_str + r"$ 和 $" + b_str + r"$ 的等差中項。"

    elif problem_type == 2:
        # Type 2 (Maps to RAG Ex 2 & 4): 給定等差數列中的首項和末項，求中間項。
        # 數學模型: x = (a + b) / 2
        # 為確保生成多樣且合理的數列，先生成等差中項 (x_val) 和公差 (d_val)。
        x_val = _generate_number(max_abs_val=12, allow_zero=True)
        # 公差應為非零整數，以確保數列有變化且項之間不同。
        d_val = _generate_number(integer_only=True, allow_zero=False, max_abs_val=5) 

        a = x_val - d_val
        b = x_val + d_val
        
        correct_answer_raw = _format_number_for_display(x_val)

        a_str = _format_number_for_display(a)
        b_str = _format_number_for_display(b)

        # [排版與 LaTeX 安全]
        question_text = r"若三個數 $" + a_str + r"$, $x$, $" + b_str + r"$ 形成等差數列，則 $x$ 的值為何？"

    elif problem_type == 3:
        # Type 3 (RAG Ex 2/4 的代數應用延伸): 給定等差數列中含未知數 k 的項，求 k 的值。
        # 數學模型: (中間項的代數表達式) = (首項 + 末項) / 2
        
        A = _generate_number(max_abs_val=10, allow_zero=True)
        B = _generate_number(max_abs_val=10, allow_zero=True)
        while A == B: # 確保 A 和 B 不同
            B = _generate_number(max_abs_val=10, allow_zero=True)

        M_target = (A + B) / 2 # 等差中項的目標數值

        # 隨機生成 k 的偏移量 (可為 0)，增加題型變化
        k_offset = _generate_number(integer_only=True, allow_zero=True, max_abs_val=5)
        # 隨機決定 k 的表達形式：(k + C) 或 (C - k)
        k_form_choice = random.choice([1, 2]) 

        k_expr_str = "" # 中間項的代數表達式字串
        k_val = 0       # k 的正確答案

        if k_form_choice == 1: # 中間項形式為 'k + k_offset'
            if k_offset == 0:
                k_expr_str = r"k"
            elif k_offset > 0:
                k_expr_str = r"k + " + _format_number_for_display(k_offset)
            else: # k_offset < 0
                k_expr_str = r"k - " + _format_number_for_display(abs(k_offset))
            k_val = M_target - k_offset # 解方程式: k + k_offset = M_target => k = M_target - k_offset
        else: # 中間項形式為 'k_offset - k' 或 '-k' (當 k_offset 為 0 時)
            if k_offset == 0:
                k_expr_str = r"-k"
                k_val = -M_target # 解方程式: -k = M_target => k = -M_target
            else:
                k_expr_str = _format_number_for_display(k_offset) + r" - k"
                k_val = k_offset - M_target # 解方程式: k_offset - k = M_target => k = k_offset - M_target
            
        correct_answer_raw = _format_number_for_display(k_val)

        A_str = _format_number_for_display(A)
        B_str = _format_number_for_display(B)

        # [排版與 LaTeX 安全]
        question_text = r"若三個數 $" + A_str + r"$, $" + k_expr_str + r"$, $" + B_str + r"$ 形成等差數列，則 $k$ 的值為何？"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer_raw, # [CRITICAL RULE: Answer Data Purity]
        "answer": correct_answer_raw, # 通常用於內部顯示或除錯
        "image_base64": image_base64, # [幾何/圖形題的特殊規範]
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    """
    [強韌閱卷邏輯 (Robust Check Logic)]
    對用戶輸入進行清洗、標準化，並與標準答案進行比對。
    [V13.6 Exact Check Logic] 必須逐字複製 4-line check logic。
    """
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=, ans= 等變數前綴
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
        
        # 使用 math.isclose 進行浮點數比較，帶有相對容忍度
        if math.isclose(parse_val(u), parse_val(c), rel_tol=1e-5):
            return {"correct": True, "result": "正確！"}
    except:
        pass # 如果解析為數字失敗，則降級為字串比對
        
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
