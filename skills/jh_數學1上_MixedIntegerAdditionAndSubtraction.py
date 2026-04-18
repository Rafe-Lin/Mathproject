# ==============================================================================
# ID: jh_數學1上_MixedIntegerAdditionAndSubtraction
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 71.08s | RAG: 5 examples
# Created At: 2026-01-13 21:57:40
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
    Standard Answer Checker [V9.8.1 Enhanced]
    1. Handles float tolerance.
    2. Normalizes strings (removes spaces, supports Chinese commas).
    3. Returns user-friendly Chinese error messages.
    """
    if user_answer is None: return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}


# import io # Not needed for calculation problems
# import base64 # Not needed for calculation problems
# from matplotlib.figure import Figure # Not needed for calculation problems

# Environment tool: to_latex(n)
# This function formats numbers for LaTeX display, especially handling negative numbers.

# def get_base64_image(fig):
#     buf = io.BytesIO()
#     fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
#     buf.seek(0)
#     return base64.b64encode(buf.read()).decode('utf-8')

def generate_type_1():
    """
    Generates a multiple-term mixed addition and subtraction problem.
    Example: (-60) - (-42) + 18
    """
    num_terms = random.randint(3, 5)
    terms = [random.randint(-100, 100) for _ in range(num_terms)]
    
    question_parts = []
    expression_for_eval = []
    
    # First term
    question_parts.append(to_latex(terms[0]))
    expression_for_eval.append(str(terms[0]))
    
    # Remaining terms with random operators
    for i in range(1, num_terms):
        op_symbol = random.choice(['+', '-'])
        term_val = terms[i]
        
        question_parts.append(f" {op_symbol} ") # Add space for readability in LaTeX
        question_parts.append(to_latex(term_val))
        
        expression_for_eval.append(f"{op_symbol}{term_val}") # For eval, just +/- directly
            
    question_text = f"計算：${''.join(question_parts)}$"
    ans = eval(''.join(expression_for_eval)) 
    
    return question_text, str(ans)

def generate_type_2():
    """
    Generates an integer operation problem involving absolute values.
    Example: | -25 | - | -75 | - 18
    """
    structure_type = random.randint(1, 4)
    
    question_latex_parts = []
    eval_expression_parts = []
    
    if structure_type == 1: # |a| op1 |b| op2 c
        a = random.randint(-50, 50)
        b = random.randint(-50, 50)
        c = random.randint(-100, 100)
        
        op1 = random.choice([' + ', ' - '])
        op2 = random.choice([' + ', ' - '])
        
        question_latex_parts.append(f"|{to_latex(a)}|")
        question_latex_parts.append(op1)
        question_latex_parts.append(f"|{to_latex(b)}|")
        question_latex_parts.append(op2)
        question_latex_parts.append(to_latex(c))
        
        eval_expression_parts.append(f"abs({a})")
        eval_expression_parts.append(op1)
        eval_expression_parts.append(f"abs({b})")
        eval_expression_parts.append(op2)
        eval_expression_parts.append(str(c))
        
    elif structure_type == 2: # c op1 |a inner_op b| op2 d
        a = random.randint(-50, 50)
        b = random.randint(-50, 50)
        c = random.randint(-100, 100)
        d = random.randint(-100, 100)
        
        op1 = random.choice([' + ', ' - '])
        inner_op = random.choice(['+', '-'])
        op2 = random.choice([' + ', ' - '])
        
        question_latex_parts.append(to_latex(c))
        question_latex_parts.append(op1)
        question_latex_parts.append(f"|{to_latex(a)}{inner_op}{to_latex(b)}|")
        question_latex_parts.append(op2)
        question_latex_parts.append(to_latex(d))
        
        eval_expression_parts.append(str(c))
        eval_expression_parts.append(op1)
        eval_expression_parts.append(f"abs({a}{inner_op}{b})")
        eval_expression_parts.append(op2)
        eval_expression_parts.append(str(d))
        
    elif structure_type == 3: # |a| op1 b op2 |c|
        a = random.randint(-50, 50)
        b = random.randint(-100, 100)
        c = random.randint(-50, 50)
        
        op1 = random.choice([' + ', ' - '])
        op2 = random.choice([' + ', ' - '])
        
        question_latex_parts.append(f"|{to_latex(a)}|")
        question_latex_parts.append(op1)
        question_latex_parts.append(to_latex(b))
        question_latex_parts.append(op2)
        question_latex_parts.append(f"|{to_latex(c)}|")
        
        eval_expression_parts.append(f"abs({a})")
        eval_expression_parts.append(op1)
        eval_expression_parts.append(str(b))
        eval_expression_parts.append(op2)
        eval_expression_parts.append(f"abs({c})")
        
    else: # structure_type == 4: |a inner_op b| op1 c op2 d
        a = random.randint(-50, 50)
        b = random.randint(-50, 50)
        c = random.randint(-100, 100)
        d = random.randint(-100, 100)
        
        inner_op = random.choice(['+', '-'])
        op1 = random.choice([' + ', ' - '])
        op2 = random.choice([' + ', ' - '])
        
        question_latex_parts.append(f"|{to_latex(a)}{inner_op}{to_latex(b)}|")
        question_latex_parts.append(op1)
        question_latex_parts.append(to_latex(c))
        question_latex_parts.append(op2)
        question_latex_parts.append(to_latex(d))
        
        eval_expression_parts.append(f"abs({a}{inner_op}{b})")
        eval_expression_parts.append(op1)
        eval_expression_parts.append(str(c))
        eval_expression_parts.append(op2)
        eval_expression_parts.append(str(d))
        
    question_text = f"計算：${''.join(question_latex_parts)}$"
    ans = eval(''.join(eval_expression_parts))
    
    return question_text, str(ans)

def generate_type_3():
    """
    Generates a problem comparing two expressions for equality, always resulting in "相同".
    Example: -( 6 + 3 ) 和 -6 - 3
    """
    structure_type = random.randint(1, 5)
    
    expr1_latex = ""
    expr2_latex = ""
    expr1_eval = ""
    expr2_eval = ""
    
    if structure_type == 1: # -(a + b) vs -a - b
        a = random.randint(1, 50)
        b = random.randint(1, 50)
        
        expr1_latex = f"-({to_latex(a)} + {to_latex(b)})"
        expr2_latex = f"{to_latex(-a)} - {to_latex(b)}"
        
        expr1_eval = f"-({a} + {b})"
        expr2_eval = f"{-a} - {b}"
        
    elif structure_type == 2: # -(a - b) vs -a + b
        a = random.randint(1, 50)
        b = random.randint(1, 50)
        
        expr1_latex = f"-({to_latex(a)} - {to_latex(b)})"
        expr2_latex = f"{to_latex(-a)} + {to_latex(b)}"
        
        expr1_eval = f"-({a} - {b})"
        expr2_eval = f"{-a} + {b}"

    elif structure_type == 3: # x + (y + z) vs x + y + z
        x = random.randint(-50, 50)
        y = random.randint(-50, 50)
        z = random.randint(-50, 50)
        
        y_latex = to_latex(y)
        z_latex = to_latex(z)
        
        expr1_latex = f"{to_latex(x)} + ({y_latex} + {z_latex})"
        expr2_latex = f"{to_latex(x)} + {y_latex} + {z_latex}"
        
        expr1_eval = f"{x} + ({y} + {z})"
        expr2_eval = f"{x} + {y} + {z}"
        
    elif structure_type == 4: # x - (y + z) vs x - y - z
        x = random.randint(-50, 50)
        y = random.randint(-50, 50)
        z = random.randint(-50, 50)
        
        y_latex = to_latex(y)
        z_latex = to_latex(z)
        
        expr1_latex = f"{to_latex(x)} - ({y_latex} + {z_latex})"
        expr2_latex = f"{to_latex(x)} - {y_latex} - {z_latex}"
        
        expr1_eval = f"{x} - ({y} + {z})"
        expr2_eval = f"{x} - {y} - {z}"
        
    else: # structure_type == 5: x - (y - z) vs x - y + z
        x = random.randint(-50, 50)
        y = random.randint(-50, 50)
        z = random.randint(-50, 50)
        
        y_latex = to_latex(y)
        z_latex = to_latex(z)
        
        expr1_latex = f"{to_latex(x)} - ({y_latex} - {z_latex})"
        expr2_latex = f"{to_latex(x)} - {y_latex} + {z_latex}"
        
        expr1_eval = f"{x} - ({y} - {z})"
        expr2_eval = f"{x} - {y} + {z}"
        
    question_text = f"判斷下列兩式運算結果是否相同：${expr1_latex}$ 和 ${expr2_latex}$"
    
    val1 = eval(expr1_eval)
    val2 = eval(expr2_eval)
    
    if val1 != val2:
        # This should not happen if structures are correctly designed for equality
        raise ValueError(f"Comparison expressions did not result in the same value! Expr1: {expr1_eval}={val1}, Expr2: {expr2_eval}={val2}")
    
    return question_text, "相同"

def generate_type_4():
    """
    Generates a problem with parentheses designed for simplification using
    distributive or associative properties (reverse engineered).
    Example: 299 - (396 + 299)
    """
    structure_type = random.randint(1, 3)
    
    question_latex = ""
    ans = 0
    
    # Generate A (100-900, not 0)
    A = random.randint(100, 900)
    # Generate B (-200 to 200, not 0)
    B = random.choice([x for x in range(-200, 201) if x != 0])
    
    if structure_type == 1: # A - (B + A) -> -B
        question_latex = f"${to_latex(A)} - ({to_latex(B)} + {to_latex(A)})$"
        ans = -B
    elif structure_type == 2: # A - (B - A) -> 2A - B
        question_latex = f"${to_latex(A)} - ({to_latex(B)} - {to_latex(A)})$"
        ans = 2 * A - B
    else: # structure_type == 3: (-A) - (B - A) -> -B
        question_latex = f"${to_latex(-A)} - ({to_latex(B)} - {to_latex(A)})$"
        ans = -B
        
    question_text = f"計算：{question_latex}"
    
    return question_text, str(ans)

def generate(level=1):
    """
    Generates an integer addition and subtraction problem based on selected type.
    """
    problem_type_choice = random.randint(1, 4)
    
    question_text = ""
    correct_answer = ""

    if problem_type_choice == 1:
        question_text, correct_answer = generate_type_1()
    elif problem_type_choice == 2:
        question_text, correct_answer = generate_type_2()
    elif problem_type_choice == 3:
        question_text, correct_answer = generate_type_3()
    else: # problem_type_choice == 4
        question_text, correct_answer = generate_type_4()

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "image_base64": "",  # CRITICAL: No image for calculation problems as per spec
        "problem_type": "純計算題",
        "difficulty": level
    }

def check(user, correct):
    """
    [V10.5.2 Standard Check]
    修正變數名稱不對稱問題，並確保使用三引號原始字串。
    """
    # 1. 基礎防錯 (確保參數名稱與 def 一致)
    if user is None: 
        return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct))}

    # 2. 正規化字串
    u = str(user).strip().replace(" ", "").replace("，", ",")
    c = str(correct).strip().replace(" ", "").replace("，", ",")
    
    # 3. 精確比對 (例如 "相同")
    if u == c: 
        return {"correct": True, "result": "正確！"}
    
    # 4. 數值比對
    try:
        if abs(float(u) - float(c)) < 1e-6:
            return {"correct": True, "result": "正確！"}
    except (ValueError, TypeError):
        pass
        
    # 5. 最終回傳 (確保變數名為 correct)
    return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct))}
    
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
