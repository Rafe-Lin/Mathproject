import random
from fractions import Fraction

# --- Polynomial Helper Functions ---

def poly_to_str(p, var='x'):
    """Converts a polynomial represented by coefficients into a LaTeX string."""
    if not any(p):
        return "0"
    
    terms = []
    degree = len(p) - 1
    for i, coeff in enumerate(p):
        if coeff == 0:
            continue
        
        current_degree = degree - i
        is_first_term = not terms
        
        # Sign and Coefficient part
        c_str = ""
        if is_first_term:
            if current_degree > 0:
                if coeff == 1: c_str = ""
                elif coeff == -1: c_str = "-"
                else: c_str = str(coeff)
            else: # constant term
                c_str = str(coeff)
        else: # not the first term
            abs_coeff = abs(coeff)
            sign = " + " if coeff > 0 else " - "
            if current_degree > 0 and abs_coeff == 1:
                coeff_val = ""
            else:
                coeff_val = str(abs_coeff)
            c_str = f"{sign}{coeff_val}"

        # Variable part
        v_str = ""
        if current_degree > 1:
            v_str = f"{var}^{current_degree}"
        elif current_degree == 1:
            v_str = var

        terms.append(f"{c_str}{v_str}")
        
    return "".join(terms)

def _pad_zeros(p, target_len):
    """Pads a polynomial with leading zeros to match a target length."""
    return [0] * (target_len - len(p)) + p

def poly_add(p1, p2):
    max_len = max(len(p1), len(p2))
    p1_padded = _pad_zeros(p1, max_len)
    p2_padded = _pad_zeros(p2, max_len)
    return [c1 + c2 for c1, c2 in zip(p1_padded, p2_padded)]

def poly_sub(p1, p2):
    max_len = max(len(p1), len(p2))
    p1_padded = _pad_zeros(p1, max_len)
    p2_padded = _pad_zeros(p2, max_len)
    return [c1 - c2 for c1, c2 in zip(p1_padded, p2_padded)]

def poly_mul_const(p, c):
    if isinstance(c, Fraction):
        return [coeff * c for coeff in p]
    return [coeff * c for coeff in p]

def poly_mul(p1, p2):
    if not p1 or not p2:
        return [0]
    result = [0] * (len(p1) + len(p2) - 1)
    for i, c1 in enumerate(p1):
        for j, c2 in enumerate(p2):
            result[i + j] += c1 * c2
    return result

def binomial_to_str(p, parenthesize=True):
    """Converts a binomial to a string, with optional parentheses for clarity in expressions."""
    s = poly_to_str(p)
    if parenthesize and any(op in s for op in [' + ', ' - ']):
        return f"({s})"
    return s

def create_binomial(allow_zero_const=False, force_positive_x=False):
    """Generates a random binomial [a, b] for ax+b."""
    if force_positive_x:
      a = random.randint(1, 3)
    else:
      a = random.choice([-2, -1, 1, 2, 3])
      if a == 0: a = 1
    
    b_range = list(range(-5, 6))
    if not allow_zero_const:
      b_range.remove(0)
    b = random.choice(b_range)
    
    return [a, b]

# --- Main Generation Logic ---

def generate(level=1):
    """
    Generates questions for comprehensive applications of polynomials.
    """
    problem_type = random.choice(['pure_calc', 'geometry_area', 'geometry_find_dimension'])
    
    if problem_type == 'pure_calc':
        return generate_pure_calculation_problem()
    elif problem_type == 'geometry_area':
        return generate_geometry_area_problem()
    else: # 'geometry_find_dimension'
        return generate_geometry_find_dimension_problem()

def generate_pure_calculation_problem():
    """Generates a polynomial arithmetic problem."""
    sub_type = random.randint(1, 4)
    
    if sub_type == 1: # (ax+b)^2 + (cx+d)
        p1 = create_binomial()
        p2 = create_binomial()
        if p1 == [-c for c in p2]: p2 = create_binomial() # Avoid trivial cancellation
        p1_str = binomial_to_str(p1)
        p2_str = binomial_to_str(p2)
        question_text = f"計算 ${p1_str}^2 + {p2_str}$。"
        res_p1_sq = poly_mul(p1, p1)
        final_res_poly = poly_add(res_p1_sq, p2)

    elif sub_type == 2: # k(ax+b)^2 - m(cx+d)
        k = random.randint(2, 5)
        m = random.randint(2, 5)
        p1 = create_binomial()
        p2 = create_binomial()
        p1_str = binomial_to_str(p1)
        p2_str = binomial_to_str(p2)
        op = random.choice(['+', '-'])
        question_text = f"計算 ${k}{p1_str}^2 {op} {m}{p2_str}$。"
        res_p1_sq = poly_mul(p1, p1)
        term1 = poly_mul_const(res_p1_sq, k)
        term2 = poly_mul_const(p2, m)
        final_res_poly = poly_add(term1, term2) if op == '+' else poly_sub(term1, term2)

    elif sub_type == 3: # (ax+b)(cx+d) - (ex+f)(gx+h)
        p1, p2, p3, p4 = [create_binomial() for _ in range(4)]
        p1_str, p2_str = binomial_to_str(p1), binomial_to_str(p2)
        p3_str, p4_str = binomial_to_str(p3), binomial_to_str(p4)
        op = random.choice(['+', '-'])
        question_text = f"計算 ${p1_str}{p2_str} {op} {p3_str}{p4_str}$。"
        term1 = poly_mul(p1, p2)
        term2 = poly_mul(p3, p4)
        final_res_poly = poly_add(term1, term2) if op == '+' else poly_sub(term1, term2)

    else: # k(ax+b)(cx+d) - m(ex+f)(gx+h)
        k, m = random.randint(2, 5), random.randint(2, 5)
        p1, p2, p3, p4 = [create_binomial() for _ in range(4)]
        p1_str, p2_str = binomial_to_str(p1), binomial_to_str(p2)
        p3_str, p4_str = binomial_to_str(p3), binomial_to_str(p4)
        op = random.choice(['+', '-'])
        question_text = f"計算 ${k}{p1_str}{p2_str} {op} {m}{p3_str}{p4_str}$。"
        term1 = poly_mul_const(poly_mul(p1, p2), k)
        term2 = poly_mul_const(poly_mul(p3, p4), m)
        final_res_poly = poly_add(term1, term2) if op == '+' else poly_sub(term1, term2)
    
    answer_str = poly_to_str(final_res_poly)
    if answer_str == "0":
        return generate_pure_calculation_problem()

    final_answer = f"${answer_str}$"
    return {
        "question_text": question_text,
        "answer": final_answer,
        "correct_answer": final_answer
    }

def generate_geometry_area_problem():
    """Generates a problem about the area/perimeter of a composite shape."""
    L_L = [random.randint(2, 4), random.randint(1, 5)]
    W_L = [random.randint(1, 2), random.randint(1, 5)]
    L_S = [random.randint(1, L_L[0] - 1 if L_L[0] > 1 else 1), random.randint(-2, L_L[1] - 1 if L_L[1] > 1 else 1)]
    W_S = [random.randint(1, W_L[0]), random.randint(-3, W_L[1] - 1 if W_L[1] > 1 else 1)]

    L_L_str, W_L_str = binomial_to_str(L_L), binomial_to_str(W_L)
    L_S_str, W_S_str = binomial_to_str(L_S), binomial_to_str(W_S)
    
    area_L = poly_mul(L_L, W_L)
    area_S = poly_mul(L_S, W_S)
    remaining_area_poly = poly_sub(area_L, area_S)
    area_str = poly_to_str(remaining_area_poly)

    if area_str == "0": return generate_geometry_area_problem()

    ask_perimeter = random.choice([True, False])
    if ask_perimeter:
        perimeter_L = poly_mul_const(poly_add(L_L, W_L), 2)
        perimeter_S = poly_mul_const(poly_add(L_S, W_S), 2)
        total_perimeter_poly = poly_add(perimeter_L, perimeter_S)
        perimeter_str = poly_to_str(total_perimeter_poly)
        question_text = f"一個大長方形的長為 ${L_L_str}$、寬為 ${W_L_str}$，其內部有一個長為 ${L_S_str}$、寬為 ${W_S_str}$ 的中空部分。試以 $x$ 的多項式表示藍色環狀區域的周長與面積。"
        final_answer = f"周長為 ${perimeter_str}$，面積為 ${area_str}$"
    else:
        question_text = f"一個大長方形的長為 ${L_L_str}$、寬為 ${W_L_str}$。從中挖去一個長為 ${L_S_str}$、寬為 ${W_S_str}$ 的小長方形，試以 $x$ 的多項式表示剩餘藍色部分的面積。"
        final_answer = f"${area_str}$"

    return {
        "question_text": question_text,
        "answer": final_answer,
        "correct_answer": final_answer
    }

def generate_geometry_find_dimension_problem():
    """Generates a problem that requires polynomial division to find a geometric dimension."""
    shape = random.choice(['trapezoid', 'triangle'])

    if shape == 'trapezoid':
        h, b_sum = None, None
        two_area = [1] # Dummy value with odd number
        while any(c % 2 != 0 for c in two_area):
            h = create_binomial(force_positive_x=True)
            b_sum = create_binomial(force_positive_x=True)
            two_area = poly_mul(b_sum, h)

        area = [int(c / 2) for c in two_area]
        
        B, C = b_sum
        if B <= 1: return generate_geometry_find_dimension_problem()
        B1 = random.randint(1, B - 1)
        B2 = B - B1
        C1 = random.randint(min(0, C), max(0, C)) if C!=0 else 0
        C2 = C - C1
        b1, b2 = [B1, C1], [B2, C2]

        b1_str, b2_str = binomial_to_str(b1), binomial_to_str(b2)
        area_str, h_str = poly_to_str(area), poly_to_str(h)
        question_text = f"一梯形的上底為 ${b1_str}$、下底為 ${b2_str}$、面積為 ${area_str}$，試以 $x$ 的多項式表示此梯形的高。"
        final_answer = f"${h_str}$"
    else: # triangle
        h, base = None, None
        two_area = [1]
        while any(c % 2 != 0 for c in two_area):
            h = create_binomial(force_positive_x=True)
            base = create_binomial(force_positive_x=True)
            two_area = poly_mul(base, h)

        area = [int(c / 2) for c in two_area]
        base_str, area_str, h_str = poly_to_str(base), poly_to_str(area), poly_to_str(h)
        question_text = f"一三角形的底為 ${base_str}$、面積為 ${area_str}$，試以 $x$ 的多項式表示此三角形的高。"
        final_answer = f"${h_str}$"

    return {
        "question_text": question_text,
        "answer": final_answer,
        "correct_answer": final_answer
    }

# --- Check Function ---

def check(user_answer, correct_answer):
    """Checks if the user's answer for a polynomial expression is correct."""
    def normalize(s):
        return s.replace('$', '').replace(' ', '').lower().replace('^', '**')

    user_ans_norm = normalize(user_answer)
    correct_ans_norm = normalize(correct_answer)
    
    is_correct = (user_ans_norm == correct_ans_norm)
    
    if not is_correct and '周長' in correct_ans_norm:
        try:
            corr_parts = correct_ans_norm.replace('周長為','p:').replace('面積為','a:').replace('，',',').split(',')
            user_parts = user_ans_norm.replace('周長為','p:').replace('面積為','a:').replace('，',',').split(',')
            corr_dict = {part.split(':')[0]: part.split(':')[1] for part in corr_parts if ':' in part}
            user_dict = {part.split(':')[0]: part.split(':')[1] for part in user_parts if ':' in part}
            if corr_dict == user_dict:
                is_correct = True
        except Exception:
            pass

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}