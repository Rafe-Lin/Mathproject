# ==============================================================================
# ID: jh_數學1上_SimplestFraction
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 48.74s | RAG: 5 examples
# Created At: 2026-01-14 20:38:02
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
import base64
from io import BytesIO

# --- 輔助函式 (Helper Functions) ---
# 遵循通用規範：明確回傳值，若用於question_text則強制轉為str，不洩漏答案數據。

def _simplify_fraction(n: int, d: int) -> tuple[int, int]:
    """
    將分數 n/d 化為最簡分數。
    回傳 (簡化後的分子, 簡化後的分母)。
    確保分母為正數。
    """
    if d == 0:
        raise ValueError("分母不能為零。")
    
    # 分子為零時，分數為零，簡化為 0/1
    if n == 0:
        return 0, 1 

    # 計算最大公因數
    common_divisor = math.gcd(abs(n), abs(d))
    
    simplified_n = n // common_divisor
    simplified_d = d // common_divisor
    
    # 確保分母為正。如果原始分母為負，將負號移至分子。
    if simplified_d < 0:
        simplified_n = -simplified_n
        simplified_d = -simplified_d
        
    return simplified_n, simplified_d

def _format_fraction_string(numerator: int, denominator: int) -> str:
    """
    將分子和分母格式化為分數或整數的字串表示。
    例如：(1, 2) -> "1/2", (5, 1) -> "5"。
    此函式回傳值會用於 correct_answer 和 answer 欄位。
    """
    if denominator == 1:
        return str(numerator)
    return f"{numerator}/{denominator}" # 此處的 f-string 不包含 LaTeX 指令，因此安全。

def _parse_fraction_string_to_simplified_tuple(s: str) -> tuple[int, int] | tuple[None, None]:
    """
    解析字串形式的分數 (e.g., "1/2", "5") 並返回其最簡形式的 (分子, 分母) tuple。
    若解析失敗或分母為零，返回 (None, None)。
    """
    s = s.strip()
    if '/' in s:
        try:
            n_str, d_str = s.split('/')
            n = int(n_str)
            d = int(d_str)
            if d == 0: 
                return None, None # 無效分數
            return _simplify_fraction(n, d)
        except ValueError:
            return None, None # 非有效分數格式
    else:
        try:
            n = int(s)
            return _simplify_fraction(n, 1) # 整數視為分母為1的分數
        except ValueError:
            return None, None # 非有效整數格式

# --- 頂層函式 (Top-Level Functions) ---
# 遵循程式結構規範：直接定義於模組最外層，嚴禁 class 封裝，不依賴全域狀態。

def generate(level: int = 1) -> dict:
    """
    生成「最簡分數」問題。
    遵循題型多樣性、排版與 LaTeX 安全、數據與欄位規範。
    """
    problem_type = random.choice([1, 2, 3])
    
    question_text = ""
    correct_answer_val = ""
    answer_display = ""
    image_base64_str = "" # 本技能無需圖片，預設為空字串

    # Type 1 (Maps to Example 1, 3): 直接計算 - 將給定分數化為最簡分數。
    if problem_type == 1:
        # 生成可簡化的分數
        common_factor = random.randint(2, 12) # 最大公因數
        num_base = random.randint(1, 15)
        den_base = random.randint(num_base + 1, 20) # 確保分母通常大於分子，形成真分數

        numerator_initial = num_base * common_factor
        denominator_initial = den_base * common_factor
        
        # 確保初始分數確實可簡化 (即不是已經是最簡分數)
        while math.gcd(numerator_initial, denominator_initial) == 1:
            common_factor = random.randint(2, 12)
            num_base = random.randint(1, 15)
            den_base = random.randint(num_base + 1, 20)
            numerator_initial = num_base * common_factor
            denominator_initial = den_base * common_factor
            
        # 增加假分數或整數的機會
        if random.random() < 0.3: # 30% 機率生成假分數或整數
            if random.random() < 0.5: # 假分數
                # 將分子和分母對調，然後確保分子大於分母
                numerator_initial, denominator_initial = denominator_initial, numerator_initial
                if numerator_initial < denominator_initial:
                    numerator_initial += denominator_initial * random.randint(1, 3)
            else: # 整數
                # 生成一個分母，使其能被分子整除
                temp_den = random.randint(1, 10)
                numerator_initial = random.randint(1, 10) * temp_den * common_factor
                denominator_initial = temp_den * common_factor
                # 避免分母為0，雖然在當前邏輯下不會發生，但保留以遵循原規範
                if denominator_initial == 0: 
                    denominator_initial = common_factor * random.randint(1, 5)
                    numerator_initial = random.randint(1, 10) * denominator_initial
        
        # 處理分子為零的特殊情況
        if random.random() < 0.05: # 5% 機率生成分子為零的題目
            numerator_initial = 0
            denominator_initial = random.randint(1, 20) * common_factor
            # 避免分母為0，雖然在當前邏輯下不會發生，但保留以遵循原規範
            if denominator_initial == 0: denominator_initial = 5 

        simplified_num, simplified_den = _simplify_fraction(numerator_initial, denominator_initial)
        
        # LaTeX 安全規範：使用 .replace() 避免 f-string 與 LaTeX 衝突
        question_text_template = r"請將分數 $\frac{{{num}}}{{{den}}}$ 化為最簡分數。"
        question_text = question_text_template.replace("{num}", str(numerator_initial)).replace("{den}", str(denominator_initial))
        
        correct_answer_val = _format_fraction_string(simplified_num, simplified_den)
        answer_display = correct_answer_val

    # Type 2 (Maps to Example 2, 4): 逆向求解 - 已知最簡分數求原分數的某部分。
    elif problem_type == 2:
        simplified_num = random.randint(1, 10)
        simplified_den = random.randint(simplified_num + 1, 15) # 確保簡化後為真分數
        
        # 確保簡化後的分數確實是最簡分數 (分子分母互質)
        while math.gcd(simplified_num, simplified_den) != 1:
            simplified_num = random.randint(1, 10)
            simplified_den = random.randint(simplified_num + 1, 15)

        multiplier = random.randint(2, 8) # 用於擴大分數的乘數
        
        # 隨機決定是分子還是分母為未知數
        if random.random() < 0.5: # 缺少分子
            unknown_den_val = simplified_den * multiplier
            correct_num_val = simplified_num * multiplier
            
            question_text_template = r"若分數 $\frac{{{unknown}}}{{{den}}}$ 化為最簡分數後是 $\frac{{{s_num}}}{{{s_den}}}$，請問 ${{unknown}}$ 是多少？"
            question_text = question_text_template.replace("{unknown}", "a").replace("{den}", str(unknown_den_val)).replace("{s_num}", str(simplified_num)).replace("{s_den}", str(simplified_den))
            correct_answer_val = str(correct_num_val)
            answer_display = str(correct_num_val)
        else: # 缺少分母
            unknown_num_val = simplified_num * multiplier
            correct_den_val = simplified_den * multiplier
            
            question_text_template = r"若分數 $\frac{{{num}}}{{{unknown}}}$ 化為最簡分數後是 $\frac{{{s_num}}}{{{s_den}}}$，請問 ${{unknown}}$ 是多少？"
            question_text = question_text_template.replace("{num}", str(unknown_num_val)).replace("{unknown}", "b").replace("{s_num}", str(simplified_num)).replace("{s_den}", str(simplified_den))
            correct_answer_val = str(correct_den_val)
            answer_display = str(correct_den_val)

    # Type 3 (Maps to Example 5, 6): 情境應用 - 應用題求最簡分數。
    elif problem_type == 3:
        scenario = random.choice([
            "班級中男生與女生的比例",
            "水果籃中蘋果與橘子的比例",
            "一份食譜中麵粉與糖的比例",
            "一個農場裡牛與羊的比例",
            "一段路程的完成比例"
        ])
        
        if "班級" in scenario:
            item1 = "男生"
            item2 = "女生"
            total_students = random.randint(20, 40)
            num1 = random.randint(5, total_students - 5)
            # num2 = total_students - num1 # num2 not directly used in question logic
            
            question_text_template = r"一個班級有 {num1} 位{item1}和 {num2} 位{item2}。請問{item1}佔全班人數的最簡分數是多少？"
            question_text = question_text_template.replace("{num1}", str(num1)).replace("{item1}", item1).replace("{num2}", str(total_students - num1)).replace("{item2}", item2)
            
            simplified_n, simplified_d = _simplify_fraction(num1, total_students)
            correct_answer_val = _format_fraction_string(simplified_n, simplified_d)
            answer_display = correct_answer_val
            
        elif "水果" in scenario:
            item1 = "蘋果"
            item2 = "橘子"
            num1 = random.randint(5, 20)
            num2 = random.randint(5, 20)
            total_fruits = num1 + num2
            
            choice_q = random.choice([item1, item2])
            
            question_text_template = r"水果籃裡有 {num1} 顆{item1}和 {num2} 顆{item2}。請問{choice_q}佔所有水果數量的最簡分數是多少？"
            question_text = question_text_template.replace("{num1}", str(num1)).replace("{item1}", item1).replace("{num2}", str(num2)).replace("{item2}", item2).replace("{choice_q}", choice_q)
            
            numerator_for_q = num1 if choice_q == item1 else num2
            simplified_n, simplified_d = _simplify_fraction(numerator_for_q, total_fruits)
            correct_answer_val = _format_fraction_string(simplified_n, simplified_d)
            answer_display = correct_answer_val
        
        elif "食譜" in scenario:
            item1 = "麵粉"
            item2 = "糖"
            unit = "克"
            num1 = random.randint(100, 500) # 麵粉重量
            num2 = random.randint(50, 300)  # 糖重量
            
            question_text_template = r"一份食譜需要 {num1}{unit}{item1}和 {num2}{unit}{item2}。請問{item1}的重量佔{item2}的重量的最簡分數是多少？"
            question_text = question_text_template.replace("{num1}", str(num1)).replace("{unit}", unit).replace("{item1}", item1).replace("{num2}", str(num2)).replace("{item2}", item2)
            
            simplified_n, simplified_d = _simplify_fraction(num1, num2)
            correct_answer_val = _format_fraction_string(simplified_n, simplified_d)
            answer_display = correct_answer_val

        elif "農場" in scenario:
            item1 = "牛"
            item2 = "羊"
            num1 = random.randint(10, 50)
            num2 = random.randint(10, 50)
            total_animals = num1 + num2
            
            choice_q = random.choice([item1, item2])
            
            question_text_template = r"一個農場裡有 {num1} 隻{item1}和 {num2} 隻{item2}。請問{choice_q}的數量佔所有動物數量的最簡分數是多少？"
            question_text = question_text_template.replace("{num1}", str(num1)).replace("{item1}", item1).replace("{num2}", str(num2)).replace("{item2}", item2).replace("{choice_q}", choice_q)
            
            numerator_for_q = num1 if choice_q == item1 else num2
            simplified_n, simplified_d = _simplify_fraction(numerator_for_q, total_animals)
            correct_answer_val = _format_fraction_string(simplified_n, simplified_d)
            answer_display = correct_answer_val
            
        elif "路程" in scenario:
            # 確保生成的路程數值可簡化
            common_factor_path = random.randint(2, 6)
            base_completed = random.randint(1, 5)
            base_total = random.randint(base_completed + 1, 10) # 確保完成部分小於總路程
            
            completed_distance_units = base_completed * common_factor_path
            total_distance_units = base_total * common_factor_path
            
            # 確保初始分數確實可簡化
            while math.gcd(completed_distance_units, total_distance_units) == 1:
                common_factor_path = random.randint(2, 6)
                base_completed = random.randint(1, 5)
                base_total = random.randint(base_completed + 1, 10)
                completed_distance_units = base_completed * common_factor_path
                total_distance_units = base_total * common_factor_path

            question_text_template = r"小明完成了一段路程的 {completed} 單元，總路程為 {total} 單元。請問小明完成了總路程的最簡分數是多少？"
            question_text = question_text_template.replace("{completed}", str(completed_distance_units)).replace("{total}", str(total_distance_units))
            
            simplified_n, simplified_d = _simplify_fraction(completed_distance_units, total_distance_units)
            correct_answer_val = _format_fraction_string(simplified_n, simplified_d)
            answer_display = correct_answer_val

    return {
        "question_text": question_text,
        "correct_answer": correct_answer_val,
        "answer": answer_display,
        "image_base64": image_base64_str,
        "created_at": datetime.now().isoformat(),
        "version": "V9.6.1" # 版本號遞增
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
