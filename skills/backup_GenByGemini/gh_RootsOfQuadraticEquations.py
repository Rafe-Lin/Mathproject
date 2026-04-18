import random
from fractions import Fraction
import math
import cmath
import re

def generate(level=1):
    problem_type = random.choice([
        'solve_quadratic',
        'discriminant_range',
        'roots_relations'
    ])
    
    if problem_type == 'solve_quadratic':
        return generate_solve_quadratic_problem(level)
    elif problem_type == 'discriminant_range':
        return generate_discriminant_range_problem(level)
    else: # roots_relations
        return generate_roots_relations_problem(level)

def _format_number(num):
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    elif isinstance(num, int):
        return str(num)
    elif isinstance(num, float):
        if num.is_integer():
            return str(int(num))
        return str(num)
    return str(num)

def _get_coeffs(level):
    if level == 1:
        a = random.randint(1, 2)
        b = random.randint(-5, 5)
        c = random.randint(-5, 5)
    else: # Higher level might have larger coeffs or lead to more complex roots
        a = random.randint(1, 3)
        b = random.randint(-10, 10)
        c = random.randint(-10, 10)
    
    return a, b, c

def generate_solve_quadratic_problem(level):
    # Strategy: generate roots first to control answer type and complexity
    choice = random.choice(['real_rational', 'real_irrational', 'complex'])

    a_coeff = random.randint(1, 3) # The 'a' in ax^2+bx+c
    
    if choice == 'real_rational':
        # Generate two roots x1, x2 (integers or simple fractions)
        x1_num = random.randint(-5, 5)
        x1_den = random.choice([1, 2]) if x1_num != 0 else 1
        x1 = Fraction(x1_num, x1_den)
        
        x2_num = random.randint(-5, 5)
        x2_den = random.choice([1, 2]) if x2_num != 0 else 1
        x2 = Fraction(x2_num, x2_den)

        if random.random() < 0.2: # Sometimes make roots equal
            x2 = x1
        else:
            while x1 == x2: # Ensure distinct if not forcing equal
                x2_num = random.randint(-5, 5)
                x2_den = random.choice([1, 2]) if x2_num != 0 else 1
                x2 = Fraction(x2_num, x2_den)

        sum_roots = x1 + x2
        prod_roots = x1 * x2

        # Form the quadratic equation x^2 - (sum_roots)x + (prod_roots) = 0
        # Multiply by a factor 'A_scale' to get integer coefficients
        A_scale = a_coeff
        
        # Find common denominator for sum_roots and prod_roots to make coeffs integers
        lcm_den = math.lcm(sum_roots.denominator, prod_roots.denominator)
        A_scale *= lcm_den

        a, b, c = int(A_scale), int(-A_scale * sum_roots), int(A_scale * prod_roots)
        if a < 0: # Ensure leading coefficient is positive
            a, b, c = -a, -b, -c
        
        if x1 == x2:
            correct_answer = f"x = {_format_number(x1)}"
        else:
            correct_answer = f"x = {_format_number(x1)} 或 x = {_format_number(x2)}"

    elif choice == 'complex':
        # Generate complex roots p +/- qi
        p_num = random.randint(-5, 5)
        p_den = random.choice([1, 2]) if p_num != 0 else 1
        p = Fraction(p_num, p_den)

        q_num = random.randint(1, 5) # q must be non-zero for complex
        q_den = random.choice([1, 2]) if q_num != 0 else 1
        q = Fraction(q_num, q_den)

        # x^2 - 2px + (p^2 + q^2) = 0
        sum_roots = 2 * p
        prod_roots = p*p + q*q

        A_scale = a_coeff
        lcm_den = math.lcm(sum_roots.denominator, prod_roots.denominator)
        A_scale *= lcm_den
        
        a, b, c = int(A_scale), int(-A_scale * sum_roots), int(A_scale * prod_roots)
        if a < 0: # Ensure a is positive
            a, b, c = -a, -b, -c
        
        p_str = _format_number(p)
        q_str = _format_number(q)
        correct_answer = f"x = ${p_str} + {q_str}i$ 或 x = ${p_str} - {q_str}i$"

    else: # real_irrational
        # Generate 'a', 'b', 'c' where D > 0 but not a perfect square
        a = random.randint(1, 2)
        
        # Pick D that is positive and not a perfect square, from a pre-defined list for simpler square roots
        possible_D_values = [2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28] 
        D_val = random.choice(possible_D_values)
        
        # Ensure (b^2 - D_val) is divisible by 4a, and c is an integer.
        found_c = False
        b_candidates = [val for val in range(-7, 8) if (val*val - D_val) % (4*a) == 0 and abs((val*val - D_val) // (4*a)) <= 10]
        if b_candidates:
            b = random.choice(b_candidates)
            c = (b*b - D_val) // (4*a)
            found_c = True
        
        if not found_c: # Fallback if no suitable b,c found for irrational roots
            # Recurse, might generate a different type of problem
            return generate_solve_quadratic_problem(level) 
        
        D_actual = b*b - 4*a*c
        
        # Simplify sqrt(D_actual)
        D_prime = D_actual
        sqrt_coeff = 1
        i = 2
        while i * i <= D_prime:
            if D_prime % (i * i) == 0:
                sqrt_coeff *= i
                D_prime //= (i * i)
            else:
                i += 1
        
        g = math.gcd(abs(b), abs(sqrt_coeff))
        g = math.gcd(g, abs(2*a))
        
        simplified_b = b // g
        simplified_sqrt_coeff = sqrt_coeff // g
        simplified_den = 2*a // g

        root_str_pos = r"\\frac{{{}}}{{{}}}".format(
            f"{(-simplified_b)} + {simplified_sqrt_coeff}{r'\\sqrt{{{}}}'.format(D_prime) if D_prime > 1 else ''}",
            simplified_den
        )
        root_str_neg = r"\\frac{{{}}}{{{}}}".format(
            f"{(-simplified_b)} - {simplified_sqrt_coeff}{r'\\sqrt{{{}}}'.format(D_prime) if D_prime > 1 else ''}",
            simplified_den
        )
        correct_answer = f"x = ${root_str_pos}$ 或 x = ${root_str_neg}$"

    question_text = f"解方程式 ${_format_number(a)}x^{{2}} + {_format_number(b)}x + {_format_number(c)} = 0$。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_discriminant_range_problem(level):
    # Equation with a variable coefficient k
    # One of a, b, c will be 'k'
    
    k_pos = random.choice(['b_coeff', 'c_coeff'])

    a = random.randint(1, 2)
    
    if k_pos == 'b_coeff':
        # Equation: ax^2 + kx + c = 0
        # Discriminant: D = k^2 - 4ac
        cond_type = random.choice(['distinct_real', 'equal_real', 'no_real', 'real_roots'])
        
        # Aim to make 4ac a perfect square for cleaner integer bounds for k
        sq_val_for_4ac = random.randint(3, 8)
        target_4ac = sq_val_for_4ac**2
        
        c_candidates = [val for val in range(1, 10) if (target_4ac % (4*a)) == 0 and (target_4ac // (4*a)) == val]
        if not c_candidates:
            # Fallback if no simple integer c found
            # Recurse, might generate a different problem
            return generate_discriminant_range_problem(level)
        c = random.choice(c_candidates)
            
        bound = math.isqrt(4*a*c)
        
        if cond_type == 'distinct_real':
            question_text = f"已知方程式 ${_format_number(a)}x^{{2}} + kx + {_format_number(c)} = 0$ 有兩相異實根，求實數 $k$ 的範圍。"
            correct_answer = f"k > {bound} 或 k < {-bound}"
        elif cond_type == 'equal_real':
            question_text = f"已知方程式 ${_format_number(a)}x^{{2}} + kx + {_format_number(c)} = 0$ 有兩相等實根，求實數 $k$ 的值。"
            correct_answer = f"k = {bound} 或 k = {-bound}"
        elif cond_type == 'no_real':
            question_text = f"已知方程式 ${_format_number(a)}x^{{2}} + kx + {_format_number(c)} = 0$ 無實數解，求實數 $k$ 的範圍。"
            correct_answer = f"{-bound} < k < {bound}"
        else: # real_roots (D >= 0)
            question_text = f"已知方程式 ${_format_number(a)}x^{{2}} + kx + {_format_number(c)} = 0$ 有兩實根，求實數 $k$ 的範圍。"
            correct_answer = f"k >= {bound} 或 k <= {-bound}"

    else: # k_pos == 'c_coeff'
        # Equation: ax^2 + bx + k = 0
        b = random.randint(-10, 10)
        while b == 0: # Avoid division by zero issues in bound_val if b becomes 0
            b = random.randint(-10, 10)
        
        cond_type = random.choice(['distinct_real', 'equal_real', 'no_real', 'real_roots'])

        # Discriminant D = b^2 - 4ak
        # b^2 - 4ak > 0 => b^2 > 4ak => k < b^2 / (4a) (if a>0)
        
        bound_val = Fraction(b*b, 4*a) # The boundary for k
        
        if cond_type == 'distinct_real':
            question_text = f"已知方程式 ${_format_number(a)}x^{{2}} + {_format_number(b)}x + k = 0$ 有兩相異實根，求實數 $k$ 的範圍。"
            correct_answer = f"k < {_format_number(bound_val)}"
        elif cond_type == 'equal_real':
            question_text = f"已知方程式 ${_format_number(a)}x^{{2}} + {_format_number(b)}x + k = 0$ 有兩相等實根，求實數 $k$ 的值。"
            correct_answer = f"k = {_format_number(bound_val)}"
        elif cond_type == 'no_real':
            question_text = f"已知方程式 ${_format_number(a)}x^{{2}} + {_format_number(b)}x + k = 0$ 無實數解，求實數 $k$ 的範圍。"
            correct_answer = f"k > {_format_number(bound_val)}"
        else: # real_roots
            question_text = f"已知方程式 ${_format_number(a)}x^{{2}} + {_format_number(b)}x + k = 0$ 有兩實根，求實數 $k$ 的範圍。"
            correct_answer = f"k <= {_format_number(bound_val)}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_roots_relations_problem(level):
    # ax^2 + bx + c = 0, roots alpha, beta
    # Calculate expressions involving alpha + beta = -b/a and alpha * beta = c/a
    
    a = random.randint(1, 3)
    b = random.randint(-10, 10)
    c = random.randint(-10, 10)

    # Ensure a, b, c lead to non-zero sum/product for selected expressions
    # e.g., for reciprocal sum, prod_roots (c/a) must not be zero.
    # for alpha^2+beta^2, sum_roots and prod_roots can't be zero simultaneously for non-zero roots.
    # For now, ensure c is not 0 for most common expressions.
    while c == 0: # Ensures prod_roots is not 0
        c = random.randint(-10, 10)

    sum_roots = Fraction(-b, a)
    prod_roots = Fraction(c, a)

    # Choose expression type
    expr_type = random.choice(['sum_sq', 'reciprocal_sum', 'sum_cubes'])
    
    question_text = f"已知 $\\alpha, \\beta$ 為方程式 ${_format_number(a)}x^{{2}} + {_format_number(b)}x + {_format_number(c)} = 0$ 的兩根，求下列各式的值。<br>"
    
    correct_answer_val = None
    if expr_type == 'sum_sq':
        # alpha^2 + beta^2 = (alpha+beta)^2 - 2*alpha*beta
        correct_answer_val = sum_roots**2 - 2 * prod_roots
        question_text += f"(1) $\\alpha^{{2}} + \\beta^{{2}}$。"
    elif expr_type == 'reciprocal_sum':
        # 1/alpha + 1/beta = (alpha+beta) / (alpha*beta)
        correct_answer_val = sum_roots / prod_roots
        question_text += f"(1) $\\frac{{1}}{{\\alpha}} + \\frac{{1}}{{\\beta}}$。"
    else: # sum_cubes
        # alpha^3 + beta^3 = (alpha+beta)(alpha^2 - alpha*beta + beta^2)
        # = (alpha+beta)((alpha+beta)^2 - 3*alpha*beta)
        sum_sq = sum_roots**2 - 2 * prod_roots # alpha^2 + beta^2
        correct_answer_val = sum_roots * (sum_sq - prod_roots)
        question_text += f"(1) $\\alpha^{{3}} + \\beta^{{3}}$。"

    correct_answer = _format_number(correct_answer_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _parse_simple_numeric_str(s):
    # Helper to parse strings that can be integers, floats, or fractions, including LaTeX fractions.
    s = s.strip()
    # Try LaTeX fraction first
    frac_match = re.fullmatch(r'\\frac\{(-?\d+)\}\{(-?\d+)\}', s)
    if frac_match:
        try:
            return Fraction(int(frac_match.group(1)), int(frac_match.group(2)))
        except ValueError:
            return None
    # Then regular fraction
    if '/' in s:
        try:
            return Fraction(s)
        except ValueError:
            return None
    # Then integer/float
    try:
        return Fraction(s)
    except ValueError:
        return None

def _parse_single_root_str(root_str):
    """
    Parses a single root string (e.g., '1+2i', '1/2', '$\\frac{1}{2}$', '$\\frac{-1+\\sqrt{3}}{2}$')
    into a canonical form (Fraction, complex, or tuple for irrational).
    Returns (type, value).
    """
    root_str = root_str.strip().replace('$', '') # Remove LaTeX delimiters for parsing

    # Try to parse as complex A + Bi or A - Bi (A and B can be fractions)
    complex_parts_match = re.fullmatch(r'(.+?)\s*([+\-])\s*(.+?)i', root_str)
    if complex_parts_match:
        real_part_str = complex_parts_match.group(1).strip()
        op = complex_parts_match.group(2)
        imag_coeff_str = complex_parts_match.group(3).strip()
        
        real_val_frac = _parse_simple_numeric_str(real_part_str)
        imag_val_frac = _parse_simple_numeric_str(imag_coeff_str)

        if real_val_frac is not None and imag_val_frac is not None:
            imag_val_frac = imag_val_frac * (-1 if op == '-' else 1)
            return ('complex', complex(float(real_val_frac), float(imag_val_frac)))
    
    # Try to parse as pure imaginary Bi (B can be fraction)
    pure_imag_match = re.fullmatch(r'([+\-])?(.+?)i', root_str)
    if pure_imag_match:
        op = pure_imag_match.group(1)
        imag_coeff_str = pure_imag_match.group(2).strip()
        
        imag_val_frac = _parse_simple_numeric_str(imag_coeff_str)
        if imag_val_frac is not None:
            imag_val_frac = imag_val_frac * (-1 if op == '-' else 1)
            return ('complex', complex(0, float(imag_val_frac)))

    # Try to parse as irrational \\frac{A \\pm B\\sqrt{D}}{C}
    irrational_match = re.fullmatch(r'\\frac\{(-?\d+)\s*([+\-])\s*(\d*)\\sqrt\{(\d+)\}\}\{(\d+)\}', root_str)
    if irrational_match:
        num_part_val = Fraction(irrational_match.group(1))
        op = irrational_match.group(2)
        sqrt_coeff_val = Fraction(irrational_match.group(3) or '1')
        D_prime = int(irrational_match.group(4))
        den_part_val = Fraction(irrational_match.group(5))
        
        sqrt_coeff_val = sqrt_coeff_val * (-1 if op == '-' else 1)
        
        return ('irrational', (num_part_val / den_part_val, sqrt_coeff_val / den_part_val, D_prime))

    # Fallback to simple numeric (Fraction)
    simple_num_val = _parse_simple_numeric_str(root_str)
    if simple_num_val is not None:
        return ('fraction', simple_num_val)

    return ('unparsed_string', root_str)

def _compare_parsed_roots(root1_parsed, root2_parsed, tolerance=1e-9):
    type1, val1 = root1_parsed
    type2, val2 = root2_parsed

    if type1 != type2:
        return False
    
    if type1 == 'fraction':
        return val1 == val2
    elif type1 == 'complex':
        return abs(val1.real - val2.real) < tolerance and abs(val1.imag - val2.imag) < tolerance
    elif type1 == 'irrational':
        # Compare components of the tuple (rational_part_frac, sqrt_coeff_frac, sqrt_D_val)
        return val1[0] == val2[0] and val1[1] == val2[1] and val1[2] == val2[2]
    else: # 'unparsed_string' - direct string comparison
        return val1 == val2

def check(user_answer, correct_answer):
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False

    # --- Handling solutions for quadratic equations (e.g., 'x = ...') ---
    if correct_answer.startswith("x = "):
        correct_root_strings = [s.strip() for s in correct_answer.replace("x = ", "").split("或")]
        user_root_strings = [s.strip() for s in user_answer.replace("x = ", "").split("或")]

        if len(correct_root_strings) == len(user_root_strings):
            parsed_correct_roots = [_parse_single_root_str(s) for s in correct_root_strings]
            parsed_user_roots = [_parse_single_root_str(s) for s in user_root_strings]

            # Check for one-to-one match, ignoring order
            matched_indices = [False] * len(parsed_correct_roots)
            temp_is_correct = True
            for u_root in parsed_user_roots:
                found_match = False
                for i, c_root in enumerate(parsed_correct_roots):
                    if not matched_indices[i] and _compare_parsed_roots(u_root, c_root):
                        matched_indices[i] = True
                        found_match = True
                        break
                if not found_match:
                    temp_is_correct = False
                    break
            
            if temp_is_correct and all(matched_indices):
                is_correct = True

    # --- Handling inequalities (e.g., 'k >= 6 或 k <= -6') ---
    elif 'k' in correct_answer and any(op in correct_answer for op in ['<', '>', '=']):
        def normalize_inequality_for_comparison(s):
            s = s.replace(' ', '').replace('$', '')
            parts = []
            
            # Split by '或' for multiple clauses
            if '或' in s:
                parts = s.split('或')
            else:
                parts = [s]
            
            canonical_parts = []
            for p in parts:
                p_with_k = p.replace('k', '_K_') # Placeholder to keep 'k' safe during sorting
                
                # Handle 'lower < _K_ < upper' form
                between_match = re.fullmatch(r'(-?\d+(?:/\d+)?)(<|_K_)(<|_K_)(-?\d+(?:/\d+)?)', p_with_k)
                if between_match:
                    lower_val = _parse_simple_numeric_str(between_match.group(1))
                    upper_val = _parse_simple_numeric_str(between_match.group(4))
                    canonical_parts.append(f"(_K_,{_format_number(min(lower_val, upper_val))},{_format_number(max(lower_val, upper_val))})")
                else:
                    # Generic comparison of left and right parts.
                    # Convert to canonical form '_K_ operator value'
                    op_match = re.fullmatch(r'(_K_)?\s*(<=|>=|<|>|=)\s*(-?\d+(?:/\d+)?)(\s*_K_)?', p_with_k)
                    if op_match:
                        op = op_match.group(2)
                        value_str = op_match.group(3)
                        value = _parse_simple_numeric_str(value_str)
                        
                        if op_match.group(1) == '_K_': # k is on left
                            canonical_parts.append(f"(_K_ {op} {_format_number(value)})")
                        elif op_match.group(4) == '_K_': # k is on right, invert operator
                            if op == '<=': op_inv = '>='
                            elif op == '>=': op_inv = '<='
                            elif op == '<': op_inv = '>'
                            elif op == '>': op_inv = '<'
                            else: op_inv = '='
                            canonical_parts.append(f"(_K_ {op_inv} {_format_number(value)})")
                        else: # Fallback
                            canonical_parts.append(p_with_k)
                    else: # Fallback
                        canonical_parts.append(p_with_k)
            
            canonical_parts.sort()
            return '或'.join(canonical_parts)
        
        if normalize_inequality_for_comparison(user_answer) == normalize_inequality_for_comparison(correct_answer):
            is_correct = True

    # --- Handling general numeric answers (e.g., Fraction results from roots_relations) ---
    else:
        # Try to parse as Fraction, including LaTeX fractions
        parsed_user = _parse_single_root_str(user_answer)
        parsed_correct = _parse_single_root_str(correct_answer)
        
        if _compare_parsed_roots(parsed_user, parsed_correct):
            is_correct = True
        else:
            # Fallback to simple string comparison if parsing fails or types don't match
            if user_answer.replace(' ', '').replace('$', '') == correct_answer.replace(' ', '').replace('$', ''):
                 is_correct = True

    feedback = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": feedback, "next_question": True}