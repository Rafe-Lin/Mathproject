# ==============================================================================
# ID: jh_數學1下_WordProblems
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 59.15s | RAG: 3 examples
# Created At: 2026-01-17 15:16:53
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

        if math.isclose(float(u), float(c), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
    except: pass
    
    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", c_raw)}



import re
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# V10.2 座標平面專用硬化規格: A. 資料結構鎖死
def _generate_coordinate_value(min_val, max_val, allow_fraction=False):
    """
    生成一個座標值，可以是整數或簡單分數。
    回傳 (float_val, (int_part, num, den, is_neg))。
    若為整數，num 與 den 設為 0；若為分數，則 int_part 為帶分數整數部。
    V13.0 座標選取控制: 使用 random.randint(-8, 8) 或 +0.5
    V13.1 禁絕假分數: numerator < denominator 且 denominator > 1
    """
    if random.random() < 0.7 or not allow_fraction: # 大部分情況生成整數
        val = random.randint(min_val, max_val)
        return float(val), (val, 0, 0, val < 0)
    else:
        int_part_abs = random.randint(0, max_val) # 整數部分
        
        # V13.1 禁絕假分數: numerator < denominator and denominator > 1
        denominator = random.choice([2, 3, 4, 5]) 
        numerator = random.randint(1, denominator - 1) # 分子小於分母
        
        is_neg = False
        if random.random() < 0.5 and (int_part_abs > 0 or numerator > 0): # 允許負數
            is_neg = True

        float_val = int_part_abs + numerator / denominator
        if is_neg:
            float_val = -float_val
        
        # 確保 float_val 在 min_val 和 max_val 之間
        if not (min_val <= float_val <= max_val):
            return _generate_coordinate_value(min_val, max_val, allow_fraction) # 重新生成

        int_part_signed = int_part_abs
        if is_neg:
            int_part_signed = -int_part_abs

        return float(float_val), (int_part_signed, numerator, denominator, is_neg)

# 視覺化輔助函式 (為幾何題預留，應用問題通常 image_base64=None)
def _draw_coordinate_plane(points_with_labels=[], x_range=(-8, 8), y_range=(-8, 8)):
    """
    V10.2 D. 視覺一致性: 鎖定 ax.set_aspect('equal'), 原點 '0' (18號加粗), 點標籤白色光暈
    V13.0 格線對齊: 座標軸範圍對稱整數，xticks 間隔 1
    V13.5 座標範圍: 範圍必須對稱且寬裕
    V13.6 API Hardened Spec: Arrow Ban, Strict Labeling
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    
    ax.set_aspect('equal')
    ax.grid(True, which='both', color='gray', linestyle='--', linewidth=0.5)
    
    ax.axhline(0, color='black', linewidth=1.5)
    ax.axvline(0, color='black', linewidth=1.5)

    # V13.6 API Hardened Spec: 使用 ax.plot 繪製箭頭
    ax.plot(x_range[1], 0, ">k", clip_on=False, markersize=8, transform=ax.get_yaxis_transform())
    ax.plot(0, y_range[1], "^k", clip_on=False, markersize=8, transform=ax.get_xaxis_transform())

    ax.set_xlim(x_range)
    ax.set_ylim(y_range)
    ax.set_xticks(np.arange(x_range[0], x_range[1] + 1, 1))
    ax.set_yticks(np.arange(y_range[0], y_range[1] + 1, 1))

    ax.text(0.1, -0.5, '0', fontsize=18, fontweight='bold', ha='left', va='top')

    # V10.2 B. 標點題防洩漏協定: 針對「在平面上標出點」的題型, points 傳入空列表 []
    # 針對「讀取坐標」題型, 則需顯示點與標籤。
    # V13.5 標籤隔離: ax.text 只能標註點名稱。
    valid_labels = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ") # V13.6 Strict Labeling: 點名稱白名單
    
    for x, y, label in points_with_labels:
        if label in valid_labels:
            ax.plot(x, y, 'o', color='red', markersize=8, zorder=5)
            ax.text(x + 0.3, y + 0.3, label, fontsize=12, ha='left', va='bottom',
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=0.5, alpha=0.9))

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# The original _robust_check_logic is superseded by the Universal Check Template 
# provided in the "CRITICAL CODING STANDARDS" section.

def generate(level=1):
    """
    生成 K12 數學應用問題。
    此函式嚴格遵循 V11.8 鏡射增強版及後續的硬化規約。
    - V5. 題型鏡射: 嚴格依據 RAG 例題 (Ex 1, Ex 2, Ex 3) 的數學模型生成三種類型問題。
    - V11. 數據禁絕常數: 所有數值均隨機生成。
    - V8. 數據與欄位: 返回字典包含 question_text, correct_answer, answer, image_base64。
    """
    problem_type = random.choice([
        "savings_goal",         # 鏡射 RAG Ex 1: 存款目標問題
        "discount_shopping",    # 鏡射 RAG Ex 2: 購物折扣與預算限制
        "tiered_discount"       # 鏡射 RAG Ex 3: 分級折扣比較問題
    ])

    question_text = ""
    correct_answer = "" 
    image_base64 = None # 應用問題通常不需要圖形

    if problem_type == "savings_goal":
        # 鏡射 RAG Ex 1: 小妍的存款問題
        # 模型: initial_amount + daily_deposit * x >= target_amount
        
        target_amount = random.randint(15000, 60000)
        initial_amount = random.randint(3000, target_amount // 3) # 確保初始存款遠低於目標
        daily_deposit = random.randint(70, 250)
        
        # 計算所需天數 x: ceil((target_amount - initial_amount) / daily_deposit)
        remaining_amount = target_amount - initial_amount
        x_days = math.ceil(remaining_amount / daily_deposit)

        # 確保 x_days 為一個合理的範圍，避免過小或過大的答案
        while x_days < 50 or x_days > 300:
            target_amount = random.randint(15000, 60000)
            initial_amount = random.randint(3000, target_amount // 3)
            daily_deposit = random.randint(70, 250)
            remaining_amount = target_amount - initial_amount
            x_days = math.ceil(remaining_amount / daily_deposit)

        person_name = random.choice(["小妍", "小華", "阿明"]) # 沿用 RAG 例題名稱
        item_name = random.choice(["筆記型電腦", "電動機車", "高階手機"])

        question_text = (
            f"{person_name} 想要購買一臺價值 {target_amount} 元的 {item_name}，"
            f"但現有存款僅 {initial_amount} 元。若從今天開始每天存 {daily_deposit} 元，"
            f"至少需要存幾天，他才有足夠的錢購買這臺 {item_name}？"
        )
        correct_answer = str(x_days)

    elif problem_type == "discount_shopping":
        # 鏡射 RAG Ex 2: 珊珊的蛋糕購物問題
        # 模型: (item1_price * count1 + item2_price * count2 + ... + itemX_price) * discount_rate <= budget
        
        discount_rate = random.choice([0.8, 0.85, 0.9]) # 8折, 85折, 9折
        discount_display = int(discount_rate * 10) # 顯示為「X折」

        person_name = "珊珊" # 沿用 RAG 例題名稱
        store_type = "蛋糕店" # 沿用 RAG 例題名稱
        event_name = "週年慶" # 沿用 RAG 例題名稱
        
        item1_name = "黑森林" # 沿用 RAG 例題名稱
        item1_price = random.randint(50, 80)
        item1_count = random.randint(1, 2)

        item2_name = "法式草莓" # 沿用 RAG 例題名稱
        item2_price = random.randint(60, 90)
        item2_count = random.randint(1, 2)

        # 其他可供選擇的蛋糕品項與價格
        # 生成 4-6 個獨特價格，確保問題的選項多樣性
        available_prices_set = set()
        while len(available_prices_set) < random.randint(4, 6):
            available_prices_set.add(random.randint(40, 100))
        available_prices = sorted(list(available_prices_set))
        
        # 計算已購買商品的總花費 (折扣後)
        fixed_cost_before_discount = item1_price * item1_count + item2_price * item2_count
        fixed_cost_after_discount = fixed_cost_before_discount * discount_rate

        # 迭代生成預算，確保最終答案（選擇數量）既非 0 也非所有選項
        while True:
            # 計算購買至少一個額外商品所需的最低預算
            min_possible_additional_cost_after_discount = min(available_prices) * discount_rate
            # 計算購買所有額外商品所需的最高預算 (用於設置預算上限)
            max_all_additional_cost_after_discount = sum(available_prices) * discount_rate

            # 設置一個合理的預算範圍，傾向於產生中間數量的選擇
            budget_lower_bound = math.ceil(fixed_cost_after_discount + min_possible_additional_cost_after_discount)
            budget_upper_bound = math.floor(fixed_cost_after_discount + max_all_additional_cost_after_discount / 2) # 避免預算過高導致全選

            if budget_lower_bound > budget_upper_bound: # 防止無限循環，若範圍不合理則擴大上限
                 budget_upper_bound = math.ceil(fixed_cost_after_discount + max(available_prices) * discount_rate * 2)
                 if budget_lower_bound > budget_upper_bound: # Still invalid, something is wrong with price generation, regenerate
                     available_prices_set = set()
                     while len(available_prices_set) < random.randint(4, 6):
                         available_prices_set.add(random.randint(40, 100))
                     available_prices = sorted(list(available_prices_set))
                     continue # Restart loop with new prices

            budget = random.randint(budget_lower_bound, budget_upper_bound)
            
            # 計算剩餘可支配的預算 (用於購買額外商品)
            remaining_budget_for_additional_item = budget - fixed_cost_after_discount
            
            choices_count = 0
            for price in available_prices:
                if (price * discount_rate) <= remaining_budget_for_additional_item:
                    choices_count += 1
            
            # 確保選擇數量既不為 0 也不等於所有可用選項的數量
            if 0 < choices_count < len(available_prices):
                break # 找到符合條件的參數
            
            # 如果不符合條件，微調預算並重試 (簡單的啟發式調整)
            if choices_count == 0:
                budget += random.randint(math.ceil(min_possible_additional_cost_after_discount / 2), math.ceil(min_possible_additional_cost_after_discount))
            elif choices_count == len(available_prices):
                budget -= random.randint(math.ceil(min_possible_additional_cost_after_discount / 2), math.ceil(min_possible_additional_cost_after_discount))

        # 將可用價格格式化為字串，用於題幹
        prices_str = "$"+", $".join(map(str, available_prices))
        
        question_text = (
            f"{store_type}{event_name}，每片蛋糕均享有{discount_display}折優惠。"
            f"{person_name} 買了 {item1_count} 片 {item1_price} 元的 {item1_name}、"
            f"{item2_count} 片 {item2_price} 元的 {item2_name} 後，"
            f"想再買 1 片不同品項的蛋糕，且總花費不超過 {budget} 元，"
            f"則 {person_name} 第 {item1_count + item2_count + 1} 片蛋糕最多有幾種選擇？"
            f"（店內其他蛋糕品項與價格為：{prices_str}）"
        )
        correct_answer = str(choices_count)

    elif problem_type == "tiered_discount":
        # 鏡射 RAG Ex 3: 出版社分級折扣問題
        # 模型: cost_under_condition1 > cost_under_condition2 (Q * base_price * discount1 > threshold2 * base_price * discount2)
        
        publisher_name = "某出版社" # 沿用 RAG 例題名稱
        item_name = "書"
        
        # 迭代生成參數，確保問題的條件和答案符合邏輯
        while True:
            base_price = random.randint(250, 400)
            threshold1 = random.randint(20, 30) # 第一個折扣門檻下限
            threshold2 = random.randint(50, 60) # 第二個折扣門檻 (含)
            
            # 確保第二個折扣優於第一個折扣
            discount1 = random.choice([0.8, 0.85, 0.9]) # 例如 8折
            possible_discount2s = [d for d in [0.6, 0.65, 0.7, 0.75] if d < discount1]
            if not possible_discount2s: # 如果無法找到更低的折扣，則重新生成 discount1
                continue
            discount2 = random.choice(possible_discount2s) # 例如 7折

            # 計算購買 threshold2 本書的總成本 (更便宜的選項)
            cost_at_threshold2 = threshold2 * base_price * discount2

            # 找出最小的原始購買數量 Q，使得 Q * base_price * discount1 > cost_at_threshold2
            # Q > (threshold2 * base_price * discount2) / (base_price * discount1)
            # Q > (threshold2 * discount2) / discount1
            min_Q_val = math.floor((threshold2 * discount2) / discount1) + 1
            
            # 問題的條件是「原預計購買數量在 threshold1 到 threshold2 本之間」
            # 且「發現一次購買 threshold2 本反而更便宜」。
            # 這意味著答案 min_Q_val 必須落在 threshold1 (含) 到 threshold2 (不含) 之間。
            if threshold1 <= min_Q_val < threshold2:
                break # 找到符合條件的參數

        discount1_display = int(discount1 * 10)
        discount2_display = int(discount2 * 10)

        question_text = (
            f"{publisher_name} 優惠：購買數量超過 {threshold1} 本不足 {threshold2} 本，每本打 {discount1_display} 折；"
            f"{threshold2} 本以上(含)每本打 {discount2_display} 折。"
            f"若學校想購買定價 {base_price} 元的 {item_name}，原預計購買數量在 {threshold1} 到 {threshold2} 本之間，"
            f"但發現一次購買 {threshold2} 本反而更便宜。問學校原本至少想購買幾本書？"
        )
        correct_answer = str(min_Q_val)
        
    return {
        "question_text": question_text,
        "correct_answer": correct_answer, # 必須是純數據 (Raw Data)
        "answer": str(correct_answer),   # 提供 answer 欄位，內容與 correct_answer 相同
        "image_base64": image_base64,    # 若無法自動批改圖片，設為 None
        "created_at": datetime.now().isoformat(),
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
