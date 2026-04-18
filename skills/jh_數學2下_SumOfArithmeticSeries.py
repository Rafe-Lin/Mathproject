# ==============================================================================
# ID: jh_數學2下_SumOfArithmeticSeries
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 30.34s | RAG: 5 examples
# Created At: 2026-01-19 15:21:00
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
import base64 # For image_base64, will be empty for this skill

# V10.2 座標平面專用硬化規格: A. 資料結構鎖死 (Prevent Unpacking Error)
# 此技能不涉及座標，但依據規範仍需定義此函式。
def _generate_coordinate_value():
    """
    統一回傳固定格式：(float_val, (int_part, num, den, is_neg))。
    若為整數，num 與 den 設為 0；若為分數，則 int_part 為帶分數整數部。
    此為等差級數的和技能的佔位符，實際不使用。
    """
    return (0.0, (0, 0, 0, False)) # Dummy return as coordinates are not used

# 視覺化輔助函式 (Visualisation Helper - Not used for this skill but required to be defined)
def _draw_coordinate_plane(points, x_range, y_range, x_ticks, y_ticks, labels, title=""):
    """
    此技能為純數字計算題，不需繪製座標平面。
    依據規範，繪圖函式僅能接收「題目已知數據」，嚴禁傳入「答案數據」。
    若題目要求畫圖但無法自動批改，則將 image_base64 設為模板或空值。
    """
    # 返回空的 base64 字符串，符合「防洩漏原則」
    return ""

def _format_fraction_latex(numerator, denominator):
    """
    將分數格式化為 LaTeX 字串，避免使用 f-string 導致 LaTeX 語法衝突。
    """
    if denominator == 1:
        return str(numerator)
    elif numerator == 0:
        return "0"
    else:
        sign = "-" if numerator * denominator < 0 else ""
        abs_num = abs(numerator)
        abs_den = abs(denominator)
        
        # 簡化分數
        common_divisor = math.gcd(abs_num, abs_den)
        abs_num //= common_divisor
        abs_den //= common_divisor

        if abs_den == 1: # 簡化後變為整數
            return f"{sign}{abs_num}"
        elif abs_num >= abs_den: # 處理帶分數
            integer_part = abs_num // abs_den
            remainder = abs_num % abs_den
            if remainder == 0: # 簡化後變為整數
                return f"{sign}{integer_part}"
            else:
                # 使用 replace 避免 f-string 與 LaTeX 衝突
                template = r"{sign_val}{integer_val}\frac{{{num_val}}}{{{den_val}}}"
                return template.replace("{sign_val}", sign).replace("{integer_val}", str(integer_part)).replace("{num_val}", str(remainder)).replace("{den_val}", str(abs_den))
        else: # 處理真分數
            template = r"{sign_val}\frac{{{num_val}}}{{{den_val}}}"
            return template.replace("{sign_val}", sign).replace("{num_val}", str(abs_num)).replace("{den_val}", str(abs_den))


### 核心生成函式 (Core Generation Function)
def generate(level=1):
    # 題型鏡射 (Problem Mirroring): 隨機分流至不同題型
    # Type 1 (Maps to Example 1): 已知首項、公差、項數，求和。
    # Type 2 (Maps to Example 2): 已知首項、末項、項數，求和。
    # Type 3 (Maps to Example 3): 已知首項、公差、和，求項數 (涉及解一元二次方程式)。
    # Type 4 (Maps to Example 4): 應用題，將實際情境轉化為等差級數求和。
    problem_type = random.choice([1, 2, 3, 4])

    question_text = ""
    correct_answer = ""
    image_base64 = "" # 此技能為純數字計算題，無圖形

    if problem_type == 1:
        # Type 1 (Maps to Example 1): 已知首項 (a1)、公差 (d)、項數 (n)，求和 (Sn)。
        # 數據禁絕常數: 隨機生成所有數據
        a1 = random.randint(-20, 20)
        d = random.randint(-5, 5)
        while d == 0: # 公差不能為 0
            d = random.randint(-5, 5)
        n = random.randint(5, 25) # 項數

        # 公式計算: Sn = n/2 * (2*a1 + (n-1)*d)
        sum_val_numerator = n * (2 * a1 + (n - 1) * d)
        sum_val_denominator = 2
        
        # 確保和為整數或可表示為簡單分數
        if sum_val_numerator % sum_val_denominator == 0:
            sum_val = sum_val_numerator // sum_val_denominator
            correct_answer = str(sum_val)
        else:
            # 如果是分數，簡化分數
            common_divisor = math.gcd(sum_val_numerator, sum_val_denominator)
            sum_val_numerator //= common_divisor
            sum_val_denominator //= common_divisor
            correct_answer = f"{sum_val_numerator}/{sum_val_denominator}" # 純數據格式

        # 排版與 LaTeX 安全: 嚴禁使用 f-string 格式化 LaTeX
        question_text_template = r"有一個等差級數，其首項為 ${a1}$，公差為 ${d}$，項數為 ${n}$。請問此等差級數的和是多少？"
        question_text = question_text_template.replace("{a1}", str(a1)).replace("{d}", str(d)).replace("{n}", str(n))

    elif problem_type == 2:
        # Type 2 (Maps to Example 2): 已知首項 (a1)、末項 (an)、項數 (n)，求和 (Sn)。
        # 數據禁絕常數: 隨機生成 a1, d, n，再計算 an 以確保一致性
        a1 = random.randint(-20, 20)
        d = random.randint(-5, 5)
        while d == 0:
            d = random.randint(-5, 5)
        n = random.randint(5, 25)

        an = a1 + (n - 1) * d # 計算末項
        
        # 公式計算: Sn = n/2 * (a1 + an)
        sum_val_numerator = n * (a1 + an)
        sum_val_denominator = 2

        if sum_val_numerator % sum_val_denominator == 0:
            sum_val = sum_val_numerator // sum_val_denominator
            correct_answer = str(sum_val)
        else:
            common_divisor = math.gcd(sum_val_numerator, sum_val_denominator)
            sum_val_numerator //= common_divisor
            sum_val_denominator //= common_divisor
            correct_answer = f"{sum_val_numerator}/{sum_val_denominator}"

        question_text_template = r"有一個等差級數，其首項為 ${a1}$，末項為 ${an}$，項數為 ${n}$。請問此等差級數的和是多少？"
        question_text = question_text_template.replace("{a1}", str(a1)).replace("{an}", str(an)).replace("{n}", str(n))

    elif problem_type == 3:
        # Type 3 (Maps to Example 3): 已知首項 (a1)、公差 (d)、和 (Sn)，求項數 (n)。
        # 邏輯驗證硬化規約: 強制運算
        # 先生成 a1, d, n_correct，再計算 Sn，確保 n_correct 為有效解。
        a1 = random.randint(-10, 10)
        d = random.randint(-4, 4)
        while d == 0:
            d = random.randint(-4, 4)
        n_correct = random.randint(5, 15) # 正確的項數

        # 計算 Sn
        sn_val_numerator = n_correct * (2 * a1 + (n_correct - 1) * d)
        sn_val_denominator = 2
        
        # Ensure Sn is an integer for K12 context when finding n.
        # If n_correct is odd and (2*a1 + (n_correct-1)*d) is odd, Sn would be X.5.
        # Adjust a1 to make (2*a1 + (n_correct-1)*d) even.
        if n_correct % 2 != 0 and (2 * a1 + (n_correct - 1) * d) % 2 != 0:
            a1 += 1 # Adjust a1 to make the term even
            sn_val_numerator = n_correct * (2 * a1 + (n_correct - 1) * d)
        
        sn_val = sn_val_numerator // sn_val_denominator # Sn should now always be an integer
        sn_display = str(sn_val)

        question_text_template = r"一個等差級數的首項為 ${a1}$，公差為 ${d}$，其和為 ${sn}$。請問此等差級數的項數是多少？"
        question_text = question_text_template.replace("{a1}", str(a1)).replace("{d}", str(d)).replace("{sn}", sn_display)
        correct_answer = str(n_correct) # 純數據格式

    elif problem_type == 4:
        # Type 4 (Maps to Example 4): 應用題 (例如：堆疊木材、鐘聲次數)
        # 選擇堆疊木材問題
        first_layer_logs = random.randint(8, 15) # 最底層木材數量 (a1)
        diff_per_layer = random.randint(1, 3) # 每層減少的數量 (abs(d))
        num_layers = random.randint(5, 10) # 總層數 (n)

        d = -diff_per_layer # 每層減少，公差為負

        # 確保最上層的木材數量為正數 (a_n > 0)
        # an = a1 + (n-1)*d
        while first_layer_logs + (num_layers - 1) * d <= 0:
            first_layer_logs = random.randint(8, 15)
            diff_per_layer = random.randint(1, 3)
            num_layers = random.randint(5, 10)
            d = -diff_per_layer

        # 計算總木材數量 Sn
        sum_logs_numerator = num_layers * (2 * first_layer_logs + (num_layers - 1) * d)
        sum_logs_denominator = 2
        sum_logs = sum_logs_numerator // sum_logs_denominator # 總數必然為整數

        question_text_template = r"某建築工地堆放一批木材，最底層有 ${first_layer}$ 根，往上每一層比下一層少 ${diff}$ 根，總共有 ${num_layers}$ 層。請問這批木材總共有多少根？"
        question_text = question_text_template.replace("{first_layer}", str(first_layer_logs)).replace("{diff}", str(diff_per_layer)).replace("{num_layers}", str(num_layers))
        correct_answer = str(sum_logs) # 純數據格式

    # 數據與欄位: 鎖死回傳字典欄位
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer, # 依據規範，此欄位與 correct_answer 相同
        "image_base64": image_base64, # 無圖形，因此為空字串
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


### 批改函式 (Check Function)
# 遵循 "通用 Check 函式模板 (Universal Check Template)"

    import re, math
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=
        s = s.replace("$", "").replace("\\", "")
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
        
        if math.isclose(parse_val(u), parse_val(c), rel_tol=1e-5, abs_tol=1e-9):
            return {"correct": True, "result": "正確！"}
    except:
        pass # 如果解析失敗，則進入字串比對

    # 3. 降級為字串比對 (例如，答案是文字或無法解析的數學表達式)
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
