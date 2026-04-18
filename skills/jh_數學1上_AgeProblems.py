# ==============================================================================
# ID: jh_數學1上_AgeProblems
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 73.13s | RAG: 2 examples
# Created At: 2026-01-14 20:54:55
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

# Coder Spec for Skill: 年齡問題 (jh_數學1上_AgeProblems)
# V9.6 Ultimate Automation Edition - Coder Spec



import base64
from datetime import datetime
# 注意：此模組不應依賴任何全域狀態，以確保 importlib.reload 的自動重載機制能正常運作。

# --- 視覺化與輔助函式通用規範 (Generic Helper Rules) ---
# 所有定義的輔助函式，最後一行必須明確使用 'return' 語句回傳結果。
# 若該函式結果會用於拼接 question_text，則回傳值必須強制轉為字串 (str)。
# 視覺化函式僅能接收「題目已知數據」。嚴禁將「答案數據」傳入繪圖函式。

def _generate_reasonable_ages(min_age=5, max_age=60, min_diff=2, max_diff=30, max_ratio=5):
    """
    輔助函式：生成兩個合理的目前年齡 (age1, age2)。
    確保 age1 > age2 且年齡差與倍數關係在合理範圍內。
    回傳 (age1, age2) tuple。
    """
    attempts = 0
    while attempts < 100: # 嘗試次數限制，避免無限迴圈
        age2 = random.randint(min_age, max_age - min_diff) # 年輕者
        age1 = random.randint(age2 + min_diff, min(max_age, age2 + max_diff)) # 年長者
        
        # 確保年長者不是年輕者的過度倍數 (對於成人與小孩而言)
        # 如果年輕者很年輕 (比如小於10歲), 那麼年長者的倍數可以大一些 (比如5倍)
        # 如果年輕者已經是青少年或成人, 倍數不宜過大
        if age2 > 10 and age1 / age2 > max_ratio and age1 > 20: # If younger person is not a very young child, ratio should be smaller
            attempts += 1
            continue
        elif age2 <= 10 and age1 / age2 > 7: # If younger person is a very young child, ratio can be up to 7, but not excessively high
             attempts += 1
             continue

        if age1 > age2:
            return age1, age2
        attempts += 1
    
    # 失敗時回傳一組預設的合理年齡
    return 30, 10

def _get_years_offset(current_age1, current_age2, min_offset=-10, max_offset=10):
    """
    輔助函式：生成一個合理的年數偏移量 (過去或未來)。
    確保偏移後兩人的年齡皆為正數。
    回傳 years_offset (int)。
    """
    attempts = 0
    while attempts < 100:
        offset = random.randint(min_offset, max_offset)
        if current_age1 + offset > 0 and current_age2 + offset > 0:
            return offset
        attempts += 1
    return 5 # 失敗時回傳預設的未來 5 年

def _format_value_for_question(value):
    """
    輔助函式：將數值安全地轉換為字串，用於問題文本，嚴格遵守 LaTeX 安全規範。
    強制轉為字串。
    """
    return str(value)

# 年齡問題通常不需要視覺化輔助，因此不定義 draw_ 函式。
# 若需視覺化，其函式簽名及內容將嚴格遵循「防洩漏原則」。

# --- 程式結構 (Structure Hardening) ---
# 嚴禁使用 class 封裝。必須直接定義 generate() 與 check() 於模組最外層。
# 確保代碼不依賴全域狀態，以便系統執行 importlib.reload。

def generate(level=1):
    """
    【頂層函式】生成 K12 數學「年齡問題」的題目。
    根據 level 調整題目複雜度 (V9.6 暫時統一難度)。
    內部使用 random.choice 實作至少 3 種不同的題型變體。
    """
    problem_type = random.choice([1, 2, 3]) # 隨機分流至 3 種題型變體

    question_text = ""
    correct_answer = "" # 答案的字串表示
    answer = None       # 答案的原始數據類型 (int 或 tuple)
    image_base64 = None # 年齡問題通常不需要圖片，保持為 None

    # 隨機生成人名，確保兩人不同名
    person1_name_options = ["爸爸", "媽媽", "小明", "姐姐", "老師", "甲", "大雄"]
    person2_name_options = ["兒子", "女兒", "小華", "弟弟", "學生", "乙", "靜香"]
    
    person1_name = random.choice(person1_name_options)
    person2_name = random.choice(person2_name_options)
    while person1_name == person2_name:
        person2_name = random.choice(person2_name_options)

    # 確保 current_age1 > current_age2 (由 _generate_reasonable_ages 輔助函式保證)
    current_age1, current_age2 = _generate_reasonable_ages()

    # 如果人名不匹配常見的長幼關係，則調整
    # 這裡假設 person1_name 對應 current_age1 (年長者), person2_name 對應 current_age2 (年輕者)
    if person1_name in ["爸爸", "媽媽", "老師"] and person2_name not in ["兒子", "女兒", "學生"]:
        person2_name = random.choice(["兒子", "女兒", "學生"])
    elif person1_name not in ["爸爸", "媽媽", "老師"] and person2_name in ["兒子", "女兒", "學生"]:
        person1_name = random.choice(["爸爸", "媽媽", "老師"])
    
    # --- 題型多樣性 (Problem Variety) ---
    # 根據 problem_type 實作至少 3 種不同的題型變體。

    if problem_type == 1:
        # Type 1 (Maps to Example 1, 3): 直接計算 (Direct Calculation - Future/Past Age Relationship)
        # 題目：已知兩人目前年齡，N 年後/前，其中一人是另一人的 K 倍，求 N 或 K。

        sub_type_choice = random.randint(1, 2)

        if sub_type_choice == 1:
            # 子題型 1: 求「幾年後」或「幾年前」會達成某倍數關係
            # 確保能得出整數年數
            years_offset_solution = 0
            target_ratio = 0
            
            attempts = 0
            while attempts < 50:
                attempts += 1
                # 隨機生成一個未來年數 (答案)
                years_offset_solution = random.randint(3, 15)
                
                # 基於這個年數，生成合理的目前年齡和倍數關係
                temp_current_age2 = random.randint(5, 15) # 年輕者目前年齡
                temp_age2_at_offset = temp_current_age2 + years_offset_solution
                
                target_ratio_options = [2, 3, 4, 5]
                if temp_age2_at_offset < 10: # 如果未來年輕者年齡很小，倍數可以大一點
                    target_ratio_options.extend([6, 7])
                target_ratio = random.choice(target_ratio_options)
                
                temp_age1_at_offset = temp_age2_at_offset * target_ratio
                
                temp_current_age1 = temp_age1_at_offset - years_offset_solution

                # 檢查目前年齡是否合理
                if (20 <= temp_current_age1 <= 60 and 5 <= temp_current_age2 <= 20 and 
                    temp_current_age1 > temp_current_age2 and (temp_current_age1 - temp_current_age2) > 10): # 年齡差至少10歲
                    current_age1, current_age2 = temp_current_age1, temp_current_age2
                    break
            
            if attempts == 50: # 實在找不到，使用預設值
                years_offset_solution = 5
                current_age2 = 10
                target_ratio = 3 
                current_age1 = target_ratio * (current_age2 + years_offset_solution) - years_offset_solution # 3*(10+5) - 5 = 45-5 = 40
            
            q_template = r"{p1_name}今年{age1}歲，{p2_name}今年{age2}歲。請問，幾年後{p1_name}的年齡會是{p2_name}年齡的{ratio}倍？"
            question_text = q_template.replace("{p1_name}", person1_name)\
                                      .replace("{age1}", _format_value_for_question(current_age1))\
                                      .replace("{p2_name}", person2_name)\
                                      .replace("{age2}", _format_value_for_question(current_age2))\
                                      .replace("{ratio}", _format_value_for_question(target_ratio))
            
            correct_answer = _format_value_for_question(years_offset_solution)
            answer = years_offset_solution

        else: # sub_type_choice == 2
            # 子題型 2: 已知 N 年後/前，其中一人是另一人的 K 倍，求目前年齡
            
            years_offset_val = random.randint(5, 10) # 強制為未來 N 年
            
            # 確保未來年齡有整數倍數關係
            temp_current_age1 = 0
            temp_current_age2 = 0
            target_ratio = 0
            
            attempts = 0
            while attempts < 50:
                attempts += 1
                temp_current_age2_candidate = random.randint(5, 15)
                temp_age2_at_offset_candidate = temp_current_age2_candidate + years_offset_val
                
                target_ratio_options = [2, 3, 4]
                if temp_age2_at_offset_candidate < 10:
                    target_ratio_options.append(5)
                target_ratio_candidate = random.choice(target_ratio_options)
                
                temp_age1_at_offset_candidate = temp_age2_at_offset_candidate * target_ratio_candidate
                temp_current_age1_candidate = temp_age1_at_offset_candidate - years_offset_val

                # 確保生成合理的目前年齡
                if (25 <= temp_current_age1_candidate <= 60 and 5 <= temp_current_age2_candidate <= 20 and 
                    temp_current_age1_candidate > temp_current_age2_candidate and 
                    (temp_current_age1_candidate - temp_current_age2_candidate) > 10):
                    
                    current_age1, current_age2 = temp_current_age1_candidate, temp_current_age2_candidate
                    target_ratio = target_ratio_candidate
                    break
            
            if attempts == 50: # 實在找不到，使用預設值
                years_offset_val = 5
                current_age2 = 10
                target_ratio = 3
                current_age1 = target_ratio * (current_age2 + years_offset_val) - years_offset_val # 3*(10+5)-5 = 40

            time_description = _format_value_for_question(years_offset_val) + "年後"
            
            q_template = r"{time_desc}{p1_name}的年齡會是{p2_name}年齡的{ratio}倍。請問{p1_name}和{p2_name}現在分別是幾歲？"
            question_text = q_template.replace("{time_desc}", time_description)\
                                      .replace("{p1_name}", person1_name)\
                                      .replace("{p2_name}", person2_name)\
                                      .replace("{ratio}", _format_value_for_question(target_ratio))
            
            correct_answer = r"({a},{b})".replace("{a}", _format_value_for_question(current_age1))\
                                         .replace("{b}", _format_value_for_question(current_age2))
            answer = (current_age1, current_age2)

    elif problem_type == 2:
        # Type 2 (Maps to Example 2, 4): 逆向求解 (Reverse Solving - Known Age Difference and Ratio)
        # 題目：已知兩人年齡差，N 年後/前，其中一人是另一人的 K 倍，求目前年齡。
        
        # 強制人名為父母與子女關係，以符合年齡差較大的情境
        person1_name = random.choice(["爸爸", "媽媽"])
        person2_name = random.choice(["兒子", "女兒"])

        age_diff = 0
        target_ratio = 0
        years_offset = 0
        final_current_age1 = 0
        final_current_age2 = 0

        attempts = 0
        while attempts < 50:
            attempts += 1
            target_ratio = random.randint(2, 4) # 倍數
            years_offset = random.randint(-8, 8) # 過去或未來年數 (可以是負數代表幾年前)
            
            # 確保年齡差是 (target_ratio - 1) 的倍數，以保證解為整數
            # age2_at_offset 是較年輕者在 years_offset 時間點的年齡
            # age1_at_offset = target_ratio * age2_at_offset
            # age1_at_offset - age2_at_offset = (target_ratio - 1) * age2_at_offset = age_diff (在偏移時間點的年齡差)
            # 由於年齡差不變，所以 age_diff 也是目前的年齡差。
            # 所以 age_diff 必須是 (target_ratio - 1) 的倍數。
            
            # Let's derive age2_at_offset first, ensuring it's positive
            age2_at_offset_candidate = random.randint(5, 15) # 年輕者在偏移時間點的年齡
            
            # Calculate current ages based on this
            temp_current_age2 = age2_at_offset_candidate - years_offset
            if temp_current_age2 <= 0: # 確保目前年齡為正
                continue

            age_diff_candidate = (target_ratio - 1) * age2_at_offset_candidate
            temp_current_age1 = temp_current_age2 + age_diff_candidate
            
            # 檢查目前年齡是否合理
            if (10 <= temp_current_age2 <= 25 and 30 <= temp_current_age1 <= 60 and 
                temp_current_age1 > temp_current_age2 and temp_current_age2 > 0):
                final_current_age1 = temp_current_age1
                final_current_age2 = temp_current_age2
                age_diff = age_diff_candidate
                break
        
        if attempts == 50: # 實在找不到，使用預設值
            final_current_age1 = 40
            final_current_age2 = 10
            age_diff = 30 # 40-10 = 30
            years_offset = 5 # 5年後: 45, 15. 45/15 = 3
            target_ratio = 3

        if years_offset > 0:
            time_description = _format_value_for_question(years_offset) + "年後"
        elif years_offset < 0:
            time_description = _format_value_for_question(abs(years_offset)) + "年前"
        else: # years_offset == 0 is unlikely but possible, means "現在"
            time_description = "現在"

        q_template = r"{p1_name}比{p2_name}大{diff}歲。{time_desc}{p1_name}的年齡會是{p2_name}年齡的{ratio}倍。請問{p1_name}和{p2_name}現在分別是幾歲？"
        question_text = q_template.replace("{p1_name}", person1_name)\
                                  .replace("{p2_name}", person2_name)\
                                  .replace("{diff}", _format_value_for_question(age_diff))\
                                  .replace("{time_desc}", time_description)\
                                  .replace("{ratio}", _format_value_for_question(target_ratio))
        
        correct_answer = r"({a},{b})".replace("{a}", _format_value_for_question(final_current_age1))\
                                     .replace("{b}", _format_value_for_question(final_current_age2))
        answer = (final_current_age1, final_current_age2)

    else: # problem_type == 3
        # Type 3 (Maps to Example 5, 6): 情境應用 (Contextual Application - Multiple Time Points/Unknowns)
        # 題目：涉及父母與子女、多個時間點（現在、過去、未來）的複雜關係。
        # 例如：爸爸比兒子大X歲，N年前爸爸的年齡是兒子的K倍，求現在年齡。

        # 強制人名為父母與子女
        person1_name = random.choice(["爸爸", "媽媽"])
        person2_name = random.choice(["兒子", "女兒"])

        final_current_parent_age = 0
        final_current_child_age = 0
        age_diff = 0
        years_ago = 0
        target_ratio = 0

        attempts = 0
        while attempts < 50:
            attempts += 1
            years_ago = random.randint(3, 10) # 過去的年數
            target_ratio_options = [3, 4, 5, 6, 7]
            if years_ago < 5: # 如果年份差不大，倍數可以大一點
                target_ratio_options.extend([8, 9])
            target_ratio = random.choice(target_ratio_options) # 過去的倍數關係
            
            # 確保年齡差是 (target_ratio - 1) 的倍數
            # past_child_age 是子女在 years_ago 時間點的年齡
            past_child_age_candidate = random.randint(3, 15) # 子女在 N 年前的年齡
            
            # 檢查過去的子女年齡是否合理 (不能為0或負)
            if past_child_age_candidate <= 0:
                continue

            # 推導目前的子女年齡和父母年齡
            age_diff_candidate = (target_ratio - 1) * past_child_age_candidate
            temp_current_child_age = past_child_age_candidate + years_ago
            temp_current_parent_age = temp_current_child_age + age_diff_candidate

            # 檢查年齡是否合理
            if (25 <= temp_current_parent_age <= 60 and 8 <= temp_current_child_age <= 20 and 
                temp_current_parent_age > temp_current_child_age and temp_current_child_age > 0):
                final_current_parent_age = temp_current_parent_age
                final_current_child_age = temp_current_child_age
                age_diff = age_diff_candidate
                break
        
        if attempts == 50: # 實在找不到，使用預設值
            final_current_parent_age = 40
            final_current_child_age = 10
            age_diff = 30 # 40-10 = 30
            years_ago = 5 # 5年前: 父母35, 子女5. 35/5 = 7
            target_ratio = 7

        q_template = r"{p1_name}比{p2_name}大{diff}歲。{years_ago}年前，{p1_name}的年齡是{p2_name}年齡的{ratio}倍。請問{p1_name}和{p2_name}現在分別是幾歲？"
        question_text = q_template.replace("{p1_name}", person1_name)\
                                  .replace("{p2_name}", person2_name)\
                                  .replace("{diff}", _format_value_for_question(age_diff))\
                                  .replace("{years_ago}", _format_value_for_question(years_ago))\
                                  .replace("{ratio}", _format_value_for_question(target_ratio))
        
        correct_answer = r"({a},{b})".replace("{a}", _format_value_for_question(final_current_parent_age))\
                                     .replace("{b}", _format_value_for_question(final_current_child_age))
        answer = (final_current_parent_age, final_current_child_age)

    # --- 數據與欄位 (Standard Fields) ---
    # 返回字典必須且僅能包含 question_text, correct_answer, answer, image_base64。
    # 更新時必須將 created_at 設為 datetime.now() 並遞增 version。
    return {
        "question_text": question_text,
        "correct_answer": correct_answer, # 字串化的答案，例如 "10" 或 "(40,10)"
        "answer": answer, # 原始數據類型，例如 10 或 (40, 10)
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(), # ISO 8601 格式時間戳
        "version": "1.0.0" # 初始版本號
    }


# 此技能 (年齡問題) 不涉及矩陣或行列式，故相關規則不適用。
# 若涉及，則 `correct_answer` 必須為字串化的二維列表 (e.g., "[[1,2],[3,4]]")，
# 且 `question_text` 必須包含 "^" 或 "[" 等手寫特徵符號以強制觸發手寫模式。 

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
