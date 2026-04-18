# ==============================================================================
# ID: jh_數學1上_IntegerAdditionOperation
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 47.37s | RAG: 5 examples
# Created At: 2026-01-13 08:40:09
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
# --- 4. Standard Answer Checker (Auto-Injected) ---
def check(user_answer, correct_answer):
    """
    Standard Answer Checker [V9.8.1 Enhanced]
    1. Handles float tolerance.
    2. Normalizes strings (removes spaces, supports Chinese commas).
    3. Returns user-friendly Chinese error messages.
    """
    if user_answer is None: return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}


import io
import base64
from matplotlib.figure import Figure
from matplotlib import rcParams # Import rcParams directly for global settings

# Set global matplotlib parameters for Traditional Chinese display and correct minus sign.
# These settings will apply to any Figure created after this point.
rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial']
rcParams['axes.unicode_minus'] = False

def get_base64_image(fig):
    """
    Converts a matplotlib Figure object to a base64 encoded PNG image string.
    This function adheres to the Golden Template's specifications.
    """
    buf = io.BytesIO()
    # Use bbox_inches='tight' to ensure no extra whitespace, and dpi for resolution.
    # transparent=True is often good for web integration.
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100, transparent=True)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    
    # CRITICAL ADAPTATION: Explicitly delete the Figure object to free memory
    # when not using pyplot's close() function.
    del fig 
    return img_str

def format_num_with_parentheses(n):
    """
    Formats an integer for display in an expression, adding parentheses if it's negative.
    e.g., -5 becomes (-5), 7 becomes 7.
    """
    return f"({n})" if n < 0 else str(n)

def generate_integer_addition_problem(level=1):
    """
    Generates an integer addition problem based on the Architect's specification,
    including diverse problem types and number line visualizations where required.
    Adheres to Traditional Chinese language and specified output format.
    """
    problem_types = [
        'number_line_two_negatives',
        'number_line_mixed_signs',
        'calculation_two_negatives',
        'calculation_mixed_signs',
        'calculation_with_zero',
        'calculation_multi_term'
    ]
    selected_type = random.choice(problem_types)

    question_text = ""
    correct_answer = ""
    image_base64 = ""
    expression_str = ""
    answer_val = 0
    
    # --- 1. Logic & Calculation based on selected problem type ---
    if selected_type == 'number_line_two_negatives':
        num1 = -random.randint(1, 6) # e.g., -2
        num2 = -random.randint(1, 6) # e.g., -5
        expression_str = f"{format_num_with_parentheses(num1)} + {format_num_with_parentheses(num2)}"
        answer_val = num1 + num2
        question_text = f"利用數線求 {expression_str} 的值。\n(答案格式：_)"

        # --- 2. Thread-Safe Plotting (No pyplot) ---
        fig = Figure(figsize=(8, 2))
        ax = fig.subplots()

        # Determine x-limits for the plot to ensure all relevant points are visible
        all_points = sorted([0, num1, answer_val])
        xlim_min = all_points[0] - 2
        xlim_max = all_points[-1] + 2
        
        ax.axhline(0, color='black', linewidth=0.8) # Main number line
        
        # First jump: from 0 to num1
        ax.arrow(0, 0, num1, 0, head_width=0.2, head_length=0.3, fc='blue', ec='blue', length_includes_head=True, zorder=2)
        ax.text(num1/2, 0.3, str(num1), ha='center', va='bottom', color='blue', fontsize=10)
        
        # Second jump: from num1 to answer_val (which is num1 + num2)
        ax.arrow(num1, 0, num2, 0, head_width=0.2, head_length=0.3, fc='red', ec='red', length_includes_head=True, zorder=2)
        ax.text(num1 + num2/2, -0.3, str(num2), ha='center', va='top', color='red', fontsize=10)

        # Mark key points on the number line
        ax.plot(0, 0, 'ko', markersize=5, zorder=3) # Start point 0
        ax.plot(num1, 0, 'ko', markersize=5, zorder=3) # Intermediate point num1
        ax.plot(answer_val, 0, 'ko', markersize=8, zorder=3) # Final answer point (No color hint)

        # Add labels for 0, num1, and the final answer
        ax.text(0, 0.3, '0', ha='center', va='bottom', fontsize=10)
        ax.text(num1, 0.3, str(num1), ha='center', va='bottom', fontsize=10)
        # Answer label removed for student practice

        # Set x-ticks for better readability, covering the full range
        ax.set_xticks(range(int(xlim_min), int(xlim_max) + 1))
        
        ax.set_yticks([]) # Remove y-axis ticks
        ax.spines[['left', 'right', 'top', 'bottom']].set_visible(False) # Hide all spines
        ax.set_xlim(xlim_min, xlim_max)
        ax.set_ylim(-1, 1) # Keep y-limits consistent for number line visualization
        ax.set_title(f"數線表示：{expression_str}", fontsize=14)
        
        image_base64 = get_base64_image(fig)

    elif selected_type == 'number_line_mixed_signs':
        while True:
            num1 = random.randint(-5, 5)
            num2 = random.randint(-5, 5)
            # Ensure one positive, one negative, neither is zero, and the sum is not zero
            # for a more interesting visualization.
            if num1 != 0 and num2 != 0 and (num1 * num2 < 0) and (num1 + num2) != 0:
                break
        expression_str = f"{format_num_with_parentheses(num1)} + {format_num_with_parentheses(num2)}"
        answer_val = num1 + num2
        question_text = f"利用數線求 {expression_str} 的值。\n(答案格式：_)"

        # --- 2. Thread-Safe Plotting (No pyplot) ---
        fig = Figure(figsize=(8, 2))
        ax = fig.subplots()

        all_points = sorted([0, num1, answer_val])
        xlim_min = all_points[0] - 2
        xlim_max = all_points[-1] + 2
        
        ax.axhline(0, color='black', linewidth=0.8)
        
        ax.arrow(0, 0, num1, 0, head_width=0.2, head_length=0.3, fc='blue', ec='blue', length_includes_head=True, zorder=2)
        ax.text(num1/2, 0.3, str(num1), ha='center', va='bottom', color='blue', fontsize=10)
        
        ax.arrow(num1, 0, num2, 0, head_width=0.2, head_length=0.3, fc='red', ec='red', length_includes_head=True, zorder=2)
        ax.text(num1 + num2/2, -0.3, str(num2), ha='center', va='top', color='red', fontsize=10)

        ax.plot(0, 0, 'ko', markersize=5, zorder=3)
        ax.plot(num1, 0, 'ko', markersize=5, zorder=3)
        ax.plot(answer_val, 0, 'ko', markersize=8, zorder=3)

        ax.text(0, 0.3, '0', ha='center', va='bottom', fontsize=10)
        ax.text(num1, 0.3, str(num1), ha='center', va='bottom', fontsize=10)
        # Answer label removed for student practice

        ax.set_xticks(range(int(xlim_min), int(xlim_max) + 1))
        
        ax.set_yticks([])
        ax.spines[['left', 'right', 'top', 'bottom']].set_visible(False)
        ax.set_xlim(xlim_min, xlim_max)
        ax.set_ylim(-1, 1)
        ax.set_title(f"數線表示：{expression_str}", fontsize=14)
        
        image_base64 = get_base64_image(fig)

    elif selected_type == 'calculation_two_negatives':
        num1 = -random.randint(5, 50)
        num2 = -random.randint(5, 50)
        expression_str = f"{format_num_with_parentheses(num1)} + {format_num_with_parentheses(num2)}"
        answer_val = num1 + num2
        question_text = f"計算 {expression_str} 的值。\n(答案格式：_)"

    elif selected_type == 'calculation_mixed_signs':
        while True:
            num1 = random.randint(-70, 70)
            num2 = random.randint(-70, 70)
            # Ensure one positive and one negative, and neither is zero.
            if num1 != 0 and num2 != 0 and (num1 * num2 < 0):
                break
        expression_str = f"{format_num_with_parentheses(num1)} + {format_num_with_parentheses(num2)}"
        answer_val = num1 + num2
        question_text = f"計算 {expression_str} 的值。\n(答案格式：_)"

    elif selected_type == 'calculation_with_zero':
        sub_type = random.choice(['A+0', '0+A', 'A+(-A)', '(-A)+A'])
        num = random.randint(1, 100) # Magnitude for the non-zero number
        if sub_type == 'A+0':
            expression_str = f"{num} + 0"
            answer_val = num
        elif sub_type == '0+A':
            expression_str = f"0 + {num}"
            answer_val = num
        elif sub_type == 'A+(-A)':
            expression_str = f"{num} + {format_num_with_parentheses(-num)}"
            answer_val = 0
        elif sub_type == '(-A)+A':
            expression_str = f"{format_num_with_parentheses(-num)} + {num}"
            answer_val = 0
        
        question_text = f"計算 {expression_str} 的值。\n(答案格式：_)"

    elif selected_type == 'calculation_multi_term':
        n_terms = random.randint(3, 5) # Generate between 3 and 5 terms
        terms = [random.randint(-150, 150) for _ in range(n_terms)]
        expression_parts = [format_num_with_parentheses(t) for t in terms]
        expression_str = " + ".join(expression_parts)
        answer_val = sum(terms)
        question_text = f"計算 {expression_str} 的值。\n(答案格式：_)"

    correct_answer = str(answer_val) # Ensure correct_answer is always a string

    # --- 3. Output Format ---
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "image_base64": image_base64,
        "problem_type": selected_type,
        "difficulty": level # Included as per Golden Template's implied usage
    }

def check(user, correct):
    """
    Robustly checks the user's answer against the correct answer.
    This function adheres to the Golden Template's specifications.
    """
    u = user.strip().replace(" ", "")
    c = correct.strip().replace(" ", "")
    if u == c: 
        return {"correct": True, "result": "正確！"}
    try:
        # Attempt float comparison for numerical robustness, even for integers.
        if abs(float(u) - float(c)) < 1e-6:
            return {"correct": True, "result": "正確！"}
    except ValueError: # Catch cases where user input or correct answer isn't a valid number
        pass
    return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct))}



# [Auto-Injected Smart Dispatcher v8.7]
def generate(level=1):
    if level == 1:
        types = ['generate_integer_addition_problem']
        selected = random.choice(types)
    else:
        types = ['generate_integer_addition_problem']
        selected = random.choice(types)
    if selected == 'generate_integer_addition_problem': return generate_integer_addition_problem()
    return generate_integer_addition_problem()

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

