import random
from fractions import Fraction
import math
import re

# Helper to normalize a polynomial dictionary (remove zero coefficients)
def normalize_poly(poly_dict):
    # Convert coefficients to int if they are effectively integers (e.g., 2.0 -> 2)
    # and remove terms with 0 coefficient.
    normalized = {}
    for deg, coeff in poly_dict.items():
        if isinstance(coeff, Fraction):
            if coeff.denominator == 1:
                coeff = int(coeff)
            else:
                # Keep Fraction if not an integer
                pass
        
        if abs(coeff) > 1e-9: # Consider values very close to zero as zero
            normalized[deg] = coeff
    return normalized

# Helper to convert polynomial dictionary to string representation
def dict_to_poly_str(poly_dict, var='x', force_parentheses=False):
    poly_dict = normalize_poly(poly_dict)
    if not poly_dict:
        return "0"
    
    terms = []
    # Sort degrees in descending order
    sorted_degrees = sorted(poly_dict.keys(), reverse=True)
    
    for degree in sorted_degrees:
        coeff = poly_dict[degree]
        
        abs_coeff = abs(coeff)
        sign = "+" if coeff > 0 else "-"
        
        term_str = ""
        if degree == 0: # Constant term
            term_str = f"{abs_coeff}"
        elif degree == 1: # Linear term
            if abs_coeff == 1:
                term_str = f"{var}"
            else:
                term_str = f"{abs_coeff}{var}"
        else: # Higher degree terms
            if abs_coeff == 1:
                term_str = f"{var}^{{{{ {degree} }}}}" # Double braces for LaTeX exponent
            else:
                term_str = f"{abs_coeff}{var}^{{{{ {degree} }}}}"
        
        terms.append(f" {sign} {term_str}")
            
    # Join terms, removing leading '+' for the first term
    result = "".join(terms).strip()
    if result.startswith("+ "):
        result = result[2:]
    elif result.startswith("- "): # For polynomials starting with a negative term
        result = result[0] + result[2:]

    # Ensure space around operators for readability
    result = result.replace("+", " + ").replace("-", " - ")
    # Remove double spaces
    result = " ".join(result.split())

    if force_parentheses and result != "0": # Only add parentheses if not '0'
        return f"({result})"
    return result

# Helper for polynomial addition
def add_polynomials(p1, p2):
    result = p1.copy()
    for degree, coeff in p2.items():
        result[degree] = result.get(degree, 0) + coeff
    return normalize_poly(result)

# Helper for polynomial subtraction
def subtract_polynomials(p1, p2):
    result = p1.copy()
    for degree, coeff in p2.items():
        result[degree] = result.get(degree, 0) - coeff
    return normalize_poly(result)

# Helper for polynomial multiplication
def multiply_polynomials(p1, p2):
    result = {}
    for deg1, coeff1 in p1.items():
        for deg2, coeff2 in p2.items():
            new_degree = deg1 + deg2
            new_coeff = coeff1 * coeff2
            result[new_degree] = result.get(new_degree, 0) + new_coeff
    return normalize_poly(result)

# Helper for polynomial long division (returns (quotient, remainder))
def divide_polynomials(dividend, divisor):
    dividend = normalize_poly(dividend)
    divisor = normalize_poly(divisor)

    if not divisor:
        raise ValueError("Divisor cannot be zero polynomial")
    if not dividend:
        return {}, {} # Quotient is 0, remainder is 0

    divisor_lead_degree = max(divisor.keys())
    divisor_lead_coeff = divisor[divisor_lead_degree]

    # If dividend degree is less than divisor degree, quotient is 0, remainder is dividend
    if not dividend or max(dividend.keys()) < divisor_lead_degree:
        return {}, dividend

    remainder = dividend.copy()
    quotient = {}

    while remainder and max(remainder.keys()) >= divisor_lead_degree:
        rem_lead_degree = max(remainder.keys())
        rem_lead_coeff = remainder[rem_lead_degree]

        # Calculate term for quotient
        q_term_degree = rem_lead_degree - divisor_lead_degree
        # Use Fraction to handle non-integer coefficients in intermediate steps
        q_term_coeff = Fraction(rem_lead_coeff, divisor_lead_coeff)

        quotient[q_term_degree] = quotient.get(q_term_degree, 0) + q_term_coeff

        # Multiply divisor by this quotient term and subtract from remainder
        subtraction_poly = {}
        for deg, coeff in divisor.items():
            subtraction_poly[deg + q_term_degree] = coeff * q_term_coeff

        for deg, coeff in subtraction_poly.items():
            remainder[deg] = remainder.get(deg, 0) - coeff
        
        remainder = normalize_poly(remainder)
        
        # If remainder became empty or its degree is less than divisor's, stop
        if not remainder or max(remainder.keys()) < divisor_lead_degree:
             break 

    return normalize_poly(quotient), normalize_poly(remainder)


# Function to perform synthetic division. Returns (quotient_poly_dict, remainder_int)
# Divisor must be of the form (x - root)
def synthetic_division(poly_dict, root):
    if not poly_dict:
        return {}, 0

    max_degree = 0
    if poly_dict:
        max_degree = max(poly_dict.keys())
    
    ordered_coeffs = [poly_dict.get(i, 0) for i in range(max_degree, -1, -1)]

    # Perform synthetic division
    result_coeffs = [ordered_coeffs[0]]
    for i in range(1, len(ordered_coeffs)):
        next_val = ordered_coeffs[i] + result_coeffs[-1] * root
        result_coeffs.append(next_val)

    # The last element is the remainder
    remainder = result_coeffs.pop()

    # The remaining elements are the coefficients of the quotient, highest degree first
    # If the original polynomial had degree N, the quotient has degree N-1
    quotient_dict = {}
    if result_coeffs:
        quotient_max_degree = max_degree - 1
        for i, coeff in enumerate(result_coeffs):
            if coeff != 0:
                quotient_dict[quotient_max_degree - i] = coeff
    
    return normalize_poly(quotient_dict), remainder

# Helper to generate a random polynomial with integer coefficients
def generate_random_polynomial(min_degree, max_degree, min_coeff, max_coeff, force_constant=False, force_lead_coeff=None):
    degree = random.randint(min_degree, max_degree)
    poly = {}
    
    # Generate leading coefficient first if specified
    if force_lead_coeff is not None:
        poly[degree] = force_lead_coeff
    else:
        # Ensure highest degree term is not zero
        poly[degree] = random.randint(min_coeff, max_coeff)
        while poly[degree] == 0:
             poly[degree] = random.randint(min_coeff, max_coeff)

    has_constant = (degree == 0 and poly[0] != 0) # Track if constant exists from degree 0
    
    for d in range(degree - 1, -1, -1): # Iterate from next highest degree down to 0
        if d == 0:
            if force_constant and not has_constant: # Ensure constant term exists if required and not already added
                 poly[d] = random.randint(min_coeff, max_coeff)
            elif not force_constant and random.random() < 0.7: # Randomly add constant if not forced
                poly[d] = random.randint(min_coeff, max_coeff)
            else: # Add if not 0 for force_constant
                if random.randint(0,1) == 1: # 50% chance of a constant
                    poly[d] = random.randint(min_coeff, max_coeff)
        else:
            if random.random() < 0.8: # Other terms have 80% chance
                poly[d] = random.randint(min_coeff, max_coeff)
        
        if d == 0 and poly.get(0) != None and poly[0] != 0:
            has_constant = True
            
    # Remove zero coefficients
    poly = normalize_poly(poly)
    
    # If the polynomial somehow became empty (e.g. all other coeffs zeroed out), ensure it has at least one term
    if not poly:
        if degree == 0:
            poly[0] = random.randint(min_coeff, max_coeff)
            while poly[0] == 0: # ensure it's not zero
                poly[0] = random.randint(min_coeff, max_coeff)
        else: # Re-generate a simple leading term
            poly[degree] = random.randint(min_coeff, max_coeff)
            while poly[degree] == 0:
                poly[degree] = random.randint(min_coeff, max_coeff)

    return poly

# Generate a problem for addition/subtraction
def generate_add_sub_problem():
    f_coeffs = generate_random_polynomial(min_degree=1, max_degree=3, min_coeff=-5, max_coeff=5, force_constant=True)
    g_coeffs = generate_random_polynomial(min_degree=1, max_degree=3, min_coeff=-5, max_coeff=5, force_constant=True)

    f_str = dict_to_poly_str(f_coeffs)
    g_str = dict_to_poly_str(g_coeffs)

    problem_choice = random.choice(['add', 'sub'])

    if problem_choice == 'add':
        result_coeffs = add_polynomials(f_coeffs, g_coeffs)
        result_str = dict_to_poly_str(result_coeffs)
        question_text = f"已知 $f(x) = {f_str}$, $g(x) = {g_str}$，求 $f(x) + g(x)$。"
        correct_answer = result_str
    else: # sub
        result_coeffs = subtract_polynomials(f_coeffs, g_coeffs)
        result_str = dict_to_poly_str(result_coeffs)
        question_text = f"已知 $f(x) = {f_str}$, $g(x) = {g_str}$，求 $f(x) - g(x)$。"
        correct_answer = result_str

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# Generate a problem for multiplication
def generate_mul_problem():
    f_coeffs = generate_random_polynomial(min_degree=1, max_degree=2, min_coeff=-3, max_coeff=3, force_constant=True)
    g_coeffs = generate_random_polynomial(min_degree=1, max_degree=1, min_coeff=-3, max_coeff=3, force_constant=True)
    
    f_str = dict_to_poly_str(f_coeffs, force_parentheses=True)
    g_str = dict_to_poly_str(g_coeffs, force_parentheses=True)

    result_coeffs = multiply_polynomials(f_coeffs, g_coeffs)
    result_str = dict_to_poly_str(result_coeffs)

    question_text = f"求多項式 $f(x) = {f_str}$ 與 $g(x) = {g_str}$ 的乘積。"
    correct_answer = result_str
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# Generate a problem for synthetic division (simplified)
def generate_synthetic_division_problem():
    # Dividend polynomial
    dividend_coeffs = generate_random_polynomial(min_degree=3, max_degree=4, min_coeff=-7, max_coeff=7, force_constant=True)
    while not dividend_coeffs: # Ensure it's not a zero polynomial
        dividend_coeffs = generate_random_polynomial(min_degree=3, max_degree=4, min_coeff=-7, max_coeff=7, force_constant=True)

    # Divisor (x - root)
    root = random.randint(-3, 3)
    while root == 0: # Avoid x as divisor for simpler problems
        root = random.randint(-3, 3)

    quotient_coeffs, remainder_val = synthetic_division(dividend_coeffs, root)
    
    dividend_str = dict_to_poly_str(dividend_coeffs)
    
    # Format (x-root) for display
    if root > 0:
        divisor_display_str = f"x - {root}"
    else:
        divisor_display_str = f"x + {abs(root)}"

    quotient_str = dict_to_poly_str(quotient_coeffs) if quotient_coeffs else "0"
    remainder_str = str(remainder_val)

    question_text = f"使用綜合除法求 $f(x) = {dividend_str}$ 除以 ${divisor_display_str}$ 的商式及餘式。"
    correct_answer = f"商式為 ${quotient_str}$，餘式為 ${remainder_str}$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# Generate a problem for general polynomial division (long division based)
def generate_long_division_problem():
    # Generate a quotient and a remainder, then compute dividend = quotient * divisor + remainder
    
    # Divisor (degree 1 or 2)
    divisor_degree = random.randint(1, 2)
    # Ensure divisor leading coeff is 1 or -1 to keep quotient/remainder integer
    divisor_lead = random.choice([-1, 1])
    divisor_coeffs = generate_random_polynomial(divisor_degree, divisor_degree, min_coeff=-3, max_coeff=3, force_constant=True, force_lead_coeff=divisor_lead)
    
    # Quotient (degree 1 to 2)
    quotient_degree = random.randint(1, 2)
    quotient_coeffs = generate_random_polynomial(quotient_degree, quotient_degree, min_coeff=-3, max_coeff=3, force_constant=True)

    # Remainder (degree < divisor degree)
    max_rem_degree = max(divisor_coeffs.keys()) - 1
    # Ensure remainder is not always zero
    remainder_coeffs = {}
    if random.random() < 0.7 and max_rem_degree >= 0: # 70% chance of a non-zero remainder
        # Coefficients should be within a reasonable range and not zero
        temp_rem = generate_random_polynomial(0, max_rem_degree, min_coeff=-5, max_coeff=5, force_constant=False)
        if temp_rem: # Only assign if not an empty polynomial (all zeros)
            remainder_coeffs = temp_rem
    
    # Construct dividend
    temp_mul = multiply_polynomials(quotient_coeffs, divisor_coeffs)
    dividend_coeffs = add_polynomials(temp_mul, remainder_coeffs)

    dividend_str = dict_to_poly_str(dividend_coeffs)
    divisor_str = dict_to_poly_str(divisor_coeffs, force_parentheses=True) # Force parentheses for divisor for clarity
    
    quotient_str = dict_to_poly_str(quotient_coeffs) if quotient_coeffs else "0"
    remainder_str = dict_to_poly_str(remainder_coeffs) if remainder_coeffs else "0"

    question_text = f"求多項式 $f(x) = {dividend_str}$ 除以 $g(x) = {divisor_str}$ 的商式及餘式。"
    correct_answer = f"商式為 ${quotient_str}$，餘式為 ${remainder_str}$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate_horner_problem():
    # Generate a polynomial f(x)
    max_degree = random.randint(3, 4)
    f_coeffs = generate_random_polynomial(min_degree=2, max_degree=max_degree, min_coeff=-3, max_coeff=3, force_constant=True)
    while len(f_coeffs) < 3: # Ensure enough terms
        f_coeffs = generate_random_polynomial(min_degree=2, max_degree=max_degree, min_coeff=-3, max_coeff=3, force_constant=True)

    f_str = dict_to_poly_str(f_coeffs)

    # Choose a value 'c' for (x-c)
    c_val = random.randint(-2, 2)
    while c_val == 0:
        c_val = random.randint(-2, 2)

    # Perform repeated synthetic division to find coefficients a_n, ..., a_0
    
    coeffs_list = [f_coeffs.get(i, 0) for i in range(max_degree, -1, -1)] # coefficients from highest degree
    
    results = [] # Stores coefficients a_0, a_1, ...
    current_coeffs = coeffs_list[:]

    for _ in range(max_degree + 1):
        if not current_coeffs:
            results.insert(0, 0)
            break
        
        # Synthetic division
        quotient_coeffs_raw = [current_coeffs[0]]
        for i in range(1, len(current_coeffs)):
            next_val = current_coeffs[i] + quotient_coeffs_raw[-1] * c_val
            quotient_coeffs_raw.append(next_val)

        remainder = quotient_coeffs_raw.pop()
        results.append(remainder) # a_0, then a_1, ...
        
        current_coeffs = quotient_coeffs_raw # The new dividend for the next step
        if all(x==0 for x in current_coeffs):
            break

    # The results list now contains [a_0, a_1, ..., a_n] but we need [a_n, ..., a_0]
    a_coeffs = [0] * (max_degree + 1)
    for i in range(len(results)):
        a_coeffs[i] = results[i] # a_coeffs[0] = a_0, a_coeffs[1] = a_1 ...
    
    a_coeffs.reverse() # Now a_coeffs are [a_n, a_{n-1}, ..., a_0]

    c_val_display_in_paren = f"x - {c_val}" if c_val > 0 else f"x + {abs(c_val)}"

    question_text = f"設 $f(x) = {f_str}$。已知 $f(x)$ 表成 $({c_val_display_in_paren})$ 的多項式之形式為 "
    
    coeff_names = ['a', 'b', 'c', 'd', 'e'] # Up to max_degree=4 means 5 coeffs (a_4, a_3, a_2, a_1, a_0)
    
    form_parts = []
    # Display the form: a(x-c)^n + b(x-c)^(n-1) + ... + d(x-c) + e
    for i in range(len(a_coeffs)):
        current_degree = len(a_coeffs) - 1 - i
        coeff_name_to_display = coeff_names[i]
        
        if current_degree == 0: # Constant term
            form_parts.append(f"{coeff_name_to_display}")
        elif current_degree == 1: # Linear term
            form_parts.append(f"{coeff_name_to_display}({c_val_display_in_paren})")
        else:
            form_parts.append(f"{coeff_name_to_display}({c_val_display_in_paren})^{{{{ {current_degree} }}}}")
            
    form_str = " + ".join(form_parts)

    question_text += f"${form_str}$，求實數"
    param_list = [f"*{coeff_names[i]}*" for i in range(len(a_coeffs))]
    question_text += f"{', '.join(param_list)}的值。"

    # Format the coefficients for the answer
    coeff_answer_parts = []
    for i in range(len(a_coeffs)):
        name = coeff_names[i]
        val = a_coeffs[i] # a_coeffs is [a_n, a_{n-1}, ..., a_0]
        coeff_answer_parts.append(f"${name} = {val}$")
    
    correct_answer = "，".join(coeff_answer_parts)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    problem_types = {
        1: ['add_sub', 'multiply'],
        2: ['add_sub', 'multiply', 'synthetic_division'],
        3: ['add_sub', 'multiply', 'synthetic_division', 'long_division', 'horner_expansion']
    }
    
    selected_types = problem_types.get(level, problem_types[1]) # Default to level 1 if invalid level
    problem_type = random.choice(selected_types)

    if problem_type == 'add_sub':
        return generate_add_sub_problem()
    elif problem_type == 'multiply':
        return generate_mul_problem()
    elif problem_type == 'synthetic_division':
        return generate_synthetic_division_problem()
    elif problem_type == 'long_division':
        return generate_long_division_problem()
    elif problem_type == 'horner_expansion':
        return generate_horner_problem()
    
    # Fallback in case problem_type is not handled
    return generate_add_sub_problem()


# Helper to parse a polynomial string into a dictionary
def parse_poly_str(poly_str, var='x'):
    poly_str = poly_str.strip().replace(' ', '').replace('−', '-') # Normalize spaces and unicode minus

    if not poly_str:
        return {} # Empty string means zero polynomial
    
    # Handle leading signs implicitly by splitting on operators
    # Ensure there's a '+' before the first term if it's not negative
    temp_poly_str = poly_str
    if not temp_poly_str.startswith('-'):
        temp_poly_str = '+' + temp_poly_str
    
    # Split by '+' or '-' keeping the delimiter
    terms = re.findall(r'([+-]?[^+-]+)', temp_poly_str)
    
    poly_dict = {}
    for term_str in terms:
        if not term_str:
            continue
        
        sign = 1
        if term_str.startswith('-'):
            sign = -1
            term_str = term_str[1:]
        elif term_str.startswith('+'):
            term_str = term_str[1:]

        coeff = 1
        degree = 0

        # Check for variable part
        if var in term_str:
            parts = term_str.split(var)
            coeff_part = parts[0]
            
            if coeff_part == '': # e.g., 'x', 'x^2'
                coeff = 1
            else:
                try:
                    coeff = float(coeff_part)
                except ValueError:
                    # This case should ideally not happen if input is well-formed like "3x"
                    # or it could be a sign error already handled.
                    pass # Keep coeff as 1

            if len(parts) > 1 and parts[1].startswith('^'):
                degree_str = parts[1][1:].replace('{','').replace('}','') # Remove LaTeX braces
                try:
                    degree = int(degree_str)
                except ValueError:
                    degree = 1 # Fallback for malformed degree
            else:
                degree = 1 # e.g., 'x' is x^1
        else: # It's a constant term
            try:
                coeff = float(term_str)
            except ValueError:
                coeff = 0 # Malformed constant term
            degree = 0

        poly_dict[degree] = poly_dict.get(degree, 0) + sign * coeff
    
    return normalize_poly(poly_dict)

# Helper for comparing two polynomial dictionaries
def compare_poly_dicts(p1, p2):
    p1_norm = normalize_poly(p1)
    p2_norm = normalize_poly(p2)
    
    if len(p1_norm) != len(p2_norm):
        return False
    
    for degree, coeff1 in p1_norm.items():
        if degree not in p2_norm:
            return False
        coeff2 = p2_norm[degree]
        # Compare coefficients, allow for floating point precision issues
        if isinstance(coeff1, Fraction) or isinstance(coeff2, Fraction):
            if Fraction(coeff1) != Fraction(coeff2):
                return False
        elif abs(coeff1 - coeff2) > 1e-9:
            return False
    return True

# Helper for parsing combined answers like "商式為 $x+1$，餘式為 $3$"
def parse_combined_answer(answer_str):
    
    result = {}
    
    # Try to parse Quotient and Remainder
    quotient_match = re.search(r'(?:商式為|quotient is)\s*\$(.*?)\$', answer_str, re.IGNORECASE)
    remainder_match = re.search(r'(?:餘式為|remainder is)\s*\$(.*?)\$', answer_str, re.IGNORECASE)
    
    q_str = quotient_match.group(1) if quotient_match else None
    r_str = remainder_match.group(1) if remainder_match else None

    if q_str is not None:
        result['quotient'] = parse_poly_str(q_str)
    if r_str is not None:
        result['remainder'] = parse_poly_str(r_str)
    
    # Try to parse coefficients for Horner's expansion
    coeff_matches = re.findall(r'\$([a-zA-Z])\s*=\s*([-+]?\d+(?:\.\d*)?)\$', answer_str)
    if coeff_matches:
        result['coeffs'] = {name: float(val) for name, val in coeff_matches}

    return result

def check(user_answer, correct_answer):
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    result_text = ""

    # Try simple polynomial comparison first
    try:
        user_poly = parse_poly_str(user_answer)
        correct_poly = parse_poly_str(correct_answer)
        if compare_poly_dicts(user_poly, correct_poly):
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer}$。"
    except Exception:
        pass # Not a simple polynomial, try combined answer parsing

    if not is_correct:
        # Handle combined answers (quotient/remainder or multiple coefficients)
        try:
            user_parsed = parse_combined_answer(user_answer)
            correct_parsed = parse_combined_answer(correct_answer)
            
            if 'quotient' in correct_parsed or 'remainder' in correct_parsed:
                # Check quotient and remainder
                q_correct = correct_parsed.get('quotient', {})
                r_correct = correct_parsed.get('remainder', {})
                q_user = user_parsed.get('quotient', {})
                r_user = user_parsed.get('remainder', {})

                is_q_correct = compare_poly_dicts(q_user, q_correct)
                is_r_correct = compare_poly_dicts(r_user, r_correct)

                if is_q_correct and is_r_correct:
                    is_correct = True
                    result_text = f"完全正確！答案是 {correct_answer}。"
                else:
                    feedback_parts = []
                    if not is_q_correct: feedback_parts.append(f"商式不正確，正確應為 ${dict_to_poly_str(q_correct)}$")
                    if not is_r_correct: feedback_parts.append(f"餘式不正確，正確應為 ${dict_to_poly_str(r_correct)}$")
                    result_text = "；".join(feedback_parts) + f"<br>正確答案應為：{correct_answer}"
            elif 'coeffs' in correct_parsed: # Horner's expansion
                # Compare coefficients for a, b, c, d...
                is_all_coeffs_correct = True
                feedback_parts = []
                # Check if all correct coefficients are present and match in user answer
                for name, correct_val in correct_parsed['coeffs'].items():
                    user_val = user_parsed.get('coeffs', {}).get(name)
                    if user_val is None or abs(user_val - correct_val) > 1e-9:
                        is_all_coeffs_correct = False
                        feedback_parts.append(f"${name}$ 值不正確，應為 ${correct_val}$")
                
                # Also check if user provided extra coefficients not in correct answer
                if len(user_parsed.get('coeffs', {})) != len(correct_parsed['coeffs']):
                    is_all_coeffs_correct = False
                    if not feedback_parts: # Add general message if no specific errors yet
                        feedback_parts.append("提供的係數數量不正確。")

                if is_all_coeffs_correct:
                    is_correct = True
                    result_text = f"完全正確！答案是 {correct_answer}。"
                else:
                    result_text = "；".join(feedback_parts)
                    if not feedback_parts:
                        result_text = "答案格式不正確或係數不符合。"
                    result_text += f"<br>正確答案應為：{correct_answer}"
            else:
                # Fallback if no specific parsing worked but user_answer and correct_answer string match
                if user_answer.strip().lower() == correct_answer.strip().lower():
                    is_correct = True
                    result_text = f"完全正確！答案是 ${correct_answer}$。"

        except Exception:
            # print(f"Error during combined answer check: {e}") # For debugging
            pass

    if not is_correct:
        if not result_text:
            result_text = f"答案不正確。請檢查您的輸入格式是否符合多項式表示法。正確答案應為：{correct_answer}"

    return {"correct": is_correct, "result": result_text, "next_question": True}