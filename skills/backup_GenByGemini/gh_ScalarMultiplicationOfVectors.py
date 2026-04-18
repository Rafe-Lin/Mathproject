import random
from fractions import Fraction
import math
import re

# Helper to generate a 2D vector
def _generate_2d_vector(min_val=-5, max_val=5, allow_zero=True):
    """Generates a 2D vector (x, y) with integer coordinates."""
    while True:
        x = random.randint(min_val, max_val)
        y = random.randint(min_val, max_val)
        if allow_zero or (x != 0 or y != 0):
            return (x, y)

# Helper to format a vector for display
def _format_vector(vec):
    """Formats a vector (x, y) as a string '(x,y)' for LaTeX display."""
    return f"({vec[0]}, {vec[1]})"

# Helper to format a Fraction as a string, possibly an integer if denominator is 1
def _format_fraction(frac):
    """Formats a Fraction object as a LaTeX string (e.g., '2', '-1/2', '\\frac{{1}}{{3}}')."""
    if frac.denominator == 1:
        return str(frac.numerator)
    # Using double braces {{}} for LaTeX \\frac command inside f-string
    return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"

# Helper to format a linear combination expression (e.g., "2u+3v", "-u", "5v")
def _format_linear_expression(coeff_map):
    """
    Formats a dictionary of variable-coefficient pairs into a human-readable linear expression string.
    Example: {"u": 2, "v": 3} -> "2u+3v"
             {"u": 1, "v": -1} -> "u-v"
             {"u": -1} -> "-u"
    """
    terms = []
    # Ensure consistent order (e.g., u then v, P then Q)
    sorted_vars = sorted(coeff_map.keys()) 

    for var in sorted_vars:
        coeff = coeff_map[var]
        if coeff == 0:
            continue
        
        term_str = ""
        if coeff == 1:
            term_str = var
        elif coeff == -1:
            term_str = f"-{var}"
        else:
            term_str = f"{coeff}{var}"
        
        # Add '+' for positive terms that are not the first term
        if terms and coeff > 0:
            terms.append(f"+{term_str}")
        else:
            terms.append(term_str)
            
    if not terms:
        return "0" # Represents the zero vector or zero scalar combination
    return "".join(terms)


def generate(level=1):
    """
    Generates a problem related to scalar multiplication of vectors.
    Problems can be:
    1. Coordinate operations (scalar multiplication + addition/subtraction, finding vector or magnitude).
    2. Parallelism condition (finding a scalar 't' for parallel vectors).
    3. Linear combination of abstract basis vectors.
    """
    problem_type = random.choice(['coordinate_ops', 'parallel_scalar', 'linear_combination'])
    
    if problem_type == 'coordinate_ops':
        return _generate_coordinate_ops_problem(level)
    elif problem_type == 'parallel_scalar':
        return _generate_parallel_scalar_problem(level)
    elif problem_type == 'linear_combination':
        return _generate_linear_combination_problem(level)

def _generate_coordinate_ops_problem(level):
    """
    Generates a problem involving scalar multiplication and vector addition/subtraction
    with vectors in coordinate form. Asks for the resulting vector, its magnitude, or both.
    """
    u = _generate_2d_vector(-5, 5, allow_zero=False) 
    v = _generate_2d_vector(-5, 5, allow_zero=False)

    # Generate scalar coefficients, ensuring at least one is non-zero
    while True:
        a = random.randint(1, 3) * random.choice([-1, 1])
        b = random.randint(1, 3) * random.choice([-1, 1])
        if a != 0 or b != 0:
            break
    
    # Calculate the resultant vector
    result_vec_x = a * u[0] + b * v[0]
    result_vec_y = a * u[1] + b * v[1]
    result_vec = (result_vec_x, result_vec_y)
    
    # Calculate magnitude
    magnitude_sq = result_vec_x**2 + result_vec_y**2
    magnitude = math.sqrt(magnitude_sq)

    question_option = random.choice(['vector', 'magnitude', 'both']) # What to ask for

    # Format the expression for the question text
    expression_str = _format_linear_expression({"u": a, "v": b})
    question_text = f"已知向量 $u={_format_vector(u)}$ 及 $v={_format_vector(v)}$。"
    
    # Determine the display string for magnitude in the solution (integer or sqrt form)
    display_mag_str = ""
    if magnitude_sq == int(magnitude_sq) and math.isclose(magnitude, round(magnitude)): # Check if it's a perfect square
        display_mag_str = str(int(magnitude))
    else:
        display_mag_str = f"\\sqrt{{{magnitude_sq}}}"

    # Format terms for solution detail with explicit signs for clarity (e.g., '+3(2,3)')
    a_term_sol = f"{a}{_format_vector(u)}" if a != 0 else ""
    b_term_sol = f"{b:+}{_format_vector(v)}" if b != 0 else "" # Use :+ to force sign
    
    sol_expression = ""
    if a_term_sol and b_term_sol:
        sol_expression = f"{a_term_sol} {b_term_sol}" # Concatenate with space, signs are explicit
    elif a_term_sol:
        sol_expression = a_term_sol
    elif b_term_sol:
        sol_expression = b_term_sol
    else:
        sol_expression = "0" # If somehow both coefficients are zero

    # Prepare detailed solution template
    detailed_answer_template = (
        f"${expression_str} = {sol_expression} = ({a*u[0]}, {a*u[1]}) {b:+}({b*v[0]}, {b*v[1]}) = {_format_vector(result_vec)}$<br>"
        f"$|{expression_str}| = \\sqrt{{{result_vec_x}^2 + {result_vec_y}^2}} = \\sqrt{{{magnitude_sq}}} = {display_mag_str}$"
    )
    
    # Construct final question text and correct answer based on question_option
    if question_option == 'vector':
        question_text += f"求向量 ${expression_str}$。"
        correct_answer_val = _format_vector(result_vec)
        detailed_answer = detailed_answer_template.split("<br>")[0] # Only vector part
    elif question_option == 'magnitude':
        question_text += f"求向量 $|{expression_str}|$ 的長度。"
        correct_answer_val = display_mag_str
        detailed_answer = detailed_answer_template.split("<br>")[1] # Only magnitude part
    else: # both
        question_text += f"求向量 ${expression_str}$ 及其長度。"
        correct_answer_val = f"{_format_vector(result_vec)},{display_mag_str}" # Expected format: (x,y),mag
        detailed_answer = detailed_answer_template # Both parts
        
    return {
        "question_text": question_text,
        "answer": correct_answer_val,
        "correct_answer": correct_answer_val,
        "solution_detail": detailed_answer
    }

def _generate_parallel_scalar_problem(level):
    """
    Generates a problem asking to find a scalar 't' such that (a+tb) is parallel to c.
    Uses the condition that for parallel vectors (x1, y1) and (x2, y2), x1*y2 - x2*y1 = 0.
    """
    a_vec = _generate_2d_vector(-5, 5)
    b_vec = _generate_2d_vector(-5, 5, allow_zero=False) # b cannot be zero for a+tb.
    c_vec = _generate_2d_vector(-5, 5, allow_zero=False) # c cannot be zero for parallelism.

    # Ensure b_vec and c_vec are not parallel to avoid division by zero or infinite solutions for t
    # Denominator for t is (bx*cy - by*cx)
    while b_vec[0] * c_vec[1] - b_vec[1] * c_vec[0] == 0:
        b_vec = _generate_2d_vector(-5, 5, allow_zero=False)
        c_vec = _generate_2d_vector(-5, 5, allow_zero=False)

    # Calculate t using the cross-product-like condition: (ax + t*bx)*cy - (ay + t*by)*cx = 0
    # t = (ay*cx - ax*cy) / (bx*cy - by*cx)
    numerator = Fraction(a_vec[1] * c_vec[0] - a_vec[0] * c_vec[1])
    denominator = Fraction(b_vec[0] * c_vec[1] - b_vec[1] * c_vec[0])
    
    t_val = numerator / denominator

    # Using unicode character for parallel symbol (escaped with double braces)
    question_text = (
        f"已知向量 $a={_format_vector(a_vec)}, b={_format_vector(b_vec)}, c={_format_vector(c_vec)}$"
        f"，且實數 $t$ 滿足 $(a+tb) \\unicode{{x2225}} c$，求 $t$ 的值。"
    )
    correct_answer_val = _format_fraction(t_val)
    
    detail_str = (
        f"因為 $(a+tb) \\unicode{{x2225}} c$，所以存在實數 $k$ 使得 $a+tb = kc$。<br>"
        f"令 $a+tb = ({a_vec[0]}+t{b_vec[0]}, {a_vec[1]}+t{b_vec[1]})$。<br>"
        f"由平行條件可知，$(a+tb)$ 與 $c$ 的方向相同或相反，"
        f"故其分量滿足 $x_1 y_2 - x_2 y_1 = 0$ (即二維向量的「外積」為零)。<br>"
        f"即 $({a_vec[0]}+t{b_vec[0]})({c_vec[1]}) - (({a_vec[1]})+t({b_vec[1]}))({c_vec[0]}) = 0$<br>"
        f"${a_vec[0]*c_vec[1]} + t({b_vec[0]*c_vec[1]}) - {a_vec[1]*c_vec[0]} - t({b_vec[1]*c_vec[0]}) = 0$<br>"
        f"$t({b_vec[0]*c_vec[1] - b_vec[1]*c_vec[0]}) = {a_vec[1]*c_vec[0] - a_vec[0]*c_vec[1]}$<br>"
        f"$t({denominator.numerator}) = {numerator.numerator}$<br>"
        f"解得 $t = {_format_fraction(t_val)}$。"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer_val,
        "correct_answer": correct_answer_val,
        "solution_detail": detail_str
    }

def _generate_linear_combination_problem(level):
    """
    Generates a problem where two vectors P and Q are expressed as linear combinations
    of basis vectors u and v. The task is to express a new vector (sP + tQ) in terms of u and v.
    """
    # Coefficients for P and Q in terms of u and v
    c1 = random.randint(1, 4) * random.choice([-1, 1])
    d1 = random.randint(1, 4) * random.choice([-1, 1])
    c2 = random.randint(1, 4) * random.choice([-1, 1])
    d2 = random.randint(1, 4) * random.choice([-1, 1])

    # Scalars for the combination sP + tQ
    s = random.randint(1, 3) * random.choice([-1, 1])
    t = random.randint(1, 3) * random.choice([-1, 1])

    # Calculate the resultant coefficients for u and v
    coeff_u = s * c1 + t * c2
    coeff_v = s * d1 + t * d2
    
    # Format P and Q expressions for the question text
    p_expr = _format_linear_expression({"u": c1, "v": d1})
    q_expr = _format_linear_expression({"u": c2, "v": d2})
    
    # Format the combined expression (sP+tQ) for the question text
    combined_expr_q_text = _format_linear_expression({"P": s, "Q": t}) 
        
    question_text = (
        f"已知向量 $P = {p_expr}$ 及 $Q = {q_expr}$。<br>"
        f"試用 $u$ 與 $v$ 表示下列向量： ${combined_expr_q_text}$。"
    )
    
    # The correct answer is the pair of coefficients (coeff_u, coeff_v)
    correct_answer_val = f"({coeff_u},{coeff_v})" 
    
    # Prepare detailed solution with explicit signs for coefficients
    detail_str = (
        f"${combined_expr_q_text} = {s}({p_expr}) {t:+}({q_expr})$<br>" # Use {t:+} for explicit sign
        f"$= {s}({c1}u {d1:+}v) {t:+}({c2}u {d2:+}v)$<br>" # Use {d1:+}, {d2:+} for explicit signs of v terms
        f"$= ({s*c1})u {s*d1:+}v {t*c2:+}u {t*d2:+}v$<br>" # Expand terms
        f"$= ({s*c1} + {t*c2})u + ({s*d1} + {t*d2})v$<br>" # Group terms
        f"$= ({coeff_u})u + ({coeff_v})v$"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer_val,
        "correct_answer": correct_answer_val,
        "solution_detail": detail_str
    }

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct for scalar multiplication of vectors.
    Handles various answer formats: scalar (fraction/integer), vector (x,y),
    magnitude (N or sqrt{N}), and combined (vector,magnitude).
    """
    user_answer = user_answer.strip().replace(' ', '')
    correct_answer = correct_answer.strip().replace(' ', '')

    is_correct = False
    result_text = ""

    # Helper to parse fractions (e.g. "1/2", "-3", "-\\frac{1}{2}")
    def parse_fraction_string(s):
        s = s.replace(r'\\frac{', '').replace('{', '').replace('}', '/')
        if s.startswith('-/') and len(s) > 2: # Handle latex negative fraction like -\\frac{1}{2} -> -/1/2
            s = '-' + s[2:]
        try:
            if '/' in s:
                num, den = map(int, s.split('/'))
                return Fraction(num, den)
            return Fraction(int(s))
        except (ValueError, ZeroDivisionError):
            return None

    # Helper to parse vector string "(x,y)"
    def parse_vector_string(s):
        # Regex to match (integer,integer) including negative numbers
        match = re.fullmatch(r'\(([-+]?\d+),([-+]?\d+)\)', s)
        if match:
            try:
                x = int(match.group(1))
                y = int(match.group(2))
                return (x, y)
            except ValueError:
                pass
        return None

    # Helper to parse magnitude string "N" or "\\sqrt{N}"
    def parse_magnitude_string_for_check(s):
        # Regex to match \\sqrt{integer}
        match_sqrt = re.fullmatch(r'\\sqrt\{(\d+)\}', s)
        if match_sqrt:
            try:
                radicand = int(match_sqrt.group(1))
                return math.sqrt(radicand)
            except ValueError:
                pass
        
        # Regex to match integer
        match_int = re.fullmatch(r'([-+]?\d+)', s)
        if match_int:
            try:
                val = int(match_int.group(1))
                return float(val) # Convert to float for comparison with sqrt results
            except ValueError:
                pass
        return None

    # --- Attempt to match different answer formats ---

    # 1. Scalar answer (e.g., 't' value from parallel_scalar or general scalar)
    user_frac = parse_fraction_string(user_answer)
    correct_frac = parse_fraction_string(correct_answer)
    if user_frac is not None and correct_frac is not None:
        if user_frac == correct_frac:
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            # If fractions don't match, try floating point comparison as a fallback
            try:
                user_float = float(user_frac)
                corr_float = float(correct_frac)
                if math.isclose(user_float, corr_float):
                    is_correct = True
                    result_text = f"完全正確！答案是 ${correct_answer}$。"
                else:
                    result_text = f"答案不正確。您的答案是 ${_format_fraction(user_frac)}$，正確答案應為：${correct_answer}$"
            except (ValueError, ZeroDivisionError): # Catch if conversion to float fails
                result_text = f"答案不正確。您的答案是 ${_format_fraction(user_frac)}$，正確答案應為：${correct_answer}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # 2. Vector answer (x,y) or (coeff_u, coeff_v)
    user_vec = parse_vector_string(user_answer)
    correct_vec = parse_vector_string(correct_answer)
    if user_vec is not None and correct_vec is not None:
        # Using math.isclose for float comparison robustness
        if math.isclose(user_vec[0], correct_vec[0]) and math.isclose(user_vec[1], correct_vec[1]):
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。您的答案是 ${_format_vector(user_vec)}$，正確答案應為：${correct_answer}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # 3. Magnitude answer (N or sqrt{N})
    user_mag = parse_magnitude_string_for_check(user_answer)
    correct_mag = parse_magnitude_string_for_check(correct_answer)
    if user_mag is not None and correct_mag is not None:
        if math.isclose(user_mag, correct_mag):
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            # Cannot use _format_magnitude for user_answer as it's not a direct parser
            result_text = f"答案不正確。您的答案是 ${user_answer}$，正確答案應為：${correct_answer}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # 4. Combined answer (vector,magnitude) - e.g., "(10,3),\\sqrt{109}"
    if ',' in correct_answer:
        correct_parts = correct_answer.split(',')
        if len(correct_parts) == 2:
            corr_vec_str, corr_mag_str = correct_parts[0], correct_parts[1]
            correct_vec_val = parse_vector_string(corr_vec_str)
            correct_mag_val = parse_magnitude_string_for_check(corr_mag_str)

            if correct_vec_val is not None and correct_mag_val is not None:
                user_parts = user_answer.split(',')
                if len(user_parts) == 2:
                    user_vec_str, user_mag_str = user_parts[0], user_parts[1]
                    user_vec_val = parse_vector_string(user_vec_str)
                    user_mag_val = parse_magnitude_string_for_check(user_mag_str)

                    if (user_vec_val is not None and user_mag_val is not None and
                        math.isclose(user_vec_val[0], correct_vec_val[0]) and
                        math.isclose(user_vec_val[1], correct_vec_val[1]) and
                        math.isclose(user_mag_val, correct_mag_val)):
                        is_correct = True
                        result_text = f"完全正確！答案是 ${correct_answer}$。"
                    else:
                        result_text = f"答案不正確。您的答案是 ${user_answer}$，正確答案應為：${correct_answer}$"
                else: # User provided something but not in (x,y),mag format
                    result_text = f"答案不正確。您的答案是 ${user_answer}$，正確答案應為：${correct_answer}$"
                return {"correct": is_correct, "result": result_text, "next_question": True}

    # If control reaches here, it means none of the parsing methods worked or matched the correct answer type.
    if not is_correct: 
        result_text = f"答案不正確。您的答案是 ${user_answer}$，正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}