import random
from fractions import Fraction
import math

# --- Helper Functions ---

def get_prime_factorization(n):
    """Returns the prime factorization of n as a dictionary."""
    n = abs(int(n))
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def simplify_radical(coefficient, radicand):
    """Simplifies a radical expression c * sqrt(r).
    Returns a tuple (new_coefficient, new_radicand).
    e.g., simplify_radical(1, 12) -> (2, 3)
    e.g., simplify_radical(3, 8) -> (6, 2)
    """
    if radicand == 0:
        return 0, 1
    if radicand < 0:
        raise ValueError("Radicand cannot be negative for real square roots.")
    if radicand == 1:
        return coefficient, 1
    
    factors = get_prime_factorization(radicand)
    out_factor = 1
    new_radicand = 1
    for p, exp in factors.items():
        out_factor *= p**(exp // 2)
        new_radicand *= p**(exp % 2)
    
    return coefficient * out_factor, new_radicand

def format_radical(coeff, radicand, is_first_term=True):
    """Formats a single radical term into a LaTeX string."""
    if coeff == 0:
        return ""
    
    coeff_val, radicand_val = simplify_radical(coeff, radicand)

    if radicand_val == 1:
        if is_first_term:
            return str(coeff_val)
        else:
            return f" + {coeff_val}" if coeff_val > 0 else f" - {-coeff_val}"
    
    sign = ""
    if not is_first_term:
        sign = " + " if coeff_val > 0 else " - "
    elif coeff_val < 0:
        sign = "-"

    abs_coeff = abs(coeff_val)
    
    coeff_str = "" if abs_coeff == 1 else str(abs_coeff)
        
    return f"{sign}{coeff_str}\\sqrt{{{radicand_val}}}"

def format_expression(terms, denominator=1):
    """
    Formats a dictionary of {radicand: coefficient} into a LaTeX string.
    Also handles a potential denominator for the whole expression.
    """
    if not terms:
        return "0"

    simplified_terms = {}
    for r, c in terms.items():
        if c == 0: continue
        c_s, r_s = simplify_radical(c, r)
        simplified_terms[r_s] = simplified_terms.get(r_s, 0) + c_s
        
    simplified_terms = {r: c for r, c in simplified_terms.items() if c != 0}

    if not simplified_terms:
        return "0"
        
    if denominator != 1:
        all_coeffs = [int(c) for c in simplified_terms.values()]
        common_divisor = abs(int(denominator))
        for c in all_coeffs:
            common_divisor = math.gcd(common_divisor, abs(c))

        if common_divisor > 1:
            denominator //= common_divisor
            for r in simplified_terms:
                simplified_terms[r] //= common_divisor

    if denominator < 0:
        denominator = -denominator
        for r in simplified_terms:
            simplified_terms[r] = -simplified_terms[r]

    sorted_radicands = sorted(simplified_terms.keys())
    if 1 in sorted_radicands:
        sorted_radicands.remove(1)
        sorted_radicands.insert(0, 1)

    parts = []
    is_first = True
    for r in sorted_radicands:
        c = simplified_terms[r]
        term_str = format_radical(c, r, is_first_term=is_first)
        if term_str:
            parts.append(term_str)
            is_first = False
            
    final_num_str = "".join(parts).lstrip()

    if denominator == 1 or not final_num_str:
        return final_num_str if final_num_str else "0"
    elif final_num_str == str(denominator):
        return "1"
    elif final_num_str == "-" + str(denominator):
        return "-1"
    else:
        return f"\\frac{{{final_num_str}}}{{{denominator}}}"

# --- Problem Generation Functions ---

def generate_identify_like_problem():
    base_r = random.choice([2, 3, 5, 6, 7, 10])
    question_str = f"圈圈看，下列哪些是 $\\sqrt{{{base_r}}}$ 的同類方根？"
    
    options = []
    correct_answers_list = []
    
    num_correct = random.randint(2, 3)
    correct_types = random.sample(['mult', 'frac', 'dec'], num_correct)
    
    used_coeffs = set()

    if 'mult' in correct_types:
        c = random.randint(2, 5)
        used_coeffs.add(c)
        rad = c*c*base_r
        opt_str = f"$\\sqrt{{{rad}}}$"
        options.append(opt_str)
        correct_answers_list.append(opt_str)
        
    if 'frac' in correct_types:
        den_part = random.randint(2, 5)
        while den_part in used_coeffs:
            den_part = random.randint(2, 5)
        used_coeffs.add(den_part)
        num = base_r * den_part
        den = den_part * den_part
        common = math.gcd(num, den)
        num //= common
        den //= common
        opt_str = f"$\\sqrt{{\\frac{{{num}}}{{{den}}}}}$"
        options.append(opt_str)
        correct_answers_list.append(opt_str)

    if 'dec' in correct_types and base_r in [2, 5, 6, 10]:
        den = 10
        rad = base_r / (den*den)
        rad_str = f"{rad:.2f}".rstrip('0')
        opt_str = f"$\\sqrt{{{rad_str}}}$"
        options.append(opt_str)
        correct_answers_list.append(opt_str)

    num_incorrect = 5 - len(correct_answers_list)
    incorrect_radicands = [r for r in [2, 3, 5, 6, 7, 10] if r != base_r]
    
    for _ in range(num_incorrect):
        inc_type = random.choice(['diff_rad', 'perfect_sq', 'rat_frac'])
        if inc_type == 'diff_rad' and incorrect_radicands:
            c = random.randint(2, 4)
            r = random.choice(incorrect_radicands)
            rad = c*c*r
            options.append(f"$\\sqrt{{{rad}}}$")
        elif inc_type == 'perfect_sq':
            c = random.randint(3, 6)
            options.append(f"$\\sqrt{{{c*c}}}$")
        else:
            if not incorrect_radicands: incorrect_radicands = [11]
            c = random.randint(2, 5)
            r = random.choice(incorrect_radicands)
            options.append(f"$\\frac{{{c}}}{{\\sqrt{{{r}}}}}$")

    random.shuffle(options)
    question_text = f"{question_str}\n{', '.join(options)}"
    correct_answer = ", ".join(sorted(correct_answers_list))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_add_subtract_simplify_problem():
    terms = {}
    q_parts = []
    
    num_terms = random.randint(2, 4)
    base_radicands = random.sample([2, 3, 5, 6, 7], k=random.randint(1, 2))
    
    for i in range(num_terms):
        base_r = random.choice(base_radicands)
        simplify_needed = random.random() < 0.6
        coeff = random.randint(1, 5) * random.choice([-1, 1])
        
        if simplify_needed and base_r != 1:
            mult = random.randint(2, 4)
            display_radicand = base_r * mult * mult
            q_parts.append(format_radical(coeff, display_radicand, is_first_term=(i==0)))
        else:
            q_parts.append(format_radical(coeff, base_r, is_first_term=(i==0)))
        
        c_s, r_s = simplify_radical(coeff, display_radicand if simplify_needed and base_r != 1 else base_r)
        terms[r_s] = terms.get(r_s, 0) + c_s

    question_text = f"化簡下列各式。\n$ {''.join(q_parts).lstrip()} $"
    correct_answer = format_expression(terms)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_multiplication_formula_problem():
    prob_type = random.choice(['diff_sq', 'sum_sq'])
    c1, r1 = (random.randint(2, 5), 1) if random.random() < 0.3 else (random.randint(1, 3), random.choice([2, 3, 5, 6, 7]))
    c2, r2 = (random.randint(2, 5), 1) if random.random() < 0.3 else (random.randint(1, 3), random.choice([2, 3, 5, 6, 7]))

    while r1 == r2 and r1 != 1: r2 = random.choice([2, 3, 5, 6, 7])
    if c1*c1*r1 == c2*c2*r2: c1 += 1

    term_A_str = format_radical(c1, r1).strip()
    term_B_str = format_radical(c2, r2).replace(" + ", "").strip()
    
    if prob_type == 'diff_sq':
        question_text = f"利用乘法公式化簡下列各式。\n$ ({term_A_str} - {term_B_str})({term_A_str} + {term_B_str}) $"
        answer_val = c1*c1*r1 - c2*c2*r2
        correct_answer = str(answer_val)
    else:
        op = random.choice(['+', '-'])
        question_text = f"利用乘法公式化簡下列各式。\n$ ({term_A_str} {op} {term_B_str})^2 $"
        cross_term_coeff = 2 * c1 * c2 * (-1 if op == '-' else 1)
        c_s, r_s = simplify_radical(cross_term_coeff, r1 * r2)
        final_terms = {1: c1*c1*r1 + c2*c2*r2, r_s: c_s}
        correct_answer = format_expression(final_terms)
        
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": correct_answer}

def generate_rationalize_problem():
    c1, r1 = (random.randint(2, 5), 1) if random.random() < 0.3 else (random.randint(1, 3), random.choice([2, 3, 5, 6, 7]))
    c2, r2 = (random.randint(2, 5), 1) if r1 != 1 and random.random() < 0.3 else (random.randint(1, 3), random.choice([2, 3, 5, 6, 7]))

    while r1 == r2 and r1 != 1: r2 = random.choice([2, 3, 5, 6, 7])
    if c1*c1*r1 == c2*c2*r2: c1 += 1

    den_op = random.choice(['+', '-'])
    term_A_str = format_radical(c1, r1).strip()
    term_B_str = format_radical(c2, r2).replace(" + ", "").strip()
    
    num_c = random.randint(1, 4)
    num_r = 1 if random.random() > 0.4 else random.choice([r for r in [2, 3, 5] if r not in [r1, r2]] or [2])
    if num_r != 1 and num_c > 2: num_c = 1
    numerator_str = format_radical(num_c, num_r).strip()
    
    question_text = f"將下列各式的分母有理化。\n$ \\frac{{{numerator_str}}}{{{term_A_str} {den_op} {term_B_str}}} $"
    
    final_den = c1*c1*r1 - c2*c2*r2
    
    new_num_c1, new_num_r1 = num_c * c1, num_r * r1
    new_num_c2, new_num_r2 = num_c * c2 * (-1 if den_op == '+' else 1), num_r * r2
    
    c_s1, r_s1 = simplify_radical(new_num_c1, new_num_r1)
    c_s2, r_s2 = simplify_radical(new_num_c2, new_num_r2)
    
    num_terms = {r_s1: c_s1}
    num_terms[r_s2] = num_terms.get(r_s2, 0) + c_s2

    correct_answer = format_expression(num_terms, final_den)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": correct_answer}
    
def generate_distributive_problem():
    op_type = random.choice(['multiply', 'divide'])
    
    op_c = random.randint(1, 3)
    op_r = random.choice([2, 3, 5])
    op_str = format_radical(op_c, op_r).strip()
    
    terms = {}
    num_terms_in_paren = random.randint(2, 3)
    base_radicands = random.sample([r for r in [2, 3, 5, 6, 7] if r != op_r], k=num_terms_in_paren)
    
    for i in range(num_terms_in_paren):
        c, r = random.randint(1, 4) * random.choice([-1, 1]), base_radicands[i]
        if op_type == 'divide':
            terms[r*op_r] = c * op_c
        else:
            terms[r] = c

    paren_str = format_expression(terms)
    
    if op_type == 'multiply':
        question_text = f"化簡下列各式。\n$ ({paren_str}) \\times {op_str} $"
        final_terms = {}
        for r, c in terms.items():
            c_s, r_s = simplify_radical(c * op_c, r * op_r)
            final_terms[r_s] = final_terms.get(r_s, 0) + c_s
        correct_answer = format_expression(final_terms)
    else: # divide
        question_text = f"化簡下列各式。\n$ ({paren_str}) \\div {op_str} $"
        final_terms = {}
        for r, c in terms.items():
            new_c, new_r = c / op_c, r / op_r
            final_terms[new_r] = final_terms.get(new_r, 0) + new_c
        correct_answer = format_expression(final_terms)
        
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": correct_answer}

def generate(level=1):
    """
    生成「根式的四則運算」相關題目。
    """
    problem_types = [
        generate_identify_like_problem,
        generate_add_subtract_simplify_problem,
        generate_distributive_problem,
        generate_multiplication_formula_problem,
        generate_rationalize_problem
    ]
    return random.choice(problem_types)()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    def normalize_latex(s):
        return s.replace(" ", "").replace("\\times", "*").replace("(", "").replace(")", "")

    user_ans_norm = normalize_latex(user_answer)
    correct_ans_norm = normalize_latex(correct_answer)
    
    is_correct = False
    if '$' in correct_ans_norm and ',' in correct_ans_norm:
        user_parts = sorted([p.strip() for p in user_ans_norm.split(',')])
        correct_parts = sorted([p.strip() for p in correct_ans_norm.split(',')])
        is_correct = (user_parts == correct_parts)
    else:
        is_correct = (user_ans_norm == correct_ans_norm)
    
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}