import random
from fractions import Fraction

# Helper function to evaluate a polynomial
def evaluate_polynomial(coeffs, x_val):
    """
    Evaluates a polynomial given its coefficients and an x-value.
    coeffs: list [c0, c1, c2, ..., cn] for c_n*x^n + ... + c1*x + c0
    x_val: the value to substitute for x (can be int or Fraction)
    """
    result = Fraction(0)
    if isinstance(x_val, (int, float)):
        x_val = Fraction(x_val)

    for i, c in enumerate(coeffs):
        coeff_frac = Fraction(c)
        result += coeff_frac * (x_val ** i)
    return result

# Helper function to format a polynomial into a LaTeX string
def format_polynomial(coeffs, var_name='x'):
    """
    Formats polynomial coefficients into a LaTeX string (e.g., "2x^{{3}} - x^{{2}} - 2x + 1").
    coeffs: list [c0, c1, c2, ..., cn]
    """
    terms = []
    degree = len(coeffs) - 1
    
    for i in range(degree, -1, -1):
        coeff = coeffs[i]
        
        if isinstance(coeff, Fraction):
            if coeff.denominator == 1:
                coeff = int(coeff)
            # else: keep as Fraction
        
        if coeff == 0:
            continue

        abs_coeff = abs(coeff)
        
        coeff_str = ""
        if isinstance(coeff, Fraction) and coeff.denominator != 1:
            coeff_str = f"\\frac{{{abs_coeff.numerator}}}{{{abs_coeff.denominator}}}"
        elif abs_coeff == 1 and i != 0:
            coeff_str = "" # Don't print '1' for '1x' or '1x^{{2}}'
        else:
            coeff_str = str(abs_coeff)

        term_str = ""
        if i == 0: # Constant term
            term_str = coeff_str
        elif i == 1: # x term
            term_str = f"{coeff_str}{var_name}"
        else: # x^n term
            term_str = f"{coeff_str}{var_name}^{{ {i} }}"

        # Add sign
        if not terms: # First term (highest degree)
            if coeff < 0:
                terms.append(f"-{term_str}")
            else:
                terms.append(term_str)
        else:
            if coeff < 0:
                terms.append(f" - {term_str}")
            else:
                terms.append(f" + {term_str}")

    if not terms:
        return "0"
    
    formatted_poly = "".join(terms).strip()
    if formatted_poly.startswith("+ "): # Remove leading '+ ' if it exists
        formatted_poly = formatted_poly[2:]
        
    return formatted_poly

# Helper function to format a factor (ax-b) into a LaTeX string
def format_factor(num, const_neg, var_name='x'):
    """
    Formats a factor given its (num*x - b) representation where const_neg = -b.
    e.g., (1, -r) -> x-r
    (a, -b) -> ax-b
    num: coefficient of x
    const_neg: negative of the constant term (e.g., for x-3, const_neg=-3 meaning b=3)
    """
    b_val = -const_neg # b in ax-b
    
    if num == 1:
        if b_val > 0:
            return f"{var_name} - {b_val}"
        elif b_val < 0:
            return f"{var_name} + {-b_val}"
        else: # b_val == 0
            return var_name
    elif num == -1:
        if b_val > 0:
            return f"-({var_name} - {b_val})"
        elif b_val < 0:
            return f"-({var_name} + {-b_val})"
        else:
            return f"-{var_name}"
    else: # num is not 1 or -1
        if b_val > 0:
            return f"{num}{var_name} - {b_val}"
        elif b_val < 0:
            return f"{num}{var_name} + {-b_val}"
        else: # b_val == 0
            return f"{num}{var_name}"

def generate_cubic_polynomial_with_roots():
    """
    Generates a cubic polynomial f(x) = L * (x-r1)(x-r2)(x-r3)
    and returns its coefficients, roots, and leading coefficient.
    """
    roots = []
    # Ensure distinct integer roots
    while len(roots) < 3:
        r = random.randint(-3, 3)
        if r not in roots:
            roots.append(r)

    leading_coeff = random.choice([1, 2, 3, -1, -2, -3]) # Leading coefficient for diversity

    # Coefficients for L * (x-r1)(x-r2)(x-r3)
    # L * (x^3 - (r1+r2+r3)x^2 + (r1r2+r1r3+r2r3)x - r1r2r3)
    r1, r2, r3 = roots[0], roots[1], roots[2]

    c3 = leading_coeff
    c2 = -leading_coeff * (r1 + r2 + r3)
    c1 = leading_coeff * (r1*r2 + r1*r3 + r2*r3)
    c0 = -leading_coeff * (r1*r2*r3)

    coeffs = [c0, c1, c2, c3] # [constant, x, x^2, x^3]
    return coeffs, roots, leading_coeff

def generate_factor_options(roots, leading_coeff):
    """
    Generates a list of potential factors (x-a or ax-b) for a polynomial.
    """
    options = []
    actual_roots_frac = [Fraction(r) for r in roots]

    # Include actual factors of form (x-r)
    for r in roots:
        options.append((1, -r)) # Represents (x-r)

    # Include actual factors of form (ax-b) where b/a is a root
    if leading_coeff != 1 and leading_coeff != -1:
        for r in roots:
            options.append((leading_coeff, -leading_coeff * r)) # Represents (L*x - L*r)
            # Add another scaled factor, e.g., (2x - 2r)
            if random.random() < 0.5:
                # Try a factor of leading_coeff
                factors_of_L = [i for i in range(1, abs(leading_coeff) + 1) if abs(leading_coeff) % i == 0]
                if len(factors_of_L) > 1:
                    a_val = random.choice([f for f in factors_of_L if f != 1])
                    if random.random() < 0.5: a_val = -a_val
                    options.append((a_val, -a_val * r))


    # Add some non-factors (x-s or ax-b)
    non_roots_candidates = list(range(-5, 6)) # Wider range for non-roots
    random.shuffle(non_roots_candidates)
    
    non_factors_count = 0
    for val in non_roots_candidates:
        test_frac = Fraction(val)
        if test_frac not in actual_roots_frac:
            # Simple non-factor (x-val)
            options.append((1, -val))
            non_factors_count += 1
            if non_factors_count >= 2: break # Add a few non-factors

    # Add a fractional non-root factor
    if random.random() < 0.7:
        num_non_root = random.randint(1, 4)
        den_non_root = random.randint(2, 4)
        if random.random() < 0.5: num_non_root = -num_non_root
        
        non_root_frac = Fraction(num_non_root, den_non_root)
        if non_root_frac not in actual_roots_frac:
            options.append((den_non_root, -num_non_root)) # (den_non_root * x - num_non_root)

    # Ensure uniqueness and shuffle for options list
    unique_options = []
    seen_normalized_roots = set()
    for num, const_neg in options:
        # Normalize (num*x + const_neg) to root -const_neg/num for comparison
        normalized_root = Fraction(-const_neg, num)
        if normalized_root not in seen_normalized_roots:
            seen_normalized_roots.add(normalized_root)
            unique_options.append((num, const_neg))
    
    random.shuffle(unique_options)
    
    # Limit to 4-6 options
    return unique_options[:random.randint(4, 6)]

def generate_check_factors_problem():
    """
    Generates a problem asking to identify factors of a given polynomial.
    """
    coeffs, roots, leading_coeff = generate_cubic_polynomial_with_roots()
    poly_str = format_polynomial(coeffs)

    possible_factors_raw = generate_factor_options(roots, leading_coeff)
    
    question_text = f"選出 $f(x) = {poly_str}$ 的因式。<br>"
    
    options_display = []
    correct_option_labels = []
    
    for i, (num, const_neg) in enumerate(possible_factors_raw):
        label = chr(ord('A') + i)
        factor_str = format_factor(num, const_neg)
        options_display.append(f"(${label}$) ${factor_str}$")
        
        test_val = Fraction(-const_neg, num)
        if evaluate_polynomial(coeffs, test_val) == 0:
            correct_option_labels.append(label)

    # Ensure at least one correct answer
    if not correct_option_labels and possible_factors_raw:
        r_actual = roots[0]
        guaranteed_factor_tuple = (1, -r_actual)
        
        normalized_guaranteed_root = Fraction(-guaranteed_factor_tuple[1], guaranteed_factor_tuple[0])
        seen_normalized_roots_in_options = set(Fraction(-cn, n) for n, cn in possible_factors_raw)
        
        if normalized_guaranteed_root not in seen_normalized_roots_in_options:
            label = chr(ord('A') + len(options_display))
            factor_str = format_factor(guaranteed_factor_tuple[0], guaranteed_factor_tuple[1])
            options_display.append(f"(${label}$) ${factor_str}$")
            correct_option_labels.append(label)

    question_text += "<br>".join(options_display)
    correct_answer = ",".join(sorted(correct_option_labels))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_coeff_problem():
    """
    Generates a problem to find an unknown coefficient 'a' in f(x)
    given that a specific linear expression is a factor.
    """
    # Choose target root for the known factor (cannot be 0)
    numerator = random.randint(-4, 4)
    denominator = random.choice([1, 2, 3])
    while numerator == 0: numerator = random.choice([1, -1]) # Ensure r_factor != 0
    r_factor = Fraction(numerator, denominator)

    # Determine the factor string (qx-p) from r_factor = p/q
    factor_str = ""
    if r_factor.denominator == 1: # Integer root (x-p)
        if r_factor.numerator > 0: factor_str = f"x - {r_factor.numerator}"
        else: factor_str = f"x + {-r_factor.numerator}"
    else: # Fractional root (qx-p)
        if r_factor.numerator > 0: factor_str = f"{r_factor.denominator}x - {r_factor.numerator}"
        else: factor_str = f"{r_factor.denominator}x + {-r_factor.numerator}"

    # Choose an index for the coefficient 'a' (1 for x, 2 for x^2)
    unknown_idx = random.choice([1, 2]) 

    # Generate other coefficients for f(x) = c3*x^3 + c2*x^2 + c1*x + c0
    coeffs_known = [0] * 4 # [c0, c1, c2, c3]
    coeffs_known[0] = random.randint(-6, 6) # c0
    coeffs_known[3] = random.choice([1, 2, 3]) # c3 (leading coeff)
    
    for i in [1, 2]: # Populate other coeffs, skipping the unknown_idx
        if i != unknown_idx:
            coeffs_known[i] = random.randint(-6, 6)
    
    # Calculate the value of 'a' using f(r_factor) = 0
    # a * (r_factor ** unknown_idx) + sum_of_known_terms = 0
    sum_known_terms = Fraction(0)
    for i, c_val in enumerate(coeffs_known):
        if i != unknown_idx:
            sum_known_terms += Fraction(c_val) * (r_factor ** i)
    
    correct_a = -sum_known_terms / (r_factor ** unknown_idx)

    # Build the polynomial string for f(x) with 'a'
    f_poly_parts = []
    degree = 3
    
    for i in range(degree, -1, -1):
        if i == unknown_idx:
            term_str = "a"
            if i == 1: term_str += "x"
            elif i > 1: term_str += f"x^{{ {i} }}"
            
            if not f_poly_parts:
                f_poly_parts.append(term_str)
            else:
                f_poly_parts.append(f" + {term_str}")
        else:
            coeff = coeffs_known[i]
            if coeff == 0:
                continue

            abs_coeff = abs(coeff)
            coeff_val_str = ""
            if isinstance(coeff, Fraction) and coeff.denominator != 1:
                coeff_val_str = f"\\frac{{{abs_coeff.numerator}}}{{{abs_coeff.denominator}}}"
            elif abs_coeff != 1 or i == 0:
                coeff_val_str = str(abs_coeff)
            
            term_suffix = ""
            if i == 1: term_suffix = "x"
            elif i > 1: term_suffix = f"x^{{ {i} }}"
            
            current_term_part = f"{coeff_val_str}{term_suffix}"
            
            if not f_poly_parts: # First term
                if coeff < 0:
                    f_poly_parts.append(f"-{current_term_part}")
                else:
                    f_poly_parts.append(current_term_part)
            else:
                if coeff < 0:
                    f_poly_parts.append(f" - {current_term_part}")
                else:
                    f_poly_parts.append(f" + {current_term_part}")
    
    if not f_poly_parts: # Fallback if polynomial turns out to be just '0' which should not happen
        f_poly_str = f"a{'' if unknown_idx == 0 else 'x' if unknown_idx == 1 else f'x^{{{unknown_idx}}}'}"
    else:
        f_poly_str = "".join(f_poly_parts).strip()
        if f_poly_str.startswith("+ "): f_poly_str = f_poly_str[2:]

    question_text = f"已知 ${factor_str}$ 是 $f(x) = {f_poly_str}$ 的因式，求實數 $a$ 的值。"
    
    answer_str = str(correct_a.numerator) if correct_a.denominator == 1 else f"\\frac{{{correct_a.numerator}}}{{{correct_a.denominator}}}"

    return {
        "question_text": question_text,
        "answer": answer_str,
        "correct_answer": answer_str
    }

def generate_construct_poly_problem():
    """
    Generates a problem to construct a cubic polynomial f(x)
    given two roots and two other points.
    """
    # 1. Generate two distinct integer roots r1, r2
    roots = []
    while len(roots) < 2:
        r = random.randint(-3, 3)
        if r != 0 and r not in roots:
            roots.append(r)
    r1, r2 = roots[0], roots[1]

    # 2. Generate a_coeff and b_coeff for (ax+b) term
    a_coeff = random.choice([1, 2, -1, -2])
    b_coeff = random.randint(-5, 5)
    
    # Ensure -b_coeff/a_coeff is not r1 or r2
    if b_coeff != 0: # Avoid division by zero when calculating Fraction
        while Fraction(-b_coeff, a_coeff) in [Fraction(r1), Fraction(r2)]:
            b_coeff = random.randint(-5, 5)

    # 3. Construct f(x) = (x-r1)(x-r2)(a_coeff*x + b_coeff)
    # Expand (x-r1)(x-r2) = x^2 - (r1+r2)x + r1r2
    poly_quad_coeffs = [r1*r2, -(r1+r2), 1] # [c0, c1, c2]
    
    # (a_coeff*x + b_coeff)
    poly_linear_coeffs = [b_coeff, a_coeff] # [c0, c1]

    # Multiply polynomial coefficients to get final cubic coefficients
    q0, q1, q2 = poly_quad_coeffs
    l0, l1 = poly_linear_coeffs

    c0_final = q0 * l0
    c1_final = q0 * l1 + q1 * l0
    c2_final = q1 * l1 + q2 * l0
    c3_final = q2 * l1

    final_coeffs = [c0_final, c1_final, c2_final, c3_final]

    # 5. Generate two points (x_p1, y_p1) and (x_p2, y_p2)
    potential_x_coords = []
    for i in range(-5, 6):
        # Exclude known roots and the root of (ax+b) to ensure distinctness
        if i not in roots and (a_coeff == 0 or Fraction(i) != Fraction(-b_coeff, a_coeff)):
            potential_x_coords.append(i)
    
    random.shuffle(potential_x_coords)
    
    # Ensure enough distinct points are available; fallback if necessary
    if len(potential_x_coords) < 2:
        # Fallback: extend range for potential x_coords
        potential_x_coords = list(set(list(range(-7, 8)) + potential_x_coords))
        potential_x_coords = [x for x in potential_x_coords if x not in roots and (a_coeff == 0 or Fraction(x) != Fraction(-b_coeff, a_coeff))]
        random.shuffle(potential_x_coords)

    # If still not enough, it implies highly constrained roots/linear factor.
    # Take distinct points that are not roots.
    
    # Ensure there are at least two distinct points after filtering
    if len(potential_x_coords) < 2:
         # If all else fails, pick distinct integers and hope for the best.
         potential_x_coords = [r1 + 1, r2 + 2, r1 - 1, r2 - 2]
         potential_x_coords = list(set([x for x in potential_x_coords if x != r1 and x != r2]))
         random.shuffle(potential_x_coords)
         potential_x_coords = potential_x_coords[:2]
         if len(potential_x_coords) < 2:
            potential_x_coords = [1, 2] # Last resort
            if 1 in roots: potential_x_coords[0] = 3
            if 2 in roots: potential_x_coords[1] = 4
            if potential_x_coords[0] == potential_x_coords[1]: potential_x_coords[1] += 1
    
    x_p1 = potential_x_coords[0]
    x_p2 = potential_x_coords[1]
    
    y_p1 = evaluate_polynomial(final_coeffs, x_p1)
    y_p2 = evaluate_polynomial(final_coeffs, x_p2)
    
    r1_str = str(r1)
    r2_str = str(r2)
    x_p1_str = str(x_p1)
    y_p1_str = str(y_p1.numerator) if y_p1.denominator == 1 else f"\\frac{{{y_p1.numerator}}}{{{y_p1.denominator}}}"
    x_p2_str = str(x_p2)
    y_p2_str = str(y_p2.numerator) if y_p2.denominator == 1 else f"\\frac{{{y_p2.numerator}}}{{{y_p2.denominator}}}"

    question_text = f"已知三次多項式 $f(x)$ 滿足 $f({{{r1_str}}})=f({{{r2_str}}})=0$ 與 $f({{{x_p1_str}}})={{{y_p1_str}}}$, $f({{{x_p2_str}}})={{{y_p2_str}}}$，求 $f(x)$ 。"
    
    correct_answer_poly_str = format_polynomial(final_coeffs)
    
    return {
        "question_text": question_text,
        "answer": correct_answer_poly_str,
        "correct_answer": correct_answer_poly_str
    }

def generate(level=1):
    """
    Generates Factor Theorem related problems.
    Problems include:
    1. Checking which expressions are factors of a given polynomial.
    2. Finding an unknown coefficient in a polynomial given a factor.
    3. Constructing a polynomial given some roots and points.
    """
    problem_type = random.choice([
        'check_factors',
        'find_coeff_from_factor',
        'construct_poly_from_roots_and_point'
    ])

    if problem_type == 'check_factors':
        return generate_check_factors_problem()
    elif problem_type == 'find_coeff_from_factor':
        return generate_find_coeff_problem()
    elif problem_type == 'construct_poly_from_roots_and_point':
        return generate_construct_poly_problem()
    
def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    Handles numeric answers (integers, fractions, decimals) and comma-separated lists.
    """
    user_answer_stripped = user_answer.strip()
    correct_answer_stripped = correct_answer.strip()

    is_correct = False

    # 1. Direct string comparison (for polynomial answers or single choice)
    if user_answer_stripped == correct_answer_stripped:
        is_correct = True
    else:
        # 2. Compare as lists for factor selection (case-insensitive, order-agnostic)
        # E.g., user "A,C", correct "C,A" -> True
        user_parts = sorted([p.strip().upper() for p in user_answer_stripped.split(',') if p.strip()])
        correct_parts = sorted([p.strip().upper() for p in correct_answer_stripped.split(',') if p.strip()])
        if user_parts == correct_parts:
            is_correct = True
        else:
            # 3. Compare as numbers (for finding 'a' coefficient)
            try:
                # Convert LaTeX fraction format \\frac{N}{D} to N/D for Fraction conversion
                parsed_correct_answer = correct_answer_stripped.replace('\\frac{', '').replace('{', '').replace('}', '/')
                
                user_frac = Fraction(user_answer_stripped)
                correct_frac = Fraction(parsed_correct_answer)
                if user_frac == correct_frac:
                    is_correct = True
            except ValueError:
                pass # Not a simple number, continue.

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}