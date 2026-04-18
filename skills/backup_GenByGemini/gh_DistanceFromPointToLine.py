import random
import math
from fractions import Fraction
import uuid

# --- Helper functions ---

# Common (A,B) pairs where A^2+B^2 is a perfect square (hypotenuse is an integer)
# Format: (abs(A), abs(B), hypotenuse_integer_value)
_PYTH_TRIPLES = [
    (3, 4, 5), (4, 3, 5),
    (5, 12, 13), (12, 5, 13),
    (6, 8, 10), (8, 6, 10),
    (7, 24, 25), (24, 7, 25),
    (8, 15, 17), (15, 8, 17)
]

def _format_number_or_fraction(num):
    """Formats a number as an integer or a simplified fraction string for LaTeX."""
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        return r"\\frac{{{}}}{{{}}}".format(num.numerator, num.denominator)
    elif isinstance(num, float):
        if num.is_integer():
            return str(int(num))
        # Try to represent floats as fractions
        fraction_num = Fraction(num).limit_denominator(10000)
        if abs(fraction_num - num) < 1e-9: # Check if fraction is a good representation
            if fraction_num.denominator == 1:
                return str(fraction_num.numerator)
            return r"\\frac{{{}}}{{{}}}".format(fraction_num.numerator, fraction_num.denominator)
        return str(num) # Fallback for irrational or very complex floats
    return str(num)

def _simplify_sqrt(n):
    """Simplifies sqrt(n) into c * sqrt(r) form. Returns (c, r)."""
    if n == 0: return 0, 0
    if n == 1: return 1, 1
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % (i*i) == 0:
            coeff, radicand = _simplify_sqrt(n // (i*i))
            return coeff * i, radicand
    return 1, n

def _format_distance_answer(numerator_val, denominator_sq_val):
    """
    Formats the distance answer, handling square roots and rationalization.
    Takes the absolute numerator value and the A^2+B^2 value.
    For Level 1, this function is configured to receive `denominator_sq_val` that is a perfect square.
    """
    if numerator_val == 0:
        return "0"

    # For Level 1, we ensure denominator_sq_val is a perfect square (e.g., from PYTH_TRIPLES)
    sqrt_den = int(math.sqrt(denominator_sq_val))
    
    return _format_number_or_fraction(Fraction(numerator_val, sqrt_den))

# --- Problem generation functions ---

def _generate_point_to_line_distance(level):
    """Generates a problem to find the distance from a point to a line."""
    # Choose (A,B) from Pythagorean triples for Level 1 to ensure integer sqrt(A^2+B^2)
    coeff_choice = random.choice(_PYTH_TRIPLES)
    abs_A, abs_B, sqrt_val = coeff_choice[0], coeff_choice[1], coeff_choice[2]

    # Assign random signs to A and B
    A = abs_A * random.choice([-1, 1])
    B = abs_B * random.choice([-1, 1])
    
    # Generate point (x0, y0)
    x0 = random.randint(-5, 5)
    y0 = random.randint(-5, 5)

    # Generate C
    C = random.randint(-10, 10)

    # Question text
    # Use f-string's format specifier {B:+} for signed numbers like +3, -4
    question_text = f"求點 $P({x0},{y0})$ 到直線 $L: {A}x {B:+}y {C:+} = 0$ 的距離。"
    
    # Calculate distance
    numerator = abs(A * x0 + B * y0 + C)
    
    correct_answer = _format_distance_answer(numerator, sqrt_val**2)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_point_to_line_unknown_coord(level):
    """Generates a problem to find an unknown coordinate given distance from point to line."""
    # Choose (A,B) from Pythagorean triples for Level 1 to ensure integer sqrt(A^2+B^2)
    coeff_choice = random.choice(_PYTH_TRIPLES)
    abs_A, abs_B, sqrt_val = coeff_choice[0], coeff_choice[1], coeff_choice[2]

    A = abs_A * random.choice([-1, 1])
    B = abs_B * random.choice([-1, 1])
    
    # Decide which coordinate is 'k'
    k_is_x = random.choice([True, False])
    
    if k_is_x: # Unknown is x-coord
        if A == 0: A = random.choice([-1, 1]) # Ensure A is not zero to solve for k
        x_coord_str = "k"
        y_coord_val = random.randint(-5, 5)
        P_x0 = None # k
        P_y0 = y_coord_val
    else: # Unknown is y-coord
        if B == 0: B = random.choice([-1, 1]) # Ensure B is not zero to solve for k
        x_coord_val = random.randint(-5, 5)
        y_coord_str = "k"
        P_x0 = x_coord_val
        P_y0 = None # k
    
    C = random.randint(-10, 10)
    
    # Generate target distance `d` such that `d * sqrt_val` is an integer,
    # making `k` an integer or simple fraction.
    num_abs_val = random.randint(1, 15) # This will be |A*x0 + B*y0 + C|
    target_distance = Fraction(num_abs_val, sqrt_val)
    
    solutions = []
    
    for sign in [1, -1]:
        if k_is_x:
            # A*k + B*P_y0 + C = sign * num_abs_val
            # A*k = sign * num_abs_val - B*P_y0 - C
            numerator_k = sign * num_abs_val - B * P_y0 - C
            k_val = Fraction(numerator_k, A)
            solutions.append(k_val)
        else: # k_is_y
            # A*P_x0 + B*k + C = sign * num_abs_val
            # B*k = sign * num_abs_val - A*P_x0 - C
            numerator_k = sign * num_abs_val - A * P_x0 - C
            k_val = Fraction(numerator_k, B)
            solutions.append(k_val)
                
    # Remove duplicate solutions and sort
    solutions = sorted(list(set(solutions)))
    
    # Format solutions
    formatted_solutions = []
    for sol in solutions:
        formatted_solutions.append(_format_number_or_fraction(sol))

    if k_is_x:
        question_text = f"已知點 $P(k,{y_coord_val})$ 到直線 $L: {A}x {B:+}y {C:+} = 0$ 的距離為 ${_format_number_or_fraction(target_distance)}$，求 $k$ 的值。"
    else:
        question_text = f"已知點 $P({x_coord_val},k)$ 到直線 $L: {A}x {B:+}y {C:+} = 0$ 的距離為 ${_format_number_or_fraction(target_distance)}$，求 $k$ 的值。"
    
    correct_answer = ", ".join(formatted_solutions)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_parallel_lines_distance(level):
    """Generates a problem to find the distance between two parallel lines."""
    # Choose (A,B) from Pythagorean triples for Level 1 to ensure integer sqrt(A^2+B^2)
    coeff_choice = random.choice(_PYTH_TRIPLES)
    abs_A, abs_B, sqrt_val = coeff_choice[0], coeff_choice[1], coeff_choice[2]

    A = abs_A * random.choice([-1, 1])
    B = abs_B * random.choice([-1, 1])

    C1 = random.randint(-10, 10)
    C2 = random.randint(-10, 10)

    # Ensure C1 and C2 (after potential scaling) are different
    # Introduce a scaling factor for L2 to make it less obvious
    multiplier = random.choice([2, 3])
    
    # Generate C2 such that C1 and C2_prime are different
    while C1 == C2 * multiplier:
        C2 = random.randint(-10, 10)
    
    L1_text = f"${A}x {B:+}y {C1:+} = 0$"
    L2_text = f"${A*multiplier}x {B*multiplier:+}y {C2*multiplier:+} = 0$"

    # To calculate distance, convert L2 to the same (A,B) coefficients as L1
    C2_prime = Fraction(C2 * multiplier, multiplier) # This is C2
    
    numerator = abs(C1 - C2_prime)
    
    question_text = f"求兩平行直線 $L_1: {L1_text}$ 與 $L_2: {L2_text}$ 的距離。"
    
    correct_answer = _format_distance_answer(numerator, sqrt_val**2)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_parallel_lines_unknown_constant(level):
    """Generates a problem to find an unknown constant in a parallel line given the distance."""
    # Choose (A,B) from Pythagorean triples for Level 1 to ensure integer sqrt(A^2+B^2)
    coeff_choice = random.choice(_PYTH_TRIPLES)
    abs_A, abs_B, sqrt_val = coeff_choice[0], coeff_choice[1], coeff_choice[2]

    A = abs_A * random.choice([-1, 1])
    B = abs_B * random.choice([-1, 1])

    C1 = random.randint(-10, 10)
    
    # Generate target distance `d` such that `d * sqrt_val` is an integer,
    # making `k` an integer or simple fraction.
    num_abs_val = random.randint(1, 15) # This will be |C1 - k|
    target_distance = Fraction(num_abs_val, sqrt_val)
    
    # Solutions for k:
    # |C1 - k| = num_abs_val
    # Case 1: C1 - k = num_abs_val  => k = C1 - num_abs_val
    # Case 2: C1 - k = -num_abs_val => k = C1 + num_abs_val
    
    solutions = [
        Fraction(C1 - num_abs_val, 1),
        Fraction(C1 + num_abs_val, 1)
    ]
    solutions = sorted(list(set(solutions))) # Remove duplicates and sort
    
    formatted_solutions = []
    for sol in solutions:
        formatted_solutions.append(_format_number_or_fraction(sol))

    L1_text = f"${A}x {B:+}y {C1:+} = 0$"
    L2_text = f"${A}x {B:+}y + k = 0$"
    
    question_text = f"已知兩平行直線 $L_1: {L1_text}$ 與 $L_2: {L2_text}$ 的距離為 ${_format_number_or_fraction(target_distance)}$，求 $k$ 的值。"
    correct_answer = ", ".join(formatted_solutions)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Main generate function ---

def generate(level=1):
    """
    生成「點到直線的距離」或「兩平行直線間的距離」相關題目。
    """
    problem_type = random.choice([
        'point_to_line_distance',
        'point_to_line_unknown_coord',
        'parallel_lines_distance',
        'parallel_lines_unknown_constant'
    ])
    
    if problem_type == 'point_to_line_distance':
        return _generate_point_to_line_distance(level)
    elif problem_type == 'point_to_line_unknown_coord':
        return _generate_point_to_line_unknown_coord(level)
    elif problem_type == 'parallel_lines_distance':
        return _generate_parallel_lines_distance(level)
    else: # 'parallel_lines_unknown_constant'
        return _generate_parallel_lines_unknown_constant(level)

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    支援整數、分數以及逗號分隔的多個答案。
    """
    user_answer_normalized = user_answer.strip().replace(' ', '')
    correct_answer_normalized = correct_answer.strip().replace(' ', '')
    
    # Handle multiple answers separated by comma
    user_parts_raw = [part.strip() for part in user_answer_normalized.split(',')]
    correct_parts_raw = [part.strip() for part in correct_answer_normalized.split(',')]

    if len(user_parts_raw) != len(correct_parts_raw):
        return {"correct": False, "result": f"答案數量不符。請檢查是否有遺漏或多餘的答案。", "next_question": False}

    is_correct = True
    user_parsed = []
    correct_parsed = []

    for u_part, c_part in zip(user_parts_raw, correct_parts_raw):
        try:
            # Normalize LaTeX fraction input for Fraction parser
            u_part = u_part.replace(r'\\frac{', '(').replace('}{', '/').replace('}', ')')
            c_part = c_part.replace(r'\\frac{', '(').replace('}{', '/').replace('}', ')')

            u_frac = Fraction(u_part)
            c_frac = Fraction(c_part)
            
            user_parsed.append(u_frac)
            correct_parsed.append(c_frac)

        except ValueError:
            # Fallback for non-fractional (e.g., possibly sqrt, though not expected for level 1)
            # For Level 1, we expect all answers to be integers or simple fractions,
            # so a ValueError here indicates incorrect input format.
            is_correct = False
            break
    
    if is_correct:
        # Compare sorted lists of Fractions
        if sorted(user_parsed) != sorted(correct_parsed):
            is_correct = False

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}