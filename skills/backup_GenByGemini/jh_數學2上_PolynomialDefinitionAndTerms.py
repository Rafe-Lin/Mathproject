import random
from fractions import Fraction

def _build_poly_string(coeffs_dict, order='desc', shuffled=False):
    """
    Helper function to build a polynomial string from a dictionary of coefficients.
    coeffs_dict: {degree: coefficient}
    order: 'desc' (降冪) or 'asc' (升冪)
    shuffled: If True, ignores order and shuffles terms.
    """
    if not coeffs_dict:
        return "0"

    degrees = list(coeffs_dict.keys())
    if shuffled:
        random.shuffle(degrees)
    elif order == 'desc':
        degrees.sort(reverse=True)
    else: # asc
        degrees.sort()

    terms = []
    for i, deg in enumerate(degrees):
        coeff = coeffs_dict[deg]
        if coeff == 0:
            continue

        # --- Sign ---
        sign = ''
        if i > 0:
            sign = ' + ' if coeff > 0 else ' - '
        elif coeff < 0:
            sign = '-'
        
        abs_coeff = abs(coeff)

        # --- Coefficient string ---
        if abs_coeff == 1 and deg > 0:
            coeff_str = ''
        else:
            if isinstance(abs_coeff, Fraction):
                coeff_str = f"\\frac{{{abs_coeff.numerator}}}{{{abs_coeff.denominator}}}"
            else:
                coeff_str = str(abs_coeff)

        # --- Variable string ---
        if deg == 0:
            # Constant term, must show '1' if it is 1.
            var_str = ''
            if coeff_str == '':
                coeff_str = '1'
        elif deg == 1:
            var_str = 'x'
        else:
            var_str = f"x^{{{deg}}}"
        
        # Combine term parts, ensuring no space between coefficient and variable
        term = f"{coeff_str}{var_str}"
        terms.append(f"{sign}{term}")
    
    # Join terms and clean up, e.g., " + -5" becomes " - 5"
    poly_str = "".join(terms).strip()
    if poly_str.startswith('+ '):
        poly_str = poly_str[2:]
        
    return poly_str

def _format_term(coeff, degree):
    """Formats a single term for display."""
    return _build_poly_string({degree: coeff})

def generate_identify_terms_problem():
    """
    Generates a problem asking to identify the degree, coefficients, and constant term.
    """
    degree = random.choice([2, 3])
    coeffs = {}
    
    # Highest degree term must be non-zero
    coeffs[degree] = random.choice([-1, 1]) * random.randint(1, 9)
    
    # Other terms can be zero (missing)
    for d in range(degree - 1, -1, -1):
        if random.random() > 0.2: # High chance of existing
            coeffs[d] = random.randint(-9, 9)
        # else coeff remains 0 (missing)
    
    poly_str = _build_poly_string(coeffs, shuffled=True)
    
    # Determine correct answers
    correct_degree = degree
    coeff_x3 = coeffs.get(3, 0)
    coeff_x2 = coeffs.get(2, 0)
    coeff_x1 = coeffs.get(1, 0)
    const_term = coeffs.get(0, 0)
    
    question_text = f"對於多項式 ${poly_str}$，請完成下列表格中的值。\n"
    question_text += "| 多項式的次數 | $x^3$ 項係數 | $x^2$ 項係數 | $x$ 項係數 | 常數項 |\n"
    question_text += "|---|---|---|---|---|\n"
    question_text += "| ? | ? | ? | ? | ? |\n"
    question_text += "請將 \"?\" 處的值由左至右依序填寫，並用逗號分隔。"
    
    correct_answer = f"{correct_degree},{coeff_x3},{coeff_x2},{coeff_x1},{const_term}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_constant_poly_condition_problem():
    """
    Generates a problem about the conditions for a constant polynomial.
    """
    k1 = random.randint(1, 9)
    k2 = random.randint(1, 9)
    c = random.randint(-9, 9)
    while c == 0:
        c = random.randint(-9, 9)

    # Randomize expressions for a and b
    a_op, b_op = random.choice(['+', '-']), random.choice(['+', '-'])
    
    a_expr = f"(a {a_op} {k1})"
    sol_a = -k1 if a_op == '+' else k1
    
    b_expr = f"(b {b_op} {k2})"
    sol_b = -k2 if b_op == '+' else k2
    
    const_str = f" + {c}" if c > 0 else f" - {-c}"
    
    poly_str = f"{a_expr}x^2 + {b_expr}x{const_str}"

    question_text = f"若多項式 ${poly_str}$ 是一個常數多項式，則 $a$、b$ 兩數的條件為何？\n(請依序回答 a 和 b 的值，並用逗號分隔，例如: 2,-3)"
    correct_answer = f"{sol_a},{sol_b}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_like_terms_problem():
    """
    Generates a problem asking to identify like terms.
    """
    base_degree = random.randint(1, 4)
    base_coeff = random.choice([-1, 1]) * random.randint(2, 9)
    base_term_str = _format_term(base_coeff, base_degree)

    options = []
    correct_indices = []
    
    # Generate 1 or 2 correct like terms
    num_correct = random.randint(1, 2)
    for _ in range(num_correct):
        coeff_type = random.choice(['int', 'frac', 'neg_int'])
        if coeff_type == 'int':
            coeff = random.randint(1, 9)
        elif coeff_type == 'frac':
            coeff = Fraction(random.randint(1, 9), random.randint(2, 5))
        else: # neg_int
            coeff = -random.randint(1, 9)
        options.append({'coeff': coeff, 'degree': base_degree, 'is_like': True})

    # Generate incorrect terms
    while len(options) < 4:
        # Choose a different degree
        degree = random.randint(0, 5)
        if degree == base_degree:
            continue
        coeff = random.choice([-1, 1]) * random.randint(1, 9)
        options.append({'coeff': coeff, 'degree': degree, 'is_like': False})
        
    random.shuffle(options)
    
    # Build question text and find correct answers
    question_parts = [f"下列哪些式子是 ${base_term_str}$ 的同類項？ (請填入選項代號，若有多個請用逗號分隔)"]
    for i, opt in enumerate(options):
        term_str = _format_term(opt['coeff'], opt['degree'])
        question_parts.append(f"({i+1}) ${term_str}$")
        if opt['is_like']:
            correct_indices.append(str(i+1))

    question_text = "\n".join(question_parts)
    correct_answer = "SORTED_LIST:" + ",".join(sorted(correct_indices))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer.replace("SORTED_LIST:", "")
    }

def generate_arrange_poly_problem():
    """
    Generates a problem asking to arrange a polynomial in ascending or descending order.
    """
    degree = random.randint(2, 4)
    coeffs = {}
    
    # Ensure at least 3 non-zero terms for a meaningful shuffle
    num_terms = 0
    while num_terms < 3:
        coeffs.clear()
        coeffs[degree] = random.choice([-1, 1]) * random.randint(1, 9)
        for d in range(degree - 1, -1, -1):
            if random.random() > 0.3:
                c = random.randint(-9, 9)
                if c != 0:
                    coeffs[d] = c
        num_terms = len(coeffs)

    shuffled_poly_str = _build_poly_string(coeffs, shuffled=True)
    
    order_type = random.choice(['升冪', '降冪'])
    order_key = 'asc' if order_type == '升冪' else 'desc'
    
    correct_poly_str = _build_poly_string(coeffs, order=order_key)
    
    question_text = f"請將多項式 ${shuffled_poly_str}$ 按照「{order_type}」的方式排列。"
    correct_answer = f"POLY:{correct_poly_str}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_poly_str
    }

def generate(level=1):
    """
    生成「多項式的定義與名詞」相關題目。
    涵蓋：
    1. 多項式的次數、係數與常數項
    2. 常數多項式的條件
    3. 同類項的判斷
    4. 多項式的升冪與降冪排列
    """
    problem_type = random.choice([
        'identify_terms', 
        'constant_poly_condition', 
        'like_terms', 
        'arrange_poly'
    ])
    
    if problem_type == 'identify_terms':
        return generate_identify_terms_problem()
    elif problem_type == 'constant_poly_condition':
        return generate_constant_poly_condition_problem()
    elif problem_type == 'like_terms':
        return generate_like_terms_problem()
    else: # arrange_poly
        return generate_arrange_poly_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_ans = user_answer.strip()
    
    is_correct = False
    feedback_answer = correct_answer # Default value

    if correct_answer.startswith("SORTED_LIST:"):
        # For like_terms, order of answers doesn't matter
        correct_val = correct_answer.replace("SORTED_LIST:", "")
        feedback_answer = correct_val
        try:
            user_items = sorted([item.strip() for item in user_ans.split(',')])
            correct_items = sorted([item.strip() for item in correct_val.split(',')])
            if user_items == correct_items:
                is_correct = True
        except:
            is_correct = False
    elif correct_answer.startswith("POLY:"):
        # For polynomial arrangement, be lenient with spacing
        correct_val = correct_answer.replace("POLY:", "")
        feedback_answer = correct_val
        # Normalize by removing all spaces and replacing "+-" with "-"
        user_norm = user_ans.replace(' ', '').replace('+-', '-')
        correct_norm = correct_val.replace(' ', '').replace('+-', '-')
        if user_norm == correct_norm:
            is_correct = True
    else:
        # Default is a simple string or comma-separated list where order matters
        feedback_answer = correct_answer
        # Normalize comma-separated list spacing
        user_items = [item.strip() for item in user_ans.split(',')]
        correct_items = [item.strip() for item in correct_answer.split(',')]
        if user_items == correct_items:
            is_correct = True

    result_text = f"完全正確！答案是 ${feedback_answer}$。" if is_correct else f"答案不正確。正確答案應為：${feedback_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}