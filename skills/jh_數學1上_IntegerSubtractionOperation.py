# ==============================================================================
# ID: jh_數學1上_IntegerSubtractionOperation
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 23.82s | RAG: 2 examples
# Created At: 2026-01-13 19:24:58
# Fix Status: [Clean Pass]
# Fixes: Regex=0, Logic=0
#==============================================================================


import random
import math
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
            if rem_num == 0: return f"{sign}{whole}"
            return f"{sign}{whole} \\frac{{{rem_num}}}{{{abs_num.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
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
        return f" - {abs_val}" if is_neg else f" + {abs_val}"
    
    if signed:
        # e.g., "+3", "-3"
        return f"-{abs_val}" if is_neg else f"+{abs_val}"
        
    # Default behavior (parentheses for negative)
    if is_neg: return f"({latex_val})"
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

def is_prime(n):
    """Check primality."""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

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
        f"{{final_label_str}}\n{{line_str}}+\n{{tick_str}}</div>"
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
    Standard Answer Checker [V9.8.1 Enhanced]
    1. Handles float tolerance.
    2. Normalizes strings (removes spaces, supports Chinese commas).
    3. Returns user-friendly Chinese error messages.
    """
    if user_answer is None: return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}


# No matplotlib imports needed for pure calculation problems as per TASK MODE SWITCHING.
# No io or base64 imports needed as image_base64 will be an empty string.

def generate_integer_subtraction_problem():
    """
    生成一個整數減法運算問題。
    問題數字和答案範圍遵循 Architect's Specification，並使用逆向工程確保數字合理。
    不涉及繪圖，image_base64 為空字串。
    """

    def format_for_latex(number):
        """
        根據 LaTeX 格式要求，將數字轉換為字串，負數帶括號和 \text{}。
        範例:
        14 -> \text{14}
        -25 -> (\text{-25})
        """
        if number < 0:
            return f"(\\text{{{number}}})"
        else:
            return f"\\text{{{number}}}"

    while True:
        # 1. 逆向工程：首先生成目標答案
        # 答案範圍建議設定在 [-100, 100]
        answer = random.randint(-100, 100)
        
        # 2. 生成第一個運算數 num1
        # num1 範圍建議設定在 [-150, 150]，且不包含 0
        num1 = random.randint(-150, 150)
        while num1 == 0:
            num1 = random.randint(-150, 150)
        
        # 3. 根據 answer = num1 - num2，計算出 num2
        # => num2 = num1 - answer
        num2 = num1 - answer
        
        # 4. 檢查 num2 是否在合理範圍內 [-150, 150] 且不為 0
        if -150 <= num2 <= 150 and num2 != 0:
            break # 如果所有條件都滿足，則跳出迴圈

    # 根據 Architect's Specification 格式化 LaTeX 數字表達式
    latex_num1_str = format_for_latex(num1)
    latex_num2_str = format_for_latex(num2)

    # 組合問題文本 (繁體中文)
    # 確保 LaTeX 格式正確，使用 \text{} 且負數加括號
    question_text = f"計算下列各式的值。${latex_num1_str} - {latex_num2_str}$"
    
    # 正確答案為計算結果的字串形式
    correct_answer = str(answer)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "image_base64": "",  # 純計算題，不需繪圖，設為空字串
        "problem_type": "純計算題",
        "difficulty": 1 # Default difficulty level
    }

# The check function from the template is not explicitly requested in the spec
# for this problem type, but for completeness and adherence to the overall system,
# it would typically be defined as follows:
def check(user_answer, correct_answer):
    """
    檢查用戶答案與正確答案是否一致。
    接受字串形式的答案，並嘗試轉換為浮點數進行數值比較。
    """
    u = user_answer.strip().replace(" ", "")
    c = correct_answer.strip().replace(" ", "")
    
    if u == c:
        return {"correct": True, "result": "正確！"}
    
    try:
        # 嘗試將答案轉換為浮點數進行比較，考慮浮點數精度問題
        if abs(float(u) - float(c)) < 1e-6:
            return {"correct": True, "result": "正確！"}
    except ValueError:
        # 如果無法轉換為數字，則按字串比較失敗處理
        pass
        
    return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}
#     
#     # user_ans = "-9"
#     # correct_ans = "-9"
#     # print(f"User: '{user_ans}', Correct: '{correct_ans}' -> {check(user_ans, correct_ans)}")
#     
#     # user_ans = "10"
#     # correct_ans = "12"
#     # print(f"User: '{user_ans}', Correct: '{correct_ans}' -> {check(user_ans, correct_ans)}")


# [Auto-Injected Smart Dispatcher v8.7]
def generate(level=1):
    if level == 1:
        types = ['generate_integer_subtraction_problem']
        selected = random.choice(types)
    else:
        types = ['generate_integer_subtraction_problem']
        selected = random.choice(types)
    if selected == 'generate_integer_subtraction_problem': return generate_integer_subtraction_problem()
    return generate_integer_subtraction_problem()

# [Auto-Injected Patch v10.4] Universal Return, Linebreak & Chinese Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if func.__name__ == "check" and isinstance(res, bool):
            return {"correct": res, "result": "正確！" if res else "答案錯誤"}
        if isinstance(res, dict):
            if "question_text" in res and isinstance(res["question_text"], str):
                res["question_text"] = res["question_text"].replace("\\n", "\n")
            if func.__name__ == "check" and "result" in res:
                msg = str(res["result"]).lower()
                if any(w in msg for w in ["correct", "right", "success"]): res["result"] = "正確！"
                elif any(w in msg for w in ["incorrect", "wrong", "error"]):
                    if "正確答案" not in res["result"]: res["result"] = "答案錯誤"
            if "answer" not in res and "correct_answer" in res: res["answer"] = res["correct_answer"]
            if "answer" in res: res["answer"] = str(res["answer"])
            if "image_base64" not in res: res["image_base64"] = ""
        return res
    return wrapper
import sys
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith("generate") or _name == "check"):
        globals()[_name] = _patch_all_returns(_func)
