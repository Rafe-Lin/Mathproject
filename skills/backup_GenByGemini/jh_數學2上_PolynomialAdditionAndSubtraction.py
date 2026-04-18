import random

# --- Helper Functions for Polynomial Manipulation ---

def _generate_polynomial(max_degree, max_coeff, min_terms, max_terms):
    """
    Generates a random polynomial as a dictionary {degree: coefficient}.
    """
    poly = {}
    # Ensure term count is valid for the given degree
    actual_max_terms = min(max_terms, max_degree + 1)
    actual_min_terms = min(min_terms, actual_max_terms)
    if actual_min_terms > actual_max_terms:
        actual_min_terms = actual_max_terms
    term_count = random.randint(actual_min_terms, actual_max_terms)
    
    # Choose the degrees for the terms
    possible_degrees = list(range(max_degree + 1))
    degrees = random.sample(possible_degrees, term_count)

    for degree in degrees:
        coeff = random.randint(-max_coeff, max_coeff)
        while coeff == 0:
            coeff = random.randint(-max_coeff, max_coeff)
        poly[degree] = coeff
    
    return poly

def _polynomial_to_string(poly_dict, ordered=False, parenthesis=False):
    """
    Converts a polynomial dictionary to a LaTeX string.
    - ordered: If True, format in descending powers (canonical form for answers).
               If False, format in random order (for questions).
    - parenthesis: If True, wrap the polynomial in parentheses.
    """
    if not poly_dict or not any(poly_dict.values()): # Handle zero polynomial
        return "(0)" if parenthesis else "0"

    if ordered:
        degrees = sorted(poly_dict.keys(), reverse=True)
    else:
        degrees = list(poly_dict.keys())
        random.shuffle(degrees)
    
    terms = []
    is_first_term = True
    for deg in degrees:
        coeff = poly_dict.get(deg, 0)
        if coeff == 0:
            continue

        # Sign part
        if is_first_term:
            sign = "-" if coeff < 0 else ""
        else:
            sign = " - " if coeff < 0 else " + "
        
        abs_coeff = abs(coeff)

        # Coefficient part
        if abs_coeff == 1 and deg > 0:
            coeff_str = ""
        else:
            coeff_str = str(abs_coeff)

        # Variable part
        if deg > 1:
            var_str = f"x^{{{deg}}}"
        elif deg == 1:
            var_str = "x"
        else: # deg == 0
            var_str = ""
        
        terms.append(f"{sign}{coeff_str}{var_str}")
        is_first_term = False
    
    result = "".join(terms)
    
    if parenthesis:
        return f"({result})"
    return result

def _add_polynomials(p1, p2):
    """Adds two polynomial dictionaries."""
    result = p1.copy()
    for deg, coeff in p2.items():
        result[deg] = result.get(deg, 0) + coeff
    return {d: c for d, c in result.items() if c != 0}

def _subtract_polynomials(p1, p2):
    """Subtracts polynomial p2 from p1."""
    result = p1.copy()
    for deg, coeff in p2.items():
        result[deg] = result.get(deg, 0) - coeff
    return {d: c for d, c in result.items() if c != 0}

# --- Problem Generation Functions ---

def _generate_addition_problem():
    max_degree = random.choice([2, 2, 3])
    p1 = _generate_polynomial(max_degree, 9, 2, max_degree + 1)
    p2 = _generate_polynomial(max_degree, 9, 2, max_degree + 1)

    p1_str = _polynomial_to_string(p1, ordered=False, parenthesis=True)
    p2_str = _polynomial_to_string(p2, ordered=False, parenthesis=True)
    
    question_text = f"計算 ${p1_str} + {p2_str}$。"
    
    result_poly = _add_polynomials(p1, p2)
    correct_answer = _polynomial_to_string(result_poly, ordered=True)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_subtraction_problem():
    max_degree = random.choice([2, 2, 3])
    p1 = _generate_polynomial(max_degree, 9, 2, max_degree + 1)
    p2 = _generate_polynomial(max_degree, 9, 2, max_degree + 1)

    p1_str = _polynomial_to_string(p1, ordered=False, parenthesis=True)
    p2_str = _polynomial_to_string(p2, ordered=False, parenthesis=True)
    
    question_text = f"計算 ${p1_str} - {p2_str}$。"
    
    result_poly = _subtract_polynomials(p1, p2)
    correct_answer = _polynomial_to_string(result_poly, ordered=True)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_find_poly_add_problem():
    # Find A in A + P = Q  =>  A = Q - P
    max_degree = random.choice([2, 3])
    p = _generate_polynomial(max_degree, 7, 2, max_degree + 1)
    q = _generate_polynomial(max_degree, 7, 2, max_degree + 1)

    p_str = _polynomial_to_string(p, ordered=False, parenthesis=True)
    q_str = _polynomial_to_string(q, ordered=True, parenthesis=False)
    
    question_text = f"若 A 為一多項式，且 $A + {p_str} = {q_str}$，則多項式 A=？"
    
    result_poly = _subtract_polynomials(q, p)
    correct_answer = _polynomial_to_string(result_poly, ordered=True)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_find_poly_sub_problem():
    # Find B in B - P = Q  =>  B = Q + P
    max_degree = random.choice([2, 3])
    p = _generate_polynomial(max_degree, 7, 2, max_degree + 1)
    q = _generate_polynomial(max_degree, 7, 2, max_degree + 1)

    p_str = _polynomial_to_string(p, ordered=False, parenthesis=True)
    q_str = _polynomial_to_string(q, ordered=True, parenthesis=False)
    
    question_text = f"若 B 為一多項式，且 $B - {p_str} = {q_str}$，則多項式 B=？"
    
    result_poly = _add_polynomials(q, p)
    correct_answer = _polynomial_to_string(result_poly, ordered=True)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_mixed_three_problem():
    max_degree = 2
    p1 = _generate_polynomial(max_degree, 5, 2, max_degree + 1)
    p2 = _generate_polynomial(max_degree, 5, 2, max_degree + 1)
    p3 = _generate_polynomial(max_degree, 5, 2, max_degree + 1)
    
    op1 = random.choice(['+', '-'])
    op2 = random.choice(['+', '-'])
    
    p1_str = _polynomial_to_string(p1, ordered=False, parenthesis=True)
    p2_str = _polynomial_to_string(p2, ordered=False, parenthesis=True)
    p3_str = _polynomial_to_string(p3, ordered=False, parenthesis=True)

    question_text = f"計算 ${p1_str} {op1} {p2_str} {op2} {p3_str}$。"
    
    # Calculate result
    if op1 == '+':
        temp_poly = _add_polynomials(p1, p2)
    else:
        temp_poly = _subtract_polynomials(p1, p2)
        
    if op2 == '+':
        result_poly = _add_polynomials(temp_poly, p3)
    else:
        result_poly = _subtract_polynomials(temp_poly, p3)
        
    correct_answer = _polynomial_to_string(result_poly, ordered=True)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Main Functions ---

def generate(level=1):
    """
    生成「多項式加減法」相關題目。
    """
    # A weighted list of problem types. Basic addition/subtraction are more common.
    problem_generators = [
        _generate_addition_problem, _generate_addition_problem, _generate_addition_problem,
        _generate_subtraction_problem, _generate_subtraction_problem, _generate_subtraction_problem,
        _generate_find_poly_add_problem,
        _generate_find_poly_sub_problem,
        _generate_mixed_three_problem
    ]
    
    chosen_generator = random.choice(problem_generators)
    return chosen_generator()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    會先將答案中的空白移除後再進行比對，以允許作答時有彈性的空格。
    """
    # Normalize strings by removing spaces and optional multiplication signs for robustness.
    user_ans_norm = user_answer.replace(" ", "").replace("*", "")
    correct_ans_norm = correct_answer.replace(" ", "").replace("*", "")
    
    is_correct = (user_ans_norm == correct_ans_norm)
    
    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$。<br>提示：請將多項式以次數由高至低排列 (降冪)，並注意正負號。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}