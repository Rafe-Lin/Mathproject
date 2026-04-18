# ==============================================================================
# ID: jh_數學1上_DiscountProblems
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 62.57s | RAG: 2 examples
# Created At: 2026-01-14 20:56:58
# Fix Status: [Repaired]
# Fixes: Regex=1, Logic=0
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


from datetime import datetime
import base64 # 僅作為占位符，此技能目前不產生圖片
 # 一般數學運算備用，折扣問題中較少直接使用

# --- 輔助函式 (Helper Functions) ---
# 確保所有輔助函式最後一行明確使用 'return' 語句回傳結果。
# 若結果會用於拼接 question_text，則回傳值強制轉為字串 (str)。
# 視覺化函式（此處無）僅能接收「題目已知數據」，嚴禁將「答案數據」傳入。

def _calculate_discounted_price(original_price: float, discount_info: str) -> float:
    """
    根據折扣資訊計算最終價格。
    折扣資訊類型包含："X折" (e.g., "八折" = 80%), "X%" (e.g., "20%" = 20% off),
    "滿X折Y" (e.g., "滿500折100"), "直接折扣X元" (e.g., "直接折扣50元")。
    """
    price = original_price

    if "折" in discount_info and len(discount_info) < 6: # 處理 "八折", "九五折"
        try:
            if "五折" in discount_info: # 處理 "九五折", "八五折" 等
                clean_discount_str = discount_info.replace("折", "").replace("五", ".5")
                discount_factor = float(clean_discount_str) / 10
            else: # 處理 "八折", "九折"
                discount_factor = float(discount_info.replace("折", "")) / 10
            price = original_price * discount_factor
        except ValueError:
            pass # 如果解析失敗，則進入其他折扣類型判斷

    elif "%" in discount_info: # 處理 "20%" (20% off)
        discount_rate = float(discount_info.replace("%", "")) / 100
        price = original_price * (1 - discount_rate)
        
    elif "滿" in discount_info and "折" in discount_info and "元" not in discount_info: # 處理 "滿X折Y"
        parts = discount_info.replace("滿", "").replace("折", ",").split(",")
        threshold = float(parts[0])
        discount_amount = float(parts[1])
        if original_price >= threshold:
            price = original_price - discount_amount
        # else: price remains original_price (no discount)
            
    elif "直接折扣" in discount_info and "元" in discount_info: # 處理 "直接折扣X元"
        discount_amount = float(discount_info.replace("直接折扣", "").replace("元", ""))
        price = original_price - discount_amount
    
    return price

def _get_discount_factor_from_info(discount_info: str) -> float:
    """
    從折扣資訊字串中提取折扣因子 (e.g., "八折" -> 0.8, "20%" -> 0.8)。
    這個輔助函式用於逆向計算，需要直接的因子。
    不處理 "滿X折Y" 或 "直接折扣X元" 類型，對這些類型返回 1.0 (無百分比折扣)。
    """
    if "折" in discount_info and len(discount_info) < 6:
        if "五折" in discount_info:
            clean_discount_str = discount_info.replace("折", "").replace("五", ".5")
            return float(clean_discount_str) / 10
        else:
            return float(discount_info.replace("折", "")) / 10
    elif "%" in discount_info:
        discount_rate = float(discount_info.replace("%", "")) / 100
        return (1 - discount_rate)
    return 1.0 # 默認無折扣或非百分比折扣類型

def _format_price(price: float) -> str:
    """
    將浮點數價格格式化為字串，確保整數價格不帶小數點，且小數點後最多兩位。
    """
    if price == int(price):
        return str(int(price))
    return str(round(price, 2))


# --- 頂層函式 (Top-level Functions) ---
# 嚴禁使用 class 封裝。必須直接定義 generate() 與 check() 於模組最外層。
# 確保代碼不依賴全域狀態，以便系統執行 importlib.reload。

def generate(level: int = 1) -> dict:
    """
    根據指定難度等級 (level) 生成一道折扣問題。
    """
    # 題型多樣性：根據該技能的教科書例題，實作至少 3 種不同的題型變體。
    problem_type_choices = [
        "direct_calculation_final_price",       # 直接計算：求售價
        "direct_calculation_discount_amount",   # 直接計算：求折扣金額
        "reverse_solve_original_price",         # 逆向求解：已知售價求原價
        "contextual_comparison_offers",         # 情境應用：比較不同方案
        "contextual_multi_step_discount",       # 情境應用：多重折扣
        "reverse_solve_with_budget",            # 逆向求解：結合預算問題 (參考範例 1, 2)
    ]
    
    selected_type = random.choice(problem_type_choices)

    question_text = ""
    correct_answer = None
    image_base64 = "" # 此技能目前不涉及圖片，故為空字串

    # 常用變數選項
    original_price_options = [100, 150, 200, 250, 300, 400, 500, 600, 750, 800, 1000, 1200, 1500, 2000]
    discount_rate_options_percent = ["10%", "15%", "20%", "25%", "30%", "40%", "50%"]
    discount_rate_options_zhe = ["九折", "八五折", "八折", "七五折", "七折", "六五折", "六折", "五折"]
    discount_rate_options_all = discount_rate_options_percent + discount_rate_options_zhe
    
    # --- 題型變體邏輯 ---

    if selected_type == "direct_calculation_final_price":
        # Type 1 (Maps to Example 1, 2): 直接計算 - 求最終售價
        original_price = random.choice([p for p in original_price_options if p >= 100])
        discount_info = random.choice(discount_rate_options_all)
        
        final_price = _calculate_discounted_price(original_price, discount_info)
        
        # 排版與 LaTeX 安全: 嚴禁使用 f-string，必須使用 .replace
        q_template = r"一件商品原價 ${op}$ 元，{di}，請問售價是多少元？"
        question_text = q_template.replace("{op}", _format_price(original_price)).replace("{di}", discount_info)
        
        correct_answer = final_price

    elif selected_type == "direct_calculation_discount_amount":
        # Type 1.1 (Maps to Example 1, 2): 直接計算 - 求折扣金額
        original_price = random.choice([p for p in original_price_options if p >= 100])
        # 為確保折扣金額為整數，選擇特定折扣率
        discount_info = random.choice(discount_rate_options_percent + ["九折", "八折", "七折", "五折"])
        
        final_price = _calculate_discounted_price(original_price, discount_info)
        discount_amount = original_price - final_price
        
        q_template = r"一件商品原價 ${op}$ 元，{di}，請問可省下多少元？"
        question_text = q_template.replace("{op}", _format_price(original_price)).replace("{di}", discount_info)
        
        correct_answer = discount_amount

    elif selected_type == "reverse_solve_original_price":
        # Type 2 (Maps to Example 3, 4): 逆向求解 - 已知售價求原價
        # 為了確保原價是整數，我們從一組預設原價和折扣率反推售價
        possible_original_prices = [200, 300, 400, 500, 600, 800, 1000, 1200, 1500, 2000]
        # 對應的折扣因子 (e.g., 0.9 for "九折")
        discount_factors = [0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.5] 
        discount_info_map = {
            0.9: "九折", 0.85: "八五折", 0.8: "八折", 0.75: "七五折", 0.7: "七折", 
            0.65: "六五折", 0.6: "六折", 0.5: "五折",
            # 可以根據需要添加更多，但要確保能被 _calculate_discounted_price 解析
            # 也可以包含百分比折扣的對應關係
            0.9: "10%", 0.85: "15%", 0.8: "20%", 0.75: "25%", 0.7: "30%", 0.65: "35%", 0.6: "40%", 0.5: "50%"
        }
        
        # 隨機選擇一組能產生整數售價的原價和折扣因子
        valid_combinations = []
        for op in possible_original_prices:
            for df_val, df_info in discount_info_map.items():
                fp = op * df_val
                if fp == int(fp): # 確保售價為整數
                    valid_combinations.append((op, df_val, df_info))
        
        if not valid_combinations: # 確保有可用的組合 (應不會發生)
            original_price = random.choice(possible_original_prices)
            discount_factor = random.choice(discount_factors)
            discount_info = random.choice(list(discount_info_map.values()))
        else:
            original_price, discount_factor, discount_info = random.choice(valid_combinations)
        
        final_price = int(original_price * discount_factor) # 確保為整數
        
        q_template = r"一件商品{di}後售價為 ${fp}$ 元，請問原價是多少元？"
        question_text = q_template.replace("{di}", discount_info).replace("{fp}", _format_price(final_price))
        
        correct_answer = float(original_price) # 回傳原始數值型別

    elif selected_type == "contextual_comparison_offers":
        # Type 3 (Maps to Example 5): 情境應用 - 比較不同優惠方案
        original_price = random.choice([500, 800, 1000, 1200, 1500, 2000, 2500])
        
        # 方案 A: 百分比或折扣
        offer1_discount_info = random.choice(discount_rate_options_zhe + discount_rate_options_percent)
        
        # 方案 B: 滿額折價或直接折價
        offer2_options = []
        # 確保滿額折價的門檻合理，且折價金額不會過高導致負數
        for val in [500, 1000, 1500, 2000]:
            if original_price >= val:
                offer2_options.append(f"滿{val}折{max(50, val // 5)}") # 滿X折X/5，至少折50
        offer2_options.extend([f"直接折扣{amount}元" for amount in [50, 100, 150, 200, 250] if original_price - amount > 0])
        
        if not offer2_options: # 避免列表為空，提供一個通用選項
            offer2_discount_info = random.choice([f"直接折扣{amount}元" for amount in [50, 100, 150]])
        else:
            offer2_discount_info = random.choice(offer2_options)
        
        final_price1 = _calculate_discounted_price(original_price, offer1_discount_info)
        final_price2 = _calculate_discounted_price(original_price, offer2_discount_info)
        
        # 題目要求回答最終售價
        correct_answer = min(final_price1, final_price2)

        q_template = r"一件商品原價 ${op}$ 元。A方案：{offer1}。B方案：{offer2}。請問哪種方案購買較划算？(請回答最終售價)"
        question_text = q_template.replace("{op}", _format_price(original_price))\
                                  .replace("{offer1}", offer1_discount_info)\
                                  .replace("{offer2}", offer2_discount_info)

    elif selected_type == "contextual_multi_step_discount":
        # Type 3.1 (Maps to Example 6): 情境應用 - 多重折扣
        original_price = random.choice([400, 600, 800, 1000, 1200, 1500])
        
        first_discount_info = random.choice(discount_rate_options_zhe)
        second_discount_info_choices = discount_rate_options_percent + ["會員再享九折", "會員再享八五折"]
        second_discount_info = random.choice(second_discount_info_choices)
        
        price_after_first_discount = _calculate_discounted_price(original_price, first_discount_info)
        final_price = _calculate_discounted_price(price_after_first_discount, second_discount_info)
        
        q_template = r"一件商品原價 ${op}$ 元，先享{d1}，結帳時再享{d2}，請問最終售價是多少元？"
        question_text = q_template.replace("{op}", _format_price(original_price))\
                                  .replace("{d1}", first_discount_info)\
                                  .replace("{d2}", second_discount_info)
        
        correct_answer = final_price

    elif selected_type == "reverse_solve_with_budget":
        # 參考範例 1, 2: 結合預算和折扣的逆向求解
        # 數學模型:
        # 設預算為 B，原價為 P。
        # 1. P = B + initial_diff (原價比預算多 initial_diff 元)
        # 2. P_discounted = P * discount_factor (打折後售價)
        # 3. P_discounted = B - final_diff (打折後售價比預算少 final_diff 元)
        #
        # 由 1, 2, 3 可推導出 B 的公式:
        # (B + initial_diff) * discount_factor = B - final_diff
        # B * discount_factor + initial_diff * discount_factor = B - final_diff
        # initial_diff * discount_factor + final_diff = B - B * discount_factor
        # initial_diff * discount_factor + final_diff = B * (1 - discount_factor)
        # B = (initial_diff * discount_factor + final_diff) / (1 - discount_factor)
        
        # 為了生成題目，我們從 B, initial_diff, discount_factor 開始，計算 final_diff
        
        budgets = [5000, 6000, 7000, 8000, 9000, 10000, 12000]
        initial_diff_options = [1000, 1500, 2000, 2500, 3000] # 原價比預算多多少
        
        # 選擇折扣資訊 (確保 discount_factor < 1)
        discount_info_tuples = [
            ("八折", 0.8), ("七五折", 0.75), ("七折", 0.7), ("六五折", 0.65), ("九折", 0.9),
            ("20%", 0.8), ("25%", 0.75), ("30%", 0.7)
        ]

        # 嘗試生成符合條件的數值
        attempts = 0
        while attempts < 100:
            current_budget = random.choice(budgets)
            current_discount_text, current_discount_factor = random.choice(discount_info_tuples)
            current_initial_diff = random.choice(initial_diff_options)

            # 計算 final_diff
            calculated_final_diff = current_budget * (1 - current_discount_factor) - current_initial_diff * current_discount_factor
            
            # 確保 final_diff 是正數 (打折後比預算少) 且是整數 (符合 K12 題型通常情況)
            if calculated_final_diff > 0 and calculated_final_diff == int(calculated_final_diff):
                budget = current_budget
                discount_text = current_discount_text
                initial_diff = current_initial_diff
                final_diff = int(calculated_final_diff)
                break
            attempts += 1
        
        if attempts == 100: # 如果無法找到合適的組合，則使用範例值作為 fallback
            budget = 7000
            discount_text = "八折"
            initial_diff = 1500
            final_diff = 200 # 7000 * (1-0.8) - 1500 * 0.8 = 1400 - 1200 = 200

        # 構建題目
        q_template = r"一件商品售價比小明的預算多 ${id}$ 元。經過一段時間後，這件商品{di}出售，這樣就比小明的預算少 ${fd}$ 元，請問小明的預算是多少元？"
        question_text = q_template.replace("{id}", _format_price(initial_diff))\
                                  .replace("{di}", discount_text)\
                                  .replace("{fd}", _format_price(final_diff))
        
        correct_answer = float(budget) # 回傳預算 B

    # 數據與欄位: 返回字典必須且僅能包含指定欄位
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": _format_price(correct_answer), # 將答案轉為字串格式
        "image_base64": image_base64, # 目前為空字串
        "created_at": datetime.now().isoformat(), # 時間戳記
        "version": "9.6.1" # 遞增版本號，表示已新增題型
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
