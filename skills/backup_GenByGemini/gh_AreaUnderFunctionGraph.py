import random
from fractions import Fraction
<<<<<<< HEAD
import math
import re

def generate(level=1):
    """
    生成「函數圖形下面積」相關題目 (標準 LaTeX 範本)。
    目前主要生成黎曼和的數值計算題目。
    """
    # For level 1, focus on direct Riemann sum calculation for simple functions.
    problem_type = 'riemann_sum_calc'
    return generate_riemann_sum_calculation_problem(level)

def generate_riemann_sum_calculation_problem(level):
    """
    生成計算黎曼和的題目。
    - 函數類型：線性或簡單二次函數。
    - 區間 [a, b]
    - 子區間數量 n
    - 黎曼和類型：左黎曼和或右黎曼和
    """
    func_type = random.choice(['linear', 'quadratic_simple'])

    # Determine interval [a, b]
    a = random.randint(-3, 1) # Start of interval
    b = a + random.randint(2, 6) # End of interval, b > a (length at least 2)

    # Determine number of subintervals n
    n_choices = [2, 3, 4] # Keep n small for level 1 for manageable calculations
    n = random.choice(n_choices)

    delta_x = Fraction(b - a, n)

    func_str_latex = ""
    f_func = None

    if func_type == 'linear':
        m = random.randint(1, 4) # Slope (positive to ensure increasing or constant)
        
        # Ensure f(x) = mx+c is non-negative on [a, b].
        # For m > 0, the minimum value is at x=a. So, we need f(a) >= 0 => m*a + c >= 0.
        # Thus, c >= -m*a.
        min_c_val = -m * a
        # Ensure c is positive or large enough, but not excessively large.
        c = random.randint(max(0, min_c_val), max(5, min_c_val + 5))

        # Format function string for LaTeX
        if m == 1 and c == 0:
            func_str_latex = "$f(x) = x$"
        elif c == 0:
            func_str_latex = f"$f(x) = {m}x$"
        elif m == 1:
            func_str_latex = f"$f(x) = x + {c}$"
        else:
            func_str_latex = f"$f(x) = {m}x + {c}$"

        def f_func_linear(x_val):
            return m * x_val + c
        f_func = f_func_linear

    elif func_type == 'quadratic_simple':
        # Use f(x) = x^2 + c where c >= 0. This is always non-negative.
        c = random.randint(0, 4) # Constant term
        if c == 0:
            func_str_latex = "$f(x) = x^{{2}}$"
        else:
            func_str_latex = f"$f(x) = x^{{2}} + {c}$"

        def f_func_quadratic(x_val):
            return x_val * x_val + c
        f_func = f_func_quadratic

    # Type of Riemann Sum (left or right endpoint)
    sum_type = random.choice(['left', 'right'])

    current_sum = Fraction(0)
    for i in range(n):
        # Calculate endpoints of the i-th subinterval [x_{i-1}, x_i]
        x_k_start = Fraction(a) + i * delta_x # Left endpoint
        x_k_end = Fraction(a) + (i + 1) * delta_x # Right endpoint

        sample_point = Fraction(0)
        if sum_type == 'left':
            sample_point = x_k_start
        elif sum_type == 'right':
            sample_point = x_k_end
        # Other sum types (midpoint, min/max for upper/lower) can be added for higher levels.

        # Add the area of the current rectangle: f(sample_point) * delta_x
        current_sum += f_func(sample_point) * delta_x

    # Format the correct answer into a string (integer or LaTeX fraction)
    correct_answer_str = _format_fraction_answer(current_sum)

    sum_type_zh = {"left": "左黎曼和", "right": "右黎曼和"}

    question_text = (
        f"計算函數 {func_str_latex} 在區間 $[{a}, {b}]$ 上，使用 ${n}$ 個等寬子區間的{sum_type_zh[sum_type]}。\n"
        f"請以分數或整數形式作答（例如 `1/2` 或 `5`）。"
=======

def generate(level=1):
    """
    生成「函數圖形下面積」相關題目。
    包含：
    1. 線性函數在 [0, 1] 上的面積 (黎曼和與梯形面積驗證)
    2. 線性函數在 [0, b] 上的面積 (黎曼和與三角形面積驗證)
    """
    problem_type = random.choice(['linear_0_1', 'linear_0_b'])
    
    if problem_type == 'linear_0_1':
        return generate_linear_on_0_1_problem(level)
    else: # 'linear_0_b'
        return generate_linear_on_0_b_problem(level)

def generate_linear_on_0_1_problem(level):
    """
    生成 f(x) = ax + b 在 [0, 1] 上的面積題目。
    """
    # Ensure a > 0 for monotonically increasing function on [0,1]
    # This simplifies upper/lower sum logic if we were to derive them explicitly,
    # though for level 1 we just ask for the area.
    a = random.randint(1, 4)
    b = random.randint(1, 5)

    # Area calculation:
    # f(0) = b
    # f(1) = a + b
    # Area of trapezoid = (f(0) + f(1)) * height / 2 = (b + (a + b)) * 1 / 2 = (a + 2b) / 2
    numerator = a + 2 * b
    denominator = 2
    
    # Correct answer as a Fraction for precise comparison
    correct_area = Fraction(numerator, denominator)

    question_text = (
        f"設函數 $f(x) = {a}x + {b}$ 的圖形與 $x$ 軸、 $x=0$ 及 $x=1$ 所圍成的區域為 $R$。<br>"
        r"(1) 請利用黎曼和 (或上和/下和的極限) 的概念計算此區域 $R$ 的面積。<br>"
        r"(2) 此區域 $R$ 為何種幾何圖形？請利用其面積公式驗證(1)的結果。<br>"
        r"(請回答面積的數值，若為分數請填寫最簡分數，例如 $\\frac{{3}}{{2}}$)"
    )
    
    # If level is higher, we could ask for U_n or L_n expressions
    # For now, just the final area.
    
    return {
        "question_text": question_text,
        "answer": str(correct_area), # Storing as string "numerator/denominator"
        "correct_answer": str(correct_area)
    }

def generate_linear_on_0_b_problem(level):
    """
    生成 f(x) = ax 在 [0, B] 上的面積題目 (三角形)。
    """
    a = random.randint(1, 3)
    B_val = random.randint(2, 6) # Using B_val to avoid conflict with 'b' coefficient if used

    # Area calculation:
    # This forms a triangle with base B_val and height f(B_val) = a * B_val
    # Area = base * height / 2 = (B_val * a * B_val) / 2 = (a * B_val**2) / 2
    numerator = a * B_val**2
    denominator = 2

    correct_area = Fraction(numerator, denominator)

    question_text = (
        f"設函數 $f(x) = {a}x$ 的圖形與 $x$ 軸、 $x=0$ 及 $x={B_val}$ 所圍成的區域為 $R$。<br>"
        r"(1) 請利用黎曼和 (例如取右端點 $c_k = x_k = \\frac{{kB}}{{\text{{n}}}}$) 的概念計算此區域 $R$ 的面積。<br>"
        r"(2) 此區域 $R$ 為何種幾何圖形？請利用其面積公式驗證(1)的結果。<br>"
        r"(請回答面積的數值，若為分數請填寫最簡分數，例如 $\\frac{{3}}{{2}}$)"
>>>>>>> 8971b16094601268e7dca18dbf60df9d4ea36182
    )

    return {
        "question_text": question_text,
<<<<<<< HEAD
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def _format_fraction_answer(fraction_val):
    """Helper to format a Fraction object into a string, using LaTeX for non-integer fractions."""
    if fraction_val.denominator == 1:
        return str(fraction_val.numerator)
    # Use raw string for LaTeX command \\frac, then format with double braces for Python.
    return r"\\frac{{{}}}{{{}}}".format(fraction_val.numerator, fraction_val.denominator)

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    支援整數、分數 (例如 "1/2") 和 LaTeX 分數格式 (\\frac{1}{2})。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    user_answer_parsed = None
    correct_answer_parsed = None

    # Attempt to parse user_answer (can be "1/2", "5", "0.5")
    try:
        if '/' in user_answer:
            num, den = map(int, user_answer.split('/'))
            if den == 0: raise ZeroDivisionError("Denominator cannot be zero.")
            user_answer_parsed = Fraction(num, den)
        else:
            user_answer_parsed = Fraction(float(user_answer))
    except (ValueError, ZeroDivisionError):
        pass # Parsing failed, user_answer_parsed remains None

    # Attempt to parse correct_answer (can be "5" or r"\\frac{3}{2}")
    try:
        # Check for LaTeX fraction format: \\frac{num}{den}
        match = re.match(r"\\frac\{(\-?\d+)\}\{(\-?\d+)\}", correct_answer)
        if match:
            num = int(match.group(1))
            den = int(match.group(2))
            if den == 0: raise ZeroDivisionError("Denominator cannot be zero.")
            correct_answer_parsed = Fraction(num, den)
        else:
            # Assume it's a simple number string (integer or float)
            correct_answer_parsed = Fraction(float(correct_answer))
    except (ValueError, ZeroDivisionError):
        pass # Parsing failed, correct_answer_parsed remains None

    is_correct = False
    result_text = ""

    if user_answer_parsed is not None and correct_answer_parsed is not None:
        if user_answer_parsed == correct_answer_parsed:
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。你輸入的是 ${user_answer}$，但正確答案應為：${correct_answer}$"
    else:
        # Provide specific feedback if parsing failed for user's answer
        if user_answer_parsed is None:
            result_text = f"你的答案格式不正確。請以整數或分數（例如 `1/2`）形式作答。正確答案應為：${correct_answer}$"
        else:
            # This case means correct_answer_parsed is None, indicating an internal error or malformed correct_answer.
            result_text = f"系統內部錯誤，無法檢查你的答案。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}
=======
        "answer": str(correct_area),
        "correct_answer": str(correct_area)
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    user_answer 和 correct_answer 預期為分數形式的字串 (e.g., "3/2" 或 "2")。
    """
    try:
        user_fraction = Fraction(user_answer.strip())
        correct_fraction = Fraction(correct_answer.strip())
        
        is_correct = (user_fraction == correct_fraction)
        
        if is_correct:
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
        return {"correct": is_correct, "result": result_text, "next_question": True}

    except ValueError:
        return {"correct": False, "result": "請輸入有效的數字或分數形式。", "next_question": False}
>>>>>>> 8971b16094601268e7dca18dbf60df9d4ea36182
