# ==============================================================================
# ID: jh_數學1上_IntegerDivision
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 22.65s | RAG: 2 examples
# Created At: 2026-01-14 13:39:08
# Fix Status: [Repaired]
# Fixes: Regex=6, Logic=0
#==============================================================================


import random
import math
import matplotlib
# [Fix] Font injection for Traditional Chinese support
matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
matplotlib.rcParams['axes.unicode_minus'] = False
from fractions import Fraction
from functools import reduce

# --- 1. Formatting Helpers ---
def to_latex(num):
    """
    Convert int/float/Fraction to LaTeX.
    Handles mixed numbers automatically for Fractions.
    """
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        # Logic for negative fractions
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return r"{s}{w}".replace("{s}", sign).replace("{w}", str(whole))
            return r"{s}{w} \frac{{rem}}{{den}}".replace("{s}", sign).replace("{w}", str(whole)).replace("{rem}", str(rem_num)).replace("{den}", str(abs_num.denominator))
        return r"\frac{{num}}{{den}}".replace("{num}", str(num.numerator)).replace("{den}", str(num.denominator))
    return str(num)

def fmt_num(num, signed=False, op=False):
    """
    Format number for LaTeX.
    
    Args:
        num: The number to format.
        signed (bool): If True, always show sign (e.g., "+3", "-5").
        op (bool): If True, format as operation with spaces (e.g., " + 3", " - 5").
    """
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    
    is_neg = (num < 0)
    abs_val = to_latex(abs(num))
    
    if op:
        # e.g., " + 3", " - 3"
        return r" - {v}".replace("{v}", abs_val) if is_neg else r" + {v}".replace("{v}", abs_val)
    
    if signed:
        # e.g., "+3", "-3"
        return r"-{v}".replace("{v}", abs_val) if is_neg else r"+{v}".replace("{v}", abs_val)
        
    # Default behavior (parentheses for negative)
    if is_neg: return r"({v})".replace("{v}", latex_val)
    return latex_val

# Alias for AI habits
fmt_fraction_latex = to_latex 

# --- 2. Number Theory Helpers ---
def get_positive_factors(n):
    """Return a sorted list of positive factors of n."""
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))


def get_prime_factorization(n):
    """Return dict {prime: exponent}."""
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

def gcd(a, b): return math.gcd(a, b)
def lcm(a, b): return abs(a * b) // math.gcd(a, b)

# --- 3. Fraction Generator Helper ---
def get_random_fraction(min_val=-10, max_val=10, denominator_limit=10, simple=True):
    """
    Generate a random Fraction within range.
    simple=True ensures it's not an integer.
    """
    for _ in range(100):
        den = random.randint(2, denominator_limit)
        num = random.randint(min_val * den, max_val * den)
        if den == 0: continue
        val = Fraction(num, den)
        if simple and val.denominator == 1: continue # Skip integers
        if val == 0: continue
        return val
    return Fraction(1, 2) # Fallback

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

# --- 4. High-Level Math Objects (Vector/Matrix/Calculus) ---
class Vector3:
    """Simple 3D Vector Class for Geometry."""
    def __init__(self, x, y, z=0): self.x, self.y, self.z = x, y, z
    def __add__(self, o): return Vector3(self.x+o.x, self.y+o.y, self.z+o.z)
    def __sub__(self, o): return Vector3(self.x-o.x, self.y-o.y, self.z-o.z)
    def dot(self, o): return self.x*o.x + self.y*o.y + self.z*o.z
    def cross(self, o): return Vector3(self.y*o.z-self.z*o.y, self.z*o.x-self.x*o.z, self.x*o.y-self.y*o.x)
    def mag(self): return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    def __repr__(self): return f"({self.x}, {self.y}, {self.z})"

class Matrix:
    """Simple Matrix (2x2 or 3x3) for transformations."""
    def __init__(self, rows): self.rows = rows
    def det(self):
        if len(self.rows) == 2: return self.rows[0][0]*self.rows[1][1] - self.rows[0][1]*self.rows[1][0]
        return 0 # Placeholder for 3x3
    def mv(self, v): # Matrix-Vector multiplication
        return Vector3(
            self.rows[0][0]*v.x + self.rows[0][1]*v.y,
            self.rows[1][0]*v.x + self.rows[1][1]*v.y, 0
        )

def draw_integral_area(func_lambda, x_range, color='blue', alpha=0.3):
    """
    [Visual] Helper to plot area under curve. 
    Usage: In generate(), ax.fill_between(x, y, ...).
    Actually, this is just a placeholder to remind AI to use fill_between.
    """
    pass

# --- 5. Standard Answer Checker (Auto-Injected) ---
def check(user_answer, correct_answer):
    """
    [V10.6 Golden Standard] 
    解決字典字串化導致的格式對齊失敗問題。
    """
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    u = str(user_answer).strip().replace(" ", "").replace("，", ",")
    
    # 核心修復：強制將可能的字典字串還原為字典物件
    c_raw = correct_answer
    if isinstance(c_raw, str) and c_raw.startswith("{") and "quotient" in c_raw:
        try:
            import ast
            c_raw = ast.literal_eval(c_raw)
        except: pass

    # 處理「商,餘數」格式
    if isinstance(c_raw, dict) and "quotient" in c_raw:
        q = str(c_raw.get("quotient", ""))
        r = str(c_raw.get("remainder", ""))
        ans_display = r"{q},{r}".replace("{q}", q).replace("{r}", r)
        try:
            # 支援使用者輸入 "8,3" 或 "商8餘3"
            u_parts = u.replace("商", "").replace("餘", ",").split(",")
            if len(u_parts) >= 2 and int(u_parts[0]) == int(q) and int(u_parts[1]) == int(r):
                return {"correct": True, "result": "正確！"}
        except: pass
    else:
        ans_display = str(c_raw).strip()

    if u == ans_display.replace(" ", ""): return {"correct": True, "result": "正確！"}
    try:
        if math.isclose(float(u), float(ans_display), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
    except: pass
    
    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", ans_display)}
           
from datetime import datetime
import base64
import io


# 輔助函式：格式化數字，尤其針對負數在 LaTeX 環境中可能需要括號的情況。
# 依照規範，即使是簡單的數字轉換，若字串可能包含 LaTeX，也需使用 .replace()
def _format_signed_number(num):
    """
    格式化數字為字串，將負數用括號括起來，以確保在 LaTeX 數學表達式中的清晰度。
    範例：-5 -> (-5), 5 -> 5
    """
    if num < 0:
        return r"({num_val})".replace("{num_val}", str(num))
    return str(num)

# 輔助函式：解析使用者輸入的商和餘數
def _parse_quotient_remainder_input(user_input_str):
    """
    解析如 "商5餘3", "5餘3", "5,3", "5 3" 等格式的字串，轉換為 (商, 餘數) 元組。
    若解析失敗，回傳 (None, None)。
    """
    user_input_str = str(user_input_str).strip().replace(" ", "").lower()
    
    # 嘗試解析 "商Q餘R" 或 "Q餘R" 格式
    if "餘" in user_input_str:
        parts = user_input_str.split("餘")
        if len(parts) == 2:
            q_str = parts[0].replace("商", "")
            r_str = parts[1]
            try:
                quotient = int(q_str)
                remainder = int(r_str)
                return (quotient, remainder)
            except ValueError:
                pass

    # 嘗試解析 "Q,R" 格式
    if "," in user_input_str:
        parts = user_input_str.split(",")
        if len(parts) == 2:
            try:
                quotient = int(parts[0])
                remainder = int(parts[1])
                return (quotient, remainder)
            except ValueError:
                pass
    
    # 若只提供一個數字，假設是精確除法的商，餘數為0
    try:
        quotient = int(user_input_str)
        return (quotient, 0)
    except ValueError:
        pass

    return (None, None) # 表示解析失敗

# 題型變體 1: 直接計算
def _generate_direct_calculation(level):
    """生成直接的整數除法計算題。"""
    
    if level == 1:
        dividend_range = (-50, 50)
        divisor_range = (2, 10) # 為了 K12 餘數定義清晰，除數設為正數
    else:
        dividend_range = (-100, 100)
        divisor_range = (2, 20)

    # 確保除數不為 0 或 1，以增加題目變化性
    while True:
        dividend = random.randint(dividend_range[0], dividend_range[1])
        divisor = random.randint(divisor_range[0], divisor_range[1])
        if divisor != 0 and abs(divisor) != 1: 
            break
            
    # 依 K12 標準計算商和餘數：0 <= 餘數 < 除數
    quotient = dividend // divisor
    remainder = dividend % divisor
    
    # Python 的 `%` 運算符會使餘數與除數同號。
    # 若 dividend 是負數，且 remainder 不為 0，則需要調整以確保餘數非負。
    # 範例：-7 // 3 = -3, -7 % 3 = 2 (此時餘數已為正，符合 K12 標準)
    # 因此，在除數為正的情況下，Python 的 `//` 和 `%` 已經符合 K12 標準。

    # 嚴格遵循 LaTeX 安全規範，使用 .replace()
    question_text = r"計算：${dividend} \div {divisor} = ?$".replace("{dividend}", _format_signed_number(dividend)).replace("{divisor}", _format_signed_number(divisor))
    
    if remainder == 0:
        correct_ans_str = str(quotient)
    else:
        # 回傳字典以符合 check 函式的特殊處理邏輯
        correct_ans_str = {"quotient": quotient, "remainder": remainder}
    
    return {
        "question_text": question_text,
        "correct_answer": correct_ans_str,
        "answer": correct_ans_str,
        "image_base64": None
    }

# 題型變體 2: 逆向求解
def _generate_inverse_problem(level):
    """生成逆向求解的整數除法問題（例如：已知商和餘數，求被除數或除數）。"""
    
    if level == 1:
        q_range = (-10, 10)
        d_range = (2, 10) # 除數保持正數
        r_range_factor = 0.8 # 餘數最大為除數的 80%
    else:
        q_range = (-20, 20)
        d_range = (2, 20)
        r_range_factor = 0.9

    problem_type = random.choice(["find_dividend", "find_divisor"])

    if problem_type == "find_dividend":
        divisor = random.randint(d_range[0], d_range[1])
        quotient = random.randint(q_range[0], q_range[1])
        remainder = random.randint(0, int(divisor * r_range_factor)) # 0 <= remainder < divisor
        
        dividend = quotient * divisor + remainder
        
        question_text = r"已知 $x \div {divisor} = {quotient} \dots {remainder}$，求 $x$。".replace("{divisor}", _format_signed_number(divisor)).replace("{quotient}", _format_signed_number(quotient)).replace("{remainder}", str(remainder))
        correct_ans_str = str(dividend)
        
    else: # find_divisor (A / X = Q ... R, 求 X)
        # A = QX + R  => X = (A - R) / Q
        # 需確保 (A - R) 能被 Q 整除，且 0 <= R < X。
        
        while True:
            # 先選定一個可能的除數 (X)，然後依此生成其他參數
            divisor_candidate = random.randint(d_range[0], d_range[1])
            quotient = random.randint(q_range[0], q_range[1])
            
            # 避免商為 0，這會讓除數 X 不明確或造成除以 0
            if quotient == 0:
                continue

            remainder = random.randint(0, int(divisor_candidate * r_range_factor))
            
            dividend = quotient * divisor_candidate + remainder

            # 驗證生成的數字是否滿足作為「求除數」的條件
            if quotient != 0 and (dividend - remainder) % quotient == 0:
                calculated_divisor = (dividend - remainder) // quotient
                # 確保餘數小於除數，且除數為正
                if calculated_divisor > remainder and calculated_divisor > 0: 
                    divisor = calculated_divisor
                    break
        
        question_text = r"已知 ${dividend} \div x = {quotient} \dots {remainder}$，求 $x$。".replace("{dividend}", _format_signed_number(dividend)).replace("{quotient}", _format_signed_number(quotient)).replace("{remainder}", str(remainder))
        correct_ans_str = str(divisor)
        
    return {
        "question_text": question_text,
        "correct_answer": correct_ans_str,
        "answer": str(correct_ans_str),
        "image_base64": None
    }

# 題型變體 3: 情境應用
def _generate_contextual_problem(level):
    """生成涉及整數除法的情境應用題。"""
    
    if level == 1:
        num_items_range = (20, 100)
        num_groups_range = (3, 15)
        temp_change_range = (2, 5) # 每天溫度變化量
    else:
        num_items_range = (50, 200)
        num_groups_range = (5, 25)
        temp_change_range = (3, 7)

    scenario_type = random.choice([
        "sharing_items",    # 分享物品 (求商和餘數)
        "packing_items",    # 裝箱物品 (求商和餘數)
        "temperature_change" # 溫度變化 (求天數，可能涉及負數，但最終答案為正整數)
    ])

    if scenario_type == "sharing_items":
        total_items = random.randint(num_items_range[0], num_items_range[1])
        num_people = random.randint(num_groups_range[0], num_groups_range[1])
        
        quotient = total_items // num_people
        remainder = total_items % num_people
        
        question_text = r"小明有 ${total_items}$ 顆糖果，平均分給 ${num_people}$ 位同學，每位同學分到幾顆？還剩下幾顆？".replace("{total_items}", str(total_items)).replace("{num_people}", str(num_people))
        correct_ans_str = {"quotient": quotient, "remainder": remainder}

    elif scenario_type == "packing_items":
        total_items = random.randint(num_items_range[0], num_items_range[1])
        items_per_box = random.randint(num_groups_range[0], num_groups_range[1])
        
        quotient = total_items // items_per_box
        remainder = total_items % items_per_box
        
        question_text = r"某工廠生產了 ${total_items}$ 個零件，每 ${items_per_box}$ 個裝成一箱。總共可以裝滿幾箱？還剩下幾個零件？".replace("{total_items}", str(total_items)).replace("{items_per_box}", str(items_per_box))
        correct_ans_str = {"quotient": quotient, "remainder": remainder}

    else: # temperature_change
        initial_temp = random.randint(10, 30)
        drop_per_day = random.randint(temp_change_range[0], temp_change_range[1])
        
        # 確保總降溫量是每天下降量的倍數，以得到整數天數
        min_total_drop = drop_per_day * 2 # 至少兩天
        max_total_drop = drop_per_day * (level * 5 + 10) # 根據 level 調整最大天數
        
        # 生成一個 `total_drop` 確保它是 `drop_per_day` 的倍數
        multiples = [i for i in range(min_total_drop, max_total_drop + 1, drop_per_day)]
        if not multiples: # 萬一範圍太小找不到倍數
            total_drop = drop_per_day * 3
        else:
            total_drop = random.choice(multiples)
        
        target_temp = initial_temp - total_drop
        quotient_days = total_drop // drop_per_day # 餘數為 0
        
        question_text = r"某地初始溫度為 ${initial_temp}$°C，每天下降 ${drop_per_day}$°C。請問經過幾天後，溫度會達到 ${target_temp}$°C？".replace("{initial_temp}", str(initial_temp)).replace("{drop_per_day}", str(drop_per_day)).replace("{target_temp}", str(target_temp))
        correct_ans_str = str(quotient_days)

    return {
        "question_text": question_text,
        "correct_answer": correct_ans_str,
        "answer": str(correct_ans_str),
        "image_base64": None
    }

# 頂層函式：生成題目
def generate(level=1):
    """
    根據指定難度等級 (level) 生成一道整數除法運算題目。
    不依賴全域狀態，確保 importlib.reload 可正常運作。
    """
    
    problem_generators = [
        _generate_direct_calculation,
        _generate_inverse_problem,
        _generate_contextual_problem,
    ]
    
    # 隨機選擇一種題型變體
    chosen_generator = random.choice(problem_generators)
    
    # 生成題目數據
    problem_data = chosen_generator(level)
    
    # 填充標準欄位
    problem_data["created_at"] = datetime.now().isoformat()
    problem_data["version"] = "9.6" 
    
    return problem_data

# 頂層函式：檢查使用者答案



# [Auto-Injected Patch v10.4] Universal Return, Linebreak & Chinese Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤。'}
        if isinstance(res, dict):
            if 'question_text' in res and isinstance(res['question_text'], str):
                res['question_text'] = res['question_text'].replace("\\n", "\n")
            if func.__name__ == 'check' and 'result' in res:
                if res['result'].lower() in ['correct!', 'correct', 'right']:
                    res['result'] = '正確！'
                elif res['result'].lower() in ['incorrect', 'wrong', 'error']:
                    res['result'] = '答案錯誤。'
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
