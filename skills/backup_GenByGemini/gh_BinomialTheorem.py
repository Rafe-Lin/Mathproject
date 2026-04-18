import random
import math
import re

# Helper to calculate binomial coefficient C(n, k)
def _binom_coeff(n, k):
    return math.comb(n, k)

# Helper to format a single term like `Cx^a y^b`
# Attempts to match the spacing style from the examples:
# `x^5`, `5x^4 y`, `10x^3 y^2`, `16x^4`, `-32x^3 y`
def _format_term(coefficient, term1_base_str, term1_exponent, term2_base_str, term2_exponent, include_sign=False):
    if coefficient == 0:
        return ""

    term_parts = [] # Parts that make up the absolute value of the term
    
    # Variable parts assembly
    var1_str = ""
    if term1_exponent > 0:
        var1_str = term1_base_str
        if term1_exponent > 1:
            var1_str += f"^{{{term1_exponent}}}"
            
    var2_str = ""
    if term2_exponent > 0:
        var2_str = term2_base_str
        if term2_exponent > 1:
            var2_str += f"^{{{term2_exponent}}}"

    # Handle coefficient part
    abs_coeff = abs(coefficient)
    # Always show coefficient if it's not 1 and it's not a variable term (i.e., it's a constant)
    # or if it's not 1 or -1 but there are variables.
    if abs_coeff != 1 or (not var1_str and not var2_str): 
        term_parts.append(str(abs_coeff))

    # Combine variable parts with a space if both exist, otherwise just add the one that exists
    if var1_str and var2_str:
        term_parts.append(f"{var1_str} {var2_str}")
    elif var1_str:
        term_parts.append(var1_str)
    elif var2_str: # This case is less common for (X+Y)^n, but ensures robustness if one term is constant
        term_parts.append(var2_str)
        
    assembled_term_body = "".join(term_parts) # Join coeff and (var parts)

    # Add sign prefix
    sign_prefix = ""
    if include_sign:
        sign_prefix = "+" if coefficient > 0 else "-"
    elif coefficient < 0:
        sign_prefix = "-"
    
    return f"{sign_prefix}{assembled_term_body}"


def generate_simple_expansion():
    """
    Generates a problem for simple binomial expansion like $(x+y)^n$.
    """
    n = random.randint(3, 6)
    var1_char = random.choice(['x', 'a'])
    var2_char = random.choice(['y', 'b'])
    # Ensure variables are different
    if var1_char == var2_char:
        var2_char = 'y' if var1_char == 'x' else 'b'

    question_text = f"寫出 $({var1_char}+{var2_char})^{{{n}}}$ 的展開式。"
    
    terms = []
    for k in range(n + 1):
        coeff_n_k = _binom_coeff(n, k)
        term_str = _format_term(coeff_n_k, var1_char, n - k, var2_char, k, include_sign=True)
        if term_str: # Only add if the term is not empty (e.g., if coeff was 0)
            terms.append(term_str)
    
    full_expansion = " ".join(terms).lstrip('+') # Join terms with spaces and remove leading '+' if any
    
    return {
        "question_text": question_text,
        "answer": full_expansion,
        "correct_answer": full_expansion
    }

def generate_expansion_with_coeffs_and_powers():
    """
    Generates a problem for binomial expansion with coefficients and powers,
    like $(Ax \\pm By)^n$ or $(Ax^p \\pm B)^n$.
    """
    n = random.randint(3, 5) # Smaller n for more complex expansions
    
    # First term: A * var1^p
    A_coeff = random.randint(1, 3)
    var1_char = random.choice(['x', 'a'])
    p_power = random.randint(1, 2)
    
    # Second term: B * var2^q or B (constant)
    B_val = random.randint(1, 3) * random.choice([1, -1]) # B can be negative
    
    term2_has_variable = random.choice([True, False]) # Decide if second term has a variable
    
    term1_display_base = f"{A_coeff}{var1_char}"
    if p_power > 1:
        term1_display_base += f"^{{{p_power}}}"
    
    term2_display_part = ""
    term2_actual_base_var = ""
    term2_actual_base_pow = 0
    
    if term2_has_variable:
        var2_char = random.choice(['y', 'b'])
        if var2_char == var1_char: # Ensure different variables
            var2_char = 'y' if var1_char == 'x' else 'b'
        q_power = random.randint(1, 2)
        
        # Format the second term for the question text, handling its sign
        if B_val < 0:
            term2_display_part = f" - {-B_val}{var2_char}"
        else:
            term2_display_part = f" + {B_val}{var2_char}"
        if q_power > 1:
            term2_display_part += f"^{{{q_power}}}"
            
        term2_actual_base_var = var2_char
        term2_actual_base_pow = q_power
    else: # Second term is a constant
        if B_val < 0:
            term2_display_part = f" - {-B_val}"
        else:
            term2_display_part = f" + {B_val}"
    
    question_text = f"寫出 $({term1_display_base}{term2_display_part})^{{{n}}}$ 的展開式。"

    terms = []
    for k in range(n + 1):
        binom_coeff = _binom_coeff(n, k)
        
        # Calculate the overall numerical coefficient for this term
        coeff_val = binom_coeff * (A_coeff**(n - k)) * (B_val**k)
        
        # Calculate the power for var1
        var1_exp = p_power * (n - k)
        
        # Calculate the power for var2
        var2_exp = term2_actual_base_pow * k

        term_str = _format_term(coeff_val, var1_char, var1_exp, term2_actual_base_var, var2_exp, include_sign=True)
        if term_str:
            terms.append(term_str)
            
    full_expansion = " ".join(terms).lstrip('+') # Join terms with spaces and remove leading '+'
    
    return {
        "question_text": question_text,
        "answer": full_expansion,
        "correct_answer": full_expansion
    }

def generate_coefficient_problem():
    """
    Generates a problem to find the coefficient of a specific term
    in an expansion like $(Ax^p + B/x^q)^n$.
    """
    n = random.randint(4, 7)
    
    A_coeff = random.randint(1, 3)
    p_power = random.randint(1, 3) # Power for x in the first term
    
    B_coeff = random.randint(1, 3) * random.choice([1, -1]) # Numerical part of the second term
    q_power = random.randint(0, 2) # Power for x in the denominator of the second term (0 means constant)
    
    # Calculate possible x powers and their corresponding `r` values.
    # General term: $C_n^r (A x^p)^{n-r} (B x^{-q})^r = C_n^r A^{n-r} B^r x^{p(n-r) - qr}$
    possible_terms_info = [] # Stores (current_x_power, r_value, coefficient)
    for r_test in range(n + 1):
        # Calculate the exponent of x for this `r`
        current_x_power = p_power * (n - r_test) - q_power * r_test
        
        # Calculate the numerical coefficient for this `r`
        coeff_at_r = _binom_coeff(n, r_test) * (A_coeff**(n-r_test)) * (B_coeff**r_test)
        
        if coeff_at_r != 0: # Only consider terms with non-zero coefficients
            possible_terms_info.append((current_x_power, r_test, coeff_at_r))
    
    if not possible_terms_info:
        # This case should be rare with the chosen ranges, but recurse if it happens
        return generate_coefficient_problem()
    
    # Randomly select one of the valid terms to ask for its coefficient
    k_target_power, _, final_coeff = random.choice(possible_terms_info)
    
    term1_display = f"{A_coeff}x^{{{p_power}}}"
    
    # Construct the second term's display for the question text
    term2_display_part = ""
    if B_coeff < 0:
        if q_power == 0: # Second term is a negative constant, e.g., (Ax^p - C)^n
            term2_display_part = f" - {-B_coeff}"
        else: # Second term is negative fraction, e.g., (Ax^p - C/x^q)^n
            term2_display_part = f" - {r'{\\frac{'}{abs(B_coeff)}{r'}{x^{{'+str(q_power)+r'}}}}'}"
    else: # B_coeff > 0
        if q_power == 0: # Second term is a positive constant, e.g., (Ax^p + C)^n
            term2_display_part = f" + {B_coeff}"
        else: # Second term is positive fraction, e.g., (Ax^p + C/x^q)^n
            term2_display_part = f" + {r'{\\frac{'}{B_coeff}{r'}{x^{{'+str(q_power)+r'}}}}'}"

    question_text = f"求 $({term1_display}{term2_display_part})^{{{n}}}$ 展開式中 $x^{{{k_target_power}}}$ 項的係數。"

    return {
        "question_text": question_text,
        "answer": str(final_coeff),
        "correct_answer": str(final_coeff)
    }

def generate(level=1):
    """
    Generates a Binomial Theorem problem.
    The level parameter is currently unused but can be expanded for difficulty.
    """
    problem_type = random.choice([
        'simple_expansion',
        'complex_expansion',
        'coefficient_problem'
    ])

    if problem_type == 'simple_expansion':
        return generate_simple_expansion()
    elif problem_type == 'complex_expansion':
        return generate_expansion_with_coeffs_and_powers()
    else: # 'coefficient_problem'
        return generate_coefficient_problem()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct, handling different formats.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    result_text = ""

    # First, try numeric comparison (for coefficient problems)
    try:
        user_num = float(user_answer)
        correct_num = float(correct_answer)
        if user_num == correct_num:
            is_correct = True
    except ValueError:
        pass # Not a pure number, proceed to string comparison for expansions

    # If not a numeric match, try string comparison (for expansion problems)
    if not is_correct:
        # Normalize answers for robust comparison:
        # 1. Remove all whitespace characters (spaces, tabs, newlines)
        # 2. Normalize signs (e.g., " + -" to "-", " - -" to "+")
        normalized_user = re.sub(r'\s+', '', user_answer).replace("+-", "-").replace("--", "+")
        normalized_correct = re.sub(r'\s+', '', correct_answer).replace("+-", "-").replace("--", "+")
        
        is_correct = (normalized_user == normalized_correct)

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$。"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}