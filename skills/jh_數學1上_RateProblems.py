# ==============================================================================
# ID: jh_數學1上_RateProblems
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 80.14s | RAG: 2 examples
# Created At: 2026-01-14 21:03:02
# Fix Status: [Repaired]
# Fixes: Regex=2, Logic=0
#==============================================================================


import random
import math
import matplotlib
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from fractions import Fraction
from functools import reduce
import ast

# [V10.6 Elite Font & Style] - Hardcoded
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# --- 1. Formatting Helpers (V10.6 No-F-String LaTeX) ---
def to_latex(num):
    """
    Convert int/float/Fraction to LaTeX using .replace() to avoid f-string conflicts.
    """
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
    """
    Format number for LaTeX (Safe Mode).
    """
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

# Alias
fmt_fraction_latex = to_latex 

# --- 2. Number Theory Helpers ---
def is_prime(n):
    """Check primality (Standard Boolean Return)."""
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
# --- 3. Fraction Generator ---
def simplify_fraction(n, d):
    """[V11.3 Standard Helper] 強力化簡分數並回傳 (分子, 分母)"""
    common = math.gcd(n, d)
    return n // common, d // common


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
    
def draw_number_line(points_map):
    """[Advanced] Generate aligned ASCII number line with HTML container."""
    if not points_map: return ""
    values = []
    for v in points_map.values():
        if isinstance(v, (int, float)): values.append(float(v))
        elif isinstance(v, Fraction): values.append(float(v))
        else: values.append(0.0)
    if not values: values = [0]
    min_val = math.floor(min(values)) - 1
    max_val = math.ceil(max(values)) + 1
    if max_val - min_val > 15:
        mid = (max_val + min_val) / 2
        min_val = int(mid - 7); max_val = int(mid + 8)
    unit_width = 6
    line_str = ""; tick_str = ""
    range_len = max_val - min_val + 1
    label_slots = [[] for _ in range(range_len)]
    for name, val in points_map.items():
        if isinstance(val, Fraction): val = float(val)
        idx = int(round(val - min_val))
        if 0 <= idx < range_len: label_slots[idx].append(name)
    for i in range(range_len):
        val = min_val + i
        line_str += "+" + "-" * (unit_width - 1)
        tick_str += f"{str(val):<{unit_width}}"
    final_label_str = ""
    for labels in label_slots:
        final_label_str += f"{labels[0]:<{unit_width}}" if labels else " " * unit_width
    result = (
        f"<div style='font-family: Consolas, monospace; white-space: pre; overflow-x: auto; background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; line-height: 1.2;'>"
        f"{final_label_str}\n{line_str}+\n{tick_str}</div>"
    )
    return result

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


import datetime
import base64
import io
# 如果需要生成圖形，可以取消註釋以下行並實現繪圖邏輯：
# import matplotlib
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_agg import FigureCanvasAgg
# from PIL import Image

# --- 輔助函式 (Helper Functions) ---
# 視覺化輔助函式範例 (目前未實作複雜圖形，僅為示範結構)
# 遵循「防洩漏原則」：僅能接收題目已知數據，嚴禁將答案數據傳入。
def draw_simple_path(distance: float, unit: str) -> str:
    """
    生成一個表示距離的簡單示意圖 (目前為空，僅作結構示範)。
    實際應用中，此函數會使用 matplotlib 或 PIL 繪製圖形，
    並將其轉換為 Base64 字串。

    注意：根據基礎設施規則，繪圖時應使用 `from matplotlib.figure import Figure`
    而非 `matplotlib.pyplot`，並設定中文字體。但目前此函數僅為結構示範，
    並未啟用繪圖功能，故返回空字串。
    """
    # 根據基礎設施規則，如果需要繪圖，將會遵循以下配置：
    # plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # 設定中文字體
    # matplotlib.rcParams['axes.unicode_minus'] = False # 處理負號顯示
    
    # fig = Figure(figsize=(6, 1))
    # canvas = FigureCanvasAgg(fig)
    # ax = fig.add_subplot(111)
    
    # ax.plot([0, distance], [0, 0], 'k-', linewidth=2)
    # ax.text(distance / 2, 0.1, f"{distance} {unit}", ha='center', va='bottom', fontsize=14)
    # ax.text(0, -0.1, '0', ha='left', va='top', fontsize=18) # 顯示原點 '0'
    # ax.set_xlim(-distance*0.1, distance*1.1)
    # ax.set_ylim(-0.5, 0.5)
    # ax.axis('off') # 隱藏坐標軸
    
    # buf = io.BytesIO()
    # fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    # fig.clear() # 清除圖形以釋放記憶體
    # return base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # 目前返回空字串，表示沒有圖片
    return ""

# --- 頂層函式 (Top-Level Functions) ---

def generate(level: int = 1) -> dict:
    """
    根據 K12 數學「速率問題」技能生成一道題目。
    嚴禁使用 class 封裝。確保代碼不依賴全域狀態。

    Args:
        level (int): 題目的難度等級 (1-5)。

    Returns:
        dict: 包含題目詳細資訊的字典，格式如下：
              - question_text (str): 題目描述，嚴格遵循 LaTeX 安全排版規範。
              - correct_answer (str): 純數字的正確答案字串。
              - answer (str): 包含單位（若有）的顯示用答案字串。
              - image_base64 (str): Base64 編碼的圖片字串 (若無圖片則為空字串)。
              - created_at (str): 題目創建時間的 ISO 格式時間戳。
              - version (int): 題目生成器的版本號。
    """
    question_text = ""
    correct_answer = ""
    answer = ""
    image_base64 = "" # 圖片 Base64 字串，若無圖片則為空

    # --- 題型隨機分流 (Problem Type Random Selection) ---
    # 實作至少 3 種不同的題型變體，並納入 RAG 範例的複雜情境
    problem_types = [
        "basic_rate_calculation",                # 基本速率計算：D=ST, S=D/T, T=D/S
        "complex_scenario_meeting",              # 情境應用：相遇問題
        "complex_scenario_catchup",              # 情境應用：追趕問題 (A追B，B先走)
        "complex_scenario_relative_distance_same_time", # RAG Ex1: 同向不同速，一人跑完另一人差X距離，求總距離
        "complex_scenario_round_trip_total_time" # RAG Ex2: 往返問題，總時間已知，求單程距離
    ]
    selected_type = random.choice(problem_types)

    # --- 變數生成與難度調整 (Variable Generation & Level Adjustment) ---
    # 根據難度等級調整數值範圍，確保題目適齡
    if level == 1:
        speed_range = (2, 10)  # 速度範圍
        time_range = (1, 5)    # 時間範圍
        distance_range = (10, 50) # 距離範圍
        complex_speed_range = (2, 8) # 用於複雜題型的速度範圍
        complex_time_range = (1, 4)  # 用於複雜題型的時間範圍
        complex_distance_range = (20, 100) # 用於複雜題型的距離範圍
        ensure_clean_division = True # 低難度確保答案多為整數或簡單小數
        decimal_places = 0 # 答案四捨五入到小數點後0位
    elif level == 2:
        speed_range = (5, 15)
        time_range = (2, 8)
        distance_range = (20, 100)
        complex_speed_range = (3, 10)
        complex_time_range = (1, 5)
        complex_distance_range = (30, 150)
        ensure_clean_division = True
        decimal_places = 1 # 答案四捨五入到小數點後1位
    else: # level >= 3，允許更複雜的數值和分數結果
        speed_range = (10, 25)
        time_range = (3, 10)
        distance_range = (50, 200)
        complex_speed_range = (5, 15)
        complex_time_range = (2, 6)
        complex_distance_range = (50, 250)
        ensure_clean_division = False
        decimal_places = 2 # 答案四捨五入到小數點後2位

    # 隨機選擇單位以增加題型多樣性，確保單位匹配
    units_options = [
        {"speed": "公里/小時", "time": "小時", "distance": "公里"},
        {"speed": "公尺/秒", "time": "秒", "distance": "公尺"},
        {"speed": "公尺/分鐘", "time": "分鐘", "distance": "公尺"}
    ]
    chosen_units = random.choice(units_options)
    chosen_speed_unit = chosen_units["speed"]
    chosen_time_unit = chosen_units["time"]
    chosen_distance_unit = chosen_units["distance"]

    # --- 題型實作 (Problem Type Implementations) ---

    if selected_type == "basic_rate_calculation":
        sub_type = random.choice(["find_distance", "find_speed", "find_time"])

        if sub_type == "find_distance":
            speed = random.randint(*speed_range)
            time = random.randint(*time_range)
            calculated_distance = speed * time
            
            q_template = r"小明以 {s} {su} 的速度走了 {t} {tu}。請問他走了多遠？"
            question_text = q_template.replace("{s}", str(speed))\
                                      .replace("{su}", chosen_speed_unit)\
                                      .replace("{t}", str(time))\
                                      .replace("{tu}", chosen_time_unit)
            
            correct_answer = str(round(calculated_distance, decimal_places))
            answer = str(round(calculated_distance, decimal_places)) + " " + chosen_distance_unit

        elif sub_type == "find_speed":
            distance = random.randint(*distance_range)
            time = random.randint(*time_range)
            
            if ensure_clean_division:
                # 嘗試找到能整除的 time
                temp_times = [t for t in range(time_range[0], time_range[1] + 1) if distance % t == 0]
                if temp_times:
                    time = random.choice(temp_times)
                else:
                    # 若找不到，允許小數結果，但仍使用範圍內的數字
                    time = random.choice(range(time_range[0], time_range[1] + 1))

            calculated_speed = distance / time

            q_template = r"小華走了 {d} {du} 花了 {t} {tu}。請問他的平均速度是多少？"
            question_text = q_template.replace("{d}", str(distance))\
                                      .replace("{du}", chosen_distance_unit)\
                                      .replace("{t}", str(time))\
                                      .replace("{tu}", chosen_time_unit)
            
            correct_answer = str(round(calculated_speed, decimal_places))
            answer = str(round(calculated_speed, decimal_places)) + " " + chosen_speed_unit

        else: # sub_type == "find_time"
            distance = random.randint(*distance_range)
            speed = random.randint(*speed_range)

            if ensure_clean_division:
                # 嘗試找到能整除的 speed
                temp_speeds = [s for s in range(speed_range[0], speed_range[1] + 1) if distance % s == 0]
                if temp_speeds:
                    speed = random.choice(temp_speeds)
                else:
                    speed = random.choice(range(speed_range[0], speed_range[1] + 1))

            calculated_time = distance / speed

            q_template = r"小麗以 {s} {su} 的速度走了 {d} {du}。請問她走了多久？"
            question_text = q_template.replace("{s}", str(speed))\
                                      .replace("{su}", chosen_speed_unit)\
                                      .replace("{d}", str(distance))\
                                      .replace("{du}", chosen_distance_unit)
            
            correct_answer = str(round(calculated_time, decimal_places))
            answer = str(round(calculated_time, decimal_places)) + " " + chosen_time_unit

    elif selected_type == "complex_scenario_meeting":
        total_distance = random.randint(*complex_distance_range)
        speed_A = random.randint(*complex_speed_range)
        speed_B = random.randint(*complex_speed_range)
        
        while speed_A + speed_B == 0: # 避免除以零
            speed_B = random.randint(*complex_speed_range)
        
        if ensure_clean_division:
            sum_speeds = speed_A + speed_B
            # 調整總距離使其能被速度和整除
            multiples = [i * sum_speeds for i in range(1, 10) 
                         if i * sum_speeds >= complex_distance_range[0] and i * sum_speeds <= complex_distance_range[1]]
            if multiples:
                total_distance = random.choice(multiples)
            else:
                pass # 若找不到，允許小數結果

        time_to_meet = total_distance / (speed_A + speed_B)

        q_template = r"甲乙兩地相距 {td} {du}。小明從甲地以 {sA} {su} 的速度出發，小華從乙地以 {sB} {su} 的速度出發，兩人同時相向而行。請問多久後他們會相遇？"
        question_text = q_template.replace("{td}", str(total_distance))\
                                  .replace("{du}", chosen_distance_unit)\
                                  .replace("{sA}", str(speed_A))\
                                  .replace("{sB}", str(speed_B))\
                                  .replace("{su}", chosen_speed_unit)
        
        correct_answer = str(round(time_to_meet, decimal_places))
        answer = str(round(time_to_meet, decimal_places)) + " " + chosen_time_unit

    elif selected_type == "complex_scenario_catchup":
        speed_B = random.randint(*complex_speed_range) # 被追趕者的速度
        speed_A = random.randint(speed_B + 1, complex_speed_range[1] + 3) # 追趕者的速度必須大於被追趕者
        
        # 確保速度差足夠大以利整除，若難度要求整數
        if ensure_clean_division:
            attempts = 0
            while speed_A - speed_B < 1 and attempts < 10: 
                speed_B = random.randint(*complex_speed_range)
                speed_A = random.randint(speed_B + 1, complex_speed_range[1] + 3)
                attempts += 1
            if attempts == 10 and speed_A - speed_B < 1: 
                speed_A = speed_B + 1 # 強制保證速度差

        time_diff = random.randint(1, complex_time_range[1] // 2 + 1) # 被追趕者的先行時間

        head_start_distance = speed_B * time_diff # 被追趕者領先的距離
        speed_difference = speed_A - speed_B      # 速度差
        
        if ensure_clean_division and speed_difference != 0:
            # 嘗試調整 time_diff 確保 head_start_distance 能被 speed_difference 整除
            potential_time_diffs = [
                td for td in range(1, complex_time_range[1] // 2 + 2)
                if (speed_B * td) % speed_difference == 0
            ]
            if potential_time_diffs:
                time_diff = random.choice(potential_time_diffs)
                head_start_distance = speed_B * time_diff
            else:
                pass # 若找不到，允許小數結果

        time_to_catch = head_start_distance / speed_difference if speed_difference != 0 else float('inf')

        q_template = r"小明比小華早 {tdiff} {tu} 出發，小明速度為 {sB} {su}，小華速度為 {sA} {su}。小華出發後多久能追上小明？"
        question_text = q_template.replace("{tdiff}", str(time_diff))\
                                  .replace("{tu}", chosen_time_unit)\
                                  .replace("{sB}", str(speed_B))\
                                  .replace("{sA}", str(speed_A))\
                                  .replace("{su}", chosen_speed_unit)
        
        correct_answer = str(round(time_to_catch, decimal_places))
        answer = str(round(time_to_catch, decimal_places)) + " " + chosen_time_unit

    elif selected_type == "complex_scenario_relative_distance_same_time":
        # RAG Ex1: 同向不同速，一人跑完另一人差X距離，求總距離
        # 為確保生成數字的合理性及答案的整潔性，先設定運行時間，再推導距離和速度
        
        # 隨機選擇一個合理的運行時間 (可以是非整數，但如果要求整數答案，會調整)
        time_taken_base = random.randint(1, complex_time_range[1])
        
        speed_slower = random.randint(complex_speed_range[0], complex_speed_range[1] // 2)
        speed_faster = random.randint(speed_slower + 1, complex_speed_range[1] + 5) 
        
        # 確保速度差是正數
        while speed_faster - speed_slower <= 0:
             speed_slower = random.randint(complex_speed_range[0], complex_speed_range[1] // 2)
             speed_faster = random.randint(speed_slower + 1, complex_speed_range[1] + 5)

        # 計算總距離和落後距離
        total_distance = speed_faster * time_taken_base
        distance_slower_covered = speed_slower * time_taken_base
        distance_behind = total_distance - distance_slower_covered

        # 確保生成的總距離在合理範圍內
        # 如果超出範圍，重新生成或放寬條件
        if not (complex_distance_range[0] <= total_distance <= complex_distance_range[1]):
            # 這裡可以根據需要調整生成邏輯，例如重新選擇 time_taken_base 或速度
            # 為簡化，目前直接使用生成的數字，如果超出範圍則可能導致題目數值較大/小
            pass 
        
        # 確保落後距離為正數
        while distance_behind <= 0:
            time_taken_base = random.randint(1, complex_time_range[1])
            speed_slower = random.randint(complex_speed_range[0], complex_speed_range[1] // 2)
            speed_faster = random.randint(speed_slower + 1, complex_speed_range[1] + 5)
            total_distance = speed_faster * time_taken_base
            distance_slower_covered = speed_slower * time_taken_base
            distance_behind = total_distance - distance_slower_covered

        calculated_total_distance = total_distance # 這就是我們要的答案

        q_template = r"小明與小華約定同時同方向環島路跑，已知小華每 {tu} 跑 {sF} {du}，小明每 {tu} 跑 {sS} {du}。當小華跑回終點時，小明還離終點 {db} {du}。請問環島公路全長多少 {du}？"
        question_text = q_template.replace("{sF}", str(speed_faster))\
                                  .replace("{sS}", str(speed_slower))\
                                  .replace("{db}", str(round(distance_behind, decimal_places)))\
                                  .replace("{tu}", chosen_time_unit)\
                                  .replace("{du}", chosen_distance_unit)
        
        correct_answer = str(round(calculated_total_distance, decimal_places))
        answer = str(round(calculated_total_distance, decimal_places)) + " " + chosen_distance_unit

    elif selected_type == "complex_scenario_round_trip_total_time":
        # RAG Ex2: 往返問題，總時間已知，求單程距離
        # 為確保生成數字的合理性及答案的整潔性，先設定單程距離，再推導總時間
        
        # 隨機選擇一個合理的單程距離
        desired_one_way_distance = random.randint(complex_distance_range[0] // 3, complex_distance_range[1] // 3)
        
        speed_uphill = random.randint(complex_speed_range[0], complex_speed_range[1] - 1)
        speed_downhill = random.randint(speed_uphill + 1, complex_speed_range[1] + 5) # 下山速度應大於上山
        
        # 計算所需的總時間
        time_uphill = desired_one_way_distance / speed_uphill
        time_downhill = desired_one_way_distance / speed_downhill
        total_time_calculated = time_uphill + time_downhill

        # 確保計算出的總時間在合理範圍內
        if not (complex_time_range[0] <= total_time_calculated <= complex_time_range[1]):
            # 如果超出範圍，這裡可以重新生成或放寬條件
            pass

        calculated_one_way_distance = desired_one_way_distance

        q_template = r"小宗沿著相同的路徑上山、下山共需要 {tt} {tu}。如果小宗上山每 {tu} 可走 {sU} {du}，下山每 {tu} 可走 {sD} {du}，則這條山路長多少 {du}？"
        question_text = q_template.replace("{tt}", str(round(total_time_calculated, decimal_places)))\
                                  .replace("{tu}", chosen_time_unit)\
                                  .replace("{sU}", str(speed_uphill))\
                                  .replace("{sD}", str(speed_downhill))\
                                  .replace("{du}", chosen_distance_unit)
        
        correct_answer = str(round(calculated_one_way_distance, decimal_places))
        answer = str(round(calculated_one_way_distance, decimal_places)) + " " + chosen_distance_unit

    # --- 返回結果字典 (Return Result Dictionary) ---
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer,
        "image_base64": image_base64, # 目前為空字串，若有圖片則會填入
        "created_at": datetime.datetime.now().isoformat(),
        "version": 1
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
                # 解決 r-string 導致的 \\n 問題
                res['question_text'] = re.sub(r'\\n', '\n', res['question_text'])
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則：若答案包含複雜運算符號，強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            triggers = ['^', '/', '_', ',', '|', '(', '[', '{', '\\\\']
            
            # [V11.1 Refined] 僅在題目尚未包含提示時注入，避免重複堆疊
            has_prompt = "手寫" in res.get('question_text', '')
            should_inject = (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers)
            
            if should_inject and not has_prompt:
                # [V11.3] 確保手寫提示語在最後一行
                res['question_text'] = res['question_text'].rstrip() + "\\n(請在手寫區作答!)"

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
