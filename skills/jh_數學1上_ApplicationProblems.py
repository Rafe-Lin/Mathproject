# ==============================================================================
# ID: jh_數學1上_ApplicationProblems
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 51.22s | RAG: 5 examples
# Created At: 2026-01-14 18:59:38
# Fix Status: [Repaired]
# Fixes: Regex=6, Logic=0
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
    if n <= 1: return {'correct': False, 'result': r'答案錯誤。正確答案為：{ans}'.replace('{ans}', str(correct_answer))}
    if n <= 3: return {'correct': True, 'result': '正確！'}
    if n % 2 == 0 or n % 3 == 0: return {'correct': False, 'result': r'答案錯誤。正確答案為：{ans}'.replace('{ans}', str(correct_answer))}
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return {'correct': False, 'result': r'答案錯誤。正確答案為：{ans}'.replace('{ans}', str(correct_answer))}
        i += 6
    return {'correct': True, 'result': '正確！'}
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
    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", ans_display)}


from datetime import datetime
import base64

# import importlib # Not directly used in the code, but mentioned for context of reload

# --- Module-level Configuration ---
# This version number represents the version of this specific problem generation module.
# It should be manually incremented when the generation logic (this file) is updated.
_MODULE_VERSION = 1.1 # Incremented due to logic refinements and enhanced problem diversity

# --- Helper Functions (遵循通用規範) ---

def _get_dummy_image_base64() -> str:
    """
    [必須回傳]：回傳一個微小的透明 GIF 圖片的 Base64 編碼字串。
    [類型一致]：回傳值強制轉為字串。
    [防洩漏原則]：不接收任何題目或答案數據。
    這個函數作為視覺化輸出的佔位符，確保 `image_base64` 欄位不為空。
    """
    # 1x1 透明 GIF 像素的 Base64 編碼
    transparent_gif_pixel = "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
    return transparent_gif_pixel

def _round_if_close(value: float, tolerance: float = 1e-9) -> float | int:
    """
    [必須回傳]：判斷浮點數是否極接近整數，若是則回傳整數，否則回傳浮點數。
    [類型一致]：回傳值可能是 float 或 int。在用於拼接 question_text 時，會再強制轉為 str。
    """
    if abs(value - round(value)) < tolerance:
        return int(round(value))
    return value

# --- 頂層函式 (遵循程式結構規範) ---

def generate(level: int = 1) -> dict:
    """
    生成 K12 數學「應用問題」題型。
    [頂層函式]：直接定義於模組最外層，嚴禁使用 class 封裝。
    [自動重載]：代碼不依賴全域狀態。
    [題型多樣性]：實作至少 3 種不同題型變體。
    [排版與 LaTeX 安全]：嚴格遵守字串格式化規範。
    [數據與欄位]：回傳字典包含指定欄位。
    """
    # 確保代碼不依賴全域狀態，這裡的 `_MODULE_VERSION` 是模組級常數，不會被 `generate` 修改
    # `datetime.now()` 也是獨立操作，不產生全域狀態。

    # [題型多樣性]：使用 random.choice 實現隨機分流
    problem_type = random.choice([
        "direct_calculation",           # 直接計算
        "inverse_problem",              # 逆向求解
        "scenario_application"          # 情境應用 (如相對運動)
    ])

    question_text = ""
    correct_answer_str = "" # correct_answer 必須為字串
    numeric_answer = None   # 內部儲存的數值答案

    # 難度調整 (level 參數影響數值範圍)
    # 基礎數值範圍，隨 level 增加
    base_min = 10 + (level - 1) * 5
    base_max = 50 + (level - 1) * 10
    # 因子數值範圍，隨 level 增加
    factor_min = 2 + level // 2
    factor_max = 5 + level // 2

    if problem_type == "direct_calculation":
        # 題型變體 1: 直接計算 (Simple Linear Equation)
        # 範例: "小明有若干顆糖果，吃了5顆後剩下12顆，請問他原本有多少顆糖果？"
        eaten_candies = random.randint(factor_min, factor_max + 5)
        remaining_candies = random.randint(base_min, base_max)
        
        original_candies = eaten_candies + remaining_candies
        
        # [排版與 LaTeX 安全]：嚴禁使用 f-string 或 % 格式化，必須使用 .replace()
        question_template = r"小明有若干顆糖果，吃了 {eaten} 顆後剩下 {remaining} 顆，請問他原本有多少顆糖果？"
        question_text = question_template.replace("{eaten}", str(eaten_candies)).replace("{remaining}", str(remaining_candies))
        
        numeric_answer = original_candies
        correct_answer_str = str(original_candies)

    elif problem_type == "inverse_problem":
        # 題型變體 2: 逆向求解 (Finding Initial Value with Percentage/Fraction)
        # 範例: "一本書打七折後賣210元，請問這本書的原價是多少元？" 或 "某數的 $\frac{2}{5}$ 是 12，請問某數是多少？"
        
        if random.random() < 0.6: # 百分比折扣類問題 (約60%機率)
            discount_percent = random.choice([10, 20, 25, 30, 35, 40, 50])
            discount_factor_numerator = 100 - discount_percent
            
            # 計算 original_price 必須是哪個數的倍數，才能確保 final_price 為整數
            # original_price * (100 - discount_percent) / 100 = final_price
            # 為確保 final_price 為整數，original_price 必須是 100 / gcd(100, 100 - discount_percent) 的倍數
            common_divisor = math.gcd(100, discount_factor_numerator)
            min_original_price_multiplier = 100 // common_divisor
            
            # 生成 original_price，確保其在合理範圍內，且為 min_original_price_multiplier 的倍數
            lower_bound_base = max(1, (base_min * 2) // min_original_price_multiplier)
            upper_bound_base = (base_max * 5) // min_original_price_multiplier
            
            original_price_val = random.randint(lower_bound_base, upper_bound_base) * min_original_price_multiplier
            
            final_price_val = int(original_price_val * discount_factor_numerator / 100)

            question_template = r"一本書打 {discount}% 後賣 {final_price} 元，請問這本書的原價是多少元？"
            question_text = question_template.replace("{discount}", str(discount_percent)).replace("{final_price}", str(final_price_val))
            
            numeric_answer = original_price_val
            correct_answer_str = str(original_price_val)
            
        else: # 分數部分求整體 (約40%機率)
            numerator = random.randint(1, factor_min + 1)
            denominator = random.randint(numerator + 1, factor_max + 3) # 確保分母大於分子
            
            # 計算 whole_value 必須是哪個數的倍數，才能確保 part_value 為整數
            # whole_value * (numerator / denominator) = part_value
            # 為確保 part_value 為整數，whole_value 必須是 denominator / gcd(numerator, denominator) 的倍數
            common_divisor_frac = math.gcd(numerator, denominator)
            min_whole_value_multiplier = denominator // common_divisor_frac
            
            # 生成 whole_value
            lower_bound_base_frac = max(1, (base_min * 2) // min_whole_value_multiplier)
            upper_bound_base_frac = (base_max * 5) // min_whole_value_multiplier
            
            whole_value_val = random.randint(lower_bound_base_frac, upper_bound_base_frac) * min_whole_value_multiplier
            
            part_value_val = int(whole_value_val * numerator / denominator)
            
            # [排版與 LaTeX 安全]：所有數學式一律使用 $...$
            question_template = r"某數的 $\frac{{{numerator}}}{{{denominator}}}$ 是 {part_value}，請問某數是多少？"
            question_text = question_template.replace("{numerator}", str(numerator)).replace("{denominator}", str(denominator)).replace("{part_value}", str(part_value_val))
            
            numeric_answer = whole_value_val
            correct_answer_str = str(whole_value_val)

    elif problem_type == "scenario_application":
        # 題型變體 3: 情境應用 (Relative Movement - Meeting Problem)
        # 範例: "甲乙兩人相距200公尺，同時相向而行。甲每分鐘走50公尺，乙每分鐘走30公尺。請問幾分鐘後兩人相遇？"
        
        distance_unit = random.choice(["公尺", "公里"]) # 距離單位多樣性
        time_unit = random.choice(["分鐘", "小時"])    # 時間單位多樣性
        
        # 生成速度
        speed_a = random.randint(factor_min * 5, factor_max * 10)
        speed_b = random.randint(factor_min * 5, factor_max * 10)
        
        total_speed = speed_a + speed_b
        
        # 生成相遇時間，確保其為整數或簡單的小數 (例如 X.5)
        time_options = [random.randint(2, 10)] # 優先生成整數時間
        if level >= 2: # 難度較高時引入半小時時間
            time_options.append(random.randint(1, 5) + 0.5)
        
        time_to_meet = random.choice(time_options)
        
        # 根據相遇時間和總速度計算總距離，確保距離數值是「乾淨」的
        distance = _round_if_close(time_to_meet * total_speed)
        
        # [排版與 LaTeX 安全]：嚴禁使用 f-string 或 % 格式化，必須使用 .replace()
        question_template = r"甲乙兩人相距 {distance} {distance_unit}，同時相向而行。甲每{time_unit}走 {speed_a} {distance_unit}，乙每{time_unit}走 {speed_b} {distance_unit}。請問幾{time_unit}後兩人相遇？"
        question_text = question_template.replace("{distance}", str(distance)) \
                                 .replace("{distance_unit}", distance_unit) \
                                 .replace("{speed_a}", str(speed_a)) \
                                 .replace("{speed_b}", str(speed_b)) \
                                 .replace("{time_unit}", time_unit)
        
        numeric_answer = time_to_meet
        correct_answer_str = str(_round_if_close(time_to_meet)) # 將答案數值轉換為字串

    # [視覺化與輔助函式通用規範]：必須回傳圖片 Base64 字串
    image_base64_str = _get_dummy_image_base64()

    # [數據與欄位]：返回字典必須且僅能包含指定欄位
    return {
        "question_text": question_text,
        "correct_answer": correct_answer_str,
        "answer": numeric_answer, # 數值型答案，供內部使用或額外展示
        "image_base64": image_base64_str,
        "created_at": datetime.now().isoformat(), # [時間戳記]：更新時設定為當前時間
        "version": _MODULE_VERSION # [時間戳記]：使用模組版本，不自動遞增
    }



# [Auto-Injected Patch v11.0] Universal Return, Linebreak & Handwriting Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        
        # 1. 針對 check 函式的布林值回傳進行容錯封裝
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤'}
        
        if isinstance(res, dict):
            # 2. [V10.3] 解決 r-string 導致的 \n 換行失效問題
            if 'question_text' in res and isinstance(res['question_text'], str):
                res['question_text'] = res['question_text'].replace("\\n", "\n")
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則：若答案包含複雜運算符號，強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            triggers = ['^', '/', '_', ',', '|', '(', '[', '{', '\\']
            if (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers) and "手寫" not in res.get('question_text', ''):
                res['question_text'] += "\n(請在手寫區作答!)"

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
