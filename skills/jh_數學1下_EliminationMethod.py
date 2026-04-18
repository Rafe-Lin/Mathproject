# ==============================================================================
# ID: jh_數學1下_EliminationMethod
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 67.80s | RAG: 3 examples
# Created At: 2026-01-15 13:21:00
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
import base64
# import matplotlib.pyplot as plt # 暫時不啟用圖形生成，若需要可解除註解
# from io import BytesIO # 暫時不啟用圖形生成，若需要可解除註解

# --- Helper Functions (通用規範: [必須回傳], [類型一致], [防洩漏原則]) ---

def _generate_coefficients_and_solution(level, problem_type):
    """
    根據問題類型和難度等級生成聯立方程式的係數和解。
    遵循 [數據禁絕常數]：首先生成解 (x, y)，然後反向計算係數。
    確保係數和解在 K12 範圍內，並避免生成退化或過於簡單的方程式。
    回傳 (a1, b1, c1, a2, b2, c2, x_ans, y_ans)。
    """
    # 隨機生成整數解 x 和 y
    # K12 範圍通常為 -5 到 5
    x_ans = random.randint(-5, 5)
    y_ans = random.randint(-5, 5)

    # 確保非特殊情況下解不全為 (0,0)
    if problem_type != 4:
        while x_ans == 0 and y_ans == 0:
            x_ans = random.randint(-5, 5)
            y_ans = random.randint(-5, 5)

    # 係數範圍設定為 K12 適用的較小整數
    coeff_range_a = (1, 5)
    coeff_range_b = (1, 5)
    
    a1, b1, a2, b2 = 0, 0, 0, 0
    c1, c2 = 0, 0

    if problem_type == 1:  # Type 1 (Maps to RAG Example 1): 直接消去 (相同或相反係數)
        # 決定是加法消去 (b1 = -b2) 還是減法消去 (b1 = b2)
        if random.choice([True, False]): # 加法消去 (係數互為相反數)
            b1 = random.randint(*coeff_range_b) * random.choice([-1, 1])
            b2 = -b1
        else: # 減法消去 (係數相同)
            b1 = random.randint(*coeff_range_b) * random.choice([-1, 1])
            b2 = b1
        
        # 確保 a1, b1, a2, b2 不會導致無限多解或無解 (即行列式不為零)
        # 並避免所有係數為零的退化情況
        while True:
            a1 = random.randint(*coeff_range_a) * random.choice([-1, 1])
            a2 = random.randint(*coeff_range_a) * random.choice([-1, 1])
            
            # 避免方程式退化為 0=C
            if a1 == 0 and b1 == 0: continue
            if a2 == 0 and b2 == 0: continue

            # 檢查行列式 (a1*b2 - a2*b1) 是否為 0，若為 0 則係數成比例，會導致無限多解或無解
            determinant = a1 * b2 - a2 * b1
            if determinant == 0: 
                continue # 重新生成 a1, a2
            break # 係數不成比例，保證唯一解

        c1 = a1 * x_ans + b1 * y_ans
        c2 = a2 * x_ans + b2 * y_ans

    elif problem_type == 2:  # Type 2 (Maps to RAG Example 2): 單邊乘法消去
        # 選擇要消去的變數 (x 或 y)
        if random.choice([True, False]): # 消去 y
            # 確保 b2 是 b1 的倍數 (或 b1 是 b2 的倍數)，且倍數不為 1 或 -1
            b_base = random.randint(1, 3) * random.choice([-1, 1])
            multiplier = random.randint(2, 4) * random.choice([-1, 1])
            b1 = b_base
            b2 = b_base * multiplier
            
            # 確保 a1, b1, a2, b2 不會導致無限多解或無解 (即行列式不為零)
            while True:
                a1 = random.randint(*coeff_range_a) * random.choice([-1, 1])
                a2 = random.randint(*coeff_range_a) * random.choice([-1, 1])
                
                # 避免方程式退化為 0=C
                if a1 == 0 and b1 == 0: continue
                if a2 == 0 and b2 == 0: continue

                determinant = a1 * b2 - a2 * b1
                if determinant == 0:
                    continue
                # 避免 a 的係數也剛好成倍數關係，導致變成 Type 1
                if (a1 != 0 and a2 != 0) and (a1 % a2 == 0 or a2 % a1 == 0) and (abs(a1) != abs(a2)):
                    # 如果 a 的係數也成倍數關係，但不是直接相等或相反，可以接受
                    # 我們主要避免同時消去 x 和 y (即 a1/a2 = b1/b2 = multiplier)
                    if a1 * multiplier == a2: # This means a1/a2 = 1/multiplier, and b1/b2 = 1/multiplier
                         continue # This would be a Type 4 problem (if c1/c2 also matches) or Type 1
                break
        else: # 消去 x
            # 確保 a2 是 a1 的倍數 (或 a1 是 a2 的倍數)，且倍數不為 1 或 -1
            a_base = random.randint(1, 3) * random.choice([-1, 1])
            multiplier = random.randint(2, 4) * random.choice([-1, 1])
            a1 = a_base
            a2 = a_base * multiplier

            # 確保 a1, b1, a2, b2 不會導致無限多解或無解 (即行列式不為零)
            while True:
                b1 = random.randint(*coeff_range_b) * random.choice([-1, 1])
                b2 = random.randint(*coeff_range_b) * random.choice([-1, 1])
                
                # 避免方程式退化為 0=C
                if a1 == 0 and b1 == 0: continue
                if a2 == 0 and b2 == 0: continue

                determinant = a1 * b2 - a2 * b1
                if determinant == 0:
                    continue
                # 避免 b 的係數也剛好成倍數關係
                if (b1 != 0 and b2 != 0) and (b1 % b2 == 0 or b2 % b1 == 0) and (abs(b1) != abs(b2)):
                    if b1 * multiplier == b2:
                        continue
                break

        c1 = a1 * x_ans + b1 * y_ans
        c2 = a2 * x_ans + b2 * y_ans

    elif problem_type == 3:  # Type 3 (Maps to RAG Example 3): 雙邊乘法消去
        # 確保兩個係數都不是對方的倍數，需要雙邊乘法
        # 同時確保 (a1, b1) 與 (a2, b2) 不成比例，保證唯一解
        while True:
            a1 = random.randint(2, 5) * random.choice([-1, 1])
            b1 = random.randint(2, 5) * random.choice([-1, 1])
            a2 = random.randint(2, 5) * random.choice([-1, 1])
            b2 = random.randint(2, 5) * random.choice([-1, 1])

            # 避免方程式退化為 0=C
            if a1 == 0 and b1 == 0: continue
            if a2 == 0 and b2 == 0: continue

            # 檢查是否為無限多解或無解情況 (係數成比例)
            determinant = a1 * b2 - a2 * b1
            if determinant == 0:
                continue

            # 確保 a1, a2 之間不成倍數關係 (除了 +/-1)
            # 確保 b1, b2 之間不成倍數關係 (除了 +/-1)
            # 這樣才能保證是雙邊乘法
            if (a1 % a2 == 0 and abs(a1 // a2) != 1) or \
               (a2 % a1 == 0 and abs(a2 // a1) != 1) or \
               (b1 % b2 == 0 and abs(b1 // b2) != 1) or \
               (b2 % b1 == 0 and abs(b2 // b1) != 1):
                continue
            
            # 確保係數絕對值大於 1，以區別於 Type 1 和 Type 2
            if abs(a1) == 1 or abs(b1) == 1 or abs(a2) == 1 or abs(b2) == 1:
                 continue

            break # 滿足所有條件

        c1 = a1 * x_ans + b1 * y_ans
        c2 = a2 * x_ans + b2 * y_ans

    elif problem_type == 4:  # Type 4 (特殊情況: 無解 / 無限多解)
        is_no_solution = random.choice([True, False]) # 隨機決定是無解還是無限多解

        a1 = random.randint(*coeff_range_a) * random.choice([-1, 1])
        b1 = random.randint(*coeff_range_b) * random.choice([-1, 1])
        c1 = random.randint(-10, 10) # 常數項可以稍大

        # 確保 a1, b1 不同時為 0
        while a1 == 0 and b1 == 0:
            a1 = random.randint(*coeff_range_a) * random.choice([-1, 1])
            b1 = random.randint(*coeff_range_b) * random.choice([-1, 1])

        multiplier = random.randint(2, 4) * random.choice([-1, 1]) # 倍數
        a2 = a1 * multiplier
        b2 = b1 * multiplier

        if is_no_solution:
            # 無解 (平行線): a1/a2 = b1/b2 != c1/c2
            c2 = c1 * multiplier + random.randint(1, 5) * random.choice([-1, 1]) # 確保常數項不與第一式成比例
            while c2 == c1 * multiplier: # 避免巧合
                c2 = c1 * multiplier + random.randint(1, 5) * random.choice([-1, 1])
            x_ans, y_ans = "No Solution", "No Solution"
        else:
            # 無限多解 (重合線): a1/a2 = b1/b2 = c1/c2
            c2 = c1 * multiplier
            x_ans, y_ans = "Infinitely Many Solutions", "Infinitely Many Solutions"
    else:
        raise ValueError("Invalid problem_type specified.")
        
    return (a1, b1, c1, a2, b2, c2, x_ans, y_ans)

def _format_equation(a, b, c):
    """
    將方程式的係數格式化為 LaTeX 安全的字串。
    遵循 [排版] 和 [LaTeX 安全] 規範。
    例如: a=1, b=-2, c=3 -> "x - 2y = 3"
    """
    eq_str_parts = []

    # 處理 x 項
    if a == 1:
        eq_str_parts.append(r"x")
    elif a == -1:
        eq_str_parts.append(r"-x")
    elif a != 0:
        eq_str_parts.append(r"{a}x".replace("{a}", str(a)))

    # 處理 y 項
    if b != 0:
        if b > 0:
            if eq_str_parts: # 如果 x 項已存在，加 "+"
                if b == 1:
                    eq_str_parts.append(r"+ y")
                else:
                    eq_str_parts.append(r"+ {b}y".replace("{b}", str(b)))
            else: # 如果 x 項不存在，直接寫 y 項
                if b == 1:
                    eq_str_parts.append(r"y")
                else:
                    eq_str_parts.append(r"{b}y".replace("{b}", str(b)))
        else: # b < 0
            if b == -1:
                eq_str_parts.append(r"- y")
            else:
                eq_str_parts.append(r"{b}y".replace("{b}", str(b))) # 負號已包含在 b 中

    # 如果方程式為 0=C 的形式，例如 0=5
    if not eq_str_parts:
        return r"0 = {c}".replace("{c}", str(c))

    # 組合成最終方程式字串
    formatted_eq = "".join(eq_str_parts)
    
    # 檢查並處理開頭的 "+ "
    if formatted_eq.startswith("+ "):
        formatted_eq = formatted_eq[2:]

    return r"{eq_str} = {c}".replace("{eq_str}", formatted_eq.strip()).replace("{c}", str(c))


def _draw_system_of_equations_placeholder(eq1_str, eq2_str):
    """
    用於生成聯立方程式視覺化圖形的輔助函式。
    遵循 [防洩漏原則]：僅接收題目已知數據。
    遵循 [必須回傳]：明確回傳結果。
    目前為佔位符，返回空字串。若需圖形，可在此處使用 matplotlib 等庫。
    """
    # 示例：若要啟用圖形，可解除下方註解並確保安裝 matplotlib
    # try:
    #     from matplotlib.figure import Figure
    #     from io import BytesIO
    #     import matplotlib.pyplot as plt # 使用 plt 進行 rcParams 和 close，但 Figure 用於物件

    #     # 設定繁體中文顯示字體
    #     plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
    #     plt.rcParams['axes.unicode_minus'] = False # 確保負號正確顯示

    #     fig = Figure(figsize=(6, 4), dpi=300)
    #     ax = fig.add_subplot(111)
    #     
    #     # 這裡需要解析 eq1_str, eq2_str 來獲取 a, b, c 係數，
    #     # 或者直接從 _generate_coefficients_and_solution 傳入 a1, b1, c1, a2, b2, c2。
    #     # 為了簡化，這裡假設係數可從字串解析或直接傳入。
    #     # 由於目前未啟用圖形生成，此處僅為示意。

    #     # 繪製兩條示意線條
    #     x_vals = [-5, 5]
    #     y_vals1 = [x for x in x_vals] # 假設 y = x
    #     y_vals2 = [-x + 2 for x in x_vals] # 假設 y = -x + 2
    #     ax.plot(x_vals, y_vals1, label='方程式 1')
    #     ax.plot(x_vals, y_vals2, label='方程式 2')
    #     
    #     ax.set_xlabel("x")
    #     ax.set_ylabel("y")
    #     ax.legend()
    #     ax.grid(True)
    #     ax.set_title("聯立方程式圖形示意")
    #     ax.set_aspect('equal', adjustable='box') # 物理比例鎖死

    #     # 這裡可以加入只顯示原點 '0' 的邏輯，如果需要數線
    #     # ax.set_xticks([0])
    #     # ax.set_xticklabels(['0'], fontsize=18)
    #     # ax.set_yticks([0])
    #     # ax.set_yticklabels(['0'], fontsize=18)
    #     
    #     buf = BytesIO()
    #     fig.savefig(buf, format='png')
    #     plt.close(fig) # 關閉圖形以釋放記憶體
    #     image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    #     return image_base64
    # except Exception as e:
    #     # 如果繪圖失敗，返回空字串並記錄錯誤
    #     # print(f"Error generating image: {e}")
    #     pass
        
    return "" # 目前不生成圖片，返回空字串

# --- Top-Level Functions (結構強化: [頂層函式], [自動重載]) ---

def generate(level=1):
    """
    生成一道加減消去法的數學題目。
    遵循 [自動重載] 原則，不依賴全域狀態。
    遵循 [隨機分流] 原則，隨機選擇題目類型。
    """
    # [隨機分流]: 隨機選擇題目類型，對應 RAG 中的例題
    # Type 1: 直接消去 (係數相同或相反) - 對應 RAG Ex 1
    # Type 2: 單邊乘法消去 - 對應 RAG Ex 2
    # Type 3: 雙邊乘法消去 - 對應 RAG Ex 3
    # Type 4: 特殊情況 (無解 / 無限多解)
    problem_type = random.choice([1, 2, 3, 4]) 
    
    # [數據禁絕常數]: 調用輔助函式生成係數和解
    a1, b1, c1, a2, b2, c2, x_ans, y_ans = _generate_coefficients_and_solution(level, problem_type)

    # [排版與 LaTeX 安全]: 格式化方程式字串
    eq1_str = _format_equation(a1, b1, c1)
    eq2_str = _format_equation(a2, b2, c2)
    
    # [排版與 LaTeX 安全]: 構建問題文本，嚴禁使用 f-string 格式化 LaTeX 字串
    question_text = r"請使用加減消去法解下列聯立方程式："
    question_text += r"\begin{cases}"
    question_text += r"  {eq1} \\ {eq2} " \
                    .replace("{eq1}", eq1_str) \
                    .replace("{eq2}", eq2_str)
    question_text += r"\end{cases}"
    
    # 根據問題類型設定正確答案和顯示答案
    if problem_type == 4 and (x_ans == "No Solution" or x_ans == "Infinitely Many Solutions"):
        correct_answer = x_ans # 例如 "No Solution"
        answer_display = x_ans
    else:
        # 正確答案格式為 "(x, y)" 字串
        # 此處的 f-string 不用於 LaTeX 內部，因此是安全的
        correct_answer = f"({x_ans}, {y_ans})" 
        # 顯示答案格式為 LaTeX 安全的字串
        answer_display = r"x = {x}, y = {y}" \
                        .replace("{x}", str(x_ans)) \
                        .replace("{y}", str(y_ans))

    # [視覺化與輔助函式通用規範]: 生成圖像 (目前為空字串)
    image_base64 = _draw_system_of_equations_placeholder(eq1_str, eq2_str)

    # [數據與欄位]: 回傳標準字典
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display, # 提供給前端顯示的答案
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(), # Coder 應確保此處為實際時間
        "version": "1.0.0" # Coder 應確保版本管理
    }


    """
    檢查使用者答案是否正確。
    遵循 [自動重載] 原則，不依賴全域狀態。
    處理特殊情況 (無解/無限多解) 和數值解。
    回傳 "正確！" 或 "答案錯誤..."。
    """
    is_correct = False

    # 處理特殊情況的答案
    if correct_answer in ["No Solution", "Infinitely Many Solutions"]:
        is_correct = user_answer.strip().lower() == correct_answer.lower()
    else:
        # 處理數值解 (x, y)
        try:
            # 解析使用者答案，預期格式如 "(x, y)"
            user_parts = user_answer.strip().replace("(", "").replace(")", "").split(",")
            if len(user_parts) != 2:
                is_correct = False
            else:
                user_x = float(user_parts[0].strip())
                user_y = float(user_parts[1].strip())

                # 解析正確答案
                correct_parts = correct_answer.strip().replace("(", "").replace(")", "").split(",")
                if len(correct_parts) != 2:
                    is_correct = False # 正確答案格式錯誤，不應該發生
                else:
                    correct_x = float(correct_parts[0].strip())
                    correct_y = float(correct_parts[1].strip())
                    
                    # 使用 math.isclose 進行浮點數比較，避免精度問題
                    is_correct = math.isclose(user_x, correct_x, rel_tol=1e-9, abs_tol=1e-9) and \
                                 math.isclose(user_y, correct_y, rel_tol=1e-9, abs_tol=1e-9)
        except (ValueError, IndexError):
            # 解析失敗 (例如輸入格式不正確)
            is_correct = False
    
    return "正確！" if is_correct else "答案錯誤..."


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
