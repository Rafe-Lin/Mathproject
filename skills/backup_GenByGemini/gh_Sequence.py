import random
from fractions import Fraction
import math

def format_number_for_display(val):
    """
    Formats a number (int, float, or Fraction) into a string suitable for display,
    especially for LaTeX fractions.
    """
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(val.numerator)
        else:
            return r"\\frac{{{}}}{{{}}}".format(val.numerator, val.denominator)
    elif isinstance(val, float):
        # If float is an integer, display as integer
        if val.is_integer():
            return str(int(val))
        else:
            # Attempt to convert to a simple fraction if possible to avoid long decimals
            temp_frac = Fraction(val).limit_denominator(1000) 
            if abs(val - float(temp_frac)) < 1e-9: # If very close to a simple fraction
                return format_number_for_display(temp_frac)
            return str(val) # Otherwise, keep as float string
    return str(val) # For integers

def generate_find_terms_from_formula():
    """
    Generates a problem where the user has to find the first few terms
    of a sequence given its general formula a_n.
    """
    num_terms = 5
    terms = []
    
    formula_type = random.choice([
        'linear',
        'quadratic',
        'geometric_int_r',
        'alternating_geometric',
        'rational'
    ])

    formula_text_latex = ""

    if formula_type == 'linear':
        A = random.randint(-5, 5)
        B = random.randint(-10, 10)
        # Ensure non-trivial linear sequence if A=0 and B=0
        while A == 0 and B == 0: 
            A = random.randint(-5, 5)
            B = random.randint(-10, 10)
        
        formula_text_latex = f"$a_n = {A}n {B:+} $" if B != 0 else f"$a_n = {A}n$"
        if A == 1: formula_text_latex = formula_text_latex.replace('1n', 'n')
        if A == -1: formula_text_latex = formula_text_latex.replace('-1n', '-n')
        if B == 0 and formula_text_latex == "$a_n = $" : formula_text_latex = "$a_n = 0$"
        
        for n_val in range(1, num_terms + 1):
            terms.append(Fraction(A * n_val + B))

    elif formula_type == 'quadratic':
        A = random.randint(-2, 2)
        B = random.randint(-5, 5)
        C = random.randint(-10, 10)
        # Ensure non-trivial quadratic sequence
        while A == 0 and B == 0 and C == 0:
            A = random.randint(-2, 2)
            B = random.randint(-5, 5)
            C = random.randint(-10, 10)
        
        formula_parts = []
        if A != 0:
            if A == 1: formula_parts.append(r"n^{{2}}")
            elif A == -1: formula_parts.append(r"-n^{{2}}")
            else: formula_parts.append(f"{A}n^{{2}}")
        if B != 0:
            if B == 1: formula_parts.append(r"+n")
            elif B == -1: formula_parts.append(r"-n")
            else: formula_parts.append(f"{B:+}n")
        if C != 0:
            formula_parts.append(f"{C:+}")
        
        formula_text_latex = f"$a_n = {''.join(formula_parts)}$"
        if formula_text_latex == "$a_n = $" : formula_text_latex = "$a_n = 0$"

        for n_val in range(1, num_terms + 1):
            terms.append(Fraction(A * n_val**2 + B * n_val + C))

    elif formula_type == 'geometric_int_r':
        a1 = random.randint(-5, 5)
        r = random.choice([-2, -1, 2, 3]) # Simple integer ratios
        while a1 == 0: a1 = random.randint(-5, 5) # a1 cannot be 0
        
        if r == 1: # Avoid r=1 for non-trivial geometric sequence
             r = random.choice([-2, 2, 3]) 
        
        if r == -1:
             formula_text_latex = f"$a_n = {a1} (-1)^{{n-1}}$"
        else:
             formula_text_latex = f"$a_n = {a1} \\cdot ({r})^{{n-1}}$"
        
        # Simplify LaTeX for a1=1 or a1=-1
        if a1 == 1: formula_text_latex = formula_text_latex.replace('1 \\cdot ', '')
        elif a1 == -1: formula_text_latex = formula_text_latex.replace('-1 \\cdot ', '-')

        for n_val in range(1, num_terms + 1):
            terms.append(Fraction(a1 * (r**(n_val - 1))))

    elif formula_type == 'alternating_geometric':
        a_base = random.randint(1, 4) # Base for the non-alternating part
        sign_offset = random.choice([1, 2]) # Exponent offset for (-1)
        
        formula_text_latex = f"$a_n = (-1)^{{n+{sign_offset}}} \\times {a_base}^{{n}}$"

        for n_val in range(1, num_terms + 1):
            terms.append(Fraction(((-1)**(n_val + sign_offset)) * (a_base**n_val)))
            
    elif formula_type == 'rational':
        C = random.randint(1, 5)
        formula_text_latex = f"$a_n = \\frac{{n}}{{n+{C}}}$"

        for n_val in range(1, num_terms + 1):
            terms.append(Fraction(n_val, n_val + C))

    question_text = f"寫出下列數列的前{num_terms}項。<br>{formula_text_latex}"
    
    correct_answer_parts = [format_number_for_display(term) for term in terms]
    correct_answer = ", ".join(correct_answer_parts)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_arithmetic_seq_find_params():
    """
    Generates problems related to arithmetic sequences:
    - Find a1 and d given two terms.
    - Find a specific term a_n given a1 and d.
    - Find the index n for a given value.
    - Find when the sequence exceeds a threshold or becomes negative.
    """
    a1_val = random.randint(-15, 15)
    d_val = random.randint(-5, 5)
    while d_val == 0: d_val = random.randint(-5, 5) # Ensure non-zero common difference

    # Choose two distinct indices for given terms
    idx1 = random.randint(2, 6) # Start from a2
    idx2 = random.randint(idx1 + 1, idx1 + 5) # idx2 > idx1
    
    term1 = a1_val + (idx1 - 1) * d_val
    term2 = a1_val + (idx2 - 1) * d_val

    # Question types
    q_type = random.choice(['find_a1_d', 'find_an', 'find_index_for_value', 'when_value_threshold'])

    if q_type == 'find_a1_d':
        question_text = (f"設等差數列 $a_n$ 滿足 $a_{{{idx1}}} = {term1}, a_{{{idx2}}} = {term2}$。<br>"
                         f"(1) 求首項 $a_1$ 及公差 $d$ 的值。<br>"
                         f"(2) 求第 $10$ 項 $a_{{10}}$ 的值。")
        
        a1_display = format_number_for_display(Fraction(a1_val))
        d_display = format_number_for_display(Fraction(d_val))
        a10_val = a1_val + (10 - 1) * d_val
        a10_display = format_number_for_display(Fraction(a10_val))
        
        correct_answer = f"(1) $a_1 = {a1_display}$, $d = {d_display}$ (2) $a_{{10}} = {a10_display}$"

    elif q_type == 'find_an':
        target_idx = random.randint(7, 12)
        target_term = a1_val + (target_idx - 1) * d_val
        
        question_text = (f"已知等差數列 $a_n$ 的首項 $a_1 = {format_number_for_display(Fraction(a1_val))}$，公差 $d = {format_number_for_display(Fraction(d_val))}$。<br>"
                         f"求第 ${target_idx}$ 項 $a_{{{target_idx}}}$ 的值。")
        correct_answer = format_number_for_display(Fraction(target_term))

    elif q_type == 'find_index_for_value':
        # Generate a target value that is definitely in the sequence
        target_n_actual = random.randint(5, 15)
        target_term_val = a1_val + (target_n_actual - 1) * d_val
        
        question_text = (f"已知等差數列 $a_n$ 的首項 $a_1 = {format_number_for_display(Fraction(a1_val))}$，公差 $d = {format_number_for_display(Fraction(d_val))}$。<br>"
                         f"請問數列中數值 ${format_number_for_display(Fraction(target_term_val))}$ 是第幾項？")
        correct_answer = str(target_n_actual)
        
    elif q_type == 'when_value_threshold':
        threshold_val = random.randint(-20, 20)
        
        if d_val > 0: # Increasing sequence
             question_text = (f"設等差數列 $a_n$ 的首項 $a_1 = {format_number_for_display(Fraction(a1_val))}$，公差 $d = {format_number_for_display(Fraction(d_val))}$。<br>"
                             f"此數列從第幾項開始，其值會大於 ${threshold_val}$？")
             actual_n = 1
             while a1_val + (actual_n - 1) * d_val <= threshold_val:
                 actual_n += 1
             correct_answer = str(actual_n)

        else: # Decreasing sequence
             question_text = (f"設等差數列 $a_n$ 的首項 $a_1 = {format_number_for_display(Fraction(a1_val))}$，公差 $d = {format_number_for_display(Fraction(d_val))}$。<br>"
                             f"此數列從第幾項開始出現負數？")
             actual_n = 1
             while a1_val + (actual_n - 1) * d_val >= 0:
                 actual_n += 1
             correct_answer = str(actual_n)
             
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_geometric_seq_find_params():
    """
    Generates problems related to geometric sequences:
    - Find a1 and r given two terms.
    - Find a specific term a_n given a1 and r.
    - Find the index n for a given value.
    """
    a1_val = random.randint(-8, 8)
    while a1_val == 0: a1_val = random.randint(-8, 8) # a1 cannot be 0
    
    r_val_num = random.choice([-2, -1, 1, 2, 3]) 
    r_val_den = 1
    
    # Introduce fractional common ratio (e.g., 1/2, -1/3)
    if random.random() < 0.3:
        r_val_num = random.choice([-1, 1])
        r_val_den = random.choice([2, 3, 4])
    
    if r_val_num == r_val_den: # If r=1 (trivial sequence), re-select
        r_val_num = random.choice([-2, 2])
        r_val_den = 1

    r_frac = Fraction(r_val_num, r_val_den)

    idx1 = random.randint(2, 4) 
    idx2 = random.randint(idx1 + 1, idx1 + 3) 
    
    term1_val = a1_val * (r_frac**(idx1 - 1))
    term2_val = a1_val * (r_frac**(idx2 - 1))

    term1_display = format_number_for_display(term1_val)
    term2_display = format_number_for_display(term2_val)

    q_type = random.choice(['find_a1_r', 'find_an', 'find_index_for_value'])

    if q_type == 'find_a1_r':
        question_text = (f"已知等比數列 $a_n$ 滿足 $a_{{{idx1}}} = {term1_display}, a_{{{idx2}}} = {term2_display}$。<br>"
                         f"求首項 $a_1$ 及公比 $r$ 的值。")
        
        a1_display = format_number_for_display(Fraction(a1_val))
        r_display = format_number_for_display(r_frac)
        
        correct_answer = f"$a_1 = {a1_display}$, $r = {r_display}$"

    elif q_type == 'find_an':
        target_idx = random.randint(5, 7) 
        target_term_val = a1_val * (r_frac**(target_idx - 1))
        
        question_text = (f"已知等比數列 $a_n$ 的首項 $a_1 = {format_number_for_display(Fraction(a1_val))}$，公比 $r = {format_number_for_display(r_frac)}$。<br>"
                         f"求第 ${target_idx}$ 項 $a_{{{target_idx}}}$ 的值。")
        correct_answer = format_number_for_display(target_term_val)

    elif q_type == 'find_index_for_value':
        # If r is 1 or -1, values repeat or stay the same. Re-generate for find_index_for_value
        if r_frac in [Fraction(1,1), Fraction(-1,1)]: 
            a1_val = random.randint(2, 10)
            r_frac = Fraction(random.choice([-2, 2])) # Force non-trivial r
        
        target_n_actual = random.randint(3, 7)
        target_val = a1_val * (r_frac**(target_n_actual - 1))

        question_text = (f"已知等比數列 $a_n$ 的首項 $a_1 = {format_number_for_display(Fraction(a1_val))}$，公比 $r = {format_number_for_display(r_frac)}$。<br>"
                         f"試問數值 ${format_number_for_display(target_val)}$ 出現在該數列的第幾項？")
        correct_answer = str(target_n_actual)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_arithmetic_geometric_mixed_simple():
    """
    Generates a problem where three numbers form a geometric sequence,
    and a slight modification of them forms an arithmetic sequence.
    Example: a, N2, N3 form GP; a, N2, N3-K form AP. Find 'a'.
    """
    K = random.randint(1, 5) # The difference for the AP term (e.g., b-1)
    N2 = random.randint(2, 10) # The middle term of both sequences
    
    valid_N1_candidates = []
    
    # Equation for N1: N1^2 - (2*N2 + K)N1 + N2^2 = 0
    # Discriminant D = (2*N2 + K)^2 - 4*N2^2 = 4*N2*K + K^2
    D = 4 * N2 * K + K * K
    sqrt_D = int(math.sqrt(D))
    
    if sqrt_D * sqrt_D == D: # If D is a perfect square, integer solutions for N1 exist
        term_sum = 2 * N2 + K
        
        N1_cand1 = (term_sum + sqrt_D) // 2
        N1_cand2 = (term_sum - sqrt_D) // 2
        
        if N1_cand1 > 0 and (term_sum + sqrt_D) % 2 == 0:
            valid_N1_candidates.append(N1_cand1)
        if N1_cand2 > 0 and (term_sum - sqrt_D) % 2 == 0:
            valid_N1_candidates.append(N1_cand2)
            
    if not valid_N1_candidates:
        return generate_arithmetic_geometric_mixed_simple() # Regenerate if no valid integer N1

    N1 = random.choice(valid_N1_candidates)
    
    # Calculate N3 based on GP condition: N2^2 = N1 * N3
    N3 = N2 * N2 // N1 
    
    question_text = (f"已知 ${format_number_for_display(N1)}$, ${format_number_for_display(N2)}$, "
                     f"${format_number_for_display(N3)}$ 三數成等比數列，"
                     f"且 ${format_number_for_display(N1)}$, ${format_number_for_display(N2)}$, "
                     f"${format_number_for_display(N3-K)}$ 三數成等差數列，求 ${format_number_for_display(N1)}$ 的值。")
    
    correct_answer = format_number_for_display(N1)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_identify_sequence_type_simple():
    """
    Generates a problem asking the user to identify if three given numbers
    form an arithmetic sequence, a geometric sequence, both, or neither.
    """
    q_type = random.choice(['AP', 'GP', 'Both', 'Neither'])
    
    terms = []
    
    if q_type == 'AP':
        a = random.randint(-10, 10)
        d = random.randint(-5, 5)
        while d == 0: d = random.randint(-5, 5) # Ensure non-constant AP
        terms = [a, a + d, a + 2 * d]
    elif q_type == 'GP':
        a = random.randint(-5, 5)
        # For level 1, try to keep GP terms as integers
        r_num = random.choice([-2, -1, 2, 3])
        r_den = 1
        r_frac = Fraction(r_num, r_den)
        
        # Ensure non-trivial, non-constant GP
        while a == 0 or r_frac == Fraction(1,1) or r_frac == Fraction(-1,1):
            a = random.randint(-5, 5)
            r_num = random.choice([-2, 2, 3])
            r_den = 1
            r_frac = Fraction(r_num, r_den)
        
        terms = [a, a * r_frac, a * r_frac * r_frac]
        # Ensure terms are integers if `r_frac` leads to non-integers, regenerate.
        # This is a bit of a hack to simplify the output to integers for GP if r is simple.
        # Otherwise, the `format_number_for_display` handles fractions.
        if not all(term.denominator == 1 for term in [Fraction(terms[0]), Fraction(terms[1]), Fraction(terms[2])]):
            return generate_identify_sequence_type_simple() # Regenerate if terms are non-integer fractions.

        terms = [int(t) for t in terms] # Convert to int after successful check
            
    elif q_type == 'Both':
        # Constant sequence is both AP and GP
        val = random.randint(-5, 5)
        terms = [val, val, val]
    elif q_type == 'Neither':
        while True:
            t1 = random.randint(-10, 10)
            t2 = random.randint(-10, 10)
            t3 = random.randint(-10, 10)
            
            # Ensure distinct values to make it harder to accidentally be AP/GP
            if t1 == t2 or t2 == t3 or t1 == t3:
                continue
            
            is_ap = (t2 - t1 == t3 - t2)
            
            is_gp = False
            if t1 != 0:
                # Check for common ratio precisely using Fraction
                if t2 % t1 == 0 and t3 % t2 == 0 and Fraction(t2, t1) == Fraction(t3, t2):
                    is_gp = True
            elif t1 == 0 and t2 == 0 and t3 == 0: # 0,0,0 is both, but we want neither here
                continue 
            elif t1 == 0 and (t2 != 0 or t3 != 0): # 0,X,Y (X!=0 or Y!=0) is not GP
                is_gp = False 
            
            if not is_ap and not is_gp:
                terms = [t1, t2, t3]
                break

    question_text = f"數列 ${', '.join([str(t) for t in terms])}$ 是等差數列、等比數列，還是兩者皆是或兩者皆非？<br>(請填寫：等差/等比/兩者皆是/兩者皆非)"
    
    if q_type == 'AP':
        correct_answer = "等差"
    elif q_type == 'GP':
        correct_answer = "等比"
    elif q_type == 'Both':
        correct_answer = "兩者皆是"
    else: # Neither
        correct_answer = "兩者皆非"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    Generates a math problem related to sequences (arithmetic and geometric).
    The problem type is randomly selected.
    """
    problem_type = random.choice([
        'find_terms_from_formula',
        'arithmetic_seq_find_params',
        'geometric_seq_find_params',
        'arithmetic_geometric_mixed_simple', 
        'identify_sequence_type_simple' 
    ])
    
    if problem_type == 'find_terms_from_formula':
        return generate_find_terms_from_formula()
    elif problem_type == 'arithmetic_seq_find_params':
        return generate_arithmetic_seq_find_params()
    elif problem_type == 'geometric_seq_find_params':
        return generate_geometric_seq_find_params()
    elif problem_type == 'arithmetic_geometric_mixed_simple':
        return generate_arithmetic_geometric_mixed_simple()
    elif problem_type == 'identify_sequence_type_simple':
        return generate_identify_sequence_type_simple()
    
    # Fallback, though should not be reached with random.choice
    return generate_find_terms_from_formula() 


def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct answer for sequence problems.
    Handles various answer formats: direct strings, comma-separated lists,
    and structured answers like "(1) key=val (2) key=val".
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    # Case 1: Direct string comparison for non-numeric answers (e.g., sequence types)
    if any(keyword in correct_answer for keyword in ['等差', '等比', '兩者皆是', '兩者皆非']):
        is_correct = (user_answer == correct_answer)
        result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # Case 2: For answers with multiple parts like "(1) Ans1 (2) Ans2"
    if "(1)" in correct_answer and "(2)" in correct_answer:
        # Parse the structured correct answer
        parsed_correct = {}
        for part in correct_answer.split('('):
            if not part.strip(): continue
            if ')' not in part: continue # Malformed part
            idx_str, content = part.split(')', 1)
            try:
                idx = int(idx_str)
            except ValueError:
                continue # Skip if index is not a number
            parsed_correct[idx] = {}
            # Content like "$a_1 = 2$, $d = 3$" or "$a_{10} = 29$"
            sub_parts = [s.strip() for s in content.split(',')]
            for sp in sub_parts:
                if '=' in sp:
                    key, val = sp.split('=', 1)
                    parsed_correct[idx][key.strip().replace('$', '').replace('{', '').replace('}', '')] = val.strip().replace('$', '').replace('{', '').replace('}', '')
                else: # Handle cases where there's no '=' (e.g., just "29" for a single value)
                    if sp.strip():
                        parsed_correct[idx]['_value'] = sp.strip().replace('$', '').replace('{', '').replace('}', '')

        # Parse the structured user answer
        parsed_user = {}
        user_parts_list = []
        if not user_answer.startswith('('): # Assume it's a single part if not starting with (
            user_parts_list.append(f"(1){user_answer}") # Treat as part (1)
        else:
            user_parts_list = user_answer.split('(')

        for part in user_parts_list:
            if not part.strip(): continue
            if ')' not in part: # User input might be incomplete, try to handle
                # If there's no ')' in the part, it might be e.g. "(1" or just "a1=X"
                if '=' in part: # Attempt to parse as key=value for implicit part 1
                    key, val = part.split('=', 1)
                    if 1 not in parsed_user: parsed_user[1] = {}
                    parsed_user[1][key.strip().replace('$', '').replace('{', '').replace('}', '')] = val.strip().replace('$', '').replace('{', '').replace('}', '')
                elif part.strip(): # Just a value for implicit part 1
                    if 1 not in parsed_user: parsed_user[1] = {}
                    parsed_user[1]['_value'] = part.strip().replace('$', '').replace('{', '').replace('}', '')
                continue

            idx_str, content = part.split(')', 1)
            try:
                idx = int(idx_str)
            except ValueError:
                continue # Not a number index, skip
            parsed_user[idx] = {}
            sub_parts = [s.strip() for s in content.split(',')]
            for sp in sub_parts:
                if '=' in sp:
                    key, val = sp.split('=', 1)
                    parsed_user[idx][key.strip().replace('$', '').replace('{', '').replace('}', '')] = val.strip().replace('$', '').replace('{', '').replace('}', '')
                else:
                    if sp.strip():
                        parsed_user[idx]['_value'] = sp.strip().replace('$', '').replace('{', '').replace('}', '')
        
        all_parts_correct = True
        feedback_parts = []

        for idx_correct, correct_content_dict in parsed_correct.items():
            user_content_dict = parsed_user.get(idx_correct, {})
            
            for key_correct, val_correct_str in correct_content_dict.items():
                val_user_str = user_content_dict.get(key_correct)
                
                if val_user_str is None: # User didn't provide this specific key
                    all_parts_correct = False
                    feedback_parts.append(f"第({idx_correct})部分缺少 '{key_correct}' 的值。")
                    continue
                
                is_sub_correct = False
                try:
                    # Attempt numeric comparison (float after Fraction conversion)
                    # Normalize string representation for comparison
                    normalized_user_val = val_user_str.replace(' ', '').replace('\\frac{', '').replace('}{', '/').replace('}', '')
                    normalized_correct_val = val_correct_str.replace(' ', '').replace('\\frac{', '').replace('}{', '/').replace('}', '')

                    user_val_num = float(Fraction(normalized_user_val))
                    correct_val_num = float(Fraction(normalized_correct_val))
                    if abs(user_val_num - correct_val_num) < 1e-9:
                        is_sub_correct = True
                except (ValueError, ZeroDivisionError):
                    # Fallback to string comparison if not numeric
                    is_sub_correct = (val_user_str.replace(' ', '').lower() == val_correct_str.replace(' ', '').lower())

                if not is_sub_correct:
                    all_parts_correct = False
                    feedback_parts.append(f"第({idx_correct})部分 '{key_correct}' 的值不正確。您的答案是 '{val_user_str}'，正確答案是 '{val_correct_str}'。")
        
        if all_parts_correct:
            result_text = f"完全正確！答案是 {correct_answer}。"
        else:
            result_text = f"答案不正確。{' '.join(feedback_parts)} 正確答案應為：{correct_answer}"
        
        return {"correct": all_parts_correct, "result": result_text, "next_question": True}

    # Case 3: Comma-separated lists of numbers or single number answers
    user_parts = [s.strip() for s in user_answer.split(',')]
    correct_parts = [s.strip() for s in correct_answer.split(',')]

    if len(user_parts) != len(correct_parts):
        is_correct = False
    else:
        is_correct = True
        for i in range(len(correct_parts)):
            # Normalize string representation for comparison
            user_str = user_parts[i].replace('$', '').replace(' ', '').replace('\\frac{', '').replace('}{', '/').replace('}', '')
            correct_str = correct_parts[i].replace('$', '').replace(' ', '').replace('\\frac{', '').replace('}{', '/').replace('}', '')
            try:
                user_val = float(Fraction(user_str))
                correct_val = float(Fraction(correct_str))
                if abs(user_val - correct_val) > 1e-9:
                    is_correct = False
                    break
            except (ValueError, ZeroDivisionError):
                # If conversion to number fails (e.g., non-numeric input for a numeric answer), treat as incorrect
                is_correct = False
                break
    
    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}