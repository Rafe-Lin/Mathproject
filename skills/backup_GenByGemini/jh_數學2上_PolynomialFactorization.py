import random
import re

# --- Helper functions to format polynomials into strings ---

def format_term(coeff, var_str, is_first_term):
    """Formats a single term of a polynomial (e.g., + 5x, -x^2, - 7)."""
    if coeff == 0:
        return ""

    # Determine the sign
    sign = ""
    if is_first_term:
        if coeff < 0:
            sign = "-"
    else:
        sign = "+ " if coeff > 0 else "- "

    # Determine the coefficient string
    coeff_abs = abs(coeff)
    if coeff_abs == 1 and var_str:
        coeff_str = ""
    else:
        coeff_str = str(coeff_abs)

    return f"{sign}{coeff_str}{var_str}"

def poly_to_string(coeffs):
    """Converts polynomial coefficients [A, B, C] to a string Ax^2 + Bx + C."""
    A, B, C = coeffs
    
    term_a_str = format_term(A, "x^2", True)
    term_b_str = format_term(B, "x", A == 0)
    term_c_str = format_term(C, "", A == 0 and B == 0)

    full_string = f"{term_a_str} {term_b_str} {term_c_str}".strip()
    # Clean up spacing and signs, e.g., "x^2 + -5x" becomes "x^2 - 5x"
    cleaned_string = re.sub(r'\s+', ' ', full_string).replace(" + - ", " - ")
    return cleaned_string if cleaned_string else "0"


def linear_poly_to_string(a, b):
    """Converts linear polynomial coefficients (a, b) to a string ax + b."""
    # a can be an int, b can be an int or a string 'm'
    
    if a == 1:
        term1 = "x"
    elif a == -1:
        term1 = "-x"
    elif a == 0:
        term1 = ""
    else:
        term1 = f"{a}x"

    if b == 0:
        return term1 if term1 else "0"
    
    if isinstance(b, str): # For the 'find_m' case
        return f"{term1} + {b}" if term1 else b

    if b > 0:
        term2 = f"+ {b}"
    else:
        term2 = f"- {abs(b)}"
        
    if not term1:
        return str(b)

    return f"{term1} {term2}"

# --- Problem generation functions ---

def generate_is_factor_and_factorize():
    """
    Generates a problem asking to verify a factor and perform factorization.
    e.g., "判別 2x+3 是不是 6x^2+5x-6 的因式。若是，則將 6x^2+5x-6 因式分解。"
    """
    # Generate two linear factors (ax+b) and (cx+d)
    a = random.randint(1, 4)
    c = random.randint(1, 4)
    b = random.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
    d = random.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])

    # Expand to get the quadratic polynomial P(x) = Ax^2 + Bx + C
    A = a * c
    B = a * d + b * c
    C = b * d
    
    poly_p_str = poly_to_string([A, B, C])
    
    # Decide whether the given polynomial is a real factor or a decoy
    is_factor = random.random() < 0.75

    if is_factor:
        # Randomly choose which factor to present in the question
        factors = [(a, b), (c, d)]
        random.shuffle(factors)
        given_factor_poly, other_factor_poly = factors[0], factors[1]
        
        given_factor_str = linear_poly_to_string(*given_factor_poly)
        other_factor_str = linear_poly_to_string(*other_factor_poly)
        
        question_text = f"判別 ${given_factor_str}$ 是不是 ${poly_p_str}$ 的因式。若是，則將 ${poly_p_str}$ 因式分解。"
        correct_answer = f"是，${poly_p_str}=({given_factor_str})({other_factor_str})$"
    else:
        # Create a decoy factor by slightly changing one of the real factors
        decoy_b = b + random.choice([-2, -1, 1, 2])
        # Ensure the decoy is not 0 and not the same as the original
        while decoy_b == 0 or decoy_b == b:
            decoy_b = b + random.choice([-2, -1, 1, 2])
            
        decoy_factor_str = linear_poly_to_string(a, decoy_b)
        
        question_text = f"判別 ${decoy_factor_str}$ 是不是 ${poly_p_str}$ 的因式。若是，則將 ${poly_p_str}$ 因式分解。"
        correct_answer = "否"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_missing_coefficient():
    """
    Generates a problem asking to find a missing coefficient in a factorization.
    e.g., "已知 2x^2+3x+1 可因式分解成 (2x+1)(x+m)，則 m 為多少？"
    """
    a = random.randint(1, 3)
    c = random.randint(1, 3)
    b = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
    d = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
    
    A = a * c
    B = a * d + b * c
    C = b * d
    
    poly_p_str = poly_to_string([A, B, C])
    
    # Randomly choose which constant term to hide (b or d)
    if random.random() < 0.5:
        # Hide d
        factor1_partial = linear_poly_to_string(a, b)
        factor2_partial = linear_poly_to_string(c, 'm')
        correct_m = d
    else:
        # Hide b
        factor1_partial = linear_poly_to_string(a, 'm')
        factor2_partial = linear_poly_to_string(c, d)
        correct_m = b

    question_text = f"已知多項式 ${poly_p_str}$ 可因式分解成 $({factor1_partial})({factor2_partial})$，則 m 為多少？"
    correct_answer = f"m={correct_m}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
# --- Main generator and checker functions ---

def generate(level=1):
    """
    Generates a problem for the 'PolynomialFactorization' skill.
    
    Two types of problems are generated:
    1.  Verify if a linear polynomial is a factor of a quadratic one and provide the full factorization.
    2.  Find a missing coefficient in a given partial factorization.
    """
    problem_type = random.choice(['is_factor_and_factorize', 'find_missing_coefficient'])
    
    if problem_type == 'is_factor_and_factorize':
        return generate_is_factor_and_factorize()
    else:
        return generate_find_missing_coefficient()

def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct one.
    Handles different answer formats: "否", "m=5", and full factorization.
    For factorization, the order of factors does not matter.
    """
    user_answer = user_answer.strip()
    is_correct = False

    def normalize(s):
        """Removes spaces and standardizes math operators for comparison."""
        return s.replace(" ", "").replace("＋", "+").replace("－", "-")

    # Case 1: Find missing coefficient (e.g., correct_answer="m=5")
    if correct_answer.startswith("m="):
        correct_val = correct_answer.split('=')[1]
        user_val = user_answer.replace("m=", "").strip()
        is_correct = (user_val == correct_val)
    
    # Case 2: Answer is "No" (e.g., correct_answer="否")
    elif correct_answer == "否":
        is_correct = (user_answer == "否")
        
    # Case 3: Full factorization (e.g., correct_answer="是，$P=(F1)(F2)$")
    elif correct_answer.startswith("是"):
        # Check if the user response includes "是"
        if "是" not in user_answer:
            is_correct = False
        else:
            try:
                # Extract the two factors from the correct answer string
                factors_correct = re.findall(r'\((.*?)\)', correct_answer)
                f1_norm = normalize(factors_correct[0])
                f2_norm = normalize(factors_correct[1])
                
                # Check if the user's answer contains both normalized factors
                user_answer_norm = normalize(user_answer)
                if f1_norm in user_answer_norm and f2_norm in user_answer_norm:
                    is_correct = True
            except (IndexError, TypeError):
                # Fallback to a simple string comparison if regex/parsing fails
                is_correct = (normalize(user_answer) == normalize(correct_answer))
    
    # Format feedback message
    if correct_answer == "否":
        result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}。"
    else:
        # Wrap mathematical answers in LaTeX delimiters
        result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}