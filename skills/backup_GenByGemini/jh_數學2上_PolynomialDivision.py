import random
from fractions import Fraction
import math

# --- Polynomial Helper Functions ---

def trim_leading_zeros(coeffs):
    """Removes leading zeros from a coefficient list."""
    if not coeffs or all(c == 0 for c in coeffs):
        return [Fraction(0)]
    
    first_nonzero = 0
    while first_nonzero < len(coeffs) and coeffs[first_nonzero] == 0:
        first_nonzero += 1
    
    return coeffs[first_nonzero:] if first_nonzero < len(coeffs) else [Fraction(0)]


def poly_to_string(coeffs, var='x'):
    """Converts a list of coefficients to a LaTeX formatted polynomial string."""
    coeffs = trim_leading_zeros(coeffs)
    if not coeffs or (len(coeffs) == 1 and coeffs[0] == 0):
        return "0"

    terms = []
    degree = len(coeffs) - 1
    for i, coeff in enumerate(coeffs):
        if coeff == 0:
            continue
        
        power = degree - i
        
        # --- Sign ---
        sign = ""
        if not terms:  # First term
            if coeff < 0:
                sign = "-"
        else:  # Subsequent terms
            sign = " - " if coeff < 0 else " + "
        
        # --- Coefficient ---
        abs_coeff = abs(coeff)
        num, den = abs_coeff.numerator, abs_coeff.denominator
        
        coeff_str = ""
        if den == 1:
            if num != 1 or power == 0:
                coeff_str = str(num)
        else:
            coeff_str = f"\\frac{{{num}}}{{{den}}}"

        # --- Variable ---
        var_str = ""
        if power > 0:
            var_str = var if power == 1 else f"{var}^{{{power}}}"
            
        # --- Combine ---
        if coeff_str and var_str:
            terms.append(f"{sign}{coeff_str}{var_str}")
        else:
            terms.append(f"{sign}{coeff_str or var_str}")

    result = "".join(terms).strip()
    if result.startswith("+"):
        result = result[1:].strip()
    return result

def poly_add(p1, p2):
    """Adds two polynomials."""
    len1, len2 = len(p1), len(p2)
    new_coeffs = [Fraction(0)] * max(len1, len2)
    
    for i in range(len1):
        new_coeffs[i + max(len1, len2) - len1] += p1[i]
    for i in range(len2):
        new_coeffs[i + max(len1, len2) - len2] += p2[i]
        
    return trim_leading_zeros(new_coeffs)

def poly_sub(p1, p2):
    """Subtracts p2 from p1."""
    neg_p2 = [-c for c in p2]
    return poly_add(p1, neg_p2)

def poly_mul(p1, p2):
    """Multiplies two polynomials."""
    len1, len2 = len(p1), len(p2)
    new_deg = len1 + len2 - 2
    new_coeffs = [Fraction(0)] * (new_deg + 1)
    
    for i in range(len1):
        for j in range(len2):
            new_coeffs[i + j] += p1[i] * p2[j]
    
    return trim_leading_zeros(new_coeffs)

def poly_div(dividend, divisor):
    """Performs polynomial division. Returns (quotient, remainder)."""
    dividend = trim_leading_zeros([Fraction(c) for c in dividend])
    divisor = trim_leading_zeros([Fraction(c) for c in divisor])

    if not divisor or divisor == [Fraction(0)]:
        raise ZeroDivisionError("Polynomial division by zero")

    if len(dividend) < len(divisor):
        return [Fraction(0)], dividend
        
    remainder = list(dividend)
    quotient = [Fraction(0)]
    
    while len(remainder) >= len(divisor) and remainder != [Fraction(0)]:
        lead_rem_coeff = remainder[0]
        lead_div_coeff = divisor[0]
        
        deg_rem = len(remainder) - 1
        deg_div = len(divisor) - 1
        
        term_coeff = lead_rem_coeff / lead_div_coeff
        term_deg_diff = deg_rem - deg_div
        
        quotient_term = [term_coeff] + [Fraction(0)] * term_deg_diff
        quotient = poly_add(quotient, quotient_term)
        
        subtrahend = poly_mul(quotient_term, divisor)
        remainder = poly_sub(remainder, subtrahend)
    
    return trim_leading_zeros(quotient), trim_leading_zeros(remainder)

def generate_polynomial(max_deg, coeff_range=(-5, 5), zero_prob=0.2, is_monic=False):
    """Generates a random polynomial."""
    deg = random.randint(1, max_deg)
    coeffs = []
    
    # Leading coefficient
    if is_monic:
        lead_coeff = 1
    else:
        lead_coeff = random.choice([i for i in range(coeff_range[0], coeff_range[1] + 1) if i != 0])
    coeffs.append(Fraction(lead_coeff))
    
    # Other coefficients
    for _ in range(deg):
        if random.random() < zero_prob:
            coeffs.append(Fraction(0))
        else:
            coeffs.append(Fraction(random.randint(coeff_range[0], coeff_range[1])))
            
    return trim_leading_zeros(coeffs)

# --- Problem Generation Functions ---

def generate_division_problem(level=1):
    """Generates a polynomial division problem."""
    # level 1: monomial/monomial or simple poly/monomial
    if level == 1:
        c1 = random.randint(2, 10)
        c2 = random.randint(2, 5)
        d1 = random.randint(2, 5)
        d2 = random.randint(1, d1)
        
        # Ensure integer division for simplicity
        c1 = c1 * c2
        dividend = [c1] + [0] * d1
        divisor = [c2] + [0] * d2
        if random.random() < 0.5: # sometimes add a term to dividend
            dividend[random.randint(1, len(dividend)-2)] = random.randint(-5, 5) * c2
        
    # level 2: poly/binomial, integer quotient/remainder, no missing terms
    elif level == 2:
        deg_q = 1
        deg_d = 1
        quotient = generate_polynomial(deg_q, coeff_range=(-3, 3), zero_prob=0)
        divisor = generate_polynomial(deg_d, coeff_range=(-3, 3), zero_prob=0, is_monic=True)
        remainder_val = random.randint(-10, 10)
        remainder = [Fraction(remainder_val)]
        dividend = poly_add(poly_mul(quotient, divisor), remainder)
    
    # level 3: higher degree, missing terms
    elif level == 3:
        deg_q = random.randint(1, 2)
        deg_d = random.randint(1, 2)
        quotient = generate_polynomial(deg_q, coeff_range=(-4, 4), zero_prob=0.3)
        divisor = generate_polynomial(deg_d, coeff_range=(-4, 4), zero_prob=0.3)
        rem_deg = random.randint(0, len(divisor) - 2)
        remainder = generate_polynomial(rem_deg, coeff_range=(-10, 10), zero_prob=0.5) if rem_deg > 0 else [Fraction(random.randint(-10, 10))]
        dividend = poly_add(poly_mul(quotient, divisor), remainder)
        
    # level 4: divisor might need reordering, quotient can be constant or fractional
    else:
        deg_p = random.randint(2, 3)
        deg_d = random.randint(deg_p, deg_p + 1) # Force degree of dividend <= divisor
        dividend = generate_polynomial(deg_p, coeff_range=(-9, 9), zero_prob=0.2)
        divisor = generate_polynomial(deg_d, coeff_range=(-5, 5), zero_prob=0.2)
        if random.random() < 0.5: # mess up order
            shuffled_divisor = list(divisor)
            random.shuffle(shuffled_divisor)
            # This is a bit naive, proper reordering representation is harder
            # For now, just generate a normal problem with higher difficulty
            deg_d = random.randint(1,2)
            dividend = generate_polynomial(random.randint(deg_d, 3), coeff_range=(-7, 7), zero_prob=0.3)
            divisor = generate_polynomial(deg_d, coeff_range=(-5,5), zero_prob=0.2)


    # Calculate true quotient and remainder
    q_coeffs, r_coeffs = poly_div(dividend, divisor)

    p_str = poly_to_string(dividend)
    d_str = poly_to_string(divisor)
    q_str = poly_to_string(q_coeffs)
    r_str = poly_to_string(r_coeffs)
    
    question_text = f"求 ($ {p_str} $) ÷ ($ {d_str} $) 的商式與餘式。"
    correct_answer = f"商式為{q_str}，餘式為{r_str}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_dividend_problem(level=1):
    """Generates a P = Q * D + R problem."""
    if level <= 2:
        deg_q = 1
        deg_d = random.randint(1, 2)
        rem_deg_max = len(generate_polynomial(deg_d, is_monic=True)) - 2
    else:
        deg_q = random.randint(1, 2)
        deg_d = random.randint(1, 2)
        rem_deg_max = len(generate_polynomial(deg_d)) - 2

    quotient = generate_polynomial(deg_q, coeff_range=(-5, 5), zero_prob=0.2)
    divisor = generate_polynomial(deg_d, coeff_range=(-5, 5), zero_prob=0.2, is_monic=(level<=2))
    rem_deg = random.randint(0, rem_deg_max) if rem_deg_max >= 0 else 0
    remainder = generate_polynomial(rem_deg, coeff_range=(-10, 10)) if rem_deg > 0 else [Fraction(random.randint(-10, 10))]

    dividend = poly_add(poly_mul(quotient, divisor), remainder)
    
    p_str = poly_to_string(dividend)
    q_str = poly_to_string(quotient)
    d_str = poly_to_string(divisor)
    r_str = poly_to_string(remainder)
    
    question_text = f"如果一個多項式 A 除以 ($ {d_str} $) 的商式為 ($ {q_str} $)，餘式為 ($ {r_str} $)，試求此多項式 A。"
    correct_answer = p_str

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_divisor_problem(level=1):
    """Generates a D = (P - R) / Q problem."""
    if level <= 2:
        deg_q = 1
        deg_d = 1
    else:
        deg_q = random.randint(1, 2)
        deg_d = random.randint(1, 2)

    # We generate Q and D first to ensure clean division
    quotient = generate_polynomial(deg_q, coeff_range=(-4, 4), zero_prob=0.1)
    divisor = generate_polynomial(deg_d, coeff_range=(-4, 4), zero_prob=0.1, is_monic=True)
    
    rem_deg_max = len(divisor) - 2
    rem_deg = random.randint(0, rem_deg_max) if rem_deg_max >= 0 else 0
    remainder = generate_polynomial(rem_deg, coeff_range=(-10, 10)) if rem_deg > 0 else [Fraction(random.randint(-10, 10))]
    
    dividend = poly_add(poly_mul(quotient, divisor), remainder)
    
    p_str = poly_to_string(dividend)
    q_str = poly_to_string(quotient)
    d_str = poly_to_string(divisor)
    r_str = poly_to_string(remainder)

    question_text = f"已知 ($ {p_str} $) 除以另一個多項式 B 後，得到商式為 ($ {q_str} $)，餘式為 ($ {r_str} $)，試求此多項式 B。"
    correct_answer = d_str

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a problem for polynomial division.
    - Level 1 & 2 focus on direct division with integer results.
    - Level 3 introduces missing terms and more complex scenarios.
    - Level 4 can involve fractional results or reordering.
    """
    problem_type = random.choice(['division'] * 4 + ['find_dividend', 'find_divisor'])
    
    # Adjust level for problem types
    if problem_type == 'division':
        effective_level = random.randint(1, 4)
        return generate_division_problem(effective_level)
    elif problem_type == 'find_dividend':
        effective_level = random.randint(1, 3)
        return generate_find_dividend_problem(effective_level)
    else: # find_divisor
        effective_level = random.randint(1, 3)
        return generate_find_divisor_problem(effective_level)

def normalize_answer(ans_str):
    """Normalizes a polynomial string for comparison."""
    # Full-width to half-width for common characters
    full_width = "＋－（），：ｘ"
    half_width = "+-():x"
    trans_table = str.maketrans(full_width, half_width)
    
    s = ans_str.strip().translate(trans_table)
    s = s.replace(" ", "")
    s = s.replace("商式為", "")
    s = s.replace("餘式為", ",")
    s = s.replace("商式:", "")
    s = s.replace("餘式:", ",")
    s = s.lower()
    return s

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    """
    user_norm = normalize_answer(user_answer)
    correct_norm = normalize_answer(correct_answer)
    
    is_correct = (user_norm == correct_norm)
    
    # Generate display-friendly correct answer with LaTeX
    # Find dividend/divisor answers are just polynomials
    if "商式為" not in correct_answer:
        feedback_answer = f"${correct_answer}$"
    else: # Division problems have a specific format
        # Example: "商式為x+2，餘式為-2"
        parts = correct_answer.replace("商式為", "").split("，餘式為")
        q_part = parts[0]
        r_part = parts[1]
        feedback_answer = f"商式為 ${q_part}$，餘式為 ${r_part}$"

    if is_correct:
        result_text = f"完全正確！答案是 {feedback_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{feedback_answer}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}