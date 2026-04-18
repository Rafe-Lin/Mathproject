# ==============================================================================
# ID: jh_數學1上_RepresentingQuantitiesWithAlgebraicExpressions
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 78.93s | RAG: 5 examples
# Created At: 2026-01-14 21:04:20
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


import datetime

import base64 # Included as per generic rules, though not used in this specific skill.
import re

# --- Helper Functions (Generic Helper Rules: Must return, type consistent for question_text) ---

def _get_random_variable(exclude=None):
    """
    Returns a random lowercase English letter, optionally excluding some.
    Ensures no global state dependency.
    """
    if exclude is None:
        exclude = []
    
    # Common variables used in K12 algebra
    variables = ['x', 'y', 'z', 'a', 'b', 'c', 'n', 'm', 'k', 'p', 'q']
    
    # Filter out excluded variables
    available_variables = [v for v in variables if v not in exclude]
    
    if not available_variables:
        # Fallback if all common variables are excluded (unlikely for 1-2 variables)
        # This ensures a variable is always returned.
        all_letters = [chr(i) for i in range(ord('a'), ord('z') + 1)]
        available_letters = [l for l in all_letters if l not in exclude]
        if not available_letters:
            # Should ideally not happen if problem design is reasonable.
            raise ValueError("No available variables left after exclusions. Consider increasing variable pool.")
        return random.choice(available_letters)
        
    return random.choice(available_variables)

def _generate_random_integer(min_val, max_val, exclude_zero=False):
    """
    Generates a random integer within the specified range.
    Ensures no global state dependency.
    """
    num = random.randint(min_val, max_val)
    if exclude_zero and num == 0:
        # Recursive call to get a non-zero number, ensuring termination for valid ranges.
        return _generate_random_integer(min_val, max_val, exclude_zero)
    return num

def _evaluate_expression_safely(expression_str, variables_dict):
    """
    Safely evaluates an algebraic expression by substituting values.
    Uses a limited global and local scope to prevent arbitrary code execution.
    Ensures no global state dependency.
    """
    # Restrict allowed functions/objects to prevent arbitrary code execution
    safe_globals = {"__builtins__": None, "abs": abs, "round": round, "min": min, "max": max, "sum": sum, "math": math}
    # Only allow valid Python identifiers as variable names in the local scope
    safe_locals = {k: v for k, v in variables_dict.items() if isinstance(k, str) and k.isidentifier()}
    
    try:
        # eval() requires expressions to be in valid Python syntax (e.g., 3*x, x**2)
        return eval(expression_str, safe_globals, safe_locals)
    except (SyntaxError, NameError, TypeError, ZeroDivisionError) as e:
        # Log error for debugging, but return None to indicate failure
        # print(f"Error evaluating expression '{expression_str}' with variables {variables_dict}: {e}")
        return None # Indicate an error in evaluation

# --- Main Functions ---

def generate(level=1):
    """
    Generates a K12 math problem for 'Representing Quantities With Algebraic Expressions'.
    
    Args:
        level (int): Difficulty level (1, 2, etc.). Currently, complexity varies randomly.

    Returns:
        dict: A dictionary containing problem details as per the Coder Spec.
    """
    problem_data = {
        "question_text": "",
        "correct_answer": "", # Internal, eval-friendly string (e.g., "3*x + 5")
        "answer": "",         # Display string (LaTeX-formatted, e.g., "$3x + 5$")
        "image_base64": "",   # No images for this skill, so empty.
        "created_at": datetime.datetime.now().isoformat(),
        "version": 1
    }

    # Problem Variety: Randomly choose one of the three main problem types
    problem_type = random.choice([1, 2, 3]) 

    if problem_type == 1:
        # Type 1: Direct Expression (Maps to Example 1, 2, 4)
        # Description: Given a simple word problem, write an algebraic expression.
        
        var1 = _get_random_variable()
        
        sub_type = random.choice([1, 2, 3, 4])
        
        if sub_type == 1: # Addition/Subtraction: "比 x 多 5" -> x+5
            num = _generate_random_integer(1, 20, exclude_zero=True)
            op_text, op_symbol = random.choice([("多", "+"), ("少", "-")])
            
            question_template = r"比 {var1_display} {op_text} {num_display} 的數為何？"
            question_text_parts = {
                "var1_display": r"$" + var1 + r"$",
                "op_text": op_text,
                "num_display": r"$" + str(num) + r"$"
            }
            # LaTeX Safety: Use .replace() for constructing question_text
            problem_data["question_text"] = question_template.replace("{var1_display}", question_text_parts["var1_display"]) \
                                                 .replace("{op_text}", question_text_parts["op_text"]) \
                                                 .replace("{num_display}", question_text_parts["num_display"])
            
            problem_data["correct_answer"] = f"{var1}{op_symbol}{num}" # "x+5" (internal eval form)
            problem_data["answer"] = r"$" + var1 + op_symbol + str(num) + r"$" # "$x+5$" (display form)
        
        elif sub_type == 2: # Multiplication: "x 的 3 倍" -> 3x
            num = _generate_random_integer(2, 12, exclude_zero=True)
            
            question_template = r"{var1_display} 的 {num_display} 倍為何？"
            question_text_parts = {
                "var1_display": r"$" + var1 + r"$",
                "num_display": r"$" + str(num) + r"$"
            }
            problem_data["question_text"] = question_template.replace("{var1_display}", question_text_parts["var1_display"]) \
                                                 .replace("{num_display}", question_text_parts["num_display"])
            
            problem_data["correct_answer"] = f"{num}*{var1}" # "3*x"
            problem_data["answer"] = r"$" + str(num) + var1 + r"$" # "$3x$"
            
        elif sub_type == 3: # Division: "x 除以 3" -> x/3
            num = _generate_random_integer(2, 10, exclude_zero=True)
            
            question_template = r"{var1_display} 除以 {num_display} 的商為何？"
            question_text_parts = {
                "var1_display": r"$" + var1 + r"$",
                "num_display": r"$" + str(num) + r"$"
            }
            problem_data["question_text"] = question_template.replace("{var1_display}", question_text_parts["var1_display"]) \
                                                 .replace("{num_display}", question_text_parts["num_display"])
            
            problem_data["correct_answer"] = f"({var1})/{num}" # "(x)/3"
            problem_data["answer"] = r"$\frac{" + var1 + r"}{" + str(num) + r"}$" # "$\frac{x}{3}$"
            
        elif sub_type == 4: # Combined operations: "x 的 3 倍再加 5" -> 3x+5
            num1 = _generate_random_integer(2, 10, exclude_zero=True)
            num2 = _generate_random_integer(1, 15, exclude_zero=False) 
            
            op2_text, op2_symbol = random.choice([("加", "+"), ("減", "-")])
            
            question_template = r"{var1_display} 的 {num1_display} 倍，再 {op2_text} {num2_display}，結果為何？"
            question_text_parts = {
                "var1_display": r"$" + var1 + r"$",
                "num1_display": r"$" + str(num1) + r"$",
                "op2_text": op2_text,
                "num2_display": r"$" + str(num2) + r"$"
            }
            problem_data["question_text"] = question_template.replace("{var1_display}", question_text_parts["var1_display"]) \
                                                 .replace("{num1_display}", question_text_parts["num1_display"]) \
                                                 .replace("{op2_text}", question_text_parts["op2_text"]) \
                                                 .replace("{num2_display}", question_text_parts["num2_display"])
            
            problem_data["correct_answer"] = f"{num1}*{var1}{op2_symbol}{num2}" # "3*x+5"
            problem_data["answer"] = r"$" + str(num1) + var1 + op2_symbol + str(num2) + r"$" # "$3x+5$"


    elif problem_type == 2:
        # Type 2: Substitution/Evaluation (Maps to Example 3, 5)
        # Description: Given an algebraic expression and values for its variables, calculate the result.
        
        var1 = _get_random_variable()
        var_val1 = _generate_random_integer(-10, 10, exclude_zero=False)
        
        sub_type = random.choice([1, 2, 3])
        
        if sub_type == 1: # Single variable, linear: "2x + 3"
            coeff = _generate_random_integer(2, 5, exclude_zero=True)
            const = _generate_random_integer(-10, 10, exclude_zero=False)
            
            expression_display_parts = [str(coeff) + var1]
            expression_eval_parts = [f"{coeff}*{var1}"]
            if const > 0:
                expression_display_parts.append(r"+" + str(const)) # LaTeX safety for +
                expression_eval_parts.append(f"+{const}")
            elif const < 0:
                expression_display_parts.append(str(const))
                expression_eval_parts.append(f"{const}")
            
            expression_display = "".join(expression_display_parts)
            expression_eval = "".join(expression_eval_parts)
            
            question_template = r"已知 {var1_display} = {val1_display}，求 {expr_display} 的值為何？"
            question_text_parts = {
                "var1_display": r"$" + var1 + r"$",
                "val1_display": r"$" + str(var_val1) + r"$",
                "expr_display": r"$" + expression_display + r"$"
            }
            problem_data["question_text"] = question_template.replace("{var1_display}", question_text_parts["var1_display"]) \
                                                 .replace("{val1_display}", question_text_parts["val1_display"]) \
                                                 .replace("{expr_display}", question_text_parts["expr_display"])
            
            variables_for_eval = {var1: var_val1}
            correct_val = _evaluate_expression_safely(expression_eval, variables_for_eval)
            
            problem_data["correct_answer"] = str(correct_val)
            problem_data["answer"] = str(correct_val) # Numerical answers are displayed as strings.
        
        elif sub_type == 2: # Single variable, with power: "2x^2 + 3"
            power = random.choice([2, 3])
            coeff = _generate_random_integer(1, 3, exclude_zero=True)
            const = _generate_random_integer(-5, 5, exclude_zero=False)
            
            # LaTeX Safety: Construct display string without f-string for '^'
            expression_display_parts = [str(coeff) + var1 + r"^" + str(power)]
            expression_eval_parts = [f"{coeff}*({var1}**{power})"] # Parentheses for negative var_val1
            if const > 0:
                expression_display_parts.append(r"+" + str(const))
                expression_eval_parts.append(f"+{const}")
            elif const < 0:
                expression_display_parts.append(str(const))
                expression_eval_parts.append(f"{const}")
            
            expression_display = "".join(expression_display_parts)
            expression_eval = "".join(expression_eval_parts)
            
            question_template = r"已知 {var1_display} = {val1_display}，求 {expr_display} 的值為何？"
            question_text_parts = {
                "var1_display": r"$" + var1 + r"$",
                "val1_display": r"$" + str(var_val1) + r"$",
                "expr_display": r"$" + expression_display + r"$" # Use Latex for power: x^2
            }
            problem_data["question_text"] = question_template.replace("{var1_display}", question_text_parts["var1_display"]) \
                                                 .replace("{val1_display}", question_text_parts["val1_display"]) \
                                                 .replace("{expr_display}", question_text_parts["expr_display"])
            
            variables_for_eval = {var1: var_val1}
            correct_val = _evaluate_expression_safely(expression_eval, variables_for_eval)
            
            problem_data["correct_answer"] = str(correct_val)
            problem_data["answer"] = str(correct_val)
            
        elif sub_type == 3: # Two variables: "3x + 2y + 1"
            var2 = _get_random_variable(exclude=[var1])
            var_val2 = _generate_random_integer(-10, 10, exclude_zero=False)
            
            coeff1 = _generate_random_integer(1, 5, exclude_zero=True)
            coeff2 = _generate_random_integer(1, 5, exclude_zero=True)
            const = _generate_random_integer(-5, 5, exclude_zero=False)
            
            expression_display_parts = [str(coeff1) + var1, str(coeff2) + var2]
            expression_eval_parts = [f"{coeff1}*{var1}", f"{coeff2}*{var2}"]
            
            # Randomly order terms for display to make it more varied
            if random.choice([True, False]):
                expression_display_parts = list(reversed(expression_display_parts))
                expression_eval_parts = list(reversed(expression_eval_parts))
            
            expression_display = expression_display_parts[0] + r" + " + expression_display_parts[1] # LaTeX safety for +
            expression_eval = expression_eval_parts[0] + " + " + expression_eval_parts[1]

            if const > 0:
                expression_display += r"+" + str(const)
                expression_eval += f"+{const}"
            elif const < 0:
                expression_display += str(const)
                expression_eval += f"{const}"
            
            question_template = r"已知 {var1_display} = {val1_display} 且 {var2_display} = {val2_display}，求 {expr_display} 的值為何？"
            question_text_parts = {
                "var1_display": r"$" + var1 + r"$",
                "val1_display": r"$" + str(var_val1) + r"$",
                "var2_display": r"$" + var2 + r"$",
                "val2_display": r"$" + str(var_val2) + r"$",
                "expr_display": r"$" + expression_display + r"$"
            }
            problem_data["question_text"] = question_template.replace("{var1_display}", question_text_parts["var1_display"]) \
                                                 .replace("{val1_display}", question_text_parts["val1_display"]) \
                                                 .replace("{var2_display}", question_text_parts["var2_display"]) \
                                                 .replace("{val2_display}", question_text_parts["val2_display"]) \
                                                 .replace("{expr_display}", question_text_parts["expr_display"])
            
            variables_for_eval = {var1: var_val1, var2: var_val2}
            correct_val = _evaluate_expression_safely(expression_eval, variables_for_eval)
            
            problem_data["correct_answer"] = str(correct_val)
            problem_data["answer"] = str(correct_val)

    elif problem_type == 3:
        # Type 3: Contextual Application (Maps to Example 6, 7)
        # Description: A more involved word problem requiring students to identify quantities and represent them algebraically.
        
        sub_type = random.choice([1, 2, 3])
        
        if sub_type == 1: # Shopping scenario (multiple items): "3個蘋果 x 元, 2個橘子 y 元, 共多少錢?" -> 3x + 2y
            item1_name = random.choice(["蘋果", "香蕉", "橘子", "梨子"])
            item2_name = random.choice([i for i in ["鉛筆", "橡皮擦", "立可白", "尺"] if i != item1_name])
            
            var1 = _get_random_variable()
            var2 = _get_random_variable(exclude=[var1])
            
            qty1 = _generate_random_integer(2, 5)
            qty2 = _generate_random_integer(2, 5)
            
            question_template = r"某商店的 {item1_name} 一個 {var1_display} 元，{item2_name} 一個 {var2_display} 元。小明買了 {qty1_display} 個 {item1_name} 和 {qty2_display} 個 {item2_name}，共需多少錢？"
            question_text_parts = {
                "item1_name": item1_name,
                "var1_display": r"$" + var1 + r"$",
                "item2_name": item2_name,
                "var2_display": r"$" + var2 + r"$",
                "qty1_display": r"$" + str(qty1) + r"$",
                "qty2_display": r"$" + str(qty2) + r"$"
            }
            problem_data["question_text"] = question_template.replace("{item1_name}", question_text_parts["item1_name"]) \
                                                 .replace("{var1_display}", question_text_parts["var1_display"]) \
                                                 .replace("{item2_name}", question_text_parts["item2_name"]) \
                                                 .replace("{var2_display}", question_text_parts["var2_display"]) \
                                                 .replace("{qty1_display}", question_text_parts["qty1_display"]) \
                                                 .replace("{qty2_display}", question_text_parts["qty2_display"])
            
            problem_data["correct_answer"] = f"{qty1}*{var1} + {qty2}*{var2}" # "3*x + 2*y"
            problem_data["answer"] = r"$" + str(qty1) + var1 + r" + " + str(qty2) + var2 + r"$" # "$3x + 2y$"
            
        elif sub_type == 2: # Remaining quantity/money: "原有 L 元，買了 n 枝筆每枝 15 元，剩下多少錢?" -> L - 15n
            initial_amount_name = random.choice(["原有", "總長", "總重"])
            initial_amount_var = _get_random_variable()
            
            item_name = random.choice(["原子筆", "繩子", "蛋糕"])
            item_unit = random.choice(["枝", "公分", "公斤"])
            
            item_price_or_length = _generate_random_integer(5, 30)
            item_qty_var = _get_random_variable(exclude=[initial_amount_var])
            
            question_template = r"小華{initial_amount_name} {initial_amount_var_display} 元，買了 {item_qty_var_display} {item_unit} {item_name}，每{item_unit} {price_display} 元。他還剩下多少錢？"
            question_text_parts = {
                "initial_amount_name": initial_amount_name,
                "initial_amount_var_display": r"$" + initial_amount_var + r"$",
                "item_qty_var_display": r"$" + item_qty_var + r"$",
                "item_unit": item_unit,
                "item_name": item_name,
                "price_display": r"$" + str(item_price_or_length) + r"$"
            }
            problem_data["question_text"] = question_template.replace("{initial_amount_name}", question_text_parts["initial_amount_name"]) \
                                                 .replace("{initial_amount_var_display}", question_text_parts["initial_amount_var_display"]) \
                                                 .replace("{item_qty_var_display}", question_text_parts["item_qty_var_display"]) \
                                                 .replace("{item_unit}", question_text_parts["item_unit"]) \
                                                 .replace("{item_name}", question_text_parts["item_name"]) \
                                                 .replace("{price_display}", question_text_parts["price_display"])
            
            problem_data["correct_answer"] = f"{initial_amount_var} - {item_price_or_length}*{item_qty_var}" # "L - 15*n"
            problem_data["answer"] = r"$" + initial_amount_var + r" - " + str(item_price_or_length) + item_qty_var + r"$" # "$L - 15n$"
            
        elif sub_type == 3: # Area/Perimeter type (simple geometric formula)
            shape = random.choice(["長方形", "正方形", "三角形"])
            var1 = _get_random_variable()
            
            if shape == "長方形": # 周長: 2(長+寬)
                var2 = _get_random_variable(exclude=[var1])
                question_template = r"一個{shape_name}的長為 {var1_display}，寬為 {var2_display}。求其周長為何？"
                question_text_parts = {
                    "shape_name": shape,
                    "var1_display": r"$" + var1 + r"$",
                    "var2_display": r"$" + var2 + r"$"
                }
                problem_data["question_text"] = question_template.replace("{shape_name}", question_text_parts["shape_name"]) \
                                                     .replace("{var1_display}", question_text_parts["var1_display"]) \
                                                     .replace("{var2_display}", question_text_parts["var2_display"])
                
                problem_data["correct_answer"] = f"2*({var1} + {var2})" # "2*(L + W)"
                problem_data["answer"] = r"$2(" + var1 + r" + " + var2 + r")$" # "$2(L + W)$"
            
            elif shape == "正方形": # 面積: 邊長^2
                question_template = r"一個{shape_name}的邊長為 {var1_display}。求其面積為何？"
                question_text_parts = {
                    "shape_name": shape,
                    "var1_display": r"$" + var1 + r"$"
                }
                problem_data["question_text"] = question_template.replace("{shape_name}", question_text_parts["shape_name"]) \
                                                     .replace("{var1_display}", question_text_parts["var1_display"])
                
                problem_data["correct_answer"] = f"{var1}**2" # "x**2"
                problem_data["answer"] = r"$" + var1 + r"^2$" # "$x^2$"
                
            elif shape == "三角形": # 面積: 1/2 * 底 * 高
                var2 = _get_random_variable(exclude=[var1])
                question_template = r"一個{shape_name}的底為 {var1_display}，高為 {var2_display}。求其面積為何？"
                question_text_parts = {
                    "shape_name": shape,
                    "var1_display": r"$" + var1 + r"$",
                    "var2_display": r"$" + var2 + r"$"
                }
                problem_data["question_text"] = question_template.replace("{shape_name}", question_text_parts["shape_name"]) \
                                                     .replace("{var1_display}", question_text_parts["var1_display"]) \
                                                     .replace("{var2_display}", question_text_parts["var2_display"])
                
                problem_data["correct_answer"] = f"0.5*{var1}*{var2}" # "0.5*b*h"
                problem_data["answer"] = r"$\frac{1}{2}" + var1 + var2 + r"$" # "$\frac{1}{2}bh$"

    return problem_data



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
