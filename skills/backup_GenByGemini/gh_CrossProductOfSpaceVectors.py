import random
import math
import re
from fractions import Fraction

# --- Helper Functions ---
def get_random_vector(min_val=-5, max_val=5, allow_zero=True):
    """Generates a random 3D integer vector."""
    while True:
        x = random.randint(min_val, max_val)
        y = random.randint(min_val, max_val)
        z = random.randint(min_val, max_val)
        if allow_zero or (x, y, z) != (0, 0, 0):
            return (x, y, z)

def cross_product(v1, v2):
    """Calculates the cross product of two 3D vectors."""
    # v1 = (a1, a2, a3)
    # v2 = (b1, b2, b3)
    # a x b = (a2b3 - a3b2, a3b1 - a1b3, a1b2 - a2b1)
    x = v1[1] * v2[2] - v1[2] * v2[1]
    y = v1[2] * v2[0] - v1[0] * v2[2]
    z = v1[0] * v2[1] - v1[1] * v2[0]
    return (x, y, z)

def vector_magnitude_squared(v):
    """Calculates the square of the magnitude of a 3D vector."""
    return v[0]**2 + v[1]**2 + v[2]**2

def format_vector_latex(v):
    """Formats a vector tuple (x, y, z) as "(x, y, z)" for LaTeX display."""
    return r"({}, {}, {})".format(v[0], v[1], v[2])

def simplify_sqrt_parts(n):
    """
    Simplifies sqrt(n) into (coefficient, radicand) where sqrt(n) = coefficient * sqrt(radicand).
    e.g., n=27 -> (3, 3) because sqrt(27) = 3*sqrt(3).
    """
    if n < 0:
        raise ValueError("Cannot simplify sqrt of negative number.")
    if n == 0:
        return (0, 1) # 0 * sqrt(1)
    
    i = 1
    factor = 1
    while i * i <= n:
        if n % (i * i) == 0:
            factor = i
        i += 1
    
    remainder = n // (factor * factor)
    return (factor, remainder)

def format_simplified_sqrt_latex(coeff, radicand):
    """
    Formats the simplified square root (coeff, radicand) into a LaTeX string.
    Expected `coeff` here is an integer from `simplify_sqrt_parts`.
    """
    if coeff == 0:
        return "0"
    if radicand == 1:
        return str(coeff)
    if coeff == 1:
        return r"\\sqrt{{{}}}".format(radicand)
    return r"{}\\sqrt{{{}}}".format(coeff, radicand)

def scalar_multiply(scalar, v):
    """Multiplies a vector by a scalar."""
    return (scalar * v[0], scalar * v[1], scalar * v[2])

def are_vectors_parallel(v1, v2):
    """Checks if two vectors are parallel by checking their cross product."""
    if v1 == (0,0,0) or v2 == (0,0,0):
        return True
    
    cp = cross_product(v1, v2)
    return cp == (0,0,0)

# --- Problem Generators ---

def generate_direct_cross_product():
    """Generates a problem to calculate the cross product of two vectors."""
    vec_a = get_random_vector()
    vec_b = get_random_vector()

    result_vec = cross_product(vec_a, vec_b)

    question_text = (
        f"已知向量 $\\vec{{a}} = {format_vector_latex(vec_a)}$ 及 $\\vec{{b}} = {format_vector_latex(vec_b)}$，"
        f"求 $\\vec{{a}} \\times \\vec{{b}}$。"
    )
    correct_answer = format_vector_latex(result_vec)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_parallelogram_area():
    """Generates a problem to find the area of a parallelogram formed by two vectors."""
    attempts = 0
    while attempts < 20: # Attempt to get non-parallel vectors for non-zero area
        vec_a = get_random_vector()
        vec_b = get_random_vector()
        if not are_vectors_parallel(vec_a, vec_b):
            break
        attempts += 1
    
    # Even if parallel, a 0 area is a valid result.
    cp_vec = cross_product(vec_a, vec_b)
    mag_sq = vector_magnitude_squared(cp_vec)
    
    coeff, radicand = simplify_sqrt_parts(mag_sq)
    formatted_mag = format_simplified_sqrt_latex(coeff, radicand)

    question_text = (
        f"已知向量 $\\vec{{a}} = {format_vector_latex(vec_a)}$ 及 $\\vec{{b}} = {format_vector_latex(vec_b)}$，"
        f"求由 $\\vec{{a}}$ 與 $\\vec{{b}}$ 決定的平行四邊形面積。"
    )
    correct_answer = formatted_mag

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_triangle_area():
    """Generates a problem to find the area of a triangle given three points."""
    attempts = 0
    while attempts < 20: # Attempt to get non-collinear points for non-zero area
        point_a = get_random_vector()
        point_b = get_random_vector()
        point_c = get_random_vector()

        vec_ab = (point_b[0] - point_a[0], point_b[1] - point_a[1], point_b[2] - point_a[2])
        vec_ac = (point_c[0] - point_a[0], point_c[1] - point_a[1], point_c[2] - point_a[2])
        
        if not are_vectors_parallel(vec_ab, vec_ac):
            break
        attempts += 1

    cp_vec = cross_product(vec_ab, vec_ac)
    mag_sq = vector_magnitude_squared(cp_vec)
    
    coeff, radicand = simplify_sqrt_parts(mag_sq)
    
    # Area is (1/2) * coeff * sqrt(radicand)
    numerator = coeff
    denominator = 2
    
    common_divisor = math.gcd(numerator, denominator)
    numerator //= common_divisor
    denominator //= common_divisor
    
    # Format the coefficient part
    if denominator == 1:
        final_coeff_str = str(numerator)
    else:
        final_coeff_str = r"\\frac{{{}}}{{{}}}".format(numerator, denominator)
    
    # Format the entire area expression
    if radicand == 1:
        formatted_area = final_coeff_str
    elif numerator == 1 and denominator == 1: # Case where coeff is 1 and no fraction (e.g., 1\\sqrt{3} -> \\sqrt{3})
        formatted_area = r"\\sqrt{{{}}}".format(radicand)
    else: # General case: (A/B)sqrt(C)
        formatted_area = f"{final_coeff_str}\\sqrt{{{radicand}}}"

    question_text = (
        f"已知空間中三點 $A{format_vector_latex(point_a)}$, $B{format_vector_latex(point_b)}$, $C{format_vector_latex(point_c)}$，"
        f"求 $\\triangle ABC$ 的面積。"
    )
    correct_answer = formatted_area

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_perpendicular_vector():
    """Generates a problem to find a vector perpendicular to two given vectors with a specific magnitude."""
    attempts = 0
    cp_vec = (0,0,0)
    mag_sq = 0

    # Loop to ensure cp_vec has an integer magnitude and is not a zero vector
    while (not math.isqrt(mag_sq)**2 == mag_sq or mag_sq == 0) and attempts < 20:
        # Use smaller range and disallow zero vectors for a and b to increase chances of non-zero cp
        vec_a = get_random_vector(min_val=-3, max_val=3, allow_zero=False)
        vec_b = get_random_vector(min_val=-3, max_val=3, allow_zero=False)
        
        cp_vec = cross_product(vec_a, vec_b)
        mag_sq = vector_magnitude_squared(cp_vec)
        attempts += 1
    
    # Fallback if a suitable vector is not found (e.g., all generated a,b are parallel)
    # This scenario is highly unlikely given the random range and number of attempts.
    # If it does occur, `magnitude_cp` might still be 0, leading to a division by zero error later.
    # For robustness, we could return a different problem type or ensure mag_sq is non-zero.
    # For now, we assume a valid `cp_vec` with integer magnitude will be found.
    
    magnitude_cp = int(math.sqrt(mag_sq)) # Should be an integer after the loop condition

    t_multiplier = random.randint(1, 3) # The scalar multiplier t can be 1, 2, or 3
    target_mag = t_multiplier * magnitude_cp

    vec_c1 = scalar_multiply(t_multiplier, cp_vec)
    vec_c2 = scalar_multiply(-t_multiplier, cp_vec)
    
    formatted_c1 = format_vector_latex(vec_c1)
    formatted_c2 = format_vector_latex(vec_c2)

    question_text = (
        f"已知向量 $\\vec{{c}}$ 與 $\\vec{{a}} = {format_vector_latex(vec_a)}$, "
        f"$\\vec{{b}} = {format_vector_latex(vec_b)}$ 都垂直，且 $|\\vec{{c}}| = {target_mag}$，求 $\\vec{{c}}$。"
    )
    
    # Sort the vector strings lexicographically for consistent answer ordering
    ans_list = sorted([formatted_c1, formatted_c2])
    correct_answer = f"{ans_list[0]} 或 {ans_list[1]}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_cross_product_properties():
    """Generates a problem to demonstrate cross product properties like a x b = -(b x a)."""
    vec_a = get_random_vector()
    vec_b = get_random_vector()

    cp_ab = cross_product(vec_a, vec_b)
    cp_ba = cross_product(vec_b, vec_a)

    question_text = (
        f"已知向量 $\\vec{{a}} = {format_vector_latex(vec_a)}$ 及 $\\vec{{b}} = {format_vector_latex(vec_b)}$，"
        f"求 $\\vec{{a}} \\times \\vec{{b}}$ 與 $\\vec{{b}} \\times \\vec{{a}}$。"
    )
    
    correct_answer_ab_str = format_vector_latex(cp_ab)
    correct_answer_ba_str = format_vector_latex(cp_ba)
    # Using a custom separator for internal checking consistency.
    # The check function will split by this, and the feedback will replace it.
    correct_answer = f"{correct_answer_ab_str} | {correct_answer_ba_str}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「空間中兩向量外積」相關題目。
    包含：
    1. 直接計算外積
    2. 由兩向量決定平行四邊形面積
    3. 由三點決定三角形面積
    4. 尋找同時垂直兩向量且具特定長度的向量
    5. 外積的反交換律 ($\vec{a} \\times \vec{b}$ 與 $\vec{b} \\times \vec{a}$)
    """
    problem_types = [
        'direct_cross_product',
        'parallelogram_area',
        'triangle_area',
        'perpendicular_vector',
        'cross_product_properties'
    ]
    problem_type = random.choice(problem_types) # For level 1, randomly pick any type.

    if problem_type == 'direct_cross_product':
        return generate_direct_cross_product()
    elif problem_type == 'parallelogram_area':
        return generate_parallelogram_area()
    elif problem_type == 'triangle_area':
        return generate_triangle_area()
    elif problem_type == 'perpendicular_vector':
        return generate_perpendicular_vector()
    elif problem_type == 'cross_product_properties':
        return generate_cross_product_properties()

# --- Answer Checking ---

def parse_vector_string(s):
    """Parses a string like '(x, y, z)' into a tuple of Fractions."""
    s = s.strip()
    if not s.startswith('(') or not s.endswith(')'):
        return None
    
    parts = s[1:-1].split(',')
    if len(parts) != 3:
        return None
    
    try:
        x = Fraction(parts[0].strip())
        y = Fraction(parts[1].strip())
        z = Fraction(parts[2].strip())
        return (x, y, z)
    except ValueError:
        return None

def parse_magnitude_string(s):
    """
    Parses a string representing a magnitude into (coeff, radicand) Fractions.
    Handles 'A', 'A/B', '\\sqrt{C}', 'A\\sqrt{C}', 'A/B\\sqrt{C}'.
    Normalizes user input to handle 'sqrt()' and '/' notations.
    """
    s = s.strip()
    
    # Try parsing as a simple number or fraction (e.g., "5", "3/2")
    # First, handle explicit fraction string like "3/2"
    match_frac_only = re.fullmatch(r"(-?\d+)\s*/\s*(-?\d+)", s)
    if match_frac_only:
        num = int(match_frac_only.group(1))
        den = int(match_frac_only.group(2))
        if den == 0: return None
        return (Fraction(num, den), 1) # Return as (coeff, radicand)

    # Then, try parsing as a simple number (integer or float to Fraction)
    try:
        return (Fraction(s), 1)
    except ValueError:
        pass

    # Handle LaTeX fraction syntax: \\frac{A}{B}
    match_latex_frac = re.fullmatch(r"\\frac\{(-?\d+)\}\{(-?\d+)\}", s)
    if match_latex_frac:
        num = int(match_latex_frac.group(1))
        den = int(match_latex_frac.group(2))
        if den == 0: return None
        return (Fraction(num, den), 1)

    # Normalize user input for square root notations (e.g., "3sqrt(3)" -> "3\\sqrt{3}")
    s_normalized = s.replace("sqrt(", r"\\sqrt{").replace(")", "}")
    
    # Case: A\\sqrt{B} or \\sqrt{B}
    match_sqrt = re.match(r"(\S*)\\sqrt\{(\d+)\}", s_normalized)
    if match_sqrt:
        coeff_str = match_sqrt.group(1).strip()
        radicand = int(match_sqrt.group(2))
        
        if not coeff_str: # Case: \\sqrt{B}
            coeff = Fraction(1)
        else: # Case: A\\sqrt{B} with A being integer or fraction
            # Try to parse A as a fraction or integer
            match_frac_coeff = re.fullmatch(r"(-?\d+)\s*/\s*(-?\d+)", coeff_str)
            match_latex_frac_coeff = re.fullmatch(r"\\frac\{(-?\d+)\}\{(-?\d+)\}", coeff_str)

            if match_frac_coeff:
                num = int(match_frac_coeff.group(1))
                den = int(match_frac_coeff.group(2))
                if den == 0: return None
                coeff = Fraction(num, den)
            elif match_latex_frac_coeff:
                num = int(match_latex_frac_coeff.group(1))
                den = int(match_latex_frac_coeff.group(2))
                if den == 0: return None
                coeff = Fraction(num, den)
            else:
                try: # Assume integer coefficient
                    coeff = Fraction(coeff_str)
                except ValueError:
                    return None
        return (coeff, radicand)

    return None # Unable to parse

def calculate_magnitude_value(parsed_mag):
    """Calculates the float value from (coeff, radicand) tuple for comparison."""
    if parsed_mag is None:
        return None
    coeff, radicand = parsed_mag
    if radicand < 0: return None # Invalid radicand
    if radicand == 0: return 0.0 # sqrt(0)
    return float(coeff * math.sqrt(radicand))

def vectors_equal(v1, v2):
    """Compares two parsed vector tuples (of Fractions) for equality."""
    if v1 is None or v2 is None:
        return False
    return v1[0] == v2[0] and v1[1] == v2[1] and v1[2] == v2[2]

def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct answer.
    Handles different formats for vectors, magnitudes, and multiple answers.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    
    # Check for problems with multiple vector answers ("或")
    if "或" in correct_answer:
        correct_parts = [p.strip() for p in correct_answer.split('或')]
        user_parts = [p.strip() for p in user_answer.split('或')]
        
        if len(correct_parts) == 2 and len(user_parts) == 2:
            uv1 = parse_vector_string(user_parts[0])
            uv2 = parse_vector_string(user_parts[1])
            cv1 = parse_vector_string(correct_parts[0])
            cv2 = parse_vector_string(correct_parts[1])
            
            # Check for both possible orderings of the two vectors
            if (vectors_equal(uv1, cv1) and vectors_equal(uv2, cv2)) or \
               (vectors_equal(uv1, cv2) and vectors_equal(uv2, cv1)):
                is_correct = True
            
    # Check for problems with two related vector results separated by '|'
    elif "|" in correct_answer:
        correct_parts = [p.strip() for p in correct_answer.split('|')]
        # User might use various separators, try splitting by common ones
        user_parts = [p.strip() for p in re.split(r'\||,|和|與|and', user_answer) if p.strip()]
        
        if len(correct_parts) == 2 and len(user_parts) == 2:
            uv1 = parse_vector_string(user_parts[0])
            uv2 = parse_vector_string(user_parts[1])
            cv1 = parse_vector_string(correct_parts[0])
            cv2 = parse_vector_string(correct_parts[1])
            
            # For properties like a x b and b x a, the order usually matters for user input.
            if vectors_equal(uv1, cv1) and vectors_equal(uv2, cv2):
                is_correct = True
        
    else: # Direct vector or magnitude answer
        parsed_user_vec = parse_vector_string(user_answer)
        parsed_correct_vec = parse_vector_string(correct_answer)
        
        if parsed_user_vec is not None and parsed_correct_vec is not None:
            # Both are vectors
            is_correct = vectors_equal(parsed_user_vec, parsed_correct_vec)
        else:
            # Try parsing as magnitude
            parsed_user_mag = parse_magnitude_string(user_answer)
            parsed_correct_mag = parse_magnitude_string(correct_answer)

            if parsed_user_mag is not None and parsed_correct_mag is not None:
                # Both are magnitudes, compare their float values
                user_val = calculate_magnitude_value(parsed_user_mag)
                correct_val = calculate_magnitude_value(parsed_correct_mag)
                
                if user_val is not None and correct_val is not None:
                    # Using a small epsilon for float comparison due to potential sqrt inaccuracies
                    is_correct = abs(user_val - correct_val) < 1e-9
    
    # Reformat correct_answer for feedback display, replacing internal delimiters with user-friendly ones
    display_correct_answer = correct_answer.replace(" | ", " 與 ")

    feedback = f"完全正確！答案是 ${display_correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${display_correct_answer}$"
    return {"correct": is_correct, "result": feedback, "next_question": True}