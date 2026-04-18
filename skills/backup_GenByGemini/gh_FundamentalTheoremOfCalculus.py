import random
from fractions import Fraction

# Helper function to format a polynomial string for LaTeX display
def format_polynomial_latex(coeffs_exps, var='x'):
    """
    Formats a list of (coefficient, exponent) tuples into a LaTeX polynomial string.
    Terms are sorted by exponent in descending order.
    Example: [(2, 3), (-1, 1), (5, 0)] -> "2x^{3} - x + 5"
    """
    terms = []
    # Sort by exponent in descending order
    sorted_terms = sorted(coeffs_exps, key=lambda x: x[1], reverse=True)

    for coeff, exp in sorted_terms:
        if coeff == 0:
            continue
        
        abs_coeff = abs(coeff)
        term_str = ""

        # Determine sign and coefficient prefix
        if coeff > 0:
            sign = "+"
        else:
            sign = "-"
        
        # Format the term itself
        if exp == 0: # Constant term
            term_str = f"{abs_coeff}"
        elif exp == 1: # Linear term
            if abs_coeff == 1:
                term_str = f"{var}"
            else:
                term_str = f"{abs_coeff}{var}"
        else: # Higher power term
            if abs_coeff == 1:
                term_str = f"{var}^{{{exp}}}"
            else:
                term_str = f"{abs_coeff}{var}^{{{exp}}}"
        
        terms.append(f"{sign}{term_str}")

    if not terms:
        return "0"

    # Join terms and handle the leading sign
    formatted_poly = "".join(terms)
    if formatted_poly.startswith("+"):
        return formatted_poly[1:] # Remove leading '+'
    return formatted_poly

# Helper function to evaluate a polynomial at a given value
def evaluate_polynomial(coeffs_exps, x_val):
    """
    Evaluates a polynomial represented by (coefficient, exponent) tuples at x_val.
    Coefficients can be Fractions.
    """
    result = Fraction(0)
    x_val_frac = Fraction(x_val)
    for coeff, exp in coeffs_exps:
        result += Fraction(coeff) * (x_val_frac**exp)
    return result

def generate_ftc2_eval_problem():
    """
    Generates a problem to evaluate a definite integral using FTC Part 2.
    """
    # Generate function f(x) = ax^n + bx^m + c
    num_terms = random.choice([1, 2, 3])
    f_coeffs_exps = []
    
    # Ensure at least one non-zero term, and unique exponents
    chosen_exps = set()
    while len(f_coeffs_exps) < num_terms:
        exp = random.randint(0, 3) # Exponents 0, 1, 2, 3
        if exp in chosen_exps:
            continue
        
        coeff = random.randint(-4, 4)
        if coeff == 0: # Reroll if coefficient is zero, to ensure `num_terms` unique non-zero terms
            continue
        
        f_coeffs_exps.append((coeff, exp))
        chosen_exps.add(exp)

    # Generate limits
    lower_limit = random.randint(-2, 2)
    # Ensure upper limit is distinct and typically greater than lower limit for standard presentation
    upper_limit = random.randint(lower_limit + 1, lower_limit + 5) 

    # Calculate antiderivative F(x)
    F_coeffs_exps = []
    for coeff, exp in f_coeffs_exps:
        # Antiderivative of c*x^n is (c/(n+1))*x^(n+1)
        F_coeffs_exps.append((Fraction(coeff, exp + 1), exp + 1))
    
    # Evaluate F(upper_limit) - F(lower_limit)
    F_upper = evaluate_polynomial(F_coeffs_exps, upper_limit)
    F_lower = evaluate_polynomial(F_coeffs_exps, lower_limit)
    correct_val = F_upper - F_lower

    # Format function f(x) for display
    f_x_str = format_polynomial_latex(f_coeffs_exps, var='x')

    # Format the integral question
    question_text = f"計算定積分：<br>$ \\int_{{{lower_limit}}}^{{{upper_limit}}} ({f_x_str}) \\, dx $"
    correct_answer = str(correct_val) # Fractions automatically stringify nicely (e.g., "1/2", "5")

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_property_linearity_problem():
    """
    Generates a problem based on the linearity property of definite integrals.
    """
    lower_limit = random.randint(-3, 1)
    upper_limit = random.randint(lower_limit + 1, lower_limit + 4)
    
    # Values for the known integrals of f(x) and g(x)
    val_f = random.randint(-10, 10)
    val_g = random.randint(-10, 10)
    
    # Coefficients for the linear combination c*f(x) + k*g(x)
    # Ensure coefficients are non-zero for meaningful combination
    coeff_f = random.choice([-2, -1, 1, 2, 3])
    coeff_g = random.choice([-2, -1, 1, 2, 3])
    
    # Construct the combined function string for display, e.g., "3f(x) - 2g(x)"
    combined_f_g_str = ""
    # Term for f(x)
    if coeff_f == 1:
        combined_f_g_str += r"f(x)"
    elif coeff_f == -1:
        combined_f_g_str += r"-f(x)"
    else:
        combined_f_g_str += f"{coeff_f}f(x)"
    
    # Term for g(x)
    if coeff_g > 0:
        if coeff_g == 1:
            combined_f_g_str += r" + g(x)"
        else:
            combined_f_g_str += f" + {coeff_g}g(x)"
    elif coeff_g < 0:
        if coeff_g == -1:
            combined_f_g_str += r" - g(x)"
        else:
            combined_f_g_str += f" - {abs(coeff_g)}g(x)"

    question_text = (
        f"已知 $\\int_{{{lower_limit}}}^{{{upper_limit}}} f(x) \\, dx = {val_f}$ 且 $\\int_{{{lower_limit}}}^{{{upper_limit}}} g(x) \\, dx = {val_g}$。"
        f"<br>試計算 $\\int_{{{lower_limit}}}^{{{upper_limit}}} ({combined_f_g_str}) \\, dx$。"
    )
    
    correct_val = coeff_f * val_f + coeff_g * val_g
    correct_answer = str(correct_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_property_additivity_problem():
    """
    Generates a problem based on the interval additivity property of definite integrals.
    """
    # Generate three distinct ordered points: p1 < p2 < p3
    points = sorted(random.sample(range(-5, 6), 3)) # e.g., [-2, 1, 3]
    p1, p2, p3 = points[0], points[1], points[2]

    # Generate values for the two 'base' integrals
    val_p1p2 = random.randint(-10, 10)
    val_p2p3 = random.randint(-10, 10)
    val_p1p3 = val_p1p2 + val_p2p3 # The sum integral

    # Define the three integral expressions and their values
    integrals_info = [
        ("p1p2", f"\\int_{{{p1}}}^{{{p2}}} f(x) \\, dx", val_p1p2),
        ("p2p3", f"\\int_{{{p2}}}^{{{p3}}} f(x) \\, dx", val_p2p3),
        ("p1p3", f"\\int_{{{p1}}}^{{{p3}}} f(x) \\, dx", val_p1p3)
    ]

    # Randomly choose which integral to ask for (the target)
    question_target_idx = random.randint(0, 2)
    
    # The other two integrals are given
    given_integrals_info = [integrals_info[i] for i in range(3) if i != question_target_idx]
    
    # Formulate the "Known" part of the question
    intro_text_parts = []
    for _, expr, val in given_integrals_info:
        intro_text_parts.append(f"${expr} = {val}$")
    
    intro_text = f"已知 {intro_text_parts[0]} 且 {intro_text_parts[1]}。"
    
    # Formulate the "Calculate" part of the question
    question_integral_expr = integrals_info[question_target_idx][1]
    correct_val = integrals_info[question_target_idx][2]

    question_text = f"{intro_text}<br>試計算 ${question_integral_expr}$。"
    correct_answer = str(correct_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_ftc1_basic_problem():
    """
    Generates a problem to find the derivative of an integral using FTC Part 1 (basic form).
    """
    # Generate function f(t) = at^n + b
    num_terms = random.choice([1, 2])
    f_coeffs_exps = []
    
    # Ensure at least one non-zero term, and unique exponents
    chosen_exps = set()
    while len(f_coeffs_exps) < num_terms:
        exp = random.randint(0, 3) # Exponents 0, 1, 2, 3
        if exp in chosen_exps:
            continue
        
        coeff = random.randint(-4, 4)
        if coeff == 0:
            continue
        
        f_coeffs_exps.append((coeff, exp))
        chosen_exps.add(exp)

    # Generate constant lower limit for the integral
    lower_limit = random.randint(-5, 5)

    # Format function f(t) for display within the integral
    f_t_str = format_polynomial_latex(f_coeffs_exps, var='t')

    # The derivative is f(x). Reformat f(t) to f(x) for the answer.
    # The coefficients and exponents are the same, just the variable name changes.
    correct_func_str = format_polynomial_latex(f_coeffs_exps, var='x')

    question_text = f"計算以下導函數：<br>$ \\frac{{d}}{{dx}} \\int_{{{lower_limit}}}^{{x}} ({f_t_str}) \\, dt $"
    correct_answer = correct_func_str 

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates problems related to the Fundamental Theorem of Calculus.
    """
    problem_type = random.choice([
        'ftc2_eval',             # Evaluate definite integral using antiderivatives
        'property_linearity',    # Linearity property of definite integrals
        'property_additivity',   # Interval additivity property of definite integrals
        'ftc1_basic'             # Basic differentiation of an integral (FTC Part 1)
    ])
    
    if problem_type == 'ftc2_eval':
        return generate_ftc2_eval_problem()
    elif problem_type == 'property_linearity':
        return generate_property_linearity_problem()
    elif problem_type == 'property_additivity':
        return generate_property_additivity_problem()
    elif problem_type == 'ftc1_basic':
        return generate_ftc1_basic_problem()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct. Handles numerical and expression answers.
    """
    user_answer_stripped = user_answer.strip()
    correct_answer_stripped = correct_answer.strip()
    
    is_correct = False

    # First, try direct string comparison for exact matches (especially for expressions)
    if user_answer_stripped == correct_answer_stripped:
        is_correct = True
    
    # If not a direct string match, try numerical comparison using Fractions for precision
    if not is_correct:
        try:
            user_val = Fraction(user_answer_stripped)
            correct_val = Fraction(correct_answer_stripped)
            if user_val == correct_val:
                is_correct = True
        except (ValueError, ZeroDivisionError):
            # If conversion to Fraction fails, it's not a simple numerical answer
            # or it's an invalid number/fraction.
            # In this case, fall back to strict string comparison (which already happened)
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}