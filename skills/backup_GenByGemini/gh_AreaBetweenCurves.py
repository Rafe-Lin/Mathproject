import random
import math
from fractions import Fraction
import re

def format_polynomial(a, b, c):
    """
    Formats a quadratic polynomial ax^2 + bx + c into a LaTeX-friendly string.
    Handles zero coefficients and coefficients of 1 or -1 for cleaner display.
    """
    parts = []
    
    # x^2 term
    if a != 0:
        if a == 1:
            parts.append("x^{{2}}")
        elif a == -1:
            parts.append("-x^{{2}}")
        else:
            parts.append(f"{a}x^{{2}}")
    
    # x term
    if b != 0:
        if b == 1:
            parts.append("+x" if parts else "x") # Prepend '+' only if not first term
        elif b == -1:
            parts.append("-x")
        elif b > 0:
            parts.append(f"+{b}x")
        else: # b < 0
            parts.append(f"{b}x")
            
    # Constant term
    if c != 0:
        if c > 0:
            parts.append(f"+{c}")
        else: # c < 0
            parts.append(f"{c}")
            
    if not parts:
        return "0"
    
    # Remove leading '+' if it exists (e.g., from "+2x+3" to "2x+3")
    return "".join(parts).lstrip('+')

def format_linear(m, c):
    """
    Formats a linear polynomial mx + c into a LaTeX-friendly string.
    Handles zero coefficients and coefficients of 1 or -1 for cleaner display.
    """
    parts = []
    
    # x term
    if m != 0:
        if m == 1:
            parts.append("x")
        elif m == -1:
            parts.append("-x")
        else:
            parts.append(f"{m}x")
            
    # Constant term
    if c != 0:
        if c > 0:
            parts.append(f"+{c}")
        else: # c < 0
            parts.append(f"{c}")
            
    if not parts:
        return "0"
        
    return "".join(parts).lstrip('+')

def generate(level=1):
    """
    生成「曲線間面積」相關題目。
    Level 1: 兩個函數 (一個二次，一個線性) 與兩個垂直線所圍成的區域面積。
             確保在指定區間內，其中一個函數總是位於另一個函數的上方或下方，
             以避免需要分段積分。
    """
    
    # Step 1: Generate coefficients for the difference function h(x) = a_diff*x^2 + b_diff*x + c_diff
    # We ensure h(x) is always positive or always negative over any interval by making its discriminant negative.
    
    # a_diff ensures it's a quadratic difference, and determines if parabola opens up/down
    a_diff = random.choice([-2, -1, 1, 2]) 
    b_diff = random.randint(-4, 4)
    
    c_diff = 0
    if a_diff > 0: # Parabola opens up, want h(x) > 0 always
        # Need b_diff^2 - 4 * a_diff * c_diff < 0  =>  4 * a_diff * c_diff > b_diff^2
        # So c_diff > b_diff^2 / (4 * a_diff)
        min_c_diff_val = math.floor(b_diff**2 / (4 * a_diff)) + 1
        c_diff = random.randint(min_c_diff_val, min_c_diff_val + 5)
    else: # a_diff < 0, Parabola opens down, want h(x) < 0 always
        # Need b_diff^2 - 4 * a_diff * c_diff < 0  =>  4 * a_diff * c_diff > b_diff^2
        # So c_diff < b_diff^2 / (4 * a_diff)
        max_c_diff_val = math.ceil(b_diff**2 / (4 * a_diff)) - 1
        c_diff = random.randint(max_c_diff_val - 5, max_c_diff_val)

    # Step 2: Deconstruct h(x) into f(x) (quadratic) and g(x) (linear)
    # Such that f(x) - g(x) = h(x)
    
    # f(x) = a_f x^2 + b_f x + c_f
    # g(x) = b_g x + c_g
    
    # a_f = a_diff
    a_f = a_diff
    
    # b_f - b_g = b_diff  => b_f = b_diff + b_g
    b_g = random.randint(-3, 3)
    b_f = b_diff + b_g
    
    # c_f - c_g = c_diff  => c_f = c_diff + c_g
    c_g = random.randint(-5, 5)
    c_f = c_diff + c_g
    
    # Ensure f(x) and g(x) are distinct and not trivial
    if a_f == 0 and b_f == 0 and c_f == 0:
        # Should not happen with current a_diff generation, but as a safety
        a_f = random.choice([1, -1])
    if b_g == 0 and c_g == 0:
        b_g = random.choice([1, -1])

    # Step 3: Generate integration limits a and b
    a = random.randint(-3, 0)
    b = random.randint(1, 4)
    
    # Ensure a < b, although current random ranges usually guarantee this.
    if a >= b:
        a, b = min(a, b), max(a, b)
        if a == b: # Highly unlikely, but to be absolutely safe, shift one
            b += 1 
            
    # Step 4: Construct question text using formatted polynomials
    problem_text_f = format_polynomial(a_f, b_f, c_f)
    problem_text_g = format_linear(b_g, c_g)
    
    question_text = f"求兩函數 $f(x) = {problem_text_f}$ 與 $g(x) = {problem_text_g}$ 的圖形與 $x = {a}$, $x = {b}$ 所圍成的區域面積。"
    
    # Step 5: Calculate the correct answer using fractions
    # The function to integrate is h(x) = a_diff*x^2 + b_diff*x + c_diff
    # Integral P(x) = (a_diff/3)x^3 + (b_diff/2)x^2 + (c_diff)x
    
    a_diff_frac = Fraction(a_diff)
    b_diff_frac = Fraction(b_diff)
    c_diff_frac = Fraction(c_diff)

    def evaluate_integral_term(x_val):
        term1 = (a_diff_frac / 3) * (x_val**3)
        term2 = (b_diff_frac / 2) * (x_val**2)
        term3 = c_diff_frac * x_val
        return term1 + term2 + term3

    val_at_b = evaluate_integral_term(b)
    val_at_a = evaluate_integral_term(a)
    
    integral_value = val_at_b - val_at_a
    
    # The area is the absolute value of the definite integral
    correct_area = abs(integral_value)
    
    # Format the answer as a string (integer or LaTeX fraction)
    if correct_area.denominator == 1:
        correct_answer_str = str(correct_area.numerator)
    else:
        correct_answer_str = f"\\frac{{{correct_area.numerator}}}{{{correct_area.denominator}}}"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def parse_fraction_string(s):
    """
    Parses a string into a Fraction object. Handles integers, simple fractions (e.g., "5/3"),
    and LaTeX fractions (e.g., "\\frac{5}{3}").
    """
    s = s.strip()
    
    # Try parsing as a simple fraction or integer (e.g., "5", "5/3")
    try:
        return Fraction(s)
    except ValueError:
        pass

    # Try parsing as a LaTeX fraction (e.g., "\\frac{5}{3}")
    # Using raw string for regex pattern to avoid issues with backslashes
    match = re.match(r"\\frac\{(\-?\d+)\}\{(\d+)\}", s)
    if match:
        numerator = int(match.group(1))
        denominator = int(match.group(2))
        if denominator == 0:
            raise ValueError("分母不能為零。")
        return Fraction(numerator, denominator)
    
    raise ValueError(f"無法解析 '{s}' 為有效的數字或分數格式。")

def check(user_answer, correct_answer_str):
    """
    檢查使用者答案是否正確。
    user_answer: 用戶輸入的字串，可能是整數, 分數(e.g., "5/3"), 或 LaTeX 分數(e.g., "\\frac{5}{3}")
    correct_answer_str: generate 函數返回的正確答案字串 (整數或 LaTeX 分數)
    """
    try:
        user_frac = parse_fraction_string(user_answer)
    except ValueError as e:
        return {"correct": False, "result": f"請輸入正確的數字或分數格式 (例如: 5, 5/6 或 \\frac{{5}}{{6}})。錯誤: {e}", "next_question": False}

    try:
        correct_frac = parse_fraction_string(correct_answer_str)
    except ValueError as e:
        # This indicates an internal error in generating the correct_answer_str, not user input.
        return {"correct": False, "result": f"內部錯誤：無法解析正確答案 '{correct_answer_str}'。請聯繫管理員。錯誤: {e}", "next_question": False}

    is_correct = (user_frac == correct_frac)
    result_text = f"完全正確！答案是 ${correct_answer_str}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_str}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}