import random
from fractions import Fraction

# Helper to format a full polynomial from a list of (coefficient, power) tuples into a LaTeX string.
# Example: [(Fraction(1,1), 2), (Fraction(5,1), 1), (Fraction(-4,1), 0)] -> "x^{2} + 5x - 4"
# With general_constant="C" for antiderivatives: "x^{2} + 5x - 4 + C"
def format_polynomial(terms, general_constant=None):
    # Filter out terms with zero coefficients
    filtered_terms = [t for t in terms if t[0] != 0]
    # Sort terms by power in descending order
    terms = sorted(filtered_terms, key=lambda x: x[1], reverse=True)

    poly_str_parts = []
    
    for i, (coeff, power) in enumerate(terms):
        part = ""
        abs_coeff = abs(coeff)

        # Determine sign for the term
        if coeff < 0:
            part += "- "
        elif i > 0: # Only add '+' if it's not the first term and positive
            part += "+ "

        # Handle coefficient part (e.g., fractions, '1' for 1x vs constant '1')
        if isinstance(abs_coeff, Fraction) and abs_coeff.denominator != 1:
            if abs_coeff.numerator == 1 and power > 0: # For terms like x/2, display as \\frac{1}{2}x
                 part += r"\\frac{{1}}{{{}}}".format(abs_coeff.denominator)
            else: # General fraction
                 part += r"\\frac{{{}}}{{{}}}".format(abs_coeff.numerator, abs_coeff.denominator)
        elif abs_coeff != 1 or power == 0: # Don't print '1' for 1x, 1x^2 etc. unless it's a constant term (power == 0)
             part += str(int(abs_coeff))

        # Handle variable part (x, x^2, etc.)
        if power == 1:
            part += "x"
        elif power > 1:
            part += f"x^{{{power}}}"

        poly_str_parts.append(part)

    poly_str = "".join(poly_str_parts).strip()

    # Handle the constant part (either arbitrary 'C' or a specific numeric value)
    if general_constant is not None:
        if general_constant == "C": # For general antiderivative
             poly_str += " + C"
        elif general_constant != 0: # For specific numeric constant (integer or fraction)
            if isinstance(general_constant, Fraction) and general_constant.denominator != 1:
                if general_constant < 0:
                    poly_str += f" - {r'\\frac{{{}}}{{{}}}'.format(abs(general_constant).numerator, abs(general_constant).denominator)}"
                else:
                    poly_str += f" + {r'\\frac{{{}}}{{{}}}'.format(general_constant.numerator, general_constant.denominator)}"
            else: # Integer constant or Fraction with denominator 1
                const_val = int(general_constant)
                if const_val < 0:
                    poly_str += f" - {abs(const_val)}"
                else:
                    poly_str += f" + {const_val}"
    
    # Special case: If the polynomial part is entirely zero, return just the constant
    if not poly_str:
        if general_constant is None or (isinstance(general_constant, (int, Fraction)) and general_constant == 0):
            return "0"
        elif general_constant == "C": # F(x) = C
            return "C"
        elif isinstance(general_constant, Fraction) and general_constant.denominator != 1:
            if general_constant < 0:
                 return f"-{r'\\frac{{{}}}{{{}}}'.format(abs(general_constant).numerator, abs(general_constant).denominator)}"
            else:
                 return r"\\frac{{{}}}{{{}}}".format(general_constant.numerator, general_constant.denominator)
        else: # Specific integer constant
            if int(general_constant) < 0:
                return f"-{abs(int(general_constant))}"
            else:
                return str(int(general_constant))
    
    # Remove leading "- " if present, replace with just "-"
    if poly_str.startswith("- "):
        poly_str = "-" + poly_str[2:]
        
    return poly_str.strip()

# Helper function to calculate the antiderivative of a single term (coeff, power)
def integrate_term(coeff, power):
    if coeff == 0:
        return (Fraction(0), 0) # Zero coefficient results in a zero term

    new_power = power + 1
    new_coeff = Fraction(coeff, new_power)
    return (new_coeff, new_power)

# Helper function to generate random integer coefficients based on level
def get_random_coeff_int(level):
    if level == 1:
        return random.randint(-4, 4) 
    elif level == 2:
        return random.randint(-6, 6)
    else: # level 3
        return random.randint(-8, 8)

def generate(level=1):
    """
    Generates a problem for finding the antiderivative of a polynomial function.
    Problems can be either finding all antiderivatives (with + C) or a specific one
    given an initial condition F(x0) = y0.
    """
    problem_type = random.choice(['general_antiderivative', 'specific_antiderivative'])

    if problem_type == 'general_antiderivative':
        return generate_general_antiderivative_problem(level)
    else:
        return generate_specific_antiderivative_problem(level)

def generate_general_antiderivative_problem(level):
    """
    Generates a problem to find all antiderivatives of a polynomial.
    """
    # Determine the degree of the polynomial based on level
    # Max degree 2 for level 1, 3 for level 2, 4 for level 3
    degree = random.randint(0, min(level + 2, 4)) 
    
    coeffs = []
    has_nonzero = False
    for i in range(degree, -1, -1):
        coeff = get_random_coeff_int(level)
        if coeff != 0:
            has_nonzero = True
        coeffs.append((coeff, i))
    
    # Ensure at least one non-zero term in the polynomial
    if not has_nonzero:
        idx_to_change = random.randint(0, len(coeffs) - 1)
        new_coeff = random.choice([c for c in range(-5, 6) if c != 0])
        coeffs[idx_to_change] = (new_coeff, coeffs[idx_to_change][1])

    function_terms = [(Fraction(c[0]), c[1]) for c in coeffs]
    function_str = format_polynomial(function_terms) # Format the original function f(x)
    
    # Calculate the antiderivative for each term
    antiderivative_terms = []
    for coeff, power in function_terms:
        antiderivative_terms.append(integrate_term(coeff, power))

    # Format the general antiderivative, including the arbitrary constant 'C'
    correct_antiderivative_str = format_polynomial(antiderivative_terms, general_constant="C")

    question_text = f"求 $f(x) = {function_str}$ 的所有反導函數。"
    
    # Generate a canonical form for the answer for robust checking (no spaces, standard frac, capital C)
    canonical_answer = correct_antiderivative_str.replace(" ", "").replace(r"\\ ", "").replace(r"\\frac", r"\\frac").replace(r"\\", "\\").replace("C", "C")

    return {
        "question_text": question_text,
        "answer": correct_antiderivative_str, # This is the display answer for the user
        "correct_answer": canonical_answer # This is the internal canonical form for checking
    }

def generate_specific_antiderivative_problem(level):
    """
    Generates a problem to find a specific antiderivative given an initial condition.
    """
    degree = random.randint(0, min(level + 2, 4))
    
    coeffs = []
    has_nonzero = False
    for i in range(degree, -1, -1):
        coeff = get_random_coeff_int(level)
        if coeff != 0:
            has_nonzero = True
        coeffs.append((coeff, i))
    
    if not has_nonzero:
        idx_to_change = random.randint(0, len(coeffs) - 1)
        new_coeff = random.choice([c for c in range(-5, 6) if c != 0])
        coeffs[idx_to_change] = (new_coeff, coeffs[idx_to_change][1])

    function_terms = [(Fraction(c[0]), c[1]) for c in coeffs]
    function_str = format_polynomial(function_terms)

    # Generate an initial condition F(x_val) = y_val
    x_val = random.randint(-2, 2)
    # For higher levels, avoid x_val = 0 if it simplifies calculations too much
    if level >= 2 and x_val == 0:
        x_val = random.choice([-2, -1, 1, 2])
    
    # Calculate the general antiderivative terms
    antiderivative_terms = []
    for coeff, power in function_terms:
        antiderivative_terms.append(integrate_term(coeff, power))

    # Evaluate the sum of the antiderivative terms at x_val (before adding C)
    f_x_val_sum = Fraction(0)
    for coeff, power in antiderivative_terms:
        term_val = coeff * (Fraction(x_val)**power if power > 0 else Fraction(1))
        f_x_val_sum += term_val

    # Determine a desired value for C
    desired_c = Fraction(get_random_coeff_int(level))
    if level >= 2 and random.random() < 0.4: # Introduce fractional C more often for higher levels
        denominator_options = [2, 3, 4]
        if level == 3: denominator_options.extend([5, 6])
        
        temp_c = Fraction(random.randint(-5, 5), random.choice(denominator_options))
        # Ensure it's actually a non-integer fraction or not 0 (unless f(x) was 0)
        while temp_c.denominator == 1 and temp_c != 0:
            temp_c = Fraction(random.randint(-5, 5), random.choice(denominator_options))
        desired_c = temp_c
        
        # If all terms in antiderivative are zero, F(x) should be just C. Ensure C is non-zero.
        if all(t[0] == 0 for t in antiderivative_terms) and desired_c == 0:
            desired_c = Fraction(random.choice([-1, 1, Fraction(1,2), Fraction(-1,2)]))

    # Calculate y_val for the initial condition: y_val = F(x_val) = f_x_val_sum + C
    y_val = f_x_val_sum + desired_c 
    
    # Format the specific antiderivative using the calculated C
    correct_antiderivative_str = format_polynomial(antiderivative_terms, general_constant=desired_c) 

    # Format y_val for display in the question
    y_val_str = str(y_val)
    if isinstance(y_val, Fraction) and y_val.denominator != 1:
        y_val_str = r"\\frac{{{}}}{{{}}}".format(y_val.numerator, y_val.denominator)
    elif isinstance(y_val, Fraction) and y_val.denominator == 1:
        y_val_str = str(int(y_val))

    question_text = f"已知 $F(x)$ 為 $f(x) = {function_str}$ 的一個反導函數且 $F({x_val}) = {y_val_str}$，求 $F(x)$。"
    
    # Generate a canonical form for checking
    canonical_answer = correct_antiderivative_str.replace(" ", "").replace(r"\\ ", "").replace(r"\\frac", r"\\frac").replace(r"\\", "\\")

    return {
        "question_text": question_text,
        "answer": correct_antiderivative_str,
        "correct_answer": canonical_answer
    }

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    It normalizes both the user's answer and the correct answer for comparison.
    For general antiderivatives, it handles variations in 'C' (case, spaces).
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip() # This is the canonical form from generate function

    is_correct = False
    feedback = ""

    # Normalize user answer: remove spaces, standardize LaTeX fraction format if possible, handle 'C' case
    normalized_user_answer = user_answer.replace(" ", "").replace(r"\\ ", "")

    # If the correct answer contains '+C', it's a general antiderivative problem
    if "+C" in correct_answer:
        # Check if user answer also contains some form of '+C'
        if "+C" in normalized_user_answer:
            # If user used '+C', convert '+c' to '+C' to allow case-insensitivity for 'C'
            normalized_user_answer = normalized_user_answer.replace("+c", "+C")
            if normalized_user_answer == correct_answer:
                is_correct = True
            else:
                feedback = f"您計算的反導函數部分可能不正確，或 $C$ 的寫法有誤。正確答案應為：${correct_answer}$"
        elif "+c" in normalized_user_answer: # Check if user used lowercase '+c'
            normalized_user_answer = normalized_user_answer.replace("+c", "+C")
            if normalized_user_answer == correct_answer:
                is_correct = True
            else:
                feedback = f"您計算的反導函數部分可能不正確。正確答案應為：${correct_answer}$"
        else: # '+C' or '+c' is missing or formatted incorrectly after normalization
            feedback = f"您的答案缺少了任意常數 $C$，或者其寫法有誤。正確答案應為：${correct_answer}$"
    else: # This is a specific antiderivative problem, strict comparison is required
        if normalized_user_answer == correct_answer:
            is_correct = True
        else:
            feedback = f"答案不正確。正確答案應為：${correct_answer}$"

    if is_correct:
        feedback = "完全正確！"
    elif not feedback: # If feedback not set yet, it means the polynomial content itself mismatched
        feedback = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": feedback, "next_question": True}