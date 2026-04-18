import random
import math
from fractions import Fraction

def _format_polynomial(coefficients, variable='x', include_fx_prefix=False, hidden_coeff_deg=None):
    """
    Formats a polynomial from a dictionary of coefficients.
    coefficients: dict {degree: coefficient_value}
    variable: str, e.g., 'x'
    include_fx_prefix: bool, if True, prepend "f(x) = " or "P(x) = "
    hidden_coeff_deg: int or None. If an integer, the coefficient for this degree
                      will be represented as 'k'.
    """
    terms = []
    # Collect all unique degrees, ensuring hidden_coeff_deg is included if specified
    all_degrees = sorted(list(coefficients.keys()) + ([hidden_coeff_deg] if hidden_coeff_deg is not None else []), reverse=True)
    all_degrees = sorted(list(set(all_degrees)), reverse=True) # Remove duplicates and re-sort

    # Filter out zero coefficients unless it's the hidden_coeff_deg
    active_degrees = []
    for d in all_degrees:
        if coefficients.get(d, 0) != 0 or d == hidden_coeff_deg:
            active_degrees.append(d)
    
    if not active_degrees:
        if include_fx_prefix:
            return f"$f({variable}) = 0$"
        return "$0$"

    first_term_processed = False
    for degree in active_degrees:
        coeff_val = coefficients.get(degree, 0) # Get actual value, or 0 if term wasn't originally there

        term_str = ""
        current_coeff_display = ""

        if degree == hidden_coeff_deg:
            current_coeff_display = 'k'
        else:
            current_coeff_display = str(abs(coeff_val))
            if abs(coeff_val) == 1 and degree > 0: # Handle '1x', '1x^2' as 'x', 'x^2'
                current_coeff_display = '' 

        # Build the variable part (e.g., 'x', 'x^2', '')
        variable_part = ""
        if degree == 1:
            variable_part = variable
        elif degree > 1:
            variable_part = f"{variable}^{{{{ {degree} }}}}"
        # If degree is 0, variable_part remains empty

        # Combine coefficient and variable part
        if current_coeff_display == '': # means it was 1 or -1 for degree > 0
            term_str = variable_part
        elif variable_part == '': # means degree is 0
            term_str = current_coeff_display
        else:
            term_str = f"{current_coeff_display}{variable_part}"

        # Add sign
        if not first_term_processed:
            if degree == hidden_coeff_deg:
                # If 'k' is the first term, assume it implicitly carries its sign.
                # Just display 'k' or 'kx' without a leading + or -.
                # The actual correct answer for 'k' will handle its sign.
                pass 
            elif coeff_val < 0:
                term_str = f"-{term_str}"
            first_term_processed = True
        else:
            if degree == hidden_coeff_deg:
                term_str = f" + {term_str}" # For 'k', assume addition to previous terms
            elif coeff_val > 0:
                term_str = f" + {term_str}"
            else: # coeff_val < 0
                term_str = f" - {term_str}"
        
        terms.append(term_str)

    poly_body = "".join(terms).strip()

    if poly_body.startswith('+ '): # Remove leading ' + ' if present (e.g., "+ 3x" -> "3x")
        poly_body = poly_body[2:]

    if include_fx_prefix:
        return f"$f({variable}) = {poly_body}$"
    return f"${poly_body}$"

def generate(level=1):
    problem_types = ['degree_coeff', 'evaluate_polynomial', 'polynomial_equality']
    problem_type = random.choice(problem_types)

    if problem_type == 'degree_coeff':
        return generate_degree_coeff_problem(level)
    elif problem_type == 'evaluate_polynomial':
        return generate_evaluate_polynomial_problem(level)
    elif problem_type == 'polynomial_equality':
        return generate_polynomial_equality_problem(level)

def generate_degree_coeff_problem(level):
    max_degree = min(level + 3, 5) # Max degree up to 5
    
    # Generate coefficients
    coefficients = {}
    num_terms = random.randint(1, max_degree + 1)
    degrees_to_include = random.sample(range(max_degree + 1), num_terms)

    for deg in degrees_to_include:
        coeff = random.randint(-5, 5)
        while coeff == 0: # Ensure coefficients are non-zero initially for included terms
            coeff = random.randint(-5, 5)
        coefficients[deg] = coeff
    
    # Ensure the leading coefficient is not zero if max_degree is not 0 (i.e. not a constant poly)
    # Also, ensure coefficients dict is not empty for consistent processing
    if not coefficients: 
        coefficients[0] = random.randint(1,5) # Make it a constant polynomial
    
    poly_degree = max(coefficients.keys())
    if poly_degree > 0 and coefficients.get(poly_degree, 0) == 0: # If by chance the max degree coefficient is 0
        coefficients[poly_degree] = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
    
    poly_str = _format_polynomial(coefficients, include_fx_prefix=True)

    problem_options = []
    problem_options.append(("degree", "多項式的次數 (deg f(x))"))
    problem_options.append(("num_terms", "項數"))
    problem_options.append(("constant_term", "常數項"))
    
    # Add coefficient questions for existing degrees
    # Iterate through possible degrees to ask for, not just existing ones
    for deg in range(poly_degree + 1):
        if deg > 1:
            problem_options.append((f"coeff_{deg}", f"$x^{{{{ {deg} }}}}$ 的係數"))
        elif deg == 1:
            problem_options.append((f"coeff_1", "$x$ 的係數"))
        # deg=0 is covered by "constant_term", so no need to add another "coeff_0" here
            
    chosen_option_type, chosen_question_text_part = random.choice(problem_options)

    correct_answer_val = ""
    if chosen_option_type == "degree":
        correct_answer_val = str(poly_degree)
    elif chosen_option_type == "num_terms":
        # Only count non-zero terms
        correct_answer_val = str(len({d:c for d,c in coefficients.items() if c != 0}))
    elif chosen_option_type == "constant_term":
        correct_answer_val = str(coefficients.get(0, 0))
    elif chosen_option_type.startswith("coeff_"):
        target_degree = int(chosen_option_type.split("_")[1])
        correct_answer_val = str(coefficients.get(target_degree, 0))
    
    question_text = f"關於多項式 {poly_str}，請問{chosen_question_text_part}為何？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer_val,
        "correct_answer": correct_answer_val,
        "type": "degree_coeff"
    }

def generate_evaluate_polynomial_problem(level):
    max_degree = min(level + 2, 4) # Max degree up to 4
    
    coefficients = {}
    num_terms = random.randint(2, max_degree + 1)
    degrees = random.sample(range(max_degree + 1), num_terms)
    
    for deg in degrees:
        coeff = random.randint(-5, 5)
        while coeff == 0: 
            coeff = random.randint(-5, 5)
        coefficients[deg] = coeff
    
    # Ensure leading coefficient is non-zero
    poly_degree = max(coefficients.keys()) if coefficients else 0
    if poly_degree > 0 and coefficients.get(poly_degree, 0) == 0:
        coefficients[poly_degree] = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])

    poly_str = _format_polynomial(coefficients, include_fx_prefix=True)
    
    eval_x = random.randint(-2, 2) # Evaluate at small integer values
    
    # Helper to evaluate polynomial
    evaluated_result = 0
    for degree, coeff in coefficients.items():
        evaluated_result += coeff * (eval_x ** degree)
    
    correct_answer = str(evaluated_result)
    
    question_text = f"已知多項式 {poly_str}，請問當 $x = {eval_x}$ 時，$f({eval_x})$ 的值為何？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "type": "evaluate_polynomial"
    }

def generate_polynomial_equality_problem(level):
    max_degree = min(level + 1, 3) # Max degree up to 3 for level 1
    
    p_coefficients = {}
    
    # Ensure at least one term and leading coefficient non-zero if max_degree > 0
    num_terms = random.randint(1, max_degree + 1)
    degrees_to_include = random.sample(range(max_degree + 1), num_terms)
    
    for deg in range(max_degree + 1):
        if deg in degrees_to_include:
            coeff = random.randint(-5, 5)
            while coeff == 0: # Ensure coefficients are non-zero
                coeff = random.randint(-5, 5)
            p_coefficients[deg] = coeff
        else:
            p_coefficients[deg] = 0 # Explicitly set to 0 if not present initially

    # Ensure leading coefficient of P(x) is non-zero if max_degree > 0
    poly_degree = max(p_coefficients.keys()) if p_coefficients else 0
    if poly_degree > 0 and p_coefficients.get(poly_degree, 0) == 0:
        p_coefficients[poly_degree] = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
    elif not p_coefficients: # If all coeffs somehow ended up 0
        p_coefficients[0] = random.randint(1,5)

    # Choose a degree to hide. Must be within the max_degree range.
    # It can be a term that was originally 0.
    hidden_degree = random.randint(0, max_degree)
    hidden_coeff_val = p_coefficients.get(hidden_degree, 0) # Use .get to safely get 0 if not present

    # Format P(x) and Q(x) for display
    poly_p_str = _format_polynomial(p_coefficients, include_fx_prefix=False)
    # For Q(x), use the same coefficients but with 'k' at the hidden degree
    poly_q_str = _format_polynomial(p_coefficients, include_fx_prefix=False, hidden_coeff_deg=hidden_degree)
    
    question_text = f"已知兩個多項式相等：${poly_p_str} = {poly_q_str}$。<br>請問常數 $k$ 的值為何？"
    correct_answer = str(hidden_coeff_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "type": "polynomial_equality"
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().lower()
    correct_answer = correct_answer.strip().lower()

    is_correct = False
    
    # Try converting to float for numerical comparison
    try:
        user_num = float(user_answer)
        correct_num = float(correct_answer)
        if user_num == correct_num:
            is_correct = True
    except ValueError:
        pass # If conversion fails, compare as strings

    # Fallback to string comparison if not numerical or numerical comparison failed
    if not is_correct and user_answer == correct_answer:
        is_correct = True
    
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}