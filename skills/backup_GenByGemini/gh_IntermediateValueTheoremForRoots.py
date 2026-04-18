import random
import math
from fractions import Fraction
import re

# Helper to evaluate polynomial f(x)
def _evaluate_polynomial(coeffs, x_val):
    result = 0
    power = len(coeffs) - 1
    for coeff in coeffs:
        result += coeff * (x_val ** power)
        power -= 1
    return result

# Helper to format polynomial string for LaTeX display
def _format_polynomial_string(coeffs, degree, is_float_coeffs=False):
    poly_terms = []
    
    # Handle the case where all coefficients are effectively zero or just a constant
    is_all_zero = True
    for c in coeffs:
        if abs(c) >= 1e-9:
            is_all_zero = False
            break
    
    if is_all_zero:
        if len(coeffs) == 1 and abs(coeffs[0]) >= 1e-9: # A non-zero constant
            return str(round(coeffs[0], 2)) if is_float_coeffs else str(int(coeffs[0]))
        return "0" # A zero polynomial

    for i, coeff_val in enumerate(coeffs):
        if abs(coeff_val) < 1e-9: # Skip terms with effectively zero coefficient
            continue
        
        power = degree - i
        
        # Determine how to display the coefficient (int or rounded float)
        coeff_str_val = round(coeff_val, 2) if is_float_coeffs else int(coeff_val)
        
        term_prefix = ""
        # Determine the sign and magnitude prefix for the term
        if i == 0: # Leading term
            if coeff_str_val == 1 and power > 0:
                term_prefix = ""
            elif coeff_str_val == -1 and power > 0:
                term_prefix = "-"
            else:
                term_prefix = str(coeff_str_val)
        else: # Non-leading terms
            if coeff_str_val > 0:
                term_prefix = "+"
            elif coeff_str_val < 0:
                term_prefix = "" # Sign will be included in the absolute value string
            
            abs_coeff_val = abs(coeff_str_val)
            if abs_coeff_val == 1 and power > 0:
                pass # Don't print '1' for x^n (e.g., +x, -x)
            else:
                term_prefix += str(abs_coeff_val)

        # Append 'x' and its power
        if power > 1:
            poly_terms.append(f"{term_prefix}x^{{{power}}}")
        elif power == 1:
            poly_terms.append(f"{term_prefix}x")
        elif power == 0: # Constant term
            # For constant term, the coeff_str_val already includes its sign if negative.
            # Only add '+' if it's a positive constant and not the very first term.
            if coeff_str_val > 0 and i > 0:
                 poly_terms.append(f"+{coeff_str_val}")
            else:
                 poly_terms.append(str(coeff_str_val)) # Already contains sign if negative or leading

    poly_str = "".join(poly_terms)
    
    # Remove leading '+' if it exists (e.g., "+3x^2-2x" should be "3x^2-2x")
    if poly_str.startswith("+"):
        poly_str = poly_str[1:]
    
    return poly_str


def generate(level=1):
    problem_type_choices = []
    if level == 1:
        problem_type_choices = ['find_intervals_for_roots']
    elif level == 2:
        problem_type_choices = ['find_intervals_for_roots', 'deduce_integer_roots']
    elif level == 3:
        problem_type_choices = ['deduce_integer_roots', 'k_range_for_distinct_roots']
    
    problem_type = random.choice(problem_type_choices)

    if problem_type == 'find_intervals_for_roots':
        return _generate_find_intervals_for_roots(level)
    elif problem_type == 'deduce_integer_roots':
        return _generate_deduce_integer_roots(level)
    else: # k_range_for_distinct_roots
        return _generate_k_range_for_distinct_roots(level)


def _generate_find_intervals_for_roots(level):
    degree = 3 if level == 1 else random.choice([3, 4])
    
    search_range = 5 # Evaluate from -5 to 5
    
    attempts = 0
    max_attempts = 10
    
    while attempts < max_attempts:
        attempts += 1
        
        num_roots = degree
        # Generate distinct integer roots for base polynomial, ensuring they are within search_range
        possible_roots = list(range(-3, 4)) # E.g., {-3, -2, ..., 3}
        if num_roots > len(possible_roots):
             num_roots = len(possible_roots) # Cap if degree is higher than available distinct roots
        
        roots = random.sample(possible_roots, num_roots)
        
        # Expand (x-r1)(x-r2)... to get base coefficients
        coeffs_base = [1]
        if degree == 3:
            r1, r2, r3 = roots
            coeffs_base.append(-(r1 + r2 + r3))
            coeffs_base.append(r1*r2 + r1*r3 + r2*r3)
            coeffs_base.append(-r1*r2*r3)
        elif degree == 4:
            r1, r2, r3, r4 = roots
            coeffs_base.append(-(r1 + r2 + r3 + r4))
            coeffs_base.append(r1*r2 + r1*r3 + r1*r4 + r2*r3 + r2*r4 + r3*r4)
            coeffs_base.append(-(r1*r2*r3 + r1*r2*r4 + r1*r3*r4 + r2*r3*r4))
            coeffs_base.append(r1*r2*r3*r4)
        
        # Add a small constant to shift the polynomial slightly, making roots non-integer
        # This makes it more likely to rely on IVT for intervals rather than exact integer roots.
        shift_constant = random.choice([-0.7, -0.5, -0.3, -0.2, 0.2, 0.3, 0.5, 0.7])
        
        # Make a copy of coeffs_base for manipulation
        coeffs_with_shift = list(coeffs_base)
        coeffs_with_shift[-1] += shift_constant # Add constant to the constant term
        
        poly_str = _format_polynomial_string(coeffs_with_shift, degree, is_float_coeffs=True)
        
        found_intervals = []
        for x_int in range(-search_range, search_range):
            val_x = _evaluate_polynomial(coeffs_with_shift, x_int)
            val_x_plus_1 = _evaluate_polynomial(coeffs_with_shift, x_int + 1)

            # Check for strict sign change, avoiding f(x)=0 exactly on integers.
            if (val_x < 0 and val_x_plus_1 > 0) or (val_x > 0 and val_x_plus_1 < 0):
                found_intervals.append(f"({x_int}, {x_int + 1})")
        
        if found_intervals: # If intervals are found, we're good to go
            break
    
    # Fallback if no intervals found after multiple attempts (e.g., roots outside search range)
    if not found_intervals:
        # Use a well-known polynomial with roots in range, e.g., x^3 - x - 1
        coeffs_fallback = [1, 0, -1, -1] # f(x) = x^3 - x - 1
        degree = 3
        poly_str = _format_polynomial_string(coeffs_fallback, degree, is_float_coeffs=False)
        found_intervals = []
        for x_int in range(-search_range, search_range):
            val_x = _evaluate_polynomial(coeffs_fallback, x_int)
            val_x_plus_1 = _evaluate_polynomial(coeffs_fallback, x_int + 1)
            if (val_x < 0 and val_x_plus_1 > 0) or (val_x > 0 and val_x_plus_1 < 0):
                found_intervals.append(f"({x_int}, {x_int + 1})")
        if not found_intervals: # Another fallback: x^3 - 8x + 1 (from example)
             coeffs_fallback = [1, 0, -8, 1]
             poly_str = _format_polynomial_string(coeffs_fallback, degree, is_float_coeffs=False)
             for x_int in range(-search_range, search_range):
                val_x = _evaluate_polynomial(coeffs_fallback, x_int)
                val_x_plus_1 = _evaluate_polynomial(coeffs_fallback, x_int + 1)
                if (val_x < 0 and val_x_plus_1 > 0) or (val_x > 0 and val_x_plus_1 < 0):
                    found_intervals.append(f"({x_int}, {x_int + 1})")

    question_text = f"設 $f(x) = {poly_str}$。請找出方程式 $f(x) = 0$ 在哪些連續整數之間有實根？<br>（請列出所有區間，例如：(-3, -2), (0, 1)）"
    correct_answer = ", ".join(sorted(found_intervals)) # Sort for consistent answer format
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def _generate_deduce_integer_roots(level):
    num_roots = 3 # This problem type is designed for cubic polynomials with integer roots
    
    # Generate distinct integer roots within a small range
    integer_roots = sorted(random.sample(range(-2, 4), num_roots)) # E.g., [-1, 1, 2]
    
    # Form the polynomial f(x) = (x-r1)(x-r2)(x-r3)
    r1, r2, r3 = integer_roots
    coeffs = [1, -(r1+r2+r3), r1*r2+r1*r3+r2*r3, -r1*r2*r3]
    
    # Select points for sign evaluation. These points should straddle the roots.
    eval_x_values_float = []
    
    # Add a point before the first root
    val_before_first_root = integer_roots[0] - random.uniform(0.5, 1.0)
    eval_x_values_float.append(val_before_first_root)

    # Add points between roots
    for i in range(num_roots - 1):
        mid_point = (integer_roots[i] + integer_roots[i+1]) / 2.0
        # If mid_point is integer or too close to an integer, slightly shift it
        # This prevents f(x_val)=0, or x_val being an integer, which complicates x_val_str formatting and problem intent.
        if abs(mid_point - round(mid_point)) < 0.1:
            mid_point += random.choice([-0.3, 0.3])
        eval_x_values_float.append(mid_point)
    
    # Add a point after the last root
    val_after_last_root = integer_roots[-1] + random.uniform(0.5, 1.0)
    eval_x_values_float.append(val_after_last_root)

    clue_sign_info = []
    for x_val in sorted(eval_x_values_float):
        f_x = _evaluate_polynomial(coeffs, x_val)
        sign = '>' if f_x > 0 else '<' # f_x should not be exactly 0 for these evaluation points
        
        x_val_str = ""
        # Try to format as sqrt(N) if x_val is close to sqrt(integer N)
        x_val_sq = x_val * x_val
        rounded_x_val_sq = round(x_val_sq)
        
        if x_val > 0 and abs(x_val_sq - rounded_x_val_sq) < 0.05: # Close to sqrt(integer) for positive x
            x_val_str = r"\\sqrt{{{}}}".format(int(rounded_x_val_sq))
        elif x_val < 0 and abs(x_val_sq - rounded_x_val_sq) < 0.05: # Close to -sqrt(integer) for negative x
            x_val_str = r"-\\sqrt{{{}}}".format(int(rounded_x_val_sq))
        else: # Regular float or integer
            x_val_str = str(round(x_val, 2))
            if x_val == int(x_val): # If it's an exact integer, display as integer
                x_val_str = str(int(x_val))

        clue_sign_info.append(f"f({x_val_str}){sign}0")
    
    question_text = (
        f"已知實係數三次多項式 $f(x)$ 滿足 {', '.join(clue_sign_info)}。<br>"
        f"又方程式 $f(x)=0$ 的三根均為整數，請問這三根為何？<br>"
        f"（請以小到大順序，用逗號分隔，例如：1, 2, 3）"
    )
    
    correct_answer_str = ", ".join(map(str, integer_roots))
    
    explanation = f"由勘根定理及根為整數的條件可知：<br>"
    
    # Provide explanation based on the determined intervals
    for i in range(len(eval_x_values_float) - 1):
        x_start = eval_x_values_float[i]
        x_end = eval_x_values_float[i+1]
        
        f_start = _evaluate_polynomial(coeffs, x_start)
        f_end = _evaluate_polynomial(coeffs, x_end)
        
        if (f_start < 0 and f_end > 0) or (f_start > 0 and f_end < 0):
            # A root must be in (x_start, x_end)
            for root in integer_roots:
                if x_start < root < x_end:
                    explanation += (
                        f"- 在 $({round(x_start, 2)}, {round(x_end, 2)})$ (約 {round(x_start,2)}, {round(x_end,2)}) 之間有一整數根，必為 ${root}$。<br>"
                    )
                    break 

    explanation += f"因此三根為 ${correct_answer_str}$。"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str,
        "explanation": explanation
    }


def _generate_k_range_for_distinct_roots(level):
    # This problem type finds the range of k for f(x) = x^3 + ax^2 + bx + k = 0
    # to have three distinct real roots, by analyzing local max/min.
    
    a, b = 0, 0
    x1_prime, x2_prime = Fraction(0), Fraction(0)
    val_at_x1_prime, val_at_x2_prime = Fraction(0), Fraction(0) # f(x) at critical points, without k

    attempts = 0
    max_attempts = 10
    while attempts < max_attempts:
        attempts += 1
        a = random.randint(-4, 4)
        b = random.randint(-10, 10)
        
        discriminant = 4 * a**2 - 12 * b
        
        if discriminant > 0: # Ensure f'(x) has two distinct real roots (critical points)
            sqrt_d = math.sqrt(discriminant)
            
            # Using Fraction for precision in critical points
            x1_prime = Fraction(-2*a - sqrt_d, 6)
            x2_prime = Fraction(-2*a + sqrt_d, 6)
            
            # Evaluate f(x) at x1_prime and x2_prime (without the constant k)
            val_at_x1_prime = (x1_prime**3) + a*(x1_prime**2) + b*x1_prime
            val_at_x2_prime = (x2_prime**3) + a*(x2_prime**2) + b*x2_prime
            
            # The condition for three distinct real roots is (f(x1_prime)+k) * (f(x2_prime)+k) < 0
            # This implies -k must be between f(x1_prime) and f(x2_prime).
            lower_k_bound_frac = Fraction(-max(val_at_x1_prime, val_at_x2_prime)).limit_denominator(100)
            upper_k_bound_frac = Fraction(-min(val_at_x1_prime, val_at_x2_prime)).limit_denominator(100)
            
            # Ensure the range for k is distinct and reasonably wide for a good problem
            if lower_k_bound_frac != upper_k_bound_frac and (upper_k_bound_frac - lower_k_bound_frac) > Fraction(2, 5): 
                break
    else: # Fallback to example values if random generation fails to produce a suitable polynomial
        a = -3
        b = -9
        x1_prime = Fraction(-1) # Critical point
        x2_prime = Fraction(3)  # Critical point
        val_at_x1_prime = Fraction(5) # f(-1) without k
        val_at_x2_prime = Fraction(-27) # f(3) without k
        lower_k_bound_frac = Fraction(-5)
        upper_k_bound_frac = Fraction(27)

    # Format polynomial string: x^3 + ax^2 + bx + k
    # First, format the part without k: f(x) = x^3 + ax^2 + bx
    f_coeffs_no_k = [1, a, b, 0] # Degree 3, constant term is 0 for this part
    poly_str_no_k = _format_polynomial_string(f_coeffs_no_k, 3, is_float_coeffs=False)
    
    question_text = (
        f"已知方程式 ${poly_str_no_k} + k = 0$ 有三個相異實根，求實數 $k$ 的範圍。"
    )
    
    # Format answer for display (LaTeX) and for internal checking (plain string)
    correct_answer_display = f"${lower_k_bound_frac} < k < {upper_k_bound_frac}$"
    correct_answer_for_check = f"{lower_k_bound_frac} < k < {upper_k_bound_frac}" 
    
    # Generate detailed explanation for feedback
    explanation = f"設 $f(x) = {poly_str_no_k} + k$。<br>"
    
    # Calculate f'(x) = 3x^2 + 2ax + b
    f_prime_coeffs = [3, 2*a, b]
    f_prime_poly_str = _format_polynomial_string(f_prime_coeffs, 2, is_float_coeffs=False) # Degree 2
    
    explanation += f"$f'(x) = {f_prime_poly_str}$。"
    
    critical_points_float = sorted([float(x1_prime), float(x2_prime)])
    
    # If critical points are integers, show factorization of f'(x) in the explanation
    if x1_prime.denominator == 1 and x2_prime.denominator == 1:
        cp1 = int(x1_prime)
        cp2 = int(x2_prime)
        
        factor1_term = f"x{'+' if -cp1 > 0 else ''}{-cp1}"
        factor2_term = f"x{'+' if -cp2 > 0 else ''}{-cp2}"
        
        explanation += f"<br>令 $f'(x)=0$ 得 ${f_prime_poly_str} = 3({factor1_term})({factor2_term}) = 0$。"
        explanation += f"<br>得極值點 $x={cp1}, {cp2}$。"
        
        exp_val_at_x1 = f"f({cp1}) = ${val_at_x1_prime} + k$"
        exp_val_at_x2 = f"f({cp2}) = ${val_at_x2_prime} + k$"
    else: # Critical points are fractions/decimals, don't show factorization
        explanation += f"<br>令 $f'(x)=0$ 得極值點 $x \\approx {critical_points_float[0]:.2f}, {critical_points_float[1]:.2f}$。"
        exp_val_at_x1 = f"f({critical_points_float[0]:.2f}) = ${val_at_x1_prime} + k$"
        exp_val_at_x2 = f"f({critical_points_float[1]:.2f}) = ${val_at_x2_prime} + k$"

    explanation += f"<br>計算在這些極值點的函數值："
    explanation += f"<br>${exp_val_at_x1}$ (極大值或極小值)"
    explanation += f"<br>${exp_val_at_x2}$ (極大值或極小值)"
    
    explanation += "<br>欲使方程式有三相異實根，需極大值與極小值異號，即其乘積 $< 0$。<br>"
    explanation += f"$({val_at_x1_prime} + k)({val_at_x2_prime} + k) < 0$<br>"
    explanation += f"解得 ${lower_k_bound_frac} < k < {upper_k_bound_frac}$。"

    return {
        "question_text": question_text,
        "answer": correct_answer_for_check, # Use plain string for checking
        "correct_answer": correct_answer_display, # Use LaTeX for displaying to user
        "explanation": explanation
    }


def check(user_answer, correct_answer):
    user_answer = user_answer.strip()
    # Remove LaTeX delimiters ($) from correct_answer for internal parsing
    correct_answer_raw = correct_answer.replace('$', '').strip() 
    
    is_correct = False
    result_text = ""

    # Check for interval type answer (e.g., (-3, -2), (0, 1))
    if "(" in correct_answer_raw and ")" in correct_answer_raw:
        # Normalize user intervals: remove spaces, split by comma, sort for consistent comparison
        user_intervals = set(s.strip() for s in user_answer.replace(" ", "").split(','))
        correct_intervals = set(s.strip() for s in correct_answer_raw.replace(" ", "").split(','))
        
        if user_intervals == correct_intervals:
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer_raw}$。"
        else:
            result_text = f"答案不正確。請檢查您列出的區間是否完整且正確。<br>正確答案應為：${correct_answer_raw}$"
    
    # Check for integer roots type answer (e.g., 1, 2, 3)
    elif "," in correct_answer_raw and not ("<" in correct_answer_raw or ">" in correct_answer_raw): 
        try:
            # Parse and sort user roots for comparison
            user_roots = sorted([int(x.strip()) for x in user_answer.replace(" ", "").split(',')])
            correct_roots = sorted([int(x.strip()) for x in correct_answer_raw.replace(" ", "").split(',')])
            
            if user_roots == correct_roots:
                is_correct = True
                result_text = f"完全正確！答案是 ${correct_answer_raw}$。"
            else:
                result_text = f"答案不正確。請檢查您找到的整數根。<br>正確答案應為：${correct_answer_raw}$"
        except ValueError:
            result_text = f"答案格式不正確，請輸入以逗號分隔的整數。<br>正確答案應為：${correct_answer_raw}$"
    
    # Check for k range type answer (e.g., -5 < k < 27)
    elif "<" in correct_answer_raw and ">" in correct_answer_raw:
        # Use regex to parse the lower and upper bounds
        match_user = re.match(r"^\s*(?P<lower>[-\d\.\/]+)\s*<\s*k\s*<\s*(?P<upper>[-\d\.\/]+)\s*$", user_answer)
        match_correct = re.match(r"^\s*(?P<lower>[-\d\.\/]+)\s*<\s*k\s*<\s*(?P<upper>[-\d\.\/]+)\s*$", correct_answer_raw)
        
        if match_user and match_correct:
            # Convert parsed strings to Fractions for precise comparison
            user_lower = Fraction(match_user.group('lower'))
            user_upper = Fraction(match_user.group('upper'))
            correct_lower = Fraction(match_correct.group('lower'))
            correct_upper = Fraction(match_correct.group('upper'))
            
            if user_lower == correct_lower and user_upper == correct_upper:
                is_correct = True
                result_text = f"完全正確！答案是 ${correct_answer_raw}$。"
            else:
                result_text = f"答案不正確。請檢查 $k$ 的範圍。<br>正確答案應為：${correct_answer_raw}$"
        else:
            result_text = f"答案格式不正確。請確保答案格式為 `a < k < b`。<br>正確答案應為：${correct_answer_raw}$"
    
    else: # Fallback for unexpected formats, try direct string comparison (case-insensitive)
        if user_answer.lower() == correct_answer_raw.lower():
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer_raw}$。"
        else:
            result_text = f"答案不正確。正確答案應為：${correct_answer_raw}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}