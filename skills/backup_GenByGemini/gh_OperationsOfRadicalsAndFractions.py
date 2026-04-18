import random
import math
import re
from fractions import Fraction

# Helper to simplify a radical sqrt(n)
# Returns (coefficient, radicand) such that sqrt(n) = coefficient * sqrt(radicand)
def _simplify_radical(n):
    if n < 0:
        raise ValueError("Radicand cannot be negative for real numbers")
    if n == 0:
        return (0, 1) # sqrt(0) = 0
    
    # Find largest perfect square factor
    i = 1
    max_square_factor = 1
    while i * i <= n:
        if n % (i * i) == 0:
            max_square_factor = i * i
        i += 1
    
    coeff = int(math.sqrt(max_square_factor))
    radicand = n // max_square_factor
    return (coeff, radicand)

# Helper to format a radical term: coeff * sqrt(radicand)
# coeff can be a Fraction.
# e.g., (Fraction(2,3), 3) -> "\\frac{2}{3}\\sqrt{3}", (Fraction(1), 5) -> "\\sqrt{5}", (Fraction(5), 1) -> "5"
def _format_radical_term(coeff_fraction, radicand):
    if coeff_fraction == Fraction(0):
        return "0"
    
    coeff_num = coeff_fraction.numerator
    coeff_den = coeff_fraction.denominator

    if radicand == 1: # Integer or fractional term
        if coeff_den == 1:
            return str(coeff_num)
        else:
            return f"\\frac{{{coeff_num}}}{{{coeff_den}}}"
    
    # Radical term
    coeff_str = ""
    if coeff_num == 1 and coeff_den == 1:
        coeff_str = "" # for 1*sqrt(R)
    elif coeff_num == -1 and coeff_den == 1:
        coeff_str = "-" # for -1*sqrt(R)
    elif coeff_den == 1:
        coeff_str = str(coeff_num)
    else:
        coeff_str = f"\\frac{{{coeff_num}}}{{{coeff_den}}}"

    if coeff_str == "":
        return f"\\sqrt{{{radicand}}}"
    elif coeff_str == "-":
        return f"-\\sqrt{{{radicand}}}"
    else:
        return f"{coeff_str}\\sqrt{{{radicand}}}"


# Function to add two radical expressions represented as lists of (Fraction(coeff), radicand) tuples
def _add_radical_expressions(terms1, terms2):
    combined = terms1 + terms2
    
    # Group by radicand and sum coefficients
    grouped = {} # radicand -> Fraction(total_coeff)
    for coeff, radicand in combined:
        if radicand not in grouped:
            grouped[radicand] = Fraction(0)
        grouped[radicand] += coeff
    
    # Normalize radicands (e.g., (Fraction(4),2) -> (Fraction(8),1))
    final_terms = []
    for radicand, coeff in grouped.items():
        if coeff != Fraction(0): # Only include non-zero terms
            s_coeff, s_radicand = _simplify_radical(radicand)
            final_terms.append((coeff * Fraction(s_coeff), s_radicand)) # coeff * s_coeff is new coeff, s_radicand is new radicand
        
    # Re-group after simplifying radicands (as s_radicand might already exist)
    grouped_final = {}
    for coeff, radicand in final_terms:
        if radicand not in grouped_final:
            grouped_final[radicand] = Fraction(0)
        grouped_final[radicand] += coeff
        
    result = []
    for radicand, coeff in grouped_final.items():
        if coeff != Fraction(0):
            result.append((coeff, radicand))
    
    # Sort for canonical form: by radicand, then by coefficient value
    return sorted(result, key=lambda x: (x[1], x[0].numerator / x[0].denominator))


# Helper to format a general expression from a list of (Fraction(coeff), radicand) tuples
def _format_radical_expression(terms):
    if not terms:
        return "0"

    # Separate integer part and radical parts
    integer_part_coeff = Fraction(0)
    radical_parts_list = [] # list of (Fraction(coeff), radicand)

    for coeff, radicand in terms:
        if radicand == 1:
            integer_part_coeff += coeff
        else:
            radical_parts_list.append((coeff, radicand))
    
    result_parts = []
    
    # Add integer part if non-zero
    if integer_part_coeff != Fraction(0):
        result_parts.append(_format_radical_term(integer_part_coeff, 1))

    # Sort radical parts (e.g., smaller radicands first)
    # Then append based on sign for natural reading: A + B - C
    
    # Separate positive and negative radical terms
    positive_radical_terms = []
    negative_radical_terms = []
    for coeff, radicand in sorted(radical_parts_list, key=lambda x: x[1]): # Sort by radicand
        if coeff > Fraction(0):
            positive_radical_terms.append((coeff, radicand))
        else:
            negative_radical_terms.append((coeff, radicand))

    for coeff, radicand in positive_radical_terms:
        term_str = _format_radical_term(coeff, radicand)
        if result_parts: # If there are preceding terms, add a '+'
            result_parts.append(f"+{term_str}")
        else:
            result_parts.append(term_str) # First term, no '+'

    for coeff, radicand in negative_radical_terms:
        term_str = _format_radical_term(coeff, radicand)
        result_parts.append(term_str) # Negative terms already include '-'
            
    if not result_parts:
        return "0"
    
    return "".join(result_parts).replace("+-", "-") # Fix "A+-B" to "A-B"


# Function to multiply two radical expressions
# terms1: list of (Fraction(coeff), radicand)
# terms2: list of (Fraction(coeff), radicand)
def _multiply_radical_expressions(terms1, terms2):
    result_terms = []
    for c1, r1 in terms1:
        for c2, r2 in terms2:
            new_coeff = c1 * c2
            new_radicand = r1 * r2
            
            s_coeff, s_radicand = _simplify_radical(new_radicand)
            result_terms.append((new_coeff * Fraction(s_coeff), s_radicand))
            
    return _add_radical_expressions([], result_terms) # Use add to group and simplify


# --- Problem Generation Functions ---

def _generate_simplify_radicals_problem():
    num_terms = random.randint(2, 4)
    problem_parts = []
    
    answer_terms = [] # List of (Fraction(coeff), radicand)

    for _ in range(num_terms):
        coeff_int = random.choice([1, -1]) * random.randint(1, 5)
        
        radicand_base = random.randint(2, 15) # base radicand
        square_factor_val = random.choice([1, 2, 3, 4, 5]) 
        original_radicand = radicand_base * (square_factor_val**2)
        
        s_coeff, s_radicand = _simplify_radical(original_radicand)
        answer_terms.append((Fraction(coeff_int * s_coeff), s_radicand))

        problem_parts.append(_format_radical_term(Fraction(coeff_int), original_radicand))
    
    question_display_parts = []
    for i, part in enumerate(problem_parts):
        if i > 0 and part.startswith('-'):
            question_display_parts.append(part)
        elif i > 0:
            question_display_parts.append(f"+{part}")
        else:
            question_display_parts.append(part)
            
    question_text = f"化簡下列各式：${''.join(question_display_parts)}$"
    
    final_answer_terms = _add_radical_expressions([], answer_terms)
    correct_answer = _format_radical_expression(final_answer_terms)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "hint": "將每個根式化簡後再合併同類項。"
    }

def _generate_multiplication_problem():
    problem_type = random.choice(['conjugate', 'square'])
    
    if problem_type == 'conjugate':
        use_radical_a = random.choice([True, False])
        if use_radical_a:
            val_a_radicand = random.randint(2, 10)
            val_a_terms = [(Fraction(1), val_a_radicand)]
            val_a_str = f"\\sqrt{{{val_a_radicand}}}"
        else:
            val_a_int = random.randint(2, 10)
            val_a_terms = [(Fraction(val_a_int), 1)]
            val_a_str = str(val_a_int)
            
        val_b_radicand = random.randint(2, 10)
        val_b_terms = [(Fraction(1), val_b_radicand)]
        val_b_str = f"\\sqrt{{{val_b_radicand}}}"
        
        op = random.choice(['+', '-'])
        
        expr1_str = f"({val_a_str}{op}{val_b_str})"
        expr2_str = f"({val_a_str}{'+' if op == '-' else '-'}{val_b_str})"
        
        question_text = f"化簡下列各式：${expr1_str}{expr2_str}$"
        
        a_squared_terms = _multiply_radical_expressions(val_a_terms, val_a_terms)
        b_squared_terms = _multiply_radical_expressions(val_b_terms, val_b_terms)
        
        negated_b_squared_terms = [(-c, r) for c, r in b_squared_terms]
        final_answer_terms = _add_radical_expressions(a_squared_terms, negated_b_squared_terms)
        
        correct_answer = _format_radical_expression(final_answer_terms)
        
    else: # square (a+b)^2 or (a-b)^2
        val_a_radicand = random.randint(2, 10)
        val_b_radicand = random.randint(2, 10)
        
        op_sign = random.choice(['+', '-'])
        
        expr_str = f"(\\sqrt{{{val_a_radicand}}}{op_sign}\\sqrt{{{val_b_radicand}}})^2"
        question_text = f"化簡下列各式：${expr_str}$"
        
        term_a = (Fraction(1), val_a_radicand)
        term_b = (Fraction(1), val_b_radicand)
        
        a_squared_terms = _multiply_radical_expressions([term_a], [term_a])
        b_squared_terms = _multiply_radical_expressions([term_b], [term_b])
        
        two_ab_coeff = Fraction(2) if op_sign == '+' else Fraction(-2)
        two_ab_terms = _multiply_radical_expressions([(two_ab_coeff, 1)], 
                                                      _multiply_radical_expressions([term_a], [term_b]))
        
        final_answer_terms = _add_radical_expressions(_add_radical_expressions(a_squared_terms, two_ab_terms), b_squared_terms)
        correct_answer = _format_radical_expression(final_answer_terms)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "hint": "利用乘法公式 $(a+b)(a-b)=a^2-b^2$ 或 $(a \\pm b)^2 = a^2 \\pm 2ab + b^2$。"
    }

def _generate_rationalize_denominator_problem():
    problem_type = random.choice(['sqrt_minus_int', 'sqrt_plus_sqrt'])
    
    if problem_type == 'sqrt_minus_int': # Num / (sqrt(A) +/- B)
        numerator_coeff = random.randint(1, 5)
        denominator_radicand = random.randint(2, 15)
        denominator_int = random.randint(1, 5)
        op_sign = random.choice(['+', '-'])
        
        question_text = f"化簡下列各式：$\\frac{{{numerator_coeff}}}{{\\sqrt{{{denominator_radicand}}}{op_sign}{denominator_int}}}$"
        
        den_orig_terms = [(Fraction(1), denominator_radicand)]
        den_orig_terms.append((Fraction(denominator_int if op_sign == '+' else -denominator_int), 1))
            
        conjugate_op = '+' if op_sign == '-' else '-'
        den_conj_terms = [(Fraction(1), denominator_radicand)]
        den_conj_terms.append((Fraction(denominator_int if conjugate_op == '+' else -denominator_int), 1))
            
        new_numerator_terms = _multiply_radical_expressions([(Fraction(numerator_coeff), 1)], den_conj_terms)
        
        new_denominator_terms = _multiply_radical_expressions(den_orig_terms, den_conj_terms)
        
        den_val_fraction = Fraction(0)
        if new_denominator_terms:
            for coeff, radicand in new_denominator_terms:
                if radicand == 1:
                    den_val_fraction += coeff
        
        if den_val_fraction == Fraction(0): 
            return _generate_rationalize_denominator_problem()
        
        final_answer_terms = []
        for c, r in new_numerator_terms:
            final_answer_terms.append((c / den_val_fraction, r))
            
        correct_answer = _format_radical_expression(final_answer_terms)

    else: # sqrt_plus_sqrt: C*sqrt(D) / (sqrt(A) +/- sqrt(B))
        numerator_coeff = random.randint(1, 5)
        numerator_radicand = random.randint(2, 15)
        
        denominator_radicand1 = random.randint(2, 15)
        denominator_radicand2 = random.randint(2, 15)
        
        while denominator_radicand1 == denominator_radicand2:
            denominator_radicand2 = random.randint(2, 15)
        
        op_sign = random.choice(['+', '-'])
        
        question_text = f"化簡下列各式：$\\frac{{{numerator_coeff}\\sqrt{{{numerator_radicand}}}}}{{\\sqrt{{{denominator_radicand1}}}{op_sign}\\sqrt{{{denominator_radicand2}}}}}$"
        
        den_orig_terms = [(Fraction(1), denominator_radicand1)]
        den_orig_terms.append((Fraction(1 if op_sign == '+' else -1), denominator_radicand2))
            
        conjugate_op = '+' if op_sign == '-' else '-'
        den_conj_terms = [(Fraction(1), denominator_radicand1)]
        den_conj_terms.append((Fraction(1 if conjugate_op == '+' else -1), denominator_radicand2))
            
        num_orig_terms = [(Fraction(numerator_coeff), numerator_radicand)]
        
        new_numerator_terms = _multiply_radical_expressions(num_orig_terms, den_conj_terms)
        
        new_denominator_terms = _multiply_radical_expressions(den_orig_terms, den_conj_terms)
        
        den_val_fraction = Fraction(0)
        if new_denominator_terms:
            for coeff, radicand in new_denominator_terms:
                if radicand == 1:
                    den_val_fraction += coeff
        
        if den_val_fraction == Fraction(0):
            return _generate_rationalize_denominator_problem()
            
        final_answer_terms = []
        for c, r in new_numerator_terms:
            final_answer_terms.append((c / den_val_fraction, r))
            
        correct_answer = _format_radical_expression(final_answer_terms)
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "hint": "將分母乘以其共軛式來有理化分母。"
    }

def _generate_double_radical_problem():
    val1 = random.randint(2, 10)
    val2 = random.randint(1, val1)
    while val1 == val2:
        val2 = random.randint(1, val1)
    
    op_sign = random.choice(['+', '-'])
    
    if op_sign == '-' and val1 < val2:
        val1, val2 = val2, val1
    
    outer_sum = val1 + val2
    inner_product = val1 * val2
    
    if random.random() < 0.5: # Type sqrt(A +/- 2sqrt(B))
        question_text = f"化簡下列各式：$\\sqrt{{{outer_sum}{op_sign}2\\sqrt{{{inner_product}}}}}$"
    else: # Type sqrt(A +/- sqrt(B)) where B is 4*inner_product
        display_inner_radicand_val = inner_product * 4
        question_text = f"化簡下列各式：$\\sqrt{{{outer_sum}{op_sign}\\sqrt{{{display_inner_radicand_val}}}}}$"

    s_val1_coeff, s_val1_rad = _simplify_radical(val1)
    s_val2_coeff, s_val2_rad = _simplify_radical(val2)

    term1 = (Fraction(s_val1_coeff), s_val1_rad)
    term2 = (Fraction(s_val2_coeff), s_val2_rad)

    if op_sign == '-':
        val1_effective = s_val1_coeff**2 * s_val1_rad
        val2_effective = s_val2_coeff**2 * s_val2_rad

        if val1_effective < val2_effective:
            term1, term2 = term2, term1
            term2 = (-term2[0], term2[1]) 
        else:
            term2 = (-term2[0], term2[1])
    
    final_answer_terms = _add_radical_expressions([term1, term2], [])
    correct_answer = _format_radical_expression(final_answer_terms)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "hint": "利用雙重根式化簡公式 $\\sqrt{ (a+b) \\pm 2\\sqrt{ab} } = \\sqrt{a} \\pm \\sqrt{b}$。若根號前不是2，需先變形。"
    }

def _generate_comparison_problem():
    num_expressions = random.randint(2, 3)
    expressions = []
    
    base_sum_options = [10, 11, 12, 13]
    base_sum = random.choice(base_sum_options)
    
    generated_pairs = set()
    
    while len(expressions) < num_expressions:
        val_x = random.randint(2, base_sum - 2)
        val_y = base_sum - val_x
        
        if val_x <= 0 or val_y <= 0 or val_x == val_y:
            continue
        
        current_pair = tuple(sorted((val_x, val_y)))
        if current_pair in generated_pairs:
            continue
        
        generated_pairs.add(current_pair)
        
        expr_str = f"\\sqrt{{{val_x}}} + \\sqrt{{{val_y}}}"
        
        square_value_radical_part = val_x * val_y
        
        expressions.append({
            "str": expr_str,
            "square_radical_part": square_value_radical_part
        })
        
    sorted_expressions = sorted(expressions, key=lambda x: (x["square_radical_part"], x["str"]))
    
    labels = ['A', 'B', 'C']
    labeled_expressions = []
    for i, expr in enumerate(sorted_expressions):
        label = labels[i]
        labeled_expressions.append(f"${label} = {expr['str']}$")
        expr["label"] = label
        
    compare_type = random.choice(['smallest', 'largest'])
    
    if compare_type == 'smallest':
        correct_label = sorted_expressions[0]["label"]
        question_text = f"比較下列各數的大小：{', '.join(labeled_expressions)}。請問何者最小？(請填代號)"
    else:
        correct_label = sorted_expressions[-1]["label"]
        question_text = f"比較下列各數的大小：{', '.join(labeled_expressions)}。請問何者最大？(請填代號)"
        
    return {
        "question_text": question_text,
        "answer": correct_label,
        "correct_answer": correct_label,
        "hint": "將每個數平方後再比較大小。"
    }


def _generate_agm_inequality_problem():
    L_total = random.randint(5, 15) * 4 
    
    correct_area = L_total * L_total // 8
    
    question_text = f"用圍籬沿著筆直的河岸圍一個矩形菜圃，其中靠河岸一邊不圍，只圍三邊。已知圍籬的總長為 ${L_total}$ 公尺，求此菜圃的最大面積為多少平方公尺？"
    correct_answer = str(correct_area)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "hint": "設矩形寬為 $x$，則長為 $L_{total}-2x$。利用算幾不等式 $a+b \\ge 2\\sqrt{ab}$ 或二次函數性質求解。"
    }

def generate(level=1):
    problem_type = random.choice([
        'simplify_radicals', 
        'multiplication', 
        'rationalize_denominator', 
        'double_radical',
        'comparison',
        'agm_inequality'
    ])
    
    if problem_type == 'simplify_radicals':
        return _generate_simplify_radicals_problem()
    elif problem_type == 'multiplication':
        return _generate_multiplication_problem()
    elif problem_type == 'rationalize_denominator':
        return _generate_rationalize_denominator_problem()
    elif problem_type == 'double_radical':
        return _generate_double_radical_problem()
    elif problem_type == 'comparison':
        return _generate_comparison_problem()
    elif problem_type == 'agm_inequality':
        return _generate_agm_inequality_problem()

# --- Check Function Helpers ---

def _parse_term(term_str):
    """Parses a single radical term string into (Fraction(coeff), radicand)."""
    term_str = term_str.strip()
    if not term_str:
        return None 

    sign = 1
    if term_str.startswith('-'):
        sign = -1
        term_str = term_str[1:]
    elif term_str.startswith('+'):
        term_str = term_str[1:]

    coeff_part = ""
    radicand_part = "1" 

    radical_match = re.search(r'\\sqrt{(\d+)}', term_str)
    if radical_match:
        radicand_part = radical_match.group(1)
        coeff_part = term_str[:radical_match.start()]
    else:
        coeff_part = term_str 

    coeff = Fraction(1)
    if not coeff_part: 
        coeff = Fraction(1)
    elif coeff_part == '1': 
        coeff = Fraction(1)
    else:
        fraction_match = re.fullmatch(r'\\frac{(\d+)}{(\d+)}', coeff_part)
        if fraction_match:
            num = int(fraction_match.group(1))
            den = int(fraction_match.group(2))
            coeff = Fraction(num, den)
        else: 
            try:
                coeff = Fraction(int(coeff_part))
            except ValueError:
                return None 

    return (sign * coeff, int(radicand_part))

def _parse_radical_expression_for_check(expr_str):
    """Parses a full radical expression string into a list of (Fraction(coeff), radicand) terms."""
    terms = []
    expr_str = expr_str.replace(' ', '')
    expr_str = expr_str.replace('--', '+')
    expr_str = expr_str.replace('+-', '-')
    
    if expr_str and expr_str[0] not in ['+', '-']:
        expr_str = '+' + expr_str
    
    current_pos = 0
    while current_pos < len(expr_str):
        next_op_pos = -1
        balance = 0
        for i in range(current_pos + 1, len(expr_str)):
            if expr_str[i] == '{':
                balance += 1
            elif expr_str[i] == '}':
                balance -= 1
            elif balance == 0 and (expr_str[i] == '+' or expr_str[i] == '-'):
                next_op_pos = i
                break
        
        term_str_raw = ""
        if next_op_pos == -1:
            term_str_raw = expr_str[current_pos:]
            current_pos = len(expr_str)
        else:
            term_str_raw = expr_str[current_pos:next_op_pos]
            current_pos = next_op_pos
        
        parsed_term = _parse_term(term_str_raw)
        if parsed_term:
            terms.append(parsed_term)
        else:
            return None
            
    return terms


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    result_text = ""

    # 1. Direct string comparison (for non-radical answers like labels A, B, C or simple integers)
    if user_answer.upper() == correct_answer.upper():
        is_correct = True
    
    # 2. Numerical comparison (for integer/decimal answers from AGM or simple radical results that are integers)
    if not is_correct:
        try:
            user_num = float(user_answer)
            correct_num = float(correct_answer)
            if abs(user_num - correct_num) < 1e-9: 
                is_correct = True
        except ValueError:
            pass 
    
    # 3. Radical expression comparison
    if not is_correct:
        try:
            user_terms = _parse_radical_expression_for_check(user_answer)
            correct_terms = _parse_radical_expression_for_check(correct_answer)

            if user_terms is not None and correct_terms is not None:
                simplified_user_terms = _add_radical_expressions([], user_terms)
                simplified_correct_terms = _add_radical_expressions([], correct_terms)
                
                if simplified_user_terms == simplified_correct_terms:
                    is_correct = True
        except Exception:
            pass 

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}