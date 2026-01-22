# ==============================================================================
# ID: jh_數學2上_PolynomialFactorization
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 52.28s | RAG: 3 examples
# Created At: 2026-01-19 10:23:12
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

# Helper Functions
def _generate_coefficient(min_val=-7, max_val=7):
    """
    目的: 生成因式分解中常用的係數或常數項。
    回傳: int。
    """
    return random.randint(min_val, max_val)

def _generate_non_zero_coefficient(min_val=-5, max_val=5):
    """
    目的: 生成非零的係數，用於避免生成退化（如 0x^2）或過於簡單的題目。
    回傳: int (保證非零)。
    """
    while True:
        coeff = random.randint(min_val, max_val)
        if coeff != 0:
            return coeff

def _generate_positive_integer(min_val=2, max_val=9):
    """
    目的: 生成正整數，常用於平方差公式中的 k 值。
          根據 Type 2 和 Type 3 描述，k 值範圍為 2 到 9。
    回傳: int (保證正數)。
    """
    return random.randint(min_val, max_val)

def _generate_integer_pair_for_product_sum(min_val=-6, max_val=6):
    """
    目的: 生成兩個整數 p, q，用於十字交乘法中構成和與積。
          確保 p 和 q 是相異整數，以符合 Type 4 的描述。
    回傳: (int, int)。
    """
    p = random.randint(min_val, max_val)
    while True: # Ensure q is distinct from p
        q = random.randint(min_val, max_val)
        if p != q:
            break
    return p, q

# Universal Check Template (as provided in CRITICAL CODING STANDARDS)

    """
    檢查使用者答案與正確答案是否一致。
    實作輸入清洗、數值序列比對及嚴格順序比對。
    """
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        # 移除 LaTeX 符號, 變數前綴及特定關鍵字
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=, a=, ans= 等
        s = re.sub(r'[\\$}{]', '', s) # 移除 LaTeX $ \ { }
        s = s.replace("ans:", "")     # 移除 "ans:"
        return s
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 數值序列比對 (V12.6 邏輯驗證硬化規約)
    # 支援逗號、分號或空白字元分割
    u_parts = [part for part in re.split(r'[,;\s]+', u) if part]
    c_parts = [part for part in re.split(r'[,;\s]+', c) if part]

    # 嘗試將分量轉換為浮點數
    try:
        u_vals = [float(part) for part in u_parts]
        c_vals = [float(part) for part in c_parts]
    except ValueError:
        # 若無法解析為數字，退化為字串比對 (但對本題型通常表示錯誤)
        if u == c: return {"correct": True, "result": "正確！"}
        return {"correct": False, "result": f"答案錯誤。無法解析為數字序列。"}

    # 比較序列長度
    if len(u_vals) != len(c_vals):
        return {"correct": False, "result": f"答案錯誤。數字序列長度不符。"}

    # 嚴格的順序比對 (V12.6 邏輯驗證硬化規約)
    for i in range(len(u_vals)):
        # 使用 math.isclose 處理浮點數精度問題
        if not math.isclose(u_vals[i], c_vals[i], rel_tol=1e-9, abs_tol=1e-9):
            return {"correct": False, "result": f"答案錯誤。序列中的第 {i+1} 個數字不正確或順序錯誤。"}
            
    return {"correct": True, "result": "正確！"}


def generate(level=1):
    """
    生成因式分解題目，隨機選擇五種題型之一。
    """
    problem_type = random.randint(1, 5)
    
    question_text = ""
    correct_answer = ""
    answer = "" # 詳解
    
    if problem_type == 1:
        # Type 1: 提取公因式 (Maps to Example: RAG Ex 1)
        common_factor_val = random.randint(2, 5) # 共同因數的數值部分
        a_prime = _generate_non_zero_coefficient()
        b_prime = _generate_non_zero_coefficient()
        
        a = a_prime * common_factor_val
        b = b_prime * common_factor_val
        
        var = random.choice(['x', 'y'])
        
        question_template = r"因式分解 ${a}{var}^2 + {b}{var} = {common_factor_val}{var}(A{var} + B)$，其中 $A$ 和 $B$ 為常數。請將 $A$ 和 $B$ 依序填入。"
        question_text = question_template.replace("{a}", str(a))\
                                         .replace("{b}", str(b))\
                                         .replace("{var}", var)\
                                         .replace("{common_factor_val}", str(common_factor_val))
        
        correct_answer = f"{a_prime},{b_prime}"
        answer = f"${a}{var}^2 + {b}{var} = {common_factor_val}{var}({a_prime}{var} + {b_prime})$"

    elif problem_type == 2:
        # Type 2: 平方差公式 (Maps to Example: RAG Ex 2)
        k = _generate_positive_integer() # k from 2 to 9
        k_sq = k * k
        
        question_template = r"因式分解 $x^2 - {k_sq} = (x+A)(x-B)$，其中 $A$ 和 $B$ 為正常數。請將 $A$ 和 $B$ 依序填入。"
        question_text = question_template.replace("{k_sq}", str(k_sq))
        
        correct_answer = f"{k},{k}"
        answer = f"$x^2 - {k_sq} = (x+{k})(x-{k})$"

    elif problem_type == 3:
        # Type 3: 完全平方公式 (Maps to Example: RAG Ex 3)
        k = _generate_positive_integer() # k from 2 to 9
        sign = random.choice([-1, 1]) # 決定中間項的正負
        
        b_coeff = 2 * k * sign
        c_coeff = k * k
        
        b_sign_str = '+' if sign == 1 else '-'
        b_coeff_abs_str = str(abs(b_coeff))
        
        question_template = r"因式分解 $x^2 {b_sign} {b_coeff_abs}x + {c_coeff} = (x+A)^2$，其中 $A$ 為常數。請填入 $A$。"
        question_text = question_template.replace("{b_sign}", b_sign_str)\
                                         .replace("{b_coeff_abs}", b_coeff_abs_str)\
                                         .replace("{c_coeff}", str(c_coeff))
        
        correct_answer = str(k * sign)
        answer = f"$x^2 {b_sign_str} {abs(b_coeff)}x + {c_coeff} = (x{b_sign_str}{k})^2$"

    elif problem_type == 4:
        # Type 4: 十字交乘法 x^2+bx+c
        p, q = _generate_integer_pair_for_product_sum() # p, q 相異整數
        b = p + q
        c = p * q
        
        # 手動構建多項式字串，處理係數為 1、-1 或 0 的情況 (遵循方程式生成鎖死規範)
        poly_parts = ["x^2"]
        if b != 0:
            if b == 1:
                poly_parts.append("+x")
            elif b == -1:
                poly_parts.append("-x")
            elif b > 0:
                poly_parts.append(f"+{b}x")
            else: # b < 0
                poly_parts.append(f"-{abs(b)}x")
        
        if c != 0:
            if c > 0:
                poly_parts.append(f"+{c}")
            else: # c < 0
                poly_parts.append(f"-{abs(c)}")
        
        polynomial_str = "".join(poly_parts)
        # 移除開頭可能多餘的 '+' 號
        if polynomial_str.startswith("+"):
            polynomial_str = polynomial_str[1:]
        
        question_template = r"因式分解 ${polynomial_str} = (x+A)(x+B)$，其中 $A$ 和 $B$ 為常數。請將 $A$ 和 $B$ 依序填入（先填較小者，再填較大者）。"
        question_text = question_template.replace("{polynomial_str}", polynomial_str)
        
        correct_answer = f"{min(p, q)},{max(p, q)}"
        answer = f"${polynomial_str} = (x+{p})(x+{q})$"

    elif problem_type == 5:
        # Type 5: 十字交乘法 ax^2+bx+c
        # 生成四個非零整數，並確保 a != 1 以區分 Type 4
        while True:
            p_coeff = _generate_non_zero_coefficient(min_val=-3, max_val=3)
            r_coeff = _generate_non_zero_coefficient(min_val=-3, max_val=3)
            q_const = _generate_non_zero_coefficient(min_val=-5, max_val=5)
            s_const = _generate_non_zero_coefficient(min_val=-5, max_val=5)
            
            a = p_coeff * r_coeff
            b = p_coeff * s_const + q_const * r_coeff
            c = q_const * s_const
            
            # 確保 'a' 不為 1 或 -1 (避免與 Type 4 重複或過於簡單)
            if abs(a) > 1:
                break
        
        # 正規化因式 (Ax+B)(Cx+D)：A, C 為正數；若 A=C 則 B<D
        factors_raw = [(p_coeff, q_const), (r_coeff, s_const)]
        
        # 確保每個因式的第一個係數為正數
        normalized_factors = []
        for coeff, const in factors_raw:
            if coeff < 0:
                normalized_factors.append((-coeff, -const))
            else:
                normalized_factors.append((coeff, const))
        
        # 對因式進行排序以確保唯一性 (A,B) vs (C,D) -> A < C OR (A == C AND B < D)
        normalized_factors.sort() 
        
        A, B = normalized_factors[0]
        C, D = normalized_factors[1]
        
        # 手動構建多項式字串 (遵循方程式生成鎖死規範)
        poly_parts = []
        if a != 0:
            if abs(a) == 1 and a > 0: # a=1
                poly_parts.append("x^2")
            elif abs(a) == 1 and a < 0: # a=-1
                poly_parts.append("-x^2")
            else:
                poly_parts.append(f"{a}x^2")
        
        if b != 0:
            if b > 0:
                if b == 1: # b=1
                    poly_parts.append("+x")
                else:
                    poly_parts.append(f"+{b}x")
            else: # b < 0
                if b == -1: # b=-1
                    poly_parts.append("-x")
                else:
                    poly_parts.append(f"-{abs(b)}x")
        
        if c != 0:
            if c > 0:
                poly_parts.append(f"+{c}")
            else: # c < 0
                poly_parts.append(f"-{abs(c)}")
        
        polynomial_str = "".join(poly_parts)
        # 移除開頭可能多餘的 '+' 號
        if polynomial_str.startswith("+"):
            polynomial_str = polynomial_str[1:]
        
        question_template = r"因式分解 ${polynomial_str} = (Ax+B)(Cx+D)$，其中 $A, B, C, D$ 為常數。請將 $A, B, C, D$ 依序填入（$A$ 和 $C$ 為正數，且若 $A=C$，則 $B<D$）。"
        question_text = question_template.replace("{polynomial_str}", polynomial_str)
        
        correct_answer = f"{A},{B},{C},{D}"

        # 詳解字串構建
        B_str = f"+{B}" if B >= 0 else f"{B}"
        D_str = f"+{D}" if D >= 0 else f"{D}"
        answer = f"${polynomial_str} = ({A}x{B_str})({C}x{D_str})$"

    # 輸出格式
    return {
        "question_text": question_text,
        "correct_answer": correct_answer, # 純數字字串
        "answer": answer, # 詳解，供前端顯示
        "image_base64": None, # 因式分解不含圖片
        "created_at": datetime.now().isoformat(), # ISO 格式時間戳
        "version": "1.0"
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
