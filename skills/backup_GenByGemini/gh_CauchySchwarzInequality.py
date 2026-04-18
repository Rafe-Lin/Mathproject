import random
import math
from fractions import Fraction

def _get_gcd(a, b):
    """Calculates the greatest common divisor of two integers."""
    while b:
        a, b = b, a % b
    return a

def _get_lcm(a, b):
    """Calculates the least common multiple of two integers."""
    if a == 0 or b == 0:
        return 0
    # Ensure gcd is not zero before division
    common_divisor = _get_gcd(a, b)
    if common_divisor == 0: # Should not happen for non-zero a, b
        return 0
    return abs(a * b) // common_divisor

def generate_min_sum_squares_given_linear_sum(level):
    """
    Generates a problem of the type:
    Given $B_1 x + B_2 y (+ B_3 z) = C$, find min $A_1 x^2 + A_2 y^2 (+ A_3 z^2)$.
    """
    n_vars = 2
    if level >= 2 and random.random() < 0.5: # More variables for higher levels
        n_vars = 3

    var_names = ['x', 'y', 'z'][:n_vars]
    
    # 1. Choose coefficients c_i for squared terms (A_i = c_i^2).
    # These are used in the vector u = (c_1 x, c_2 y, ...)
    c_coeffs = [random.randint(1, 3) for _ in range(n_vars)]
    A_coeffs = [c**2 for c in c_coeffs] # A_i are the actual coefficients in the problem statement
    
    # 2. Choose v_i (coefficients for vector v). For simplicity, use 1s as in examples.
    v_coeffs = [1] * n_vars

    # 3. Determine K_ratio for the equality condition: c_i * x_i / v_i = K_ratio.
    # To ensure x_eq,i are integers, K_ratio must be a common multiple of c_i (since v_i=1).
    K_ratio_lcm = 1
    for c in c_coeffs:
        K_ratio_lcm = _get_lcm(K_ratio_lcm, c)
    if K_ratio_lcm == 0: K_ratio_lcm = 1 # Fallback for edge cases

    K_ratio_factor = random.choice([1, 2, 3])
    K_ratio = K_ratio_lcm * K_ratio_factor
    
    # Adjust K_ratio to ensure x_eq_vals are distinct and non-zero
    temp_x_eq_vals = [K_ratio // c for c in c_coeffs]
    initial_K_ratio = K_ratio # Store initial K_ratio to ensure distinct values
    retries = 0
    while (any(x == 0 for x in temp_x_eq_vals) or len(set(temp_x_eq_vals)) < n_vars) and retries < 10:
        K_ratio_factor += 1
        K_ratio = K_ratio_lcm * K_ratio_factor
        temp_x_eq_vals = [K_ratio // c for c in c_coeffs]
        retries += 1
    
    # If still not distinct/non-zero after retries, try simpler coefficients
    if retries >= 10:
        c_coeffs = [random.randint(1, 2) for _ in range(n_vars)]
        A_coeffs = [c**2 for c in c_coeffs]
        K_ratio_lcm = 1
        for c in c_coeffs:
            K_ratio_lcm = _get_lcm(K_ratio_lcm, c)
        if K_ratio_lcm == 0: K_ratio_lcm = 1
        K_ratio = K_ratio_lcm * random.choice([1, 2])
        temp_x_eq_vals = [K_ratio // c for c in c_coeffs]

    x_eq_vals = temp_x_eq_vals

    # 4. Calculate B_i = c_i * v_i. These are coefficients for the given linear equation.
    B_coeffs = [c * v for c, v in zip(c_coeffs, v_coeffs)]
    
    # 5. Calculate C_linear_sum = sum(B_i * x_eq,i). This is the RHS of the given linear equation.
    C_linear_sum = sum(b * x_val for b, x_val in zip(B_coeffs, x_eq_vals))

    # 6. Calculate min_val = C_linear_sum^2 / sum(v_i^2).
    sum_v_sq = sum(v**2 for v in v_coeffs)
    min_value = Fraction(C_linear_sum**2, sum_v_sq)

    # Construct question text
    B_terms = []
    for i in range(n_vars):
        if B_coeffs[i] == 1: B_terms.append(f"{var_names[i]}")
        elif B_coeffs[i] == -1: B_terms.append(f"-{var_names[i]}")
        elif B_coeffs[i] > 0: B_terms.append(f"{B_coeffs[i]}{var_names[i]}")
        else: B_terms.append(f"({B_coeffs[i]}{var_names[i]})") 
    
    A_sq_terms = []
    for i in range(n_vars):
        if A_coeffs[i] == 1: A_sq_terms.append(f"{var_names[i]}^{{2}}")
        else: A_sq_terms.append(f"{A_coeffs[i]}{var_names[i]}^{{2}}")
    
    question_text = (
        f"已知實數 ${', '.join(var_names)}$ 滿足 ${'+'.join(B_terms)} = {C_linear_sum}$，"
        f"求 ${'+'.join(A_sq_terms)}$ 的最小值，及此時 ${', '.join(var_names)}$ 的值。"
    )

    # Construct correct answer string
    answer_parts = [f"{min_value}"]
    for i in range(n_vars):
        answer_parts.append(f"{var_names[i]}={x_eq_vals[i]}")
    correct_answer = "; ".join(answer_parts)

    # Solution steps (for detailed feedback/explanation)
    u_vec_terms = [f'{c}{v}' for c, v in zip(c_coeffs, var_names)]
    v_vec_terms_str = [str(v) for v in v_coeffs]

    B_terms_latex = []
    for i in range(n_vars):
        if B_coeffs[i] == 1: B_terms_latex.append(f"{var_names[i]}")
        elif B_coeffs[i] == -1: B_terms_latex.append(f"-{var_names[i]}")
        elif B_coeffs[i] > 0: B_terms_latex.append(f"{B_coeffs[i]}{var_names[i]}")
        else: B_terms_latex.append(f"({B_coeffs[i]}{var_names[i]})") 
    
    A_sq_terms_latex = []
    for i in range(n_vars):
        if A_coeffs[i] == 1: A_sq_terms_latex.append(f"{var_names[i]}^{{2}}")
        else: A_sq_terms_latex.append(f"{A_coeffs[i]}{var_names[i]}^{{2}}")

    v_sq_terms_latex = [f"{v}^{{2}}" for v in v_coeffs]

    equality_cond_terms = [f"\\frac{{{c_coeffs[i]}{var_names[i]}}}{{{v_coeffs[i]}}}" for i in range(n_vars)]
    equality_simple_terms = [f"{c_coeffs[i]}{var_names[i]}" for i in range(n_vars)]

    solution_steps = {
        "u_vector": f"令向量 $\\mathbf{{u}} = ({', '.join(u_vec_terms)})$，$\\mathbf{{v}} = ({', '.join(v_vec_terms_str)})$。",
        "cauchy_schwarz_setup": (
            f"利用柯西不等式 $(\\mathbf{{u}} \\cdot \\mathbf{{v}})^2 \\le |\\!|\\mathbf{{u}}|\\!|^2 |\\!|\\mathbf{{v}}|\\!|^2$，得<br>"
            f"$(\\left({'+'.join(B_terms_latex)}\\right))^2 \\le "
            f"(\\left({'+'.join(A_sq_terms_latex)}\\right)) "
            f"(\\left({'+'.join(v_sq_terms_latex)}\\right))$"
        ),
        "substitution": (
            f"將 ${'+'.join(B_terms_latex)} = {C_linear_sum}$ 代入，得<br>"
            f"${C_linear_sum}^{{2}} \\le (\\left({'+'.join(A_sq_terms_latex)}\\right)) \\times ({sum_v_sq})$<br>"
            f"${C_linear_sum**2} \\le (\\left({'+'.join(A_sq_terms_latex)}\\right)) \\times ({sum_v_sq})$"
        ),
        "inequality_result": (
            f"整理得 ${'+'.join(A_sq_terms_latex)} \\ge {min_value}$。"
        ),
        "equality_condition": (
            f"等號成立於 ${' = '.join(equality_cond_terms)}$，"
            f"即 ${' = '.join(equality_simple_terms)}$。"
        ),
        "solve_system": (
            f"解聯立方程式<br>"
            f"$\\begin{{cases}} {B_terms_latex[0]}{'+' if n_vars>1 else ''}{B_terms_latex[1]}{'+' if n_vars==3 else ''}{B_terms_latex[2] if n_vars==3 else ''} = {C_linear_sum} \\\\ "
            f"{' = '.join(equality_simple_terms)} \\end{{cases}}$<br>"
            f"得 ${', '.join([f'{v}={x_val}' for v, x_val in zip(var_names, x_eq_vals)])}$。"
        ),
        "final_answer": (
            f"故當 ${', '.join([f'{v}={x_val}' for v, x_val in zip(var_names, x_eq_vals)])}$ 時，"
            f"${'+'.join(A_sq_terms_latex)}$ 有最小值 ${min_value}$。"
        )
    }
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution_steps": solution_steps
    }

def generate_max_min_linear_sum_given_sum_squares(level):
    """
    Generates a problem of the type:
    Given $A_1 x^2 + A_2 y^2 (+ A_3 z^2) = C$, find max/min $B_1 x + B_2 y (+ B_3 z)$.
    """
    n_vars = 2
    if level >= 2 and random.random() < 0.5: # More variables for higher levels
        n_vars = 3

    var_names = ['x', 'y', 'z'][:n_vars]

    # 1. Choose coefficients c_i for squared terms (A_i = c_i^2).
    c_coeffs = [random.randint(1, 3) for _ in range(n_vars)]
    A_coeffs = [c**2 for c in c_coeffs]

    # 2. Choose coefficients B_i for linear sum. Allow negative.
    B_coeffs = []
    for _ in range(n_vars):
        b = random.randint(1, 4)
        if random.random() < 0.5: b = -b
        B_coeffs.append(b)
    
    # 3. Choose the proportionality constant 't' from the equality condition (A_i x_i / B_i = t).
    # To ensure x_eq,i are integers, 't' must be a common multiple of A_i / gcd(A_i, B_i).
    # Simple approach: let 't' be a multiple of the LCM of all A_i.
    t_lcm = 1
    for A in A_coeffs:
        t_lcm = _get_lcm(t_lcm, A)
    if t_lcm == 0: t_lcm = 1

    t_factor = random.choice([1, 2])
    t_val = t_lcm * t_factor
    if t_val == 0: t_val = 1 # Fallback
    
    # 4. Calculate x_eq,i for the positive case, using x_i = t * B_i / A_i.
    x_eq_vals_pos = []
    retries = 0
    while True:
        temp_x_eq_vals = []
        for i in range(n_vars):
            x_val = t_val * B_coeffs[i] // A_coeffs[i]
            temp_x_eq_vals.append(x_val)
        
        if all(x == 0 for x in temp_x_eq_vals) and retries < 10:
            # Re-generate B_coeffs if all x_eq are zero
            B_coeffs = []
            for _ in range(n_vars):
                b = random.randint(1, 4)
                if random.random() < 0.5: b = -b
                B_coeffs.append(b)
            retries += 1
            if retries >= 10: # If still failing, simplify coefficients
                c_coeffs = [random.randint(1, 2) for _ in range(n_vars)]
                A_coeffs = [c**2 for c in c_coeffs]
                t_lcm = 1
                for A in A_coeffs: t_lcm = _get_lcm(t_lcm, A)
                if t_lcm == 0: t_lcm = 1
                t_val = t_lcm * random.choice([1, 2])
        else:
            x_eq_vals_pos = temp_x_eq_vals
            break

    # 5. Calculate C_sum_squares = sum(A_i * x_eq,i^2). This is the RHS of the given sum of squares equation.
    C_sum_squares = sum(A * x_val**2 for A, x_val in zip(A_coeffs, x_eq_vals_pos))

    # 6. Calculate sum(B_i^2 / A_i), used in the CS inequality.
    sum_B_sq_over_A = sum(Fraction(b**2, A) for b, A in zip(B_coeffs, A_coeffs))
    
    # Calculate the absolute max/min value of the linear sum.
    # (Linear sum)^2 <= C_sum_squares * sum(B_i^2 / A_i)
    max_min_val_sq_fraction = Fraction(C_sum_squares) * sum_B_sq_over_A
    max_min_val_sq = max_min_val_sq_fraction.numerator // max_min_val_sq_fraction.denominator
    max_min_val_abs = int(math.sqrt(max_min_val_sq))

    # Calculate the actual max/min linear sum values
    max_answer_linear_sum = sum(b * x_val for b, x_val in zip(B_coeffs, x_eq_vals_pos))
    min_answer_linear_sum = sum(b * (-x_val) for b, x_val in zip(B_coeffs, x_eq_vals_pos))
    
    # Ensure max_answer_linear_sum is truly the max and min_answer_linear_sum is min
    x_eq_max_vals = list(x_eq_vals_pos) # Copy for max
    x_eq_min_vals = [-x for x in x_eq_vals_pos] # Copy for min
    
    if max_answer_linear_sum < min_answer_linear_sum:
        max_answer_linear_sum, min_answer_linear_sum = min_answer_linear_sum, max_answer_linear_sum
        x_eq_max_vals, x_eq_min_vals = x_eq_min_vals, x_eq_max_vals # Swap x values too

    # Construct question text
    A_sq_terms = []
    for i in range(n_vars):
        if A_coeffs[i] == 1: A_sq_terms.append(f"{var_names[i]}^{{2}}")
        else: A_sq_terms.append(f"{A_coeffs[i]}{var_names[i]}^{{2}}")
    
    B_terms = []
    for i in range(n_vars):
        if B_coeffs[i] == 1: B_terms.append(f"{var_names[i]}")
        elif B_coeffs[i] == -1: B_terms.append(f"-{var_names[i]}")
        elif B_coeffs[i] > 0: B_terms.append(f"{B_coeffs[i]}{var_names[i]}")
        else: B_terms.append(f"({B_coeffs[i]}{var_names[i]})") 

    question_text = (
        f"已知實數 ${', '.join(var_names)}$ 滿足 ${'+'.join(A_sq_terms)} = {C_sum_squares}$，"
        f"求 ${'+'.join(B_terms)}$ 的最大值與最小值，及此時 ${', '.join(var_names)}$ 的值。"
    )

    # Construct correct answer string
    answer_parts = [
        f"最大值{max_answer_linear_sum}",
        f"最小值{min_answer_linear_sum}",
        f"Max時: {', '.join([f'{v}={x_val}' for v, x_val in zip(var_names, x_eq_max_vals)])}",
        f"Min時: {', '.join([f'{v}={x_val}' for v, x_val in zip(var_names, x_eq_min_vals)])}"
    ]
    correct_answer = "; ".join(answer_parts)

    # Solution steps
    u_vec_terms = [f"\\sqrt{{{A_coeffs[i]}}}{var_names[i]}" for i in range(n_vars)]
    v_vec_terms = []
    for i in range(n_vars):
        if math.isqrt(A_coeffs[i])**2 == A_coeffs[i]:
            v_vec_terms.append(f"\\frac{{{B_coeffs[i]}}}{{{math.isqrt(A_coeffs[i])}}}")
        else:
            v_vec_terms.append(f"\\frac{{{B_coeffs[i]}}}{{\\sqrt{{{A_coeffs[i]}}}}}")

    sum_u_sq_terms_latex = []
    for i in range(n_vars):
        if A_coeffs[i] == 1: sum_u_sq_terms_latex.append(f"{var_names[i]}^{{2}}")
        else: sum_u_sq_terms_latex.append(f"{A_coeffs[i]}{var_names[i]}^{{2}}")

    sum_v_sq_terms_latex = []
    for i in range(n_vars):
        if A_coeffs[i] == 1:
            if B_coeffs[i] == 1: sum_v_sq_terms_latex.append("1")
            elif B_coeffs[i] == -1: sum_v_sq_terms_latex.append("1")
            else: sum_v_sq_terms_latex.append(f"{B_coeffs[i]}^{{2}}")
        else:
            if B_coeffs[i] == 1: sum_v_sq_terms_latex.append(f"\\frac{{1}}{{{A_coeffs[i]}}}")
            elif B_coeffs[i] == -1: sum_v_sq_terms_latex.append(f"\\frac{{1}}{{{A_coeffs[i]}}}")
            else: sum_v_sq_terms_latex.append(f"\\frac{{{B_coeffs[i]}^{{2}}}}{{{A_coeffs[i]}}}")

    equality_cond_terms = [f"\\frac{{{A_coeffs[i]}{var_names[i]}}}{{{B_coeffs[i]}}}" for i in range(n_vars)]
    equality_str = " = ".join(equality_cond_terms)

    sum_B_sq_over_A_str = f"{sum_B_sq_over_A.numerator}{'' if sum_B_sq_over_A.denominator==1 else f'/{sum_B_sq_over_A.denominator}'}"
    linear_sum_expr_latex = '+'.join(B_terms)

    solution_steps = {
        "u_v_def": (
            f"令向量 $\\mathbf{{u}} = ({', '.join(u_vec_terms)})$，$\\mathbf{{v}} = ({', '.join(v_vec_terms)})$。"
        ),
        "cauchy_schwarz_setup": (
            f"利用柯西不等式 $(\\mathbf{{u}} \\cdot \\mathbf{{v}})^2 \\le |\\!|\\mathbf{{u}}|\\!|^2 |\\!|\\mathbf{{v}}|\\!|^2$，得<br>"
            f"$(\\left({linear_sum_expr_latex}\\right))^2 \\le "
            f"(\\left({'+'.join(sum_u_sq_terms_latex)}\\right)) "
            f"(\\left({'+'.join(sum_v_sq_terms_latex)}\\right))$"
        ),
        "substitution": (
            f"將 ${'+'.join(A_sq_terms)} = {C_sum_squares}$ 代入，得<br>"
            f"$(\\left({linear_sum_expr_latex}\\right))^2 \\le {C_sum_squares} \\times ({sum_B_sq_over_A_str})$<br>"
            f"$(\\left({linear_sum_expr_latex}\\right))^2 \\le {max_min_val_sq}"
        ),
        "inequality_result": (
            f"整理得 $-{max_min_val_abs} \\le {linear_sum_expr_latex} \\le {max_min_val_abs}$。"
        ),
        "equality_condition": (
            f"等號成立於 ${equality_str}$。"
        ),
        "solve_system": (
            f"令此比值為 $t$，則 ${', '.join([f'{v}={B_coeffs[i]}t/{A_coeffs[i]}' for i, v in enumerate(var_names)])}$。<br>"
            f"代入 ${'+'.join(A_sq_terms)} = {C_sum_squares}$，整理得 $t^2 \\times ({sum_B_sq_over_A_str}) = {C_sum_squares}$，解得 $t = \\pm {t_val}$。"
            f"故當 $t = {t_val}$ 時：${', '.join([f'{v}={x_val}' for v, x_val in zip(var_names, x_eq_max_vals)])}$；<br>"
            f"當 $t = -{t_val}$ 時：${', '.join([f'{v}={x_val}' for v, x_val in zip(var_names, x_eq_min_vals)])}$。"
        ),
        "final_answer": (
            f"故當 ${', '.join([f'{v}={x_val}' for v, x_val in zip(var_names, x_eq_max_vals)])}$ 時，"
            f"${linear_sum_expr_latex}$ 有最大值 ${max_answer_linear_sum}$；<br>"
            f"當 ${', '.join([f'{v}={x_val}' for v, x_val in zip(var_names, x_eq_min_vals)])}$ 時，"
            f"${linear_sum_expr_latex}$ 有最小值 ${min_answer_linear_sum}$。"
        )
    }

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution_steps": solution_steps
    }

def generate(level=1):
    problem_type_choice = random.choice([
        'min_sum_squares_given_linear_sum',
        'max_min_linear_sum_given_sum_squares'
    ])

    if problem_type_choice == 'min_sum_squares_given_linear_sum':
        return generate_min_sum_squares_given_linear_sum(level)
    else: # 'max_min_linear_sum_given_sum_squares'
        return generate_max_min_linear_sum_given_sum_squares(level)

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    Expected user_answer formats:
    - For min_sum_squares: "VALUE; x=X_VAL; y=Y_VAL"
    - For max_min_linear_sum: "最大值MAX_VAL; 最小值MIN_VAL; Max時: x=X_MAX, y=Y_MAX; Min時: x=X_MIN, y=Y_MIN"
    """
    user_answer = user_answer.strip().replace(' ', '').replace('$', '')
    correct_answer = correct_answer.strip().replace(' ', '').replace('$', '')

    user_parts_raw = [part.strip() for part in user_answer.split(';')]
    correct_parts_raw = [part.strip() for part in correct_answer.split(';')]

    if len(user_parts_raw) != len(correct_parts_raw):
        return {"correct": False, "result": "答案格式不符或資訊不完整。請檢查最大/最小值以及對應的變數值。"}

    def parse_value_part(part_str):
        if part_str.startswith("最小值"):
            return "最小值", float(Fraction(part_str[3:]))
        elif part_str.startswith("最大值"):
            return "最大值", float(Fraction(part_str[3:]))
        elif part_str.startswith("Max時:"):
            return "Max時", {p.split('=')[0]: float(Fraction(p.split('=')[1])) for p in part_str[5:].split(',')}
        elif part_str.startswith("Min時:"):
            return "Min時", {p.split('=')[0]: float(Fraction(p.split('=')[1])) for p in part_str[5:].split(',')}
        else: # Likely a variable assignment or just the min value
            if '=' in part_str:
                key, val = part_str.split('=')
                return key, float(Fraction(val))
            else: # It's just the value for min_sum_squares
                return "最小值", float(Fraction(part_str))

    user_parsed = {}
    for part in user_parts_raw:
        key, val = parse_value_part(part)
        user_parsed[key] = val

    correct_parsed = {}
    for part in correct_parts_raw:
        key, val = parse_value_part(part)
        correct_parsed[key] = val

    is_correct = True
    result_messages = []

    for key, correct_val in correct_parsed.items():
        if key not in user_parsed:
            is_correct = False
            result_messages.append(f"您的答案缺少 '{key}' 的值。")
            continue
        
        user_val = user_parsed[key]

        if isinstance(correct_val, float):
            if not math.isclose(user_val, correct_val, rel_tol=1e-9, abs_tol=1e-9):
                is_correct = False
                result_messages.append(f"'{key}' 的值不正確。您的答案是 {user_val}，正確答案是 {correct_val}。")
        elif isinstance(correct_val, dict): # For Max時/Min時 variable assignments
            if not isinstance(user_val, dict):
                is_correct = False
                result_messages.append(f"'{key}' 的格式不正確。應為變數賦值列表。")
                continue
            
            if len(user_val) != len(correct_val):
                is_correct = False
                result_messages.append(f"'{key}' 的變數數量不符。")
            else:
                for sub_key, sub_correct_val in correct_val.items():
                    if sub_key not in user_val or not math.isclose(user_val[sub_key], sub_correct_val, rel_tol=1e-9, abs_tol=1e-9):
                        is_correct = False
                        result_messages.append(f"'{key}' 中的變數 '{sub_key}' 值不正確。")
        else: # Fallback for unexpected types
            if user_val != correct_val:
                is_correct = False
                result_messages.append(f"'{key}' 的值不正確。您的答案是 {user_val}，正確答案是 {correct_val}。")
            
    if not result_messages:
        result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    else:
        result_text = "答案不完全正確。<br>" + "<br>".join(result_messages)

    return {"correct": is_correct, "result": result_text, "next_question": True}