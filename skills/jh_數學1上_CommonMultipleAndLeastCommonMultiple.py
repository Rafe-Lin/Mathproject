# ==============================================================================
# ID: jh_數學1上_CommonMultipleAndLeastCommonMultiple
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 51.22s | RAG: 5 examples
# Created At: 2026-01-14 19:01:57
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



import datetime
import base64
import io

# --- 輔助函式通用規範 (Generic Helper Rules) ---
# 所有輔助函式必須明確使用 'return' 語句回傳結果。
# 若結果用於拼接 question_text，則回傳值必須強制轉為字串 (str)。
# 視覺化函式 (若有) 僅能接收「題目已知數據」，嚴禁將「答案數據」傳入。

def _gcd(a, b):
    """計算兩個數字的最大公因數。"""
    while b:
        a, b = b, a % b
    return a

def _lcm(a, b):
    """計算兩個數字的最小公倍數。"""
    if a == 0 or b == 0:
        return 0
    # 使用公式 lcm(a, b) = |a*b| / gcd(a, b)
    # 為了避免中間乘積溢位 (雖然在K12範圍內不太可能，但為良好習慣)，先除後乘
    return abs(a // _gcd(a, b) * b)

def _lcm_multiple(numbers):
    """計算一系列數字的最小公倍數。"""
    if not numbers:
        return 1
    result = numbers[0]
    for i in range(1, len(numbers)):
        result = _lcm(result, numbers[i])
    return result

# --- 頂層函式 ---
# 嚴禁使用 class 封裝。必須直接定義 generate() 與 check() 於模組最外層。
# 確保代碼不依賴全域狀態，以便系統執行 importlib.reload。

def generate(level=1):
    """
    生成 K12 數學「公倍數與最小公倍數」的題目。
    根據規範，確保程式結構、題型多樣性、排版與 LaTeX 安全，以及數據欄位標準。
    """
    # 確保代碼不依賴全域狀態，每次執行時重新初始化隨機數生成器
    random.seed()

    # 初始化返回字典的欄位
    question_text = ""
    correct_answer = ""  # 用於程式檢查的標準答案格式 (純數字或逗號分隔)
    answer_display = ""  # 用於向用戶顯示的答案格式 (可能包含單位或連接詞)
    image_base64 = None  # 本技能暫無視覺化需求，預設為 None

    # 題型多樣性：實作至少 3 種不同的題型變體
    problem_types = [
        "direct_calculation",     # 直接計算最小公倍數或公倍數
        "inverse_problem",        # 逆向求解，已知LCM求原數
        "contextual_application"  # 情境應用題
    ]
    selected_type = random.choice(problem_types)

    if selected_type == "direct_calculation":
        # 直接計算題型的子變體
        sub_type = random.choice(["lcm_two_numbers", "lcm_three_numbers", "common_multiples_in_range"])

        if sub_type == "lcm_two_numbers":
            # 題目：求兩個數字的最小公倍數
            num1 = random.randint(6, 40)
            num2 = random.randint(6, 40)
            # 確保數字不相同，且非簡單的倍數關係 (非互質，非倍數關係)，使題目更具挑戰性
            # 重新生成直到滿足條件
            while num1 == num2 or num1 % num2 == 0 or num2 % num1 == 0 or _gcd(num1, num2) == 1:
                num1 = random.randint(6, 40)
                num2 = random.randint(6, 40)
            
            ans_val = _lcm(num1, num2)
            
            # 排版與 LaTeX 安全：嚴禁使用 f-string 或 % 格式化
            question_text = r"求出 {num1} 和 {num2} 的最小公倍數。".replace("{num1}", str(num1)).replace("{num2}", str(num2))
            answer_display = str(ans_val)
            correct_answer = str(ans_val)

        elif sub_type == "lcm_three_numbers":
            # 題目：求三個數字的最小公倍數
            num1 = random.randint(3, 15)
            num2 = random.randint(3, 15)
            num3 = random.randint(3, 15)
            # 確保三個數字不同，且LCM不是其中任何一個數字 (避免 2, 4, 8 這種 LCM 為 8 的簡單情況)
            while (len(set([num1, num2, num3])) < 3 or 
                   _lcm_multiple([num1, num2, num3]) in [num1, num2, num3]):
                num1 = random.randint(3, 15)
                num2 = random.randint(3, 15)
                num3 = random.randint(3, 15)
            
            ans_val = _lcm_multiple([num1, num2, num3])

            question_text = r"求出 {num1}、{num2} 和 {num3} 的最小公倍數。".replace("{num1}", str(num1)).replace("{num2}", str(num2)).replace("{num3}", str(num3))
            answer_display = str(ans_val)
            correct_answer = str(ans_val)

        elif sub_type == "common_multiples_in_range":
            # 題目：找出在特定範圍內的所有公倍數
            num1 = random.randint(4, 15)
            num2 = random.randint(4, 15)
            # 確保非互質且非倍數關係，以產生更多樣的LCM
            while num1 == num2 or num1 % num2 == 0 or num2 % num1 == 0 or _gcd(num1, num2) == 1:
                num1 = random.randint(4, 15)
                num2 = random.randint(4, 15)
            
            lcm_val = _lcm(num1, num2)
            
            # 設定範圍，確保範圍內至少有幾個公倍數
            min_multiples_count = 2 # 範圍內至少2個公倍數
            max_multiples_count = 5 # 範圍內最多5個公倍數

            # 確保起始點在 LCM 的倍數附近，且不至於太小
            start_multiple_factor = random.randint(1, 3) 
            start_range_lower_bound = lcm_val * start_multiple_factor
            start_range_upper_bound = lcm_val * (start_multiple_factor + 1) - 1 # 確保不會跳過LCM的倍數
            start_range = random.randint(start_range_lower_bound, start_range_upper_bound)

            # 確保結束點能包含足夠的公倍數
            end_range_min_val = start_range + lcm_val * min_multiples_count
            end_range_max_val = start_range + lcm_val * max_multiples_count + lcm_val - 1
            end_range = random.randint(end_range_min_val, end_range_max_val)
            
            common_multiples = []
            # 找到第一個大於等於 start_range 的公倍數
            first_multiple_in_range = ((start_range - 1) // lcm_val + 1) * lcm_val
            
            current_multiple = first_multiple_in_range
            while current_multiple <= end_range:
                common_multiples.append(current_multiple)
                current_multiple += lcm_val
            
            # 確保生成的題目至少有 min_multiples_count 個公倍數
            # 避免因隨機範圍導致公倍數過少或沒有 (儘管上面的邏輯已盡力避免)
            if len(common_multiples) < min_multiples_count:
                # 重新調整範圍以保證數量
                start_range = lcm_val * random.randint(1, 2)
                end_range = start_range + lcm_val * random.randint(min_multiples_count + 1, max_multiples_count + 2)
                common_multiples = []
                first_multiple_in_range = ((start_range - 1) // lcm_val + 1) * lcm_val
                current_multiple = first_multiple_in_range
                while current_multiple <= end_range:
                    common_multiples.append(current_multiple)
                    current_multiple += lcm_val
            
            ans_val_str = ", ".join(map(str, sorted(common_multiples))) # 逗號分隔
            
            question_text = r"找出 {num1} 和 {num2} 在 {start} 到 {end} 之間的所有公倍數 (包含 {start} 和 {end})，並由小到大排列，用逗號分隔。".replace("{num1}", str(num1)).replace("{num2}", str(num2)).replace("{start}", str(start_range)).replace("{end}", str(end_range))
            answer_display = ans_val_str
            correct_answer = ans_val_str

    elif selected_type == "inverse_problem":
        # 逆向求解題型的子變體
        sub_type = random.choice(["find_other_number_given_lcm_and_one", "find_numbers_given_lcm_and_ratio"])

        if sub_type == "find_other_number_given_lcm_and_one":
            # 題目：已知兩個正整數的最小公倍數和其中一個數，求另一個數。
            # 策略：先生成兩個數，再計算LCM，然後隱藏其中一個。
            n1 = random.randint(6, 20)
            n2 = random.randint(6, 20)
            # 確保數字不相同，且非簡單的倍數關係，也不是互質，使題目有挑戰性
            while n1 == n2 or n1 % n2 == 0 or n2 % n1 == 0 or _gcd(n1, n2) == 1:
                n1 = random.randint(6, 20)
                n2 = random.randint(6, 20)
            
            lcm_val = _lcm(n1, n2)
            
            # 隨機選擇一個數作為已知數
            if random.choice([True, False]):
                known_num = n1
                ans_val = n2
            else:
                known_num = n2
                ans_val = n1
            
            question_text = r"已知兩個正整數的最小公倍數是 {lcm_val}。如果其中一個數是 {known_num}，那麼另一個數是多少？".replace("{lcm_val}", str(lcm_val)).replace("{known_num}", str(known_num))
            answer_display = str(ans_val)
            correct_answer = str(ans_val)

        elif sub_type == "find_numbers_given_lcm_and_ratio":
            # 題目：已知兩個正整數的最小公倍數和它們的比，求這兩個數。
            # 策略：選擇兩個互質的比例數 r1, r2 和一個公因數 k。
            # 兩個數為 r1*k 和 r2*k。LCM 為 r1*r2*k。
            r1 = random.randint(2, 7)
            r2 = random.randint(2, 7)
            while r1 == r2 or _gcd(r1, r2) != 1: # 確保 r1, r2 互質且不相等
                r1 = random.randint(2, 7)
                r2 = random.randint(2, 7)
            
            k = random.randint(2, 5) # 公因數
            
            num1 = r1 * k
            num2 = r2 * k
            
            lcm_val = _lcm(num1, num2) # 計算實際的LCM
            
            # 確保比例數 r1 < r2，以保持問題描述一致性
            if r1 > r2:
                r1, r2 = r2, r1
            
            ans_val_pair = sorted([num1, num2]) # 答案以排序後的數字呈現
            ans_val_str = r"{n1} 和 {n2}".replace("{n1}", str(ans_val_pair[0])).replace("{n2}", str(ans_val_pair[1]))
            
            question_text = r"有兩個正整數，它們的最小公倍數是 {lcm_val}，且它們的比是 {r1}:{r2}。請問這兩個數分別是多少？(請由小到大排列，用'和'字連接)".replace("{lcm_val}", str(lcm_val)).replace("{r1}", str(r1)).replace("{r2}", str(r2))
            correct_answer = f"{ans_val_pair[0]},{ans_val_pair[1]}" # 用逗號分隔作為程式檢查標準
            answer_display = ans_val_str

    elif selected_type == "contextual_application":
        # 情境應用題型的子變體
        sub_type = random.choice(["event_scheduling", "tiling_problem"])

        if sub_type == "event_scheduling":
            # 題目：兩種事件同時發生後，下次再同時發生的時間（公車、火車等）
            interval1 = random.randint(5, 18)
            interval2 = random.randint(5, 18)
            while interval1 == interval2 or _gcd(interval1, interval2) == 1: # 確保間隔時間不同且非互質，使LCM不等於乘積
                interval1 = random.randint(5, 18)
                interval2 = random.randint(5, 18)
            
            ans_val = _lcm(interval1, interval2)
            
            entity_options = ["公車", "火車", "航班", "船班"]
            unit_options = ["分鐘", "小時"]
            
            entity1 = random.choice(entity_options)
            entity2 = random.choice([e for e in entity_options if e != entity1]) # 確保兩種實體不同
            unit = random.choice(unit_options)
            
            question_text = r"某車站有兩種 {entity1} 和 {entity2}。{entity1} 每 {interval1} {unit} 發一班，{entity2} 每 {interval2} {unit} 發一班。如果現在兩種 {entity1} 和 {entity2} 同時發車，請問最快要再過多久兩種車會再次同時發車？".replace("{entity1}", entity1).replace("{entity2}", entity2).replace("{interval1}", str(interval1)).replace("{interval2}", str(interval2)).replace("{unit}", unit)
            answer_display = r"{ans_val}{unit}".replace("{ans_val}", str(ans_val)).replace("{unit}", unit)
            correct_answer = str(ans_val) # 程式檢查僅需數字部分

        elif sub_type == "tiling_problem":
            # 題目：用長方形磁磚鋪成最小正方形的邊長
            len1 = random.randint(8, 25)
            len2 = random.randint(8, 25)
            while len1 == len2 or _gcd(len1, len2) == 1: # 確保非互質且非倍數關係
                len1 = random.randint(8, 25)
                len2 = random.randint(8, 25)
            
            ans_val = _lcm(len1, len2)
            
            unit = random.choice(["公分", "公尺"])
            
            question_text = r"小明想用長 {len1} {unit}、寬 {len2} {unit} 的長方形磁磚鋪成一個最小的正方形。請問這個正方形的邊長是多少 {unit}？".replace("{len1}", str(len1)).replace("{len2}", str(len2)).replace("{unit}", unit)
            answer_display = r"{ans_val}{unit}".replace("{ans_val}", str(ans_val)).replace("{unit}", unit)
            correct_answer = str(ans_val) # 程式檢查僅需數字部分
            
    # 返回字典必須且僅能包含 question_text, correct_answer, answer, image_base64
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "image_base64": image_base64,
        "created_at": datetime.datetime.now().isoformat(), # 時間戳記
        "version": "1.0" # 遞增版本號
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
