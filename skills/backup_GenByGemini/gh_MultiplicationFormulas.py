import random
from fractions import Fraction
import re # For cleaning up algebraic expressions

# Helper function to format a single term (coefficient * variables)
def _format_term(coeff, var_powers):
    """
    Formats a single algebraic term, handling coefficients of 1, -1, and exponents.
    coeff: integer coefficient
    var_powers: dict like {'x': 2, 'y': 1}
    Returns: string like '3x^2y', '-y^3', 'x'
    """
    if coeff == 0:
        return ""

    term_parts = []

    # Sort variables for consistent output (e.g., 'ab' instead of 'ba')
    sorted_vars = sorted(var_powers.keys())

    # Format coefficient
    if coeff == 1:
        coeff_str = ""
    elif coeff == -1:
        coeff_str = "-"
    else:
        coeff_str = str(coeff)

    # Format variables with exponents
    for var in sorted_vars:
        power = var_powers[var]
        if power == 0:
            continue
        elif power == 1:
            term_parts.append(var)
        else:
            term_parts.append(f"{var}^{power}")

    # Special case: if coefficient is not 1 or -1, prepend it
    if coeff_str not in ["", "-"]:
        return coeff_str + "".join(term_parts)
    elif coeff_str == "-":
        return "-" + "".join(term_parts) if term_parts else "-1" # e.g. -x, -1
    else: # coeff_str is "" (coeff == 1)
        return "".join(term_parts) if term_parts else "1" # e.g. x, 1

# Helper function to format a polynomial from a dictionary of terms
def _format_polynomial(terms_dict):
    """
    Formats a polynomial from a dictionary of term_signature: coefficient.
    e.g., {'x^2': 1, 'xy': -4, 'y^2': 4} -> 'x^2-4xy+4y^2'
    term_signature: string representing the variable part (e.g., 'x^2', 'xy', 'y^3')
    """
    # Create a list of (coefficient, var_powers_dict, original_signature)
    processed_terms = []
    for signature, coeff in terms_dict.items():
        if coeff == 0:
            continue
        var_powers = {}
        # Parse signature to extract variables and their powers
        # This regex assumes 'x^2y' or 'x' or 'y^3' etc.
        parts = re.findall(r'([a-zA-Z])(?:\^(\d+))?', signature)
        total_degree = 0
        for var, power_str in parts:
            power = int(power_str) if power_str else 1
            var_powers[var] = power
            total_degree += power
        
        # Add a placeholder for constant terms to ensure correct sorting later
        if signature == "1": # Constant term
            total_degree = 0 # Assign degree 0 for constants
            var_powers = {}

        processed_terms.append((coeff, var_powers, signature, total_degree))

    # Sort terms for canonical representation:
    # 1. By total degree (descending)
    # 2. By alphabetical order of original signature (for ties in degree)
    # Example: x^2, y^2, z^2, xy, xz, yz, x, y, z, constant
    processed_terms.sort(key=lambda x: (-x[3], x[2])) # -x[3] for descending degree, x[2] for alphabetical signature

    formatted_parts = []
    for i, (coeff, var_powers, _, _) in enumerate(processed_terms):
        term_str = _format_term(coeff, var_powers)
        if not term_str: # Skip zero terms
            continue

        if i > 0 and not term_str.startswith('-'):
            formatted_parts.append(f"+{term_str}")
        else:
            formatted_parts.append(term_str)

    if not formatted_parts:
        return "0"
    return "".join(formatted_parts)

# Function to add/combine terms in a polynomial dictionary
def _add_to_poly_dict(poly_dict, signature, coeff):
    poly_dict[signature] = poly_dict.get(signature, 0) + coeff

# --- Problem Type Generators ---

# 1. Expand (A +/- B)^2 + (C +/- D)^2 or (A +/- B)(A +/- B)
def _generate_expand_quadratic_sum_diff_problem():
    vars_pool = ['a', 'b'] # Keep it simple for now with two variables
    
    # Generate (A +/- B)^2
    var_a, var_b = random.sample(vars_pool, 2)
    coeff_a = random.randint(1, 3)
    coeff_b = random.randint(1, 3)
    op1 = random.choice(['+', '-'])

    A_str = f"{coeff_a}{var_a}" if coeff_a != 1 else var_a
    B_str = f"{coeff_b}{var_b}" if coeff_b != 1 else var_b
    
    # Generate (C +/- D)^2 or just another (A +/- B)^2
    choice = random.choice([1, 2])
    if choice == 1: # (A +/- B)^2 + (C +/- D)^2
        var_c, var_d = random.sample(vars_pool, 2)
        coeff_c = random.randint(1, 3)
        coeff_d = random.randint(1, 3)
        op2 = random.choice(['+', '-'])
        C_str = f"{coeff_c}{var_c}" if coeff_c != 1 else var_c
        D_str = f"{coeff_d}{var_d}" if coeff_d != 1 else var_d
        
        question_expr = f"({A_str}{op1}{B_str})^2 + ({C_str}{op2}{D_str})^2"
        
        # Calculate expansion for (A_str +/- B_str)^2
        poly_dict = {}
        # (c_a*va)^2
        _add_to_poly_dict(poly_dict, f"{var_a}^2", coeff_a**2)
        # 2*(c_a*va)*(c_b*vb)
        _add_to_poly_dict(poly_dict, "".join(sorted([var_a, var_b])), 2 * coeff_a * coeff_b * (1 if op1 == '+' else -1))
        # (c_b*vb)^2
        _add_to_poly_dict(poly_dict, f"{var_b}^2", coeff_b**2)

        # Calculate expansion for (C_str +/- D_str)^2
        _add_to_poly_dict(poly_dict, f"{var_c}^2", coeff_c**2)
        _add_to_poly_dict(poly_dict, "".join(sorted([var_c, var_d])), 2 * coeff_c * coeff_d * (1 if op2 == '+' else -1))
        _add_to_poly_dict(poly_dict, f"{var_d}^2", coeff_d**2)

    else: # (A +/- B)^2 + (A +/- B)^2 (just different coeffs/ops) - simpler
        coeff_a_2 = random.randint(1, 3)
        coeff_b_2 = random.randint(1, 3)
        op2 = random.choice(['+', '-'])
        A_str_2 = f"{coeff_a_2}{var_a}" if coeff_a_2 != 1 else var_a
        B_str_2 = f"{coeff_b_2}{var_b}" if coeff_b_2 != 1 else var_b
        
        question_expr = f"({A_str}{op1}{B_str})^2 + ({A_str_2}{op2}{B_str_2})^2"

        poly_dict = {}
        _add_to_poly_dict(poly_dict, f"{var_a}^2", coeff_a**2)
        _add_to_poly_dict(poly_dict, "".join(sorted([var_a, var_b])), 2 * coeff_a * coeff_b * (1 if op1 == '+' else -1))
        _add_to_poly_dict(poly_dict, f"{var_b}^2", coeff_b**2)
        
        _add_to_poly_dict(poly_dict, f"{var_a}^2", coeff_a_2**2)
        _add_to_poly_dict(poly_dict, "".join(sorted([var_a, var_b])), 2 * coeff_a_2 * coeff_b_2 * (1 if op2 == '+' else -1))
        _add_to_poly_dict(poly_dict, f"{var_b}^2", coeff_b_2**2)

    question_text = f"利用乘法公式，展開下列各式：<br>$ {question_expr} $"
    correct_answer = _format_polynomial(poly_dict)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# 2. Expand (A+B)(A-B) where A, B can be expressions
def _generate_expand_quadratic_diff_of_squares_problem():
    vars_pool = ['a', 'b', 'x', 'y']
    
    # Revisit: (a-b+1)(a-b-1) is the specific example. So A=(a-b), B=1.
    # This means A is a binomial, B is a constant.
    
    var_base1, var_base2 = random.sample(vars_pool, 2)
    coeff_base1 = random.randint(1, 2)
    coeff_base2 = random.randint(1, 2)
    op_base = random.choice(['+', '-'])
    base_expr_str = f"{coeff_base1}{var_base1}" if coeff_base1 != 1 else var_base1
    base_expr_str += f"{op_base}{coeff_base2}{var_base2}"
    if coeff_base2 == 1: base_expr_str = base_expr_str.replace(f"{op_base}1{var_base2}", f"{op_base}{var_base2}")

    const_term = random.randint(1, 5)

    # Option 1: (Base + Const)(Base - Const)  -> Base^2 - Const^2
    if random.random() < 0.5:
        question_expr = f"({base_expr_str}+{const_term})({base_expr_str}-{const_term})"
        
        poly_dict = {}
        _add_to_poly_dict(poly_dict, f"{var_base1}^2", coeff_base1**2)
        _add_to_poly_dict(poly_dict, "".join(sorted([var_base1, var_base2])), 2 * coeff_base1 * coeff_base2 * (1 if op_base == '+' else -1))
        _add_to_poly_dict(poly_dict, f"{var_base2}^2", coeff_base2**2)
        _add_to_poly_dict(poly_dict, "1", -(const_term**2)) # '1' for constant term
    # Option 2: (Const + Base)(Const - Base) -> Const^2 - Base^2
    else:
        question_expr = f"({const_term}+{base_expr_str})({const_term}-{base_expr_str})"
        
        poly_dict = {}
        _add_to_poly_dict(poly_dict, "1", const_term**2)
        _add_to_poly_dict(poly_dict, f"{var_base1}^2", -coeff_base1**2)
        _add_to_poly_dict(poly_dict, "".join(sorted([var_base1, var_base2])), -2 * coeff_base1 * coeff_base2 * (1 if op_base == '+' else -1))
        _add_to_poly_dict(poly_dict, f"{var_base2}^2", -coeff_base2**2)


    question_text = f"利用乘法公式，展開下列各式：<br>$ {question_expr} $"
    correct_answer = _format_polynomial(poly_dict)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# 3. Expand (a+b+c)^2
def _generate_expand_trinomial_square_problem():
    vars_pool = ['a', 'b', 'c', 'x', 'y', 'z']
    var1, var2, var3 = random.sample(vars_pool, 3)
    
    coeff1 = random.randint(1, 3) * random.choice([1, -1])
    coeff2 = random.randint(1, 3) * random.choice([1, -1])
    coeff3 = random.randint(1, 3) * random.choice([1, -1])
    
    term1_str = f"{coeff1}{var1}" if abs(coeff1) != 1 else (f"-{var1}" if coeff1 == -1 else var1)
    term2_str = f"{'+' if coeff2 > 0 else ''}{coeff2}{var2}" if abs(coeff2) != 1 else (f"-{var2}" if coeff2 == -1 else f"+{var2}")
    term3_str = f"{'+' if coeff3 > 0 else ''}{coeff3}{var3}" if abs(coeff3) != 1 else (f"-{var3}" if coeff3 == -1 else f"+{var3}")
    
    question_expr = f"({term1_str}{term2_str}{term3_str})^2"
    
    poly_dict = {}
    _add_to_poly_dict(poly_dict, f"{var1}^2", coeff1**2)
    _add_to_poly_dict(poly_dict, f"{var2}^2", coeff2**2)
    _add_to_poly_dict(poly_dict, f"{var3}^2", coeff3**2)
    
    _add_to_poly_dict(poly_dict, "".join(sorted([var1, var2])), 2 * coeff1 * coeff2)
    _add_to_poly_dict(poly_dict, "".join(sorted([var2, var3])), 2 * coeff2 * coeff3)
    _add_to_poly_dict(poly_dict, "".join(sorted([var1, var3])), 2 * coeff1 * coeff3)

    question_text = f"利用乘法公式，展開下列各式：<br>$ {question_expr} $"
    correct_answer = _format_polynomial(poly_dict)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# 4. Expand (a +/- b)^3
def _generate_expand_cubic_problem():
    vars_pool = ['a', 'b', 'x', 'y']
    var1, var2 = random.sample(vars_pool, 2)
    
    coeff1 = random.randint(1, 2)
    coeff2 = random.randint(1, 2)
    op = random.choice(['+', '-'])
    
    term1_str = f"{coeff1}{var1}" if coeff1 != 1 else var1
    term2_str = f"{coeff2}{var2}" if coeff2 != 1 else var2
    
    question_expr = f"({term1_str}{op}{term2_str})^3"
    
    poly_dict = {}
    
    sign_b = 1 if op == '+' else -1
    
    # (A+B)^3 = A^3 + 3A^2B + 3AB^2 + B^3
    # (A-B)^3 = A^3 - 3A^2B + 3AB^2 - B^3
    
    # A^3 term
    _add_to_poly_dict(poly_dict, f"{var1}^3", coeff1**3)
    
    # 3A^2B term
    _add_to_poly_dict(poly_dict, f"{var1}^2{var2}", 3 * (coeff1**2) * coeff2 * sign_b)
    
    # 3AB^2 term
    _add_to_poly_dict(poly_dict, f"{var1}{var2}^2", 3 * coeff1 * (coeff2**2))
    
    # B^3 term
    _add_to_poly_dict(poly_dict, f"{var2}^3", (coeff2**3) * sign_b)

    question_text = f"利用乘法公式，展開下列各式：<br>$ {question_expr} $"
    correct_answer = _format_polynomial(poly_dict)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# 5. Expand (a +/- b)(a^2 -/+ ab + b^2)
def _generate_expand_sum_diff_of_cubes_form_problem():
    vars_pool = ['a', 'b', 'x', 'y']
    var1, var2 = random.sample(vars_pool, 2)
    
    coeff1 = random.randint(1, 3)
    coeff2 = random.randint(1, 3)
    op = random.choice(['+', '-'])
    
    A_str = f"{coeff1}{var1}" if coeff1 != 1 else var1
    B_str = f"{coeff2}{var2}" if coeff2 != 1 else var2
    
    if op == '+': # (A+B)(A^2-AB+B^2) = A^3+B^3
        # Construct the second factor (A^2-AB+B^2)
        term1_sq = f"{coeff1**2}{var1}^2" if coeff1**2 != 1 else f"{var1}^2"
        term_prod = f"{coeff1*coeff2}{var1}{var2}" if coeff1*coeff2 != 1 else f"{var1}{var2}"
        term2_sq = f"{coeff2**2}{var2}^2" if coeff2**2 != 1 else f"{var2}^2"

        question_expr = f"({A_str}+{B_str})({term1_sq}-{term_prod}+{term2_sq})"
        
        poly_dict = {}
        _add_to_poly_dict(poly_dict, f"{var1}^3", coeff1**3)
        _add_to_poly_dict(poly_dict, f"{var2}^3", coeff2**3)
        
    else: # (A-B)(A^2+AB+B^2) = A^3-B^3
        # Construct the second factor (A^2+AB+B^2)
        term1_sq = f"{coeff1**2}{var1}^2" if coeff1**2 != 1 else f"{var1}^2"
        term_prod = f"{coeff1*coeff2}{var1}{var2}" if coeff1*coeff2 != 1 else f"{var1}{var2}"
        term2_sq = f"{coeff2**2}{var2}^2" if coeff2**2 != 1 else f"{var2}^2"

        question_expr = f"({A_str}-{B_str})({term1_sq}+{term_prod}+{term2_sq})"
        
        poly_dict = {}
        _add_to_poly_dict(poly_dict, f"{var1}^3", coeff1**3)
        _add_to_poly_dict(poly_dict, f"{var2}^3", -coeff2**3)

    question_text = f"利用乘法公式，展開下列各式：<br>$ {question_expr} $"
    correct_answer = _format_polynomial(poly_dict)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# 6. Factor cubic formulas (A^3 +/- B^3 or (A +/- B)^3)
def _generate_factor_cubic_formula_problem():
    vars_pool = ['x', 'y']
    var = random.choice(vars_pool)
    
    type_choice = random.choice(['sum_diff_cubes', 'binomial_cube_expanded'])
    
    if type_choice == 'sum_diff_cubes':
        coeff1 = random.randint(1, 3) # for coeff1*var
        coeff2 = random.randint(1, 5) # for constant term or coeff2*var
        op = random.choice(['+', '-'])
        
        # Form: (coeff1*var)^3 op (coeff2)^3
        
        A_val_for_factoring = coeff1
        B_val_for_factoring = coeff2

        A_str_factored = f"{A_val_for_factoring}{var}" if A_val_for_factoring != 1 else var
        B_str_factored = str(B_val_for_factoring)
        
        # Generate the expanded term for the question
        question_expr = f"{A_val_for_factoring**3}{var}^3 {op} {B_val_for_factoring**3}"
        if A_val_for_factoring**3 == 1: question_expr = question_expr.replace("1"+var+"^3", var+"^3")
        
        # Factorization
        if op == '+': # A^3+B^3 = (A+B)(A^2-AB+B^2)
            factor1_inner = f"{A_str_factored}+{B_str_factored}"
            
            term1_sq = f"{A_val_for_factoring**2}{var}^2" if A_val_for_factoring**2 != 1 else f"{var}^2"
            term_prod = f"{A_val_for_factoring*B_val_for_factoring}{var}" if A_val_for_factoring*B_val_for_factoring != 1 else var
            term2_sq = f"{B_val_for_factoring**2}"
            
            factor2_inner = f"{term1_sq}-{term_prod}+{term2_sq}"
        else: # A^3-B^3 = (A-B)(A^2+AB+B^2)
            factor1_inner = f"{A_str_factored}-{B_str_factored}"
            
            term1_sq = f"{A_val_for_factoring**2}{var}^2" if A_val_for_factoring**2 != 1 else f"{var}^2"
            term_prod = f"{A_val_for_factoring*B_val_for_factoring}{var}" if A_val_for_factoring*B_val_for_factoring != 1 else var
            term2_sq = f"{B_val_for_factoring**2}"
            
            factor2_inner = f"{term1_sq}+{term_prod}+{term2_sq}"

        correct_answer = f"({factor1_inner})({factor2_inner})"
        
    else: # type_choice == 'binomial_cube_expanded' (A +/- B)^3
        var1 = var
        coeff1 = random.randint(1, 2)
        coeff2 = random.randint(1, 3)
        op = random.choice(['+', '-'])
        
        A_val = coeff1
        B_val = coeff2
        
        # Generate the expanded form of (A_val*var1 +/- B_val)^3
        poly_dict = {}
        
        sign_b = 1 if op == '+' else -1
        
        # (A*var1)^3
        _add_to_poly_dict(poly_dict, f"{var1}^3", A_val**3)
        
        # 3*(A*var1)^2 * B_val
        _add_to_poly_dict(poly_dict, f"{var1}^2", 3 * (A_val**2) * B_val * sign_b)
        
        # 3*(A*var1) * B_val^2
        _add_to_poly_dict(poly_dict, f"{var1}", 3 * A_val * (B_val**2))
        
        # B_val^3
        _add_to_poly_dict(poly_dict, "1", (B_val**3) * sign_b) # '1' for constant term

        question_expr = _format_polynomial(poly_dict)
        
        # Expected factorization
        A_str_factored = f"{coeff1}{var1}" if coeff1 != 1 else var1
        B_str_factored = str(coeff2)
        
        correct_answer = f"({A_str_factored}{op}{B_str_factored})^3"
    
    question_text = f"利用乘法公式，因式分解下列各式：<br>$ {question_expr} $"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# 7. Evaluate expressions like x + 1/x = k
def _generate_evaluate_expression_problem():
    k = random.randint(3, 7)
    
    type_choice = random.choice(['square', 'cube'])
    
    if type_choice == 'square':
        # Find x^2 + 1/x^2
        question_text = f"已知 $x+\\frac{{1}}{{x}}={k}$ ，求 $x^2+\\frac{{1}}{{x^2}}$ 的值。"
        correct_answer = str(k**2 - 2) # (x+1/x)^2 = x^2 + 2(x)(1/x) + 1/x^2 = x^2 + 2 + 1/x^2
    else: # cube
        # Find x^3 + 1/x^3
        # (x+1/x)^3 = x^3 + 3(x^2)(1/x) + 3(x)(1/x^2) + 1/x^3
        #             = x^3 + 3x + 3/x + 1/x^3
        #             = x^3 + 1/x^3 + 3(x+1/x)
        # So, x^3 + 1/x^3 = (x+1/x)^3 - 3(x+1/x)
        question_text = f"已知 $x+\\frac{{1}}{{x}}={k}$ ，求 $x^3+\\frac{{1}}{{x^3}}$ 的值。"
        correct_answer = str(k**3 - 3*k)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    生成「乘法公式」相關題目。
    """
    problem_type = random.choice([
        'expand_quadratic_sum_diff',
        'expand_quadratic_diff_of_squares',
        'expand_trinomial_square',
        'expand_cubic',
        'expand_sum_diff_of_cubes_form',
        'factor_cubic_formula',
        'evaluate_expression'
    ])
    
    if problem_type == 'expand_quadratic_sum_diff':
        return _generate_expand_quadratic_sum_diff_problem()
    elif problem_type == 'expand_quadratic_diff_of_squares':
        return _generate_expand_quadratic_diff_of_squares_problem()
    elif problem_type == 'expand_trinomial_square':
        return _generate_expand_trinomial_square_problem()
    elif problem_type == 'expand_cubic':
        return _generate_expand_cubic_problem()
    elif problem_type == 'expand_sum_diff_of_cubes_form':
        return _generate_expand_sum_diff_of_cubes_form_problem()
    elif problem_type == 'factor_cubic_formula':
        return _generate_factor_cubic_formula_problem()
    elif problem_type == 'evaluate_expression':
        return _generate_evaluate_expression_problem()
    else:
        # Fallback, should not happen
        return _generate_expand_quadratic_sum_diff_problem()

def _normalize_answer_string(s):
    """
    Normalizes a string for comparison. Removes spaces and converts to lowercase.
    This is a basic normalization. For algebraic expressions, it assumes a canonical form
    is generated and the user inputs something close to it.
    """
    s = s.strip().replace(' ', '')
    # For exponents, replace ** with ^ (if needed, but our generation uses ^)
    # s = s.replace('**', '^')
    return s

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # For numerical answers, perform float comparison
    try:
        user_num = float(user_answer)
        correct_num = float(correct_answer)
        is_correct = (user_num == correct_num)
    except ValueError:
        # For algebraic answers, normalize strings and compare
        # Note: algebraic variables are case-sensitive. Lowercasing can cause issues if 'A' and 'a' are distinct.
        # Assuming single-letter lowercase variables for consistency.
        normalized_user = _normalize_answer_string(user_answer)
        normalized_correct = _normalize_answer_string(correct_answer)
        is_correct = (normalized_user == normalized_correct)

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}